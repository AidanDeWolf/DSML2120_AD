# PART 1 - READ API
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time

st.set_page_config(page_title="Denver Weather", page_icon="🌤️", layout="wide")
# Disable fade/transition so charts don't blink between reruns
st.markdown("""
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
""", unsafe_allow_html=True)

st.title("🌤️ Denver Weather Over Time")
st.caption("Live weather data from Open-Meteo.")

# PART 2 - CONFIG
lat, lon = 39.7392, -104.9903  # Denver
wurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
@st.cache_data(ttl=600)
def get_weather():
    r = requests.get(wurl, timeout=10); r.raise_for_status()
    j = r.json()["current"]
    return pd.DataFrame([{"time": pd.to_datetime(j["time"]),
                          "temperature": j["temperature_2m"],
                          "wind": j["wind_speed_10m"]}])


# PART 4 - REFRESH BUTTON
# --- Auto Refresh Controls ---
st.subheader("🔁 Auto Refresh Settings")

# Let user choose how often to refresh (in seconds)
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)

# Toggle to turn automatic refreshing on/off
auto_refresh = st.toggle("Enable auto-refresh", value=False)

# Show current refresh time
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# PART 5 - MAIN VIEW
st.subheader("Current Weather")
df = get_weather()

# PART 5 - KEEP HISTORY IN SESSION STATE
if "weather_history" not in st.session_state:
    st.session_state.weather_history = pd.DataFrame(
        columns=["time", "temperature", "wind"]
    )

history = st.session_state.weather_history

history = pd.concat([history, df], ignore_index=True)
history = history.drop_duplicates(subset="time", keep="last")
history = history.sort_values("time").tail(30)

st.session_state.weather_history = history

# PART 6 - DISPLAY METRICS
latest = history.iloc[-1]

col1, col2 = st.columns(2)

col1.metric(
    "Temperature",
    f"{latest['temperature']} °C"
)

col2.metric(
    "Wind Speed",
    f"{latest['wind']} km/h"
)

# PART 7 - TEMPERATURE LINE CHART
fig = px.line(
    history,
    x="time",
    y="temperature",
    markers=True,
    title="Denver Temperature Over Time"
)

fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Temperature (°C)"
)

st.plotly_chart(fig, use_container_width=True)

st.dataframe(history, use_container_width=True)

st.caption(f"Latest observation: {latest['time']}")

if auto_refresh:
    time.sleep(refresh_sec)
    get_weather.clear()
    st.rerun()
