import streamlit as st
import yfinance as yf
import pandas_ta as ta
import plotly.graph_objects as go

# ඇප් එකේ පෙනුම සෙට් කිරීම
st.set_page_config(page_title="Crypto Pro Signal AI", layout="wide")

# Custom CSS පාවිච්චි කරලා පෙනුම ලස්සන කිරීම
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #f63366; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Crypto Pro Signal AI v2.0")
st.sidebar.header("Settings")

# Sidebar එකේ පරාමිතීන්
coin = st.sidebar.selectbox("Select Crypto", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "ADA-USD"])
timeframe = st.sidebar.selectbox("Timeframe", ["15m", "30m", "1h", "4h"])

if st.button('🚀 Get Premium Signals'):
    with st.spinner('දත්ත සහ Indicators විශ්ලේෂණය කරමින්...'):
        df = yf.download(coin, period="5d", interval=timeframe)
        
        # Indicators ගණනය කිරීම
        df['RSI'] = ta.rsi(df['Close'], length=14)
        macd = ta.macd(df['Close'])
        df = df.join(macd)
        df.ta.bbands(length=20, std=2, append=True)
        
        last_price = df['Close'].iloc[-1]
        last_rsi = df['RSI'].iloc[-1]
        bb_lower = df['BBL_20_2.0'].iloc[-1]
        bb_upper = df['BBU_20_2.0'].iloc[-1]

        # දත්ත පෙන්වීම (Metrics)
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${last_price:,.2f}")
        col2.metric("RSI (14)", f"{last_rsi:.2f}")
        col3.metric("Volatility", "High" if last_price > bb_upper else "Low")

        # Trading Signals (වැදගත්ම කොටස)
        st.subheader("📊 Market Analysis")
        if last_rsi < 30 and last_price <= bb_lower:
            st.success("💎 STRONG BUY SIGNAL: Market is oversold and hitting Support!")
        elif last_rsi > 70 and last_price >= bb_upper:
            st.error("⚠️ STRONG SELL SIGNAL: Market is overbought and hitting Resistance!")
        else:
            st.info("⚖️ NEUTRAL: Wait for a better entry point.")

        # ප්‍රස්ථාරය (Charting)
        fig = go.Figure(data=[go.Candlestick(x=df.index,
                        open=df['Open'], high=df['High'],
                        low=df['Low'], close=df['Close'], name='Market')])
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

st.sidebar.info("Tip: RSI 30 ට අඩු වෙලා Bollinger Band එකේ පහළ වැදුණාම BUY කරන්න.")
