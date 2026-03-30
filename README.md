#  AIoT-Powered Predictive Maintenance for Industrial Machinery

##  Overview
This project is an end-to-end **IoT + AI-based predictive maintenance system** that forecasts machine failures using real-time sensor data.

It integrates:
- ESP32 (sensor data collection)
- MQTT (communication)
- LSTM Deep Learning model (prediction)
- Streamlit dashboard (visualization)
- Blynk + Buzzer (alerts)

---

##  Problem Statement
Industries face:
- Unexpected machine failures
- High downtime costs
- Reactive maintenance

 This project predicts failures in advance using AI.

---

##  Solution
The system predicts:
- **Remaining Useful Life (RUL)** (in days)
- **Machine State** (Normal / Warning / Critical)

---

##  Model Performance

### LSTM Model
- MAE: ~0.4 days 
- RMSE: ~0.48
- R² Score: ~0.99

 Target achieved: MAE < 3 days

---

##  System Architecture

Sensors → ESP32 → MQTT → Python Listener → ML Model → Prediction  
                                             ↓  
                              Dashboard + Alerts + Storage  

---

##  Hardware Components

- ESP32
- LM35 (Temperature sensor)
- ACS712 (Current sensor)
- SW-420 (Vibration sensor)
- L298N Motor Driver

---

##  Features Used

- Temperature
- Vibration
- Current

---

##  Key Features

- Real-time data streaming
- AI-based failure prediction
- Early warning system
- Live dashboard
- Historical data logging

---

## 🔔 Alert Logic

| RUL (Days) | Status   | Action                  |
|-----------|----------|-------------------------|
| > 14      | Normal   | No alert                |
| 7 – 14    | Warning  | Blynk notification      |
| < 7       | Critical | Buzzer + Stop motor     |

---

## 🌐 Communication

- Protocol: MQTT  
- Broker: broker.hivemq.com  

Topics:
- machine/sensors
- esp32/prediction

---

## 📁 Project Structure
project/
│
├── esp32_code/
|  ├── esp32_main.ino
│  ├── config.h          
├── mqtt_listener.py
├── app.py
├── models/
│ ├── lstm_rul_model.keras
│ ├── lstm_scaler.pkl
├── data/
│ ├── latest_sensor.json
│ ├── sensor_history.csv

---

## ▶️ How to Run



### 1. Install dependencies

pip install -r requirements.txt


### 2. Start MQTT Listener

python mqtt_listener.py


### 3. Run Streamlit Dashboard

streamlit run app.py


### 4. Upload ESP32 Code
- Configure WiFi & Blynk
- Upload using Arduino IDE
## 🔌 ESP32 Setup

1. Open Arduino IDE
2. Install ESP32 board
3. Install libraries:
   - Blynk
   - PubSubClient
4. Update config.h
5. Upload code
---

## 🔍 Model Workflow

1. Collect sensor data  
2. Normalize using scaler  
3. Create sequences (window = 20)  
4. Train LSTM model  
5. Predict RUL  

---

## ⚠️ Limitations

- Uses low-cost sensors (not industrial-grade)
- Requires internet for cloud inference
- Needs historical data for training

---

## 🔮 Future Improvements

- Edge AI deployment (offline mode)
- Industrial-grade sensors
- Multi-machine monitoring
- Digital twin integration

---

## 🏭 Use Cases

- Manufacturing plants
- Automotive systems
- Smart factories 

---

## 💰 Business Impact

- Reduced downtime
- Lower maintenance cost
- Increased machine life
- Improved efficiency

---

## 🧑‍💻 Tech Stack

- Python
- TensorFlow / Keras
- XGBoost
- MQTT
- ESP32
- Streamlit
- Blynk IoT

---

## 📌 Conclusion

This project converts reactive maintenance into **predictive maintenance**, helping industries prevent failures before they happen.

---

⭐ If you like this project, give it a star!