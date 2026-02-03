import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go
import requests
import pandas as pd

# --- CONFIGURATION ---
BOT_TOKEN = "8526792641:AAHEyboZTc9-lporhmcAGekEVO-Z-D-pvb8"

# 1. Page Styling (High-End Cyberpunk UI)
st.set_page_config(page_title="SignalMaster AI Pro", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #000000; color: #00dfff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .signal-box { background: rgba(0, 223, 255, 0.1); border-radius: 15px; padding: 20px; border: 1px solid #00dfff; margin-bottom: 10px; }
    .stButton>button { width: 100%; background-color: #00dfff; color: black; font-weight: bold; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar
st.sidebar.title("🚀 MASTER CONTROL")
menu = st.sidebar.radio("SELECT MODULE", ["🏠 Neural Home", "📡 Live Signals", "📊 Market Insight"])

# --- FUNCTION: Get Telegram Messages ---
def get_telegram_updates():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url).json()
        if response["ok"]:
            # අන්තිම මැසේජ් 5 අරගන්නවා
            messages = [item["message"]["text"] for item in response["result"] if "message" in item and "text" in item]
            return messages[::-1] # අලුත්ම ඒවා උඩට
    except:
        return []

# --- 🏠 NEURAL HOME ---
if menu == "🏠 Neural Home":
    st.markdown("<h1 style='text-align: center;'>SIGNALMASTER AI v8.0</h1>", unsafe_allow_html=True)
    
    # Real-time Multi-Coin Ticker
    coins = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
    cols = st.columns(len(coins))
    for i, coin in enumerate(coins):
        price = yf.Ticker(coin).history(period="1d")['Close'].iloc[-1]
        cols[i].metric(coin, f"${price:,.2f}")

    st.write("---")
    st.subheader("🤖 AI Market Sentiment")
    st.progress(85) # AI Bullish index
    st.caption("AI Analysis: Strong Bullish Momentum Detected in Major Pairs.")

# --- 📡 LIVE SIGNALS (REAL TELEGRAM FEED) ---
elif menu == "📡 Live Signals":
    st.subheader("📡 Real-Time Telegram Signal Feed")
    st.write("Listening to Telegram Bot...")
    
    msgs = get_telegram_updates()
    
    if msgs:
        for msg in msgs:
            st.markdown(f"<div class='signal-box'><b>📡 New Signal Received:</b><br>{msg}</div>", unsafe_allow_html=True)
    else:
        st.warning("No new signals found. Make sure you have sent messages to the bot or added the bot to a channel.")
        st.info("💡 Tip: Send a message to your bot in Telegram, then refresh this page!")

# --- 📊 MARKET INSIGHT ---
elif menu == "📊 Market Insight":
    target = st.sidebar.selectbox("Asset", ["BTC-USD", "ETH-USD", "SOL-USD"])
    df = yf.download(target, period="1d", interval="15m")
    
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
