#include <SPI.h>
#include <LoRa.h>

// -------- LoRa Pins --------
#define LORA_SS 5
#define LORA_RST 14
#define LORA_DIO0 2

void setup() {
  Serial.begin(115200);

  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(433E6)) {
    Serial.println("LoRa Init Failed!");
    while (1);
  }

  Serial.println("Receiver Ready");
}

void loop() {
  int packetSize = LoRa.parsePacket();

  if (packetSize) {
    String receivedData = "";

    while (LoRa.available()) {
      receivedData += (char)LoRa.read();
    }

    Serial.println("================================");
    Serial.println("Received Data:");
    Serial.println(receivedData);
    Serial.println("================================");
  }
}
