import asyncio
import csv
import json
import os
import re
import sys
import time
import threading
import serial
import serial.tools.list_ports
from datetime import datetime

# ─────────────────────────────────────────────────────
# CONFIGURATION  (edit these if needed)
# ─────────────────────────────────────────────────────
WS_HOST        = "localhost"
WS_PORT        = 8765
DEFAULT_BAUD   = 115200

LOG_DIR        = os.path.dirname(os.path.abspath(__file__))
CSV_FILENAME   = "data.csv"
CSV_PATH       = os.path.join(LOG_DIR, CSV_FILENAME)

CSV_HEADER = [
    "timestamp", "node_id", "location",
    "night", "motion", "brightness_pct",
    "voltage_V", "current_A", "power_W",
    "energy_kWh", "rssi"
]

# ─────────────────────────────────────────────────────
# TERMINAL COLOURS
# ─────────────────────────────────────────────────────
CY  = "\033[96m"   # cyan
GR  = "\033[92m"   # green
YL  = "\033[93m"   # yellow
RD  = "\033[91m"   # red
MG  = "\033[95m"   # magenta
RS  = "\033[0m"    # reset
BD  = "\033[1m"    # bold
DM  = "\033[2m"    # dim

def cc(col, t): return f"{col}{t}{RS}"
def bold(t):    return f"{BD}{t}{RS}"
def dim(t):     return f"{DM}{t}{RS}"

# ─────────────────────────────────────────────────────
# SHARED STATE  (thread-safe via asyncio queue + lock)
# ─────────────────────────────────────────────────────
connected_clients = set()        # WebSocket clients
energy_state      = {}           # {node_id: {eAcc, lastTs}}
packet_count      = 0
row_count         = 0

# asyncio event loop (set in main)
_loop = None

# ─────────────────────────────────────────────────────
# PORT / BAUD SELECTION
# ─────────────────────────────────────────────────────
def pick_port():
    ports = sorted(serial.tools.list_ports.comports(), key=lambda p: p.device)
    if not ports:
        print(cc(RD, "\n✗ No serial ports found. Is the receiver ESP32 plugged in?\n"))
        sys.exit(1)

    print(cc(CY, "\n┌─ Available Serial Ports " + "─"*30))
    for i, p in enumerate(ports):
        print(f"│  [{i+1}] {bold(p.device)}  —  {dim(p.description or 'Unknown')}")
    print(cc(CY, "└" + "─"*56))

    while True:
        try:
            choice = input(f"\n  Select port [1-{len(ports)}]: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(ports):
                return ports[idx].device
        except (ValueError, KeyboardInterrupt):
            pass
        print(cc(YL, "  Invalid choice, try again."))


def pick_baud():
    options = [9600, 19200, 57600, 115200, 230400]
    print(cc(CY, "\n┌─ Baud Rate " + "─"*43))
    for i, b in enumerate(options):
        marker = dim("◀ default") if b == DEFAULT_BAUD else ""
        print(f"│  [{i+1}] {b}  {marker}")
    print(cc(CY, "└" + "─"*56))

    choice = input(f"\n  Select [1-{len(options)}] or Enter for {DEFAULT_BAUD}: ").strip()
    if not choice:
        return DEFAULT_BAUD
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]
    except ValueError:
        pass
    return DEFAULT_BAUD

# ─────────────────────────────────────────────────────
# PACKET PARSING
# ─────────────────────────────────────────────────────
def parse_packet(line):
    """
    Parse: ID:SL-01,Loc:KIIT_GATE_1,N:1,M:0,B:30,V:230.5,I:1.23,P:284.5
    Returns dict or None.
    """
    if "ID:" not in line:
        return None

    # Optional RSSI appended by receiver
    rssi = None
    m = re.search(r"RSSI:\s*(-?\d+)", line, re.IGNORECASE)
    if m:
        rssi = int(m.group(1))
        line = re.sub(r",?\s*RSSI:\s*-?\d+", "", line, flags=re.IGNORECASE)

    fields = {}
    for part in line.split(","):
        part = part.strip()
        if ":" not in part:
            continue
        k, _, v = part.partition(":")
        fields[k.strip()] = v.strip()

    node_id = fields.get("ID")
    if not node_id:
        return None

    try:
        return {
            "node_id":    node_id,
            "location":   fields.get("Loc", node_id),
            "night":      int(fields.get("N", 0)),
            "motion":     int(fields.get("M", 0)),
            "brightness": float(fields.get("B", 0)),
            "voltage":    float(fields.get("V", 0)),
            "current":    float(fields.get("I", 0)),
            "power":      float(fields.get("P", 0)),
            "rssi":       rssi,
        }
    except (ValueError, TypeError):
        return None


def accumulate_energy(node_id, power_w, now_ts):
    if node_id not in energy_state:
        energy_state[node_id] = {"eAcc": 0.0, "lastTs": now_ts}
        return 0.0
    s = energy_state[node_id]
    dt_h = (now_ts - s["lastTs"]) / 3600.0
    s["eAcc"] += (power_w * dt_h) / 1000.0
    s["lastTs"] = now_ts
    return s["eAcc"]

# ─────────────────────────────────────────────────────
# WEBSOCKET SERVER
# ─────────────────────────────────────────────────────
async def ws_handler(websocket):
    """Handle one dashboard WebSocket connection."""
    addr = websocket.remote_address
    connected_clients.add(websocket)
    print(cc(GR, f"  ✔ Dashboard connected  ({addr[0]}:{addr[1]})  —  {len(connected_clients)} client(s)"))

    # Send a welcome / status message so the dashboard knows Python is alive
    try:
        await websocket.send(json.dumps({
            "type":    "status",
            "msg":     "Logger connected",
            "csv":     CSV_FILENAME,
            "ws_port": WS_PORT,
        }))
        # Keep connection alive — just wait until client disconnects
        await websocket.wait_closed()
    except Exception:
        pass
    finally:
        connected_clients.discard(websocket)
        print(cc(YL, f"  ✗ Dashboard disconnected  ({addr[0]}:{addr[1]})  —  {len(connected_clients)} client(s)"))


async def broadcast(payload: dict):
    """Send JSON payload to all connected dashboard clients."""
    if not connected_clients:
        return
    msg = json.dumps(payload)
    dead = set()
    for ws in connected_clients:
        try:
            await ws.send(msg)
        except Exception:
            dead.add(ws)
    connected_clients.difference_update(dead)


def broadcast_from_thread(payload: dict):
    """Thread-safe: schedule a broadcast on the asyncio loop."""
    if _loop and not _loop.is_closed():
        asyncio.run_coroutine_threadsafe(broadcast(payload), _loop)

# ─────────────────────────────────────────────────────
# SERIAL READER  (runs in a background thread)
# ─────────────────────────────────────────────────────
def serial_reader(port: str, baud: int, csv_writer, csv_file):
    global packet_count, row_count

    print(f"\n  {cc(GR,'▶')} Opening {bold(port)} @ {bold(str(baud))} baud…")
    try:
        ser = serial.Serial(port, baud, timeout=2)
        time.sleep(1.5)
    except serial.SerialException as e:
        print(cc(RD, f"\n  ✗ Cannot open port: {e}\n"))
        os._exit(1)

    print(f"  {cc(GR,'✔')} Serial port open.")
    print(f"  {cc(GR,'✔')} Logging to: {bold(CSV_PATH)}")
    print(cc(CY, "\n  " + "─"*56))

    while True:
        try:
            raw  = ser.readline()
            if not raw:
                continue
            line = raw.decode("utf-8", errors="replace").strip()
        except serial.SerialException as e:
            print(cc(RD, f"\n  ✗ Serial error: {e}"))
            break

        if not line:
            continue

        now    = datetime.now()
        now_ts = now.timestamp()
        ts_str = now.strftime("%Y-%m-%d %H:%M:%S")
        packet_count += 1

        # ── Print raw line ──
        prefix = dim(f"[{ts_str}] ")
        if "ID:" in line:
            print(f"{prefix}{cc(CY, line)}")
        elif re.search(r"err|fail", line, re.I):
            print(f"{prefix}{cc(RD, line)}")
        elif re.search(r"warn|high", line, re.I):
            print(f"{prefix}{cc(YL, line)}")
        else:
            print(f"{prefix}{dim(line)}")

        # ── Broadcast raw line to dashboard ──
        broadcast_from_thread({"type": "raw", "line": line, "ts": ts_str})

        # ── Parse ──
        pkt = parse_packet(line)
        if pkt is None:
            continue

        energy_kwh = accumulate_energy(pkt["node_id"], pkt["power"], now_ts)

        # ── Write CSV ──
        csv_writer.writerow([
            ts_str,
            pkt["node_id"],
            pkt["location"],
            pkt["night"],
            pkt["motion"],
            pkt["brightness"],
            pkt["voltage"],
            pkt["current"],
            pkt["power"],
            round(energy_kwh, 6),
            pkt["rssi"] if pkt["rssi"] is not None else "",
        ])
        csv_file.flush()
        row_count += 1

        # ── Broadcast parsed packet to dashboard ──
        broadcast_from_thread({
            "type":       "packet",
            "ts":         ts_str,
            "node_id":    pkt["node_id"],
            "location":   pkt["location"],
            "night":      pkt["night"],
            "motion":     pkt["motion"],
            "brightness": pkt["brightness"],
            "voltage":    pkt["voltage"],
            "current":    pkt["current"],
            "power":      pkt["power"],
            "energy_kwh": round(energy_kwh, 6),
            "rssi":       pkt["rssi"],
            "row":        row_count,
        })

        # ── Terminal summary ──
        print(
            f"  {cc(GR,'✔')} {bold(pkt['node_id'])} | "
            f"{'🌙 NIGHT' if pkt['night'] else '☀  DAY  '} | "
            f"{'🚶 MOTION' if pkt['motion'] else '  quiet '} | "
            f"B={pkt['brightness']:3.0f}% | "
            f"V={pkt['voltage']:6.2f}V | "
            f"I={pkt['current']:5.3f}A | "
            f"P={pkt['power']:6.1f}W | "
            f"E={energy_kwh:.4f}kWh | "
            f"WS clients={len(connected_clients)} | "
            f"Row #{row_count}"
        )

    ser.close()

# ─────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────
async def main_async(port, baud, csv_writer, csv_file):
    global _loop
    _loop = asyncio.get_running_loop()

    # Start WebSocket server
    try:
        import websockets
    except ImportError:
        print(cc(RD, "\n  ✗ 'websockets' not installed. Run:  pip install websockets\n"))
        sys.exit(1)

    server = await websockets.serve(ws_handler, WS_HOST, WS_PORT)
    print(cc(GR, f"\n  ✔ WebSocket server running at ws://{WS_HOST}:{WS_PORT}"))
    print(cc(GR,  "  ✔ Open streetlight_dashboard.html → it will auto-connect"))
    print(cc(YL,  "\n  Press Ctrl+C to stop.\n"))

    # Run serial reader in background thread
    t = threading.Thread(
        target=serial_reader,
        args=(port, baud, csv_writer, csv_file),
        daemon=True
    )
    t.start()

    # Keep event loop alive
    try:
        await asyncio.Future()   # runs forever
    except asyncio.CancelledError:
        pass
    finally:
        server.close()
        await server.wait_closed()


def main():
    print()
    print(bold(cc(CY, "╔══════════════════════════════════════════════════════════╗")))
    print(bold(cc(CY, "║   STREET LIGHT DASHBOARD — LOGGER + WEBSOCKET BRIDGE     ║")))
    print(bold(cc(CY, "╚══════════════════════════════════════════════════════════╝")))
    print(dim("  Serial → CSV logger  +  ws://localhost:8765 → Dashboard\n"))

    port = pick_port()
    baud = pick_baud()

    print(f"\n  {cc(CY,'CSV')} → {bold(CSV_PATH)}")
    print(f"  {cc(CY,'WS')}  → ws://{WS_HOST}:{WS_PORT}\n")

    try:
        csv_file   = open(CSV_PATH, "a", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        if csv_file.tell() == 0:          # new or empty file — write header
            csv_writer.writerow(CSV_HEADER)
            csv_file.flush()

        asyncio.run(main_async(port, baud, csv_writer, csv_file))

    except KeyboardInterrupt:
        pass
    finally:
        try:
            csv_file.flush()
            csv_file.close()
        except Exception:
            pass

    print()
    print(cc(CY, "  " + "─"*58))
    print(f"  {cc(GR,'✔')} Stopped.  {row_count} rows written to:")
    print(f"     {bold(CSV_PATH)}")
    print()


if __name__ == "__main__":
    main()
