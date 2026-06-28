/*
=========================================================
            ESP32 MAC ADDRESS READER
=========================================================

This program prints the unique Wi-Fi Station (STA)
MAC (Media Access Control) Address of the ESP32.

Example MAC Address Format:

XX:XX:XX:XX:XX:XX

Example Output:

30:C6:F7:12:34:56

Notes:
- The MAC Address is 6 bytes (48 bits) long.
- Each "XX" is a hexadecimal byte (00 to FF).
- Every ESP32 has a unique factory-programmed MAC Address.

=========================================================
*/

#include <WiFi.h>

void setup()
{
  // Start Serial Communication
  Serial.begin(115200);

  // Initialize Wi-Fi in Station mode
  WiFi.mode(WIFI_STA);

  // Print the ESP32 MAC Address
  Serial.print("ESP32 MAC Address: ");
  Serial.println(WiFi.macAddress());
}

void loop()
{
  // Nothing to do
}
