
#include <WiFi.h>
#include <PubSubClient.h>
#include <BlynkSimpleEsp32.h>
#include "config.h"

const char* mqtt_server = "broker.hivemq.com";
WiFiClient espClient;
PubSubClient client(espClient);


#define VIB_PIN      13
#define TEMP_PIN     34
#define CURR_PIN     35

#define MOTOR_IN1    27
#define MOTOR_IN2    14


BlynkTimer timer;
volatile bool ml_fault = false;



void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("MQTT connecting...");
    if (client.connect("ESP32Client_PM")) {
      Serial.println("connected");
      client.subscribe("esp32/fault_prediction");
    } else {
      Serial.println("retrying...");
      delay(1000);
    }
  }
}



void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String msg;
  for (int i = 0; i < length; i++) msg += (char)payload[i];

  if (String(topic) == "esp32/fault_prediction") {
    ml_fault = (msg == "1" || msg == "true");
    Serial.print("ML Prediction Fault = ");
    Serial.println(ml_fault);
  }
}



void sendSensorData() {

  // ---- SENSOR READ ----
  int vib = digitalRead(VIB_PIN);

  int tADC = analogRead(TEMP_PIN);
  float tVolt = tADC * (3.3 / 4095.0);
  float tempC = tVolt * 100.0;

  int cADC = analogRead(CURR_PIN);
  float current = cADC * (3.3 / 4095.0);

  // ---- MQTT SEND ----
  if (!client.connected()) reconnectMQTT();
  client.loop();

  String payload = "{";
  payload += "\"temperature\":" + String(tempC,2) + ",";
  payload += "\"current\":" + String(current,3) + ",";
  payload += "\"vibration\":" + String(vib);
  payload += "}";

  client.publish("machine/sensors", payload.c_str());

  // ---- MOTOR CONTROL ----
  if (ml_fault) {
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, LOW);   // Stop motor
  } else {
    digitalWrite(MOTOR_IN1, LOW);
    digitalWrite(MOTOR_IN2, HIGH);  // Run motor
  }

  

  // ---- BLYNK ----
  Blynk.virtualWrite(V0, tempC);
  Blynk.virtualWrite(V1, current);
  Blynk.virtualWrite(V2, vib);
  Blynk.virtualWrite(V3, ml_fault);

  if (ml_fault)
    Blynk.logEvent("failure_predicted","ML predicted failure risk");

  
  Serial.print("Temp: ");
  Serial.print(tempC);
  Serial.print("  Current: ");
  Serial.print(current);
  Serial.print("  Vib: ");
  Serial.print(vib);
  Serial.print("  ML Fault: ");
  Serial.println(ml_fault);
}



void setup() {
  Serial.begin(115200);

  pinMode(VIB_PIN, INPUT);
  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  

  

  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);

  client.setServer(mqtt_server, 1883);
  client.setCallback(mqttCallback);

  timer.setInterval(2000L, sendSensorData);
}



void loop() {
  Blynk.run();
  timer.run();

  if (!client.connected()) reconnectMQTT();
  client.loop();
}