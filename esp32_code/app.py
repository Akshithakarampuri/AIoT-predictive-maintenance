import streamlit as st
import json
import os
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
DATA_FILE = "latest_sensor.json"
HISTORY_FILE = "sensor_history.csv"

st.set_page_config(
    layout="wide",
    page_title="Predictive Maintenance Dashboard",
    page_icon="🏭"
)

# =========================
# HEADER
# =========================
st.markdown("""
# 🏭 Predictive Maintenance Dashboard
""")

# =========================
# SIDEBAR
# =========================
st.sidebar.header("⚙ Dashboard Controls")
refresh_rate = st.sidebar.slider("Auto refresh (sec)", 1, 10, 2)
st_autorefresh(interval=refresh_rate * 1000, key="refresh")

st.sidebar.divider()
st.sidebar.caption("ESP32 + MQTT + ML Model + Streamlit")

# =========================
# LOAD DATA (SAFE)
# =========================
d = None
hist = None

if os.path.exists(DATA_FILE):
    try:
        with open(DATA_FILE) as f:
            d = json.load(f)
    except:
        d = None

if os.path.exists(HISTORY_FILE):
    try:
        hist = pd.read_csv(HISTORY_FILE).tail(300)
        if "timestamp" in hist.columns:
            hist["timestamp"] = pd.to_datetime(hist["timestamp"])
            hist = hist.sort_values("timestamp")
    except:
        hist = None

# =========================
# STATUS BANNER
# =========================
if d and "predicted_days_to_failure" in d:

    days = float(d.get("predicted_days_to_failure", 0))

    if days < 3:
        status = "CRITICAL"
        color = "red"
        msg = "Immediate maintenance required"
    elif days < 7:
        status = "WARNING"
        color = "orange"
        msg = "Maintenance window approaching"
    else:
        status = "NORMAL"
        color = "green"
        msg = "System operating normally"

    st.markdown(f"""
    <div style="padding:15px;border-radius:12px;background:{color};
    color:white;text-align:center;font-size:22px">
    🚦 SYSTEM STATUS: <b>{status}</b> — {msg}
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("Waiting for live sensor data...")

st.divider()

# =========================
# KPI CARDS
# =========================
c1, c2, c3, c4 = st.columns(4)

def metric_card(col, title, value):
    col.markdown(f"""
    <div style="padding:18px;border-radius:14px;background:#111827">
        <div style="font-size:14px;color:#9ca3af">{title}</div>
        <div style="font-size:28px;font-weight:700">{value}</div>
    </div>
    """, unsafe_allow_html=True)

if d:
    metric_card(c1, "🌡 Temperature", f"{d.get('temperature',0):.1f} °C")
    metric_card(c2, "📳 Vibration", f"{d.get('vibration',0):.3f}")
    metric_card(c3, "⚡ Current", f"{d.get('current',0):.2f} A")
    metric_card(c4, "⏳ RUL", f"{d.get('predicted_days_to_failure',0):.1f} days")

# =========================
# FAULT BADGE (NEW)
# =========================
if d:
    if d.get("fault", False):
        st.error("⚠ Fault Signal Sent to ESP32")
    else:
        st.success("✅ No Fault Signal")

st.divider()

# =========================
# GAUGE + INFO GRID
# =========================
left, right = st.columns([2,1])

if d and "predicted_days_to_failure" in d:

    days = float(d.get("predicted_days_to_failure", 0))
    health = max(0, min(100, (days / 30) * 100))

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health,
        title={'text': "Machine Health %"},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 40], 'color': "#ef4444"},
                {'range': [40, 70], 'color': "#f59e0b"},
                {'range': [70, 100], 'color': "#22c55e"}
            ]
        }
    ))

    left.plotly_chart(gauge, use_container_width=True)

    # Insight Box
    right.markdown("### 📌 Prediction Insight")
    right.write(f"**Predicted failure in:** {days:.1f} days")
    right.write(f"**Health Score:** {health:.1f}%")
    right.write("Model uses vibration + temperature + current")
    right.write("Auto-updated from IoT stream")

# =========================
# TABS
# =========================
tab1, tab2, tab3 = st.tabs(["📈 Trends", "⏳ RUL", "📋 Data"])

# =========================
# TRENDS TAB
# =========================
with tab1:
    if hist is not None and len(hist) > 5:

        hist["t_avg"] = hist["temperature"].rolling(5).mean()
        hist["v_avg"] = hist["vibration"].rolling(5).mean()
        hist["c_avg"] = hist["current"].rolling(5).mean()

        a,b,c = st.columns(3)

        with a:
            f = go.Figure()
            f.add_trace(go.Scatter(y=hist["temperature"], name="Raw"))
            f.add_trace(go.Scatter(y=hist["t_avg"], name="Avg"))
            f.update_layout(title="Temperature")
            st.plotly_chart(f, use_container_width=True)

        with b:
            f = go.Figure()
            f.add_trace(go.Scatter(y=hist["vibration"], name="Raw"))
            f.add_trace(go.Scatter(y=hist["v_avg"], name="Avg"))
            f.update_layout(title="Vibration")
            st.plotly_chart(f, use_container_width=True)

        with c:
            f = go.Figure()
            f.add_trace(go.Scatter(y=hist["current"], name="Raw"))
            f.add_trace(go.Scatter(y=hist["c_avg"], name="Avg"))
            f.update_layout(title="Current")
            st.plotly_chart(f, use_container_width=True)

# =========================
# RUL TAB
# =========================
with tab2:
    if hist is not None and "predicted_days_to_failure" in hist.columns:
        fig = go.Figure()
        fig.add_trace(go.Bar(y=hist["predicted_days_to_failure"]))
        fig.update_layout(title="Remaining Useful Life Trend")
        st.plotly_chart(fig, use_container_width=True)

# =========================
# DATA TAB
# =========================
with tab3:
    if hist is not None:
        st.dataframe(
            hist.tail(25),
            use_container_width=True,
            height=400
        )

# =========================
# DEBUG PANEL
# =========================
with st.expander("🔧 Raw Sensor Packet"):
    st.json(d)