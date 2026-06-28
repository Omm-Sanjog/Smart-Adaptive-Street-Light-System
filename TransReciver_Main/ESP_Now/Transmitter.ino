#include <WiFi.h>
#include <esp_now.h>

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

// ---------------- OBJECTS ----------------
dimmerLamp dimmer(DIMMER_PIN, ZC_PIN);

HardwareSerial pzemSerial(2);
PZEM004Tv30 pzem(pzemSerial, 16, 17);

// Replace with Receiver ESP32 MAC Address
uint8_t receiverMAC[] = {0x24,0x6F,0x28,0xAA,0xBB,0xCC};

// ---------------- DATA STRUCTURE ----------------
typedef struct {

  char nodeID[20];
  char location[30];

  bool isNight;
  bool motion;

  int brightness;

  float voltage;
  float current;
  float power;

} SensorData;

SensorData data;

// ---------------- VARIABLES ----------------
bool isNight = false;
bool motionDetected = false;

float voltage = 0;
float current = 0;
float power = 0;

int brightness = 0;

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL = 300000;   //5 min

// ===================================================

void OnDataSent(const wifi_tx_info_t *info, esp_now_send_status_t status)
{
  Serial.print("Delivery Status : ");

  if(status == ESP_NOW_SEND_SUCCESS)
    Serial.println("Success");
  else
    Serial.println("Failed");
}

// ===================================================

void setup()
{
  Serial.begin(115200);

  pinMode(LDR_PIN, INPUT);
  pinMode(MOTION_PIN, INPUT);
  pinMode(RELAY_PIN, OUTPUT);

  digitalWrite(RELAY_PIN, LOW);

  dimmer.begin(NORMAL_MODE, ON);

  WiFi.mode(WIFI_STA);

  if(esp_now_init()!=ESP_OK)
  {
    Serial.println("ESP-NOW Init Failed");
    while(true);
  }

  esp_now_register_send_cb(OnDataSent);

  esp_now_peer_info_t peerInfo={};

  memcpy(peerInfo.peer_addr,receiverMAC,6);
  peerInfo.channel=0;
  peerInfo.encrypt=false;

  if(esp_now_add_peer(&peerInfo)!=ESP_OK)
  {
    Serial.println("Peer Add Failed");
    while(true);
  }

  Serial.println("ESP-NOW Transmitter Ready");
}

// ===================================================

void loop()
{
  readSensors();

  updateLightingLogic();

  controlRelay();

  controlDimmer();

  readEnergy();

  if(millis()-lastSend>=SEND_INTERVAL)
  {
    strcpy(data.nodeID,NODE_ID);
    strcpy(data.location,LOCATION);

    data.isNight=isNight;
    data.motion=motionDetected;

    data.brightness=brightness;

    data.voltage=voltage;
    data.current=current;
    data.power=power;

    esp_now_send(receiverMAC,(uint8_t *)&data,sizeof(data));

    lastSend=millis();
  }
}

// ===================================================

void readSensors()
{
  isNight=digitalRead(LDR_PIN);
  motionDetected=digitalRead(MOTION_PIN);
}

void updateLightingLogic()
{
  if(!isNight)
      brightness=0;
  else
      brightness=motionDetected?100:30;
}

void controlRelay()
{
  digitalWrite(RELAY_PIN,isNight);
}

void controlDimmer()
{
  dimmer.setPower(brightness);
}

void readEnergy()
{
  voltage=pzem.voltage();
  current=pzem.current();
  power=pzem.power();
}
