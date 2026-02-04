import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import random

# --- 1. SETUP ---
def init_db():
    conn = sqlite3.connect('crypto_elite_v30.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. THE "LIVING" UI (ANIMATION & DESIGN) ---
def apply_full_dynamic_style():
    # Real Crypto Icon URLs
    coins = [
        "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
        "https://cryptologos.cc/logos/ethereum-eth-logo.png",
        "https://cryptologos.cc/logos/cardano-ada-logo.png",
        "https://cryptologos.cc/logos/litecoin-ltc-logo.png",
        "https://cryptologos.cc/logos/tether-usdt-logo.png"
    ]
    
    # HTML for animated background
    coin_elements = "".join([f'<img src="{random.choice(coins)}" class="coin" style="left:{random.randint(5,95)}%; animation-delay:{random.randint(0,10)}s; width:{random.randint(30,50)}px;">' for _ in range(12)])

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    .stApp {{ background-color: #080a0c; color: #ffffff; font-family: 'Inter', sans-serif; }}
    
    /* BACKGROUND ANIMATION */
    .bg-wrap {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; overflow: hidden; }}
    .coin {{ position: absolute; bottom: -100px; opacity: 0.15; animation: rise 20s linear infinite; filter: drop-shadow(0 0 5px rgba(255,255,255,0.2)); }}
    @keyframes rise {{
        0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
        20% {{ opacity: 0.15; }}
        80% {{ opacity: 0.15; }}
        100% {{ transform: translateY(-120vh) rotate(360deg); opacity: 0; }}
    }}

    /* GLASS CARDS */
    .glass-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(12px);
        margin-bottom: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
    }}

    .neon-text {{ color: #00ff88; text-shadow: 0 0 8px rgba(0,255,136,0.3); }}
    
    .stButton>button {{
        background: linear-gradient(90deg, #f0b90b, #ffca28) !important;
        border: none !important; color: black !important; font-weight: bold !important;
        border-radius: 12px !important; width: 100%; height: 45px;
    }}
    </style>
    <div class="bg-wrap">{coin_elements}</div>
    """, unsafe_allow_html=True)

# --- 3. DASHBOARD WIDGETS ---
def user_view():
    # 1. Top Price Ticker
    components.html("""<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}], "colorTheme": "dark", "isTransparent": true}</script>""", height=50)

    # 2. Hero Section (Fear & Greed)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card"><small>Sentiment</small><h2 class="neon-text">BULLISH</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card"><small>Accuracy</small><h2 style="color:#f0b90b;">94%</h2></div>', unsafe_allow_html=True)

    # 3. LIVE SIGNALS
    st.markdown("### 🎯 VIP Signals")
    df = pd.read_sql("SELECT * FROM signals ORDER BY id DESC LIMIT 3", db_conn)
    if df.empty:
        st.markdown('<div class="glass-card" style="text-align:center; color:#666;">Analyzing Markets...</div>', unsafe_allow_html=True)
    for _, r in df.iterrows():
        side_color = "#00ff88" if r['side'] == "LONG" else "#ff3b3b"
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between;">
                <b>{r['pair']}</b> <span style="color:{side_color};">{r['side']}</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-top:15px; text-align:center;">
                <div style="background:rgba(255,255,255,0.05); padding:8px; border-radius:10px;"><small>Entry</small><br><b>{r['entry']}</b></div>
                <div style="background:rgba(255,255,255,0.05); padding:8px; border-radius:10px;"><small>TP</small><br><b class="neon-text">{r['tp']}</b></div>
                <div style="background:rgba(255,255,255,0.05); padding:8px; border-radius:10px;"><small>SL</small><br><b style="color:#ff3b3b;">{r['sl']}</b></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # 4. Live Technical Gauge (මෙතනින් තමයි පාලු ගතිය නැති වෙන්නේ)
    st.markdown("### ⚡ Live Market Pulse")
    components.html("""
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    {"interval": "1m", "width": "100%", "isTransparent": true, "height": "380", "symbol": "BINANCE:BTCUSDT", "showIntervalTabs": true, "colorTheme": "dark"}
    </script>""", height=400)

# --- 4. APP LOGIC ---
apply_full_dynamic_style()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("<br><br><br><br><h1 style='text-align:center;'>ELITE LOGIN</h1>", unsafe_allow_html=True)
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("SIGN IN"):
            st.session_state.update({"logged_in": True, "is_admin": (u=="ushan2008@gmail.com")})
            st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()
    if st.session_state.is_admin:
        st.title("Admin Panel")
        with st.form("new"):
            p = st.text_input("Pair"); s = st.selectbox("Side", ["LONG", "SHORT"])
            en = st.text_input("Entry"); tp = st.text_input("TP"); sl = st.text_input("SL")
            if st.form_submit_button("Post"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)", (p,s,en,tp,sl,"Active",datetime.now().strftime("%H:%M")))
                db_conn.commit(); st.success("Live!")
    else:
        user_view()
