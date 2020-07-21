#include <ESP8266WiFi.h>

#ifndef STASSID
#define STASSID "raven"
#define STAPSK  "supertajneheslo"
#endif

const char* ssid     = STASSID;
const char* password = STAPSK;

const char* host = "192.168.5.99";
const uint16_t port = 1717;
uint16_t tries = 5;

void setup() {
  Serial.begin(115200);

  // We start by connecting to a WiFi network

  Serial.println();
  Serial.println();
  Serial.println("Initialization of the LED and rellay");
  pinMode(12, OUTPUT); // Relay
  pinMode(13, OUTPUT); // LED
  digitalWrite(12, LOW); // rellay off
  digitalWrite(13, HIGH); // LED off
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  Serial.print("connecting to ");
  Serial.print(host);
  Serial.print(':');
  Serial.println(port);

  // Use WiFiClient class to create TCP connections
  WiFiClient client;
  while (!client.connect(host, port)) {
    Serial.println("connection failed");
    delay(5000);
    if (! tries--) {
        return;
    }
  }

  // This will send a string to the server
  Serial.println("sending data to server");
  if (client.connected()) {
    client.println("hello from ESP8266");
  }

  // wait for data to be available
  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > 5000) {
      Serial.println(">>> Client Timeout !");
      client.stop();
      delay(60000);
      return;
    }
  }

  String command = "";
  while (client.available()) {
    char ch = static_cast<char>(client.read());
    if (ch != '\n') {
      command += ch;
    } else {
      Serial.println('Received command: ' + command);
      if (command == "ZHASNI") {
        digitalWrite(12, LOW); // Switch off the rellay
        digitalWrite(13, HIGH); // Switch off the LED
      } else if ( command == "ROZNI") {
        digitalWrite(12, HIGH); // Rellay ON
        digitalWrite(13, LOW); // LED ON
      } else {
        Serial.println("Unknown command: " + command);
      }
    }
  }

  // Close the connection
  Serial.println();
  Serial.println("closing connection");
  client.stop();

  delay(300000); // execute once every 5 minutes, don't flood remote service
}
