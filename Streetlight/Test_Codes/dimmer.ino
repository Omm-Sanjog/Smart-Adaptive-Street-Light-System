#include <RBDdimmer.h>

#define DIMMER_PIN 25
#define ZC_PIN 4

dimmerLamp dimmer(DIMMER_PIN, ZC_PIN);

void setup() {
  Serial.begin(115200);
  dimmer.begin(NORMAL_MODE, ON);
}

void loop() {

  Serial.println("25% Brightness");
  dimmer.setPower(25);
  delay(5000);

  Serial.println("50% Brightness");
  dimmer.setPower(50);
  delay(5000);

  Serial.println("100% Brightness");
  dimmer.setPower(100);
  delay(5000);
}