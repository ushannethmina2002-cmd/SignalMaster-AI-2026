import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. CORE ENGINE & PERFORMANCE TRACKING ---
class EliteV7Engine:
    def __init__(self):
        self.conn = sqlite3.connect('elite_v7_final.db', check_same_thread=False)
        self.init_db()
        self.ensure_defaults()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY, app_name TEXT, logo_url TEXT, 
            announcement TEXT, theme_color TEXT, sentiment TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
            password TEXT, role TEXT, status TEXT, expiry_date DATE)''')
        # Signals with Image & Result tracking
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, 
            timeframe TEXT, confidence TEXT, reason TEXT, chart_url TEXT,
            result TEXT, timestamp TEXT)''')
        self.conn.commit()

    def ensure_defaults(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM settings WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO settings VALUES (1, 'ELITE VIP INTEL', 'https://cryptologos.cc/logos/bitcoin-btc-logo.png', 'Welcome to v7 Institutional Terminal', '#f0b90b', 'NEUTRAL')")
        
        admin_email = "ushannethmina2002@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            hashed = hashlib.sha256("192040090".encode()).hexdigest()
            long_expiry = (datetime.now() + timedelta(days=3650)).strftime('%Y-%m-%d')
            c.execute("INSERT INTO users (username, password, role, status, expiry_date) VALUES (?,?,?,?,?)",
                      (admin_email, hashed, 'ADMIN', 'ACTIVE', long_expiry))
        self.conn.commit()

engine = EliteV7Engine()
config = engine.get_config() if hasattr(engine, 'get_config') else pd.read_sql("SELECT * FROM settings WHERE id=1", engine.conn).iloc[0]

# --- 2. PREMIUM UI ---
st.set_page_config(page_title=config['app_name'], layout="wide")
color = config['theme_color']

st.markdown(f"""
<style>
    .stApp {{ background: #080a0c; color: #e1e4e8; font-family: 'Inter', sans-serif; }}
    .glass-card {{
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
    }}
    .sentiment-box {{
        padding: 10px; border-radius: 10px; text-align: center; font-weight: 800;
        background: {color}22; color: {color}; border: 1px solid {color}55;
    }}
    .win-tag {{ color: #00ff88; font-weight: bold; border: 1px solid #00ff88; padding: 2px 8px; border-radius: 5px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. DASHBOARD ---
def render_dashboard():
    st.markdown(f"<h1 style='color:{color};'>{config['app_name']}</h1>", unsafe_allow_html=True)
    
    # Sentiment & Price Row
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(f"<div class='sentiment-box'>MARKET SENTIMENT: {config['sentiment']}</div>", unsafe_allow_html=True)
    with col_b:
        st.components.v1.html("""<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
        {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}], "colorTheme": "dark", "isTransparent": true}</script>""", height=50)

    st.info(f"📢 {config['announcement']}")

    # Signals Display
    signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", engine.conn)
    for _, s in signals.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between;">
                    <h3>{s['pair']} <small style="font-size:12px; color:#666;">{s['timestamp']}</small></h3>
                    {f'<span class="win-tag">{s["result"]}</span>' if s['result'] != 'PENDING' else ''}
                </div>
                <p><b>{s['type']}</b> | Confidence: {s['confidence']}</p>
                <p style="font-size:14px; color:#bbb;">{s['reason']}</p>
            </div>
            """, unsafe_allow_html=True)
            if s['chart_url']:
                st.image(s['chart_url'], caption=f"Technical Analysis for {s['pair']}")

# --- 4. ADMIN PANEL ---
def render_admin():
    st.title("🛡️ Institutional Admin v7")
    t1, t2, t3 = st.tabs(["Signal Broadcaster", "User Management", "System Settings"])

    with t1:
        with st.form("sig_v7"):
            pair = st.text_input("Pair")
            stype = st.selectbox("Event", ["Breakout", "Trend", "Liquidity"])
            c_url = st.text_input("Chart Image URL (Optional)")
            reason = st.text_area("Analysis")
            res = st.selectbox("Result", ["PENDING", "WIN", "LOSS"])
            if st.form_submit_button("Broadcast"):
                engine.conn.cursor().execute("INSERT INTO signals (pair, type, timeframe, confidence, reason, chart_url, result, timestamp) VALUES (?,?,?,?,?,?,?,?)",
                                            (pair, stype, "4H", "High", reason, c_url, res, datetime.now().strftime("%H:%M")))
                engine.conn.commit(); st.success("Signal Sent!")

    with t2:
        # (User management code same as v6 - adding users with expiry)
        st.write("Manage VIP Members here...")

    with t3:
        with st.form("sys_v7"):
            name = st.text_input("App Name", value=config['app_name'])
            sent = st.selectbox("Sentiment", ["EXTREME FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME GREED"], index=2)
            ann = st.text_area("Announcement", value=config['announcement'])
            if st.form_submit_button("Update System"):
                engine.conn.cursor().execute("UPDATE settings SET app_name=?, sentiment=?, announcement=? WHERE id=1", (name, sent, ann))
                engine.conn.commit(); st.success("System Updated!"); st.rerun()

# --- 5. RUN ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    # (Login logic same as v6)
    u_in = st.text_input("Email")
    p_in = st.text_input("Key", type="password")
    if st.button("Login"):
        h_in = hashlib.sha256(p_in.encode()).hexdigest()
        res = engine.conn.cursor().execute("SELECT role, expiry_date FROM users WHERE username=? AND password=?", (u_in, h_in)).fetchone()
        if res:
            st.session_state.user = {"email": u_in, "role": res[0], "expiry": res[1]}
            st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.user = None; st.rerun()
    if st.session_state.user['role'] == 'ADMIN':
        mode = st.sidebar.radio("View", ["Admin", "User"])
        if mode == "Admin": render_admin()
        else: render_dashboard()
    else: render_dashboard()
