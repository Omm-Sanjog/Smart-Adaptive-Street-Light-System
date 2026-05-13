#define MOTION_PIN 27

void setup() {
  Serial.begin(115200);
  pinMode(MOTION_PIN, INPUT);
}

void loop() {
  int motion = digitalRead(MOTION_PIN);

  if (motion == HIGH) {
    Serial.println("Motion Detected!");
  } else {
    Serial.println("No Motion");
  }

  delay(500);
}