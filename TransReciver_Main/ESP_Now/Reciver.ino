#include <WiFi.h>
#include <esp_now.h>

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

SensorData incomingData;

//=====================================================

void OnDataRecv(const esp_now_recv_info_t *recv_info,
                const uint8_t *incomingDataBytes,
                int len)
{
  memcpy(&incomingData,incomingDataBytes,sizeof(incomingData));

  Serial.println("--------------------------------");

  Serial.print("Node ID : ");
  Serial.println(incomingData.nodeID);

  Serial.print("Location : ");
  Serial.println(incomingData.location);

  Serial.print("Night : ");
  Serial.println(incomingData.isNight);

  Serial.print("Motion : ");
  Serial.println(incomingData.motion);

  Serial.print("Brightness : ");
  Serial.println(incomingData.brightness);

  Serial.print("Voltage : ");
  Serial.print(incomingData.voltage);
  Serial.println(" V");

  Serial.print("Current : ");
  Serial.print(incomingData.current);
  Serial.println(" A");

  Serial.print("Power : ");
  Serial.print(incomingData.power);
  Serial.println(" W");

  Serial.println("--------------------------------");
}

//=====================================================

void setup()
{
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);

  Serial.print("Receiver MAC Address : ");
  Serial.println(WiFi.macAddress());

  if(esp_now_init()!=ESP_OK)
  {
    Serial.println("ESP-NOW Init Failed");
    while(true);
  }

  esp_now_register_recv_cb(OnDataRecv);

  Serial.println("ESP-NOW Receiver Ready");
}

void loop()
{

}
