import streamlit as st
import pandas as pd
import sqlite3
import bcrypt
import time
import random
from datetime import datetime

# --- 1. CORE ARCHITECTURE & SECURITY ---
class EnterpriseVault:
    def __init__(self):
        self.conn = sqlite3.connect('intel_core_v2.db', check_same_thread=False)
        self.init_db()
        self.ensure_admin()

    def init_db(self):
        c = self.conn.cursor()
        # Identity Management
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
            password TEXT, role TEXT, status TEXT, last_login TEXT)''')
        # Intelligence & Signals
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, 
            entry TEXT, tp TEXT, sl TEXT, confidence TEXT, time TEXT)''')
        # System Logs
        c.execute('''CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, action TEXT, timestamp TEXT)''')
        self.conn.commit()

    def ensure_admin(self):
        """Hardcoded Secure Admin Seed"""
        c = self.conn.cursor()
        admin_email = "ushan2008@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            hashed = bcrypt.hashpw("Admin@2026".encode('utf-8'), bcrypt.gensalt())
            c.execute("INSERT INTO users (username, password, role, status) VALUES (?,?,?,?)",
                      (admin_email, hashed, 'ADMIN', 'ACTIVE'))
            self.conn.commit()

    def verify_auth(self, u, p):
        c = self.conn.cursor()
        c.execute("SELECT password, role, status FROM users WHERE username=?", (u,))
        res = c.fetchone()
        if res and bcrypt.checkpw(p.encode('utf-8'), res[0]):
            return {"role": res[1], "status": res[2]}
        return None

vault = EnterpriseVault()

# --- 2. GLOBAL DESIGN SYSTEM (PREMIUM UI/UX) ---
def apply_institutional_style():
    # Animated Coin Background Assets
    coin_logos = [
        "https://cryptologos.cc/logos/bitcoin-btc-logo.png",
        "https://cryptologos.cc/logos/ethereum-eth-logo.png",
        "https://cryptologos.cc/logos/tether-usdt-logo.png",
        "https://cryptologos.cc/logos/cardano-ada-logo.png"
    ]
    bg_icons = "".join([f'<img src="{random.choice(coin_logos)}" class="bg-coin" style="left:{random.randint(5,95)}%; animation-delay:{random.randint(0,10)}s;">' for _ in range(12)])

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
    
    .stApp {{ background: #080a0c; color: #e1e1e1; font-family: 'Plus Jakarta Sans', sans-serif; }}
    
    /* Animated Background */
    .bg-animation {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; pointer-events: none; }}
    .bg-coin {{ position: absolute; bottom: -100px; width: 40px; opacity: 0.1; animation: floatUp 20s linear infinite; }}
    @keyframes floatUp {{ 
        0% {{ transform: translateY(0) rotate(0deg); opacity: 0; }} 
        20% {{ opacity: 0.1; }} 100% {{ transform: translateY(-120vh) rotate(360deg); opacity: 0; }} 
    }}

    /* Institutional Cards */
    .glass-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; padding: 24px; backdrop-filter: blur(15px); margin-bottom: 20px;
    }}
    .neon-gold {{ color: #f0b90b; text-shadow: 0 0 10px rgba(240, 185, 11, 0.3); }}
    
    /* Buttons */
    .stButton>button {{
        background: linear-gradient(135deg, #f0b90b, #ffca28) !important;
        color: #000 !important; font-weight: 800 !important; border-radius: 12px !important;
        border: none !important; width: 100%; height: 45px; transition: 0.4s;
    }}
    .stButton>button:hover {{ transform: translateY(-2px); box-shadow: 0 8px 20px rgba(240, 185, 11, 0.4); }}
    </style>
    <div class="bg-animation">{bg_icons}</div>
    """, unsafe_allow_html=True)

# --- 3. CORE MODULES (USER & INTELLIGENCE) ---
def render_dashboard():
    st.markdown("<h2 class='neon-gold'>Market Intelligence Hub</h2>", unsafe_allow_html=True)
    
    # Live Ticker
    st.components.v1.html("""<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}], "colorTheme": "dark", "isTransparent": true}</script>""", height=50)

    # Market Pulse Cards
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown('<div class="glass-card"><small>SENTIMENT</small><h3>BULLISH</h3></div>', unsafe_allow_html=True)
    with col2: st.markdown('<div class="glass-card"><small>VOLATILITY</small><h3>LOW</h3></div>', unsafe_allow_html=True)
    with col3: st.markdown('<div class="glass-card"><small>BTC DOMINANCE</small><h3>52.1%</h3></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎯 Intelligence Signals", "📰 Expert Analysis", "🎓 Learning Path"])
    
    with tab1:
        signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", vault.conn)
        if signals.empty: st.info("Scanning for institutional liquidity... No active signals.")
        for _, s in signals.iterrows():
            color = "#00ff88" if s['side'] == "LONG" else "#ff3b3b"
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between;">
                    <b>{s['pair']}</b> <span style="color:{color}; font-weight:800;">{s['side']}</span>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1fr 1fr; margin-top:15px; text-align:center;">
                    <div><small>ZONE</small><br><b>{s['entry']}</b></div>
                    <div style="color:#00ff88;"><small>TARGET</small><br><b>{s['tp']}</b></div>
                    <div><small>CONFIDENCE</small><br><b>{s['confidence']}</b></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab2:
        st.markdown("### Institutional Weekly Outlook")
        st.markdown('<div class="glass-card"><h4>Market Context: Q1 2026</h4><p>Global liquidity is shifting towards decentralized assets as macro-inflation stabilizes...</p></div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("### Fundamental Education")
        st.markdown('<div class="glass-card"><b>Lesson 1:</b> Risk-to-Reward Ratio<br><small>Understand how institutions manage capital preservation before profit seeking.</small></div>', unsafe_allow_html=True)

# --- 4. ADMIN CONTROL PANEL ---
def render_admin_terminal():
    st.title("🛡️ Institutional Control")
    m = st.sidebar.radio("Command", ["User Management", "Signal Broadcasting", "Audit Logs"])
    
    if m == "User Management":
        st.subheader("Manage Personnel Access")
        with st.form("add_user"):
            new_u = st.text_input("Institutional Email")
            new_p = st.text_input("Temporary Access Key", type="password")
            if st.form_submit_button("Grant Access"):
                try:
                    h = bcrypt.hashpw(new_p.encode('utf-8'), bcrypt.gensalt())
                    vault.conn.cursor().execute("INSERT INTO users (username, password, role, status) VALUES (?,?,?,?)",
                                                (new_u, h, 'USER', 'ACTIVE'))
                    vault.conn.commit()
                    st.success("Access Granted.")
                except: st.error("User already exists.")
        
        users = pd.read_sql("SELECT username, role, status FROM users", vault.conn)
        st.table(users)

    elif m == "Signal Broadcasting":
        with st.form("sig"):
            p = st.text_input("Pair"); s = st.selectbox("Side", ["LONG", "SHORT"])
            en = st.text_input("Entry"); tp = st.text_input("Target"); sl = st.text_input("Stop")
            conf = st.selectbox("Confidence", ["INSTITUTIONAL", "HIGH", "MODERATE"])
            if st.form_submit_button("Broadcast"):
                vault.conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,confidence,time) VALUES (?,?,?,?,?,?,?)",
                                            (p,s,en,tp,sl,conf, datetime.now().strftime("%H:%M")))
                vault.conn.commit()
                st.success("Broadcast Live.")

# --- 5. SYSTEM LOGIC ---
apply_institutional_style()

if 'session_auth' not in st.session_state:
    st.session_state.session_auth = None

if not st.session_state.session_auth:
    _, login_col, _ = st.columns([1, 1.5, 1])
    with login_col:
        st.markdown("<br><br><h1 style='text-align:center;'>ELITE INTEL</h1>", unsafe_allow_html=True)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        u = st.text_input("Access Identity")
        p = st.text_input("Security Key", type="password")
        if st.button("AUTHENTICATE"):
            auth_res = vault.verify_auth(u, p)
            if auth_res:
                st.session_state.session_auth = {"user": u, "role": auth_res['role']}
                st.rerun()
            else: st.error("Access Denied.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # Sidebar UX
    with st.sidebar:
        st.markdown(f"**Session:** `{st.session_state.session_auth['user']}`")
        st.markdown(f"**Clearance:** <span class='neon-gold'>{st.session_state.session_auth['role']}</span>", unsafe_allow_html=True)
        st.divider()
        if st.button("Terminate Session"):
            st.session_state.session_auth = None
            st.rerun()

    if st.session_state.session_auth['role'] == 'ADMIN':
        render_admin_terminal()
    else:
        render_dashboard()
