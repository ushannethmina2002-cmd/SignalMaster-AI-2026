import streamlit as st
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="SignalMaster AI", layout="centered")
st.title("🎯 SignalMaster AI Bot")

# කාසි වර්ග
coin = st.selectbox("Select Crypto", ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "XRP-USD"])

if st.button('Analyze Market'):
    with st.spinner('දත්ත පරීක්ෂා කරමින්...'):
        data = yf.download(coin, period="1d", interval="15m")
        data['RSI'] = ta.rsi(data['Close'], length=14)
        
        price = data['Close'].iloc[-1]
        rsi = data['RSI'].iloc[-1]
        
        st.metric("Current Price", f"${price:,.2f}")
        st.write(f"Market RSI: {rsi:.2f}")

        if rsi < 30:
            st.success("🚀 BUY SIGNAL: Market is Oversold!")
        elif rsi > 70:
            st.error("⚠️ SELL SIGNAL: Market is Overbought!")
        else:
            st.info("⚖️ Neutral: No clear signal yet.")
