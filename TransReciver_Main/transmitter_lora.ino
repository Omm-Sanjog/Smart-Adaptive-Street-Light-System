#include <SPI.h>
#include <LoRa.h>
#include <PZEM004Tv30.h>
#include <RBDdimmer.h>

// ---------------- NODE DETAILS ----------------
#define NODE_ID "SL-01"
#define LOCATION "IIT_GATE_1"

// ---------------- PIN DEFINITIONS ----------------
#define LDR_PIN 34
#define MOTION_PIN 27
#define RELAY_PIN 26

#define DIMMER_PIN 25
#define ZC_PIN 4

#define LORA_SS 5
#define LORA_RST 14
#define LORA_DIO0 2

// ---------------- OBJECTS ----------------
dimmerLamp dimmer(DIMMER_PIN, ZC_PIN);
HardwareSerial pzemSerial(2);
PZEM004Tv30 pzem(pzemSerial, 16, 17);

// ---------------- GLOBAL VARIABLES ----------------
bool isNight = false;
bool motionDetected = false;

float voltage = 0;
float current = 0;
float power = 0;

int brightness = 0;

// ---------------- TIMING ----------------
unsigned long lastLoRaTime = 0;
const unsigned long LORA_INTERVAL = 300000; // 5 minutes

// ======================================================
// SETUP
// ======================================================
void setup() {
  Serial.begin(115200);

  pinMode(LDR_PIN, INPUT);
  pinMode(MOTION_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, LOW);

  // Dimmer init
  dimmer.begin(NORMAL_MODE, ON);

  // LoRa init
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(433E6)) {
    Serial.println("LoRa Init Failed!");
    while (1);
  }

  Serial.println("Transmitter Ready");
}

// ======================================================
// LOOP
// ======================================================
void loop() {
  readSensors();
  updateLightingLogic();
  controlRelay();
  controlDimmer();
  readEnergy();

  if (millis() - lastLoRaTime >= LORA_INTERVAL) {
    sendLoRaData();
    lastLoRaTime = millis();
  }
}

// ======================================================
// FUNCTIONS
// ======================================================

void readSensors() {
  isNight = digitalRead(LDR_PIN);
  motionDetected = digitalRead(MOTION_PIN);
}

void updateLightingLogic() {
  if (!isNight) {
    brightness = 0;
  } else {
    brightness = motionDetected ? 100 : 30;
  }
}

void controlRelay() {
  digitalWrite(RELAY_PIN, isNight ? HIGH : LOW);
}

void controlDimmer() {
  dimmer.setPower(brightness);
}

void readEnergy() {
  voltage = pzem.voltage();
  current = pzem.current();
  power = pzem.power();
}

void sendLoRaData() {

  String data = "";

  data += "ID:" + String(NODE_ID);
  data += ",Loc:" + String(LOCATION);
  data += ",N:" + String(isNight);
  data += ",M:" + String(motionDetected);
  data += ",B:" + String(brightness);
  data += ",V:" + String(voltage);
  data += ",I:" + String(current);
  data += ",P:" + String(power);

  LoRa.beginPacket();
  LoRa.print(data);
  LoRa.endPacket();

  Serial.println("LoRa Sent:");
  Serial.println(data);
}
