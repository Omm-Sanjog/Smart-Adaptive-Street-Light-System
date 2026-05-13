#include <SPI.h>
#include <LoRa.h>

#define SS   5
#define RST  14
#define DIO0 26

void setup() {
  Serial.begin(115200);

  LoRa.setPins(SS, RST, DIO0);

  if (!LoRa.begin(433E6)) {
    Serial.println("LoRa Initialization Failed!");
    while (1);
  }

  Serial.println("LoRa Sender Initialized Successfully");
}

void loop() {
  Serial.println("Sending Packet...");

  LoRa.beginPacket();
  LoRa.print("Hello from ESP32");
  LoRa.endPacket();

  delay(2000);
}