import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
import random

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('crypto_elite_v29.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, msg TEXT, time TEXT)')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. ADVANCED UI WITH LIVE COIN ANIMATION ---
def apply_elite_animation():
    # Real Coin Logos URLs
    coins = {
        "BTC": "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
        "ETH": "https://cryptologos.cc/logos/ethereum-eth-logo.png",
        "USDT": "https://cryptologos.cc/logos/tether-usdt-logo.png",
        "ADA": "https://cryptologos.cc/logos/cardano-ada-logo.png",
        "LTC": "https://cryptologos.cc/logos/litecoin-ltc-logo.png"
    }
    
    coin_list = list(coins.values())
    
    # CSS for Floating Animation
    animation_html = ""
    for i in range(15): # 15 coins floating
        img_url = random.choice(coin_list)
        left = random.randint(5, 95)
        delay = random.randint(0, 10)
        duration = random.randint(15, 25)
        size = random.randint(25, 45)
        animation_html += f'<img src="{img_url}" class="floating-coin" style="left:{left}%; animation-delay:{delay}s; animation-duration:{duration}s; width:{size}px;">'

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    .stApp {{ 
        background-color: #0b0e11;
        color: white; 
        font-family: 'Inter', sans-serif;
    }}

    /* Background Animation Container */
    .bg-animation {{
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1;
        overflow: hidden;
        pointer-events: none;
    }}

    .floating-coin {{
        position: absolute;
        bottom: -100px;
        opacity: 0.2;
        animation: floatUp linear infinite;
    }}

    @keyframes floatUp {{
        0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
        10% {{ opacity: 0.2; }}
        90% {{ opacity: 0.2; }}
        100% {{ transform: translateY(-120vh) rotate(360deg); opacity: 0; }}
    }}

    .glass-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }}

    .neon-green {{ color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.5); }}
    .stButton>button {{
        background: linear-gradient(90deg, #f0b90b, #ffca28) !important;
        color: black !important; font-weight: bold !important; border-radius: 12px !important; width: 100%;
    }}
    </style>
    <div class="bg-animation">{animation_html}</div>
    """, unsafe_allow_html=True)

# --- 3. DASHBOARD CONTENT ---
def user_dashboard():
    # 1. Ticker Tape
    components.html("""<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}], "colorTheme": "dark", "isTransparent": true}</script>""", height=50)

    # 2. Alerts
    alerts = pd.read_sql("SELECT * FROM alerts ORDER BY id DESC LIMIT 1", db_conn)
    for _, a in alerts.iterrows():
        st.warning(f"🚨 ALERT: {a['msg']}")

    # 3. Stats
    st.markdown("### 📊 Market Intelligence")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card"><small>BTC Status</small><h2 class="neon-green">STRONG BUY</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card"><small>AI Accuracy</small><h2 style="color:#f0b90b;">96.8%</h2></div>', unsafe_allow_html=True)

    # 4. Signals
    st.markdown("### 🎯 Live VIP Signals")
    df = pd.read_sql("SELECT * FROM signals ORDER BY id DESC LIMIT 5", db_conn)
    if df.empty: st.info("Scanning for new entries...")
    for _, r in df.iterrows():
        color = "#00ff88" if r['side'] == "LONG" else "#ff3b3b"
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between;">
                <b>{r['pair']}</b> <span style="color:{color}; font-weight:bold;">{r['side']}</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; margin-top:10px; text-align:center;">
                <div style="background:#161a1e; padding:5px; border-radius:8px;"><small>Entry</small><br><b>{r['entry']}</b></div>
                <div style="background:#161a1e; padding:5px; border-radius:8px;"><small>TP</small><br><b class="neon-green">{r['tp']}</b></div>
                <div style="background:#161a1e; padding:5px; border-radius:8px;"><small>SL</small><br><b style="color:#ff3b3b;">{r['sl']}</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 4. EXECUTION ---
apply_elite_animation()

if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("<br><br><br><h1 style='text-align:center;'>ELITE ACCESS</h1>", unsafe_allow_html=True)
        u = st.text_input("Username").lower()
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            st.session_state.update({"logged_in": True, "is_admin": (u=="ushan2008@gmail.com")})
            st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()
    if st.session_state.is_admin:
        # Admin Panel
        st.title("Admin Hub")
        with st.form("new"):
            p = st.text_input("Pair"); s = st.selectbox("Side", ["LONG", "SHORT"])
            en = st.text_input("Entry"); tp = st.text_input("TP"); sl = st.text_input("SL")
            if st.form_submit_button("Post"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)",
                                         (p,s,en,tp,sl,"Active",datetime.now().strftime("%H:%M")))
                db_conn.commit(); st.success("Live!")
    else:
        user_dashboard()
