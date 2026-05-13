#define LDR_PIN 34

void setup() {
  Serial.begin(115200);
  pinMode(LDR_PIN, INPUT);
}

void loop() {
  int ldrState = digitalRead(LDR_PIN);

  if (ldrState == HIGH) {
    Serial.println("DARK (Night)");
  } else {
    Serial.println("BRIGHT (Day)");
  }

  delay(500);
}