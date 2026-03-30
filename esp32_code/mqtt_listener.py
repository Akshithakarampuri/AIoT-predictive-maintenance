import json
import joblib
import paho.mqtt.client as mqtt
import pandas as pd
import numpy as np
import os
from datetime import datetime
from tensorflow.keras.models import load_model
import warnings
warnings.filterwarnings("ignore")

# =========================
# CONFIG
# =========================
BROKER = "broker.hivemq.com"
SENSOR_TOPIC = "machine/sensors"
PRED_TOPIC = "esp32/fault_prediction"

MODEL_FILE = "lstm_rul_model.keras"
SCALER_FILE = "lstm_scaler.pkl"

LATEST_FILE = "latest_sensor.json"
HISTORY_FILE = "sensor_history.csv"

WINDOW_SIZE = 20
FAULT_THRESHOLD_DAYS = 7   # You can adjust

# =========================
# LOAD MODEL + SCALER
# =========================
model = load_model(MODEL_FILE)
scaler = joblib.load(SCALER_FILE)

print("✅ LSTM Model Loaded")
print("✅ Scaler Loaded")

sequence_buffer = []

# =========================
# CREATE HISTORY FILE IF NOT EXISTS
# =========================
if not os.path.exists(HISTORY_FILE):
    pd.DataFrame(columns=[
        "timestamp",
        "temperature",
        "current",
        "vibration",
        "predicted_days_to_failure",
        "fault"
    ]).to_csv(HISTORY_FILE, index=False)

# =========================
# MQTT CALLBACKS
# =========================
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT:", rc)
    client.subscribe(SENSOR_TOPIC)


def on_message(client, userdata, msg):
    global sequence_buffer

    try:
        d = json.loads(msg.payload.decode())
        print("📩 Sensor Data:", d)

        # -------------------------
        # Feature order MUST match training
        # -------------------------
        features = [
            d["temperature"],
            d["current"],
            d["vibration"]
        ]

        scaled = scaler.transform([features])
        sequence_buffer.append(scaled[0])

        if len(sequence_buffer) > WINDOW_SIZE:
            sequence_buffer.pop(0)

        # Only predict when buffer full
        if len(sequence_buffer) == WINDOW_SIZE:

            input_seq = np.array(sequence_buffer)
            input_seq = np.expand_dims(input_seq, axis=0)

            pred_days = float(model.predict(input_seq, verbose=0)[0][0])

            print("🧠 Predicted RUL days:", pred_days)

            # -------------------------
            # Fault Decision
            # -------------------------
            fault_flag = pred_days < FAULT_THRESHOLD_DAYS

            client.publish(PRED_TOPIC, "1" if fault_flag else "0")

            # -------------------------
            # Save latest JSON
            # -------------------------
            out = {
                "timestamp": datetime.now().isoformat(),
                "temperature": d["temperature"],
                "current": d["current"],
                "vibration": d["vibration"],
                "predicted_days_to_failure": pred_days,
                "fault": fault_flag
            }

            with open(LATEST_FILE, "w") as f:
                json.dump(out, f, indent=2)

            # -------------------------
            # Append CSV history
            # -------------------------
            new_row = pd.DataFrame([out])
            hist = pd.read_csv(HISTORY_FILE)
            hist = pd.concat([hist, new_row], ignore_index=True)
            hist.to_csv(HISTORY_FILE, index=False)

            print("💾 Stored to JSON + CSV")
            print("-----------------------")

        else:
            print(f"⏳ Collecting sequence ({len(sequence_buffer)}/{WINDOW_SIZE})")

    except Exception as e:
        print("❌ Error:", e)


# =========================
# MQTT SETUP
# =========================
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883, 60)

print("🚀 MQTT Listener Running...")
client.loop_forever()