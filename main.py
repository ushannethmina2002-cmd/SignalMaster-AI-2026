import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import streamlit.components.v1 as components
import random

# --- 1. CORE SECURITY & AUTHENTICATION ---
class Security:
    @staticmethod
    def hash_pw(password):
        return hashlib.sha256(str.encode(password)).hexdigest()

    @staticmethod
    def check_auth(user, pw):
        conn = sqlite3.connect('core_system.db')
        c = conn.cursor()
        c.execute('SELECT role FROM users WHERE username=? AND password=?', (user, Security.hash_pw(pw)))
        res = c.fetchone()
        conn.close()
        return res[0] if res else None

# --- 2. DATABASE ARCHITECTURE ---
def init_system():
    conn = sqlite3.connect('core_system.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE, password TEXT, role TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS signals (pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, time TEXT)')
    
    # Default Admin: ushan2008@gmail.com | Password: 2008
    admin_hash = Security.hash_pw("2008")
    c.execute("INSERT OR IGNORE INTO users VALUES (?,?,?)", ('ushan2008@gmail.com', admin_hash, 'ADMIN'))
    conn.commit()
    return conn

db_conn = init_system()

# --- 3. PREMIUM UI DESIGN SYSTEM (ANIMATED & GLASS) ---
def apply_global_design():
    # Real Crypto Logos for Animation
    coin_icons = [
        "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
        "https://cryptologos.cc/logos/ethereum-eth-logo.png",
        "https://cryptologos.cc/logos/cardano-ada-logo.png",
        "https://cryptologos.cc/logos/litecoin-ltc-logo.png",
        "https://cryptologos.cc/logos/tether-usdt-logo.png",
        "https://cryptologos.cc/logos/solana-sol-logo.png"
    ]
    
    # Generate 15 floating icons with different properties
    floating_html = "".join([
        f'<img src="{random.choice(coin_icons)}" class="float-icon" style="left:{random.randint(5,95)}%; animation-delay:{random.randint(0,12)}s; animation-duration:{random.randint(15,25)}s; width:{random.randint(30,55)}px;">' 
        for _ in range(15)
    ])

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;700;800&display=swap');
    
    .stApp {{ background: #080a0c; color: #ffffff; font-family: 'Plus Jakarta Sans', sans-serif; overflow: hidden; }}
    
    /* 🌍 GLOBAL FLOATING BACKGROUND */
    .bg-animation {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; }}
    .float-icon {{ position: absolute; bottom: -100px; opacity: 0.15; animation: floatUp linear infinite; filter: drop-shadow(0 0 10px rgba(255,255,255,0.1)); }}
    
    @keyframes floatUp {{
        0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }}
        10% {{ opacity: 0.2; }}
        90% {{ opacity: 0.2; }}
        100% {{ transform: translateY(-120vh) rotate(360deg); opacity: 0; }}
    }}

    /* 💎 GLASSMORPHISM CARDS */
    .glass-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 25px;
        backdrop-filter: blur(15px);
        margin-bottom: 20px;
        transition: 0.3s ease;
    }}
    .glass-card:hover {{ border: 1px solid rgba(240, 185, 11, 0.3); transform: translateY(-5px); }}

    /* ⚡ NEON & BUTTONS */
    .neon-green {{ color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.4); }}
    .stButton>button {{
        background: linear-gradient(135deg, #f0b90b, #ffca28) !important;
        border: none !important; color: black !important; font-weight: 800 !important;
        border-radius: 14px !important; height: 50px !important; width: 100%;
    }}
    </style>
    <div class="bg-animation">{floating_html}</div>
    """, unsafe_allow_html=True)

# --- 4. USER INTELLIGENCE HUB ---
def render_user_dashboard():
    # Live Ticker Header
    components.html("""<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}], "colorTheme": "dark", "isTransparent": true}</script>""", height=50)

    st.markdown("<h1 style='letter-spacing:-1px;'>Intelligence Dashboard</h1>", unsafe_allow_html=True)

    # Market Summary Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="glass-card"><small>SENTIMENT</small><h2 class="neon-green">BULLISH</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card"><small>AI ACCURACY</small><h2 style="color:#f0b90b;">97.2%</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-card"><small>ACTIVE SIGNALS</small><h2>05</h2></div>', unsafe_allow_html=True)

    # VIP Signal Stream
    st.markdown("### 🎯 Live Institutional Signals")
    df = pd.read_sql("SELECT * FROM signals ORDER BY time DESC LIMIT 5", db_conn)
    if df.empty:
        st.markdown('<div class="glass-card" style="text-align:center; color:#555;">Scanning Liquidity Zones...</div>', unsafe_allow_html=True)
    for _, r in df.iterrows():
        color = "#00ff88" if r['side'] == "LONG" else "#ff3b3b"
        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:20px; font-weight:800;">{r['pair']}</span>
                <span style="background:rgba(255,255,255,0.05); padding:5px 15px; border-radius:50px; color:{color}; font-weight:bold; border:1px solid {color}55;">{r['side']}</span>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:15px; margin-top:20px; text-align:center;">
                <div style="background:rgba(255,255,255,0.02); padding:10px; border-radius:15px;"><small>ENTRY</small><br><b>{r['entry']}</b></div>
                <div style="background:rgba(0,255,136,0.05); padding:10px; border-radius:15px;"><small style="color:#00ff88;">TARGET</small><br><b class="neon-green">{r['tp']}</b></div>
                <div style="background:rgba(255,59,59,0.05); padding:10px; border-radius:15px;"><small style="color:#ff3b3b;">STOP</small><br><b style="color:#ff3b3b;">{r['sl']}</b></div>
            </div>
        </div>""", unsafe_allow_html=True)

    # Full-Width Technical Widget (පාලු ගතිය නැති කරන ප්‍රධාන කොටස)
    st.markdown("### 📈 Real-time Market Pulse")
    components.html("""
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
    {"interval": "1m", "width": "100%", "isTransparent": true, "height": "400", "symbol": "BINANCE:BTCUSDT", "showIntervalTabs": true, "locale": "en", "colorTheme": "dark"}
    </script>""", height=420)

# --- 5. SYSTEM LOGIC ---
apply_global_design()

if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    # --- AUTHENTICATION SCREEN ---
    _, col, _ = st.columns([1,1.8,1])
    with col:
        st.markdown("<br><br><br><h1 style='text-align:center; font-weight:800; font-size:45px;'>ELITE PORTAL</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#848e9c; margin-bottom:30px;'>Authorized Personnel Only</p>", unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            u = st.text_input("GMAIL / USERNAME").lower()
            p = st.text_input("PASSWORD", type="password")
            if st.button("AUTHENTICATE"):
                role = Security.check_auth(u, p)
                if role:
                    st.session_state.auth = {'user': u, 'role': role}
                    st.rerun()
                else: st.error("Access Denied: Invalid Credentials")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    # --- DASHBOARD SCREEN ---
    with st.sidebar:
        st.markdown(f"### 🛡️ SESSION ACTIVE")
        st.markdown(f"**Account:** {st.session_state.auth['user']}")
        st.markdown(f"**Level:** <span class='neon-green'>{st.session_state.auth['role']}</span>", unsafe_allow_html=True)
        st.divider()
        if st.button("Logout"): 
            st.session_state.auth = None
            st.rerun()

    if st.session_state.auth['role'] == 'ADMIN':
        st.title("Master Command Hub")
        with st.form("broadcast"):
            st.markdown("#### 📢 Broadcast New Signal")
            pair = st.text_input("Asset Pair"); side = st.selectbox("Side", ["LONG", "SHORT"])
            en = st.text_input("Entry Zone"); tp = st.text_input("Target"); sl = st.text_input("Stop Loss")
            if st.form_submit_button("PUBLISH TO NETWORK"):
                db_conn.cursor().execute("INSERT INTO signals VALUES (?,?,?,?,?,?)", (pair, side, en, tp, sl, datetime.now().strftime("%H:%M")))
                db_conn.commit(); st.success("Signal Distributed Successfully")
    else:
        render_user_dashboard()
