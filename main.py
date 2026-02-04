import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. DATABASE & ENGINE ---
class EliteEngineV9:
    def __init__(self):
        self.conn = sqlite3.connect('elite_v9_final.db', check_same_thread=False)
        self.init_db()
        self.ensure_defaults()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, app_name TEXT, logo_url TEXT, theme_color TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT, role TEXT, expiry_date DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, reason TEXT, chart_url TEXT, timestamp TEXT)''')
        self.conn.commit()

    def ensure_defaults(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM settings WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO settings VALUES (1, 'ELITE VIP TERMINAL', 'https://cryptologos.cc/logos/bitcoin-btc-logo.png', '#f0b90b')")
        
        admin_email = "ushannethmina2002@gmail.com"
        c.execute("SELECT * FROM users WHERE username=?", (admin_email,))
        if not c.fetchone():
            hashed = hashlib.sha256("192040090".encode()).hexdigest()
            c.execute("INSERT INTO users (username, password, role, expiry_date) VALUES (?,?,?,?)", (admin_email, hashed, 'ADMIN', '2030-01-01'))
        self.conn.commit()

engine = EliteEngineV9()
config = pd.read_sql("SELECT * FROM settings WHERE id=1", engine.conn).iloc[0]

# --- 2. STYLING ---
st.set_page_config(page_title=config['app_name'], layout="wide")
color = config['theme_color']

def apply_ui():
    st.markdown(f"""
    <style>
        .stApp {{ background: #050709; color: #e1e4e8; }}
        .glass-card {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
        .neon-text {{ color: {color}; text-shadow: 0 0 10px {color}55; font-weight: 800; }}
        .stButton>button {{ background: {color} !important; color: black !important; font-weight: bold; border-radius: 8px; width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. USER INTERFACE ---
def render_user_view():
    apply_ui()
    st.markdown(f"<h1 class='neon-text'>{config['app_name']}</h1>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🎯 SIGNALS", "📈 LIVE CHART", "📅 CALENDAR"])
    
    with t1:
        signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", engine.conn)
        if signals.empty: st.info("No active signals.")
        for _, s in signals.iterrows():
            st.markdown(f"<div class='glass-card'><h3>{s['pair']} | {s['type']}</h3><p>{s['reason']}</p><small>{s['timestamp']}</small></div>", unsafe_allow_html=True)
            if s['chart_url']: st.image(s['chart_url'])
            
    with t2:
        symbol = st.selectbox("Market", ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:SOLUSDT"])
        st.components.v1.html(f'<script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "{symbol}", "interval": "240", "theme": "dark", "container_id": "tv"}});</script><div id="tv" style="height:500px;"></div>', height=510)

    with t3:
        st.components.v1.html('<iframe src="https://sslecal2.forexpross.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&timeZone=8&lang=1" width="100%" height="500"></iframe>', height=510)

# --- 4. ADMIN INTERFACE (FULLY UPDATED) ---
def render_admin_view():
    st.markdown(f"<h1 class='neon-text'>🛡️ ADMIN CONTROL TOWER</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🚀 BROADCAST SIGNAL", "👥 VIP MEMBERS", "🎨 APP CONFIG"])

    with tab1:
        st.subheader("Send New Signal to VIPs")
        with st.form("sig_form"):
            p = st.text_input("Pair (e.g. BTC/USDT)")
            t = st.selectbox("Type", ["LONG 🟢", "SHORT 🔴", "BREAKOUT ⚡", "SCALP ⚖️"])
            c_url = st.text_input("Chart Link (Direct Image URL)")
            reason = st.text_area("Analysis / Instructions")
            if st.form_submit_button("PUBLISH SIGNAL"):
                engine.conn.cursor().execute("INSERT INTO signals (pair, type, reason, chart_url, timestamp) VALUES (?,?,?,?,?)",
                                            (p, t, reason, c_url, datetime.now().strftime("%Y-%m-%d %H:%M")))
                engine.conn.commit(); st.success("Signal Broadcasted!")

    with tab2:
        st.subheader("Manage VIP Members")
        with st.form("user_form"):
            u = st.text_input("Member Email")
            p = st.text_input("Security Key (Password)")
            days = st.number_input("Access (Days)", min_value=1, value=30)
            if st.form_submit_button("ADD VIP MEMBER"):
                exp = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
                hashed = hashlib.sha256(p.encode()).hexdigest()
                try:
                    engine.conn.cursor().execute("INSERT INTO users (username, password, role, expiry_date) VALUES (?,?,?,?)", (u, hashed, 'USER', exp))
                    engine.conn.commit(); st.success(f"Added {u} until {exp}")
                except: st.error("User already exists!")
        
        st.divider()
        users_df = pd.read_sql("SELECT username, expiry_date FROM users WHERE role='USER'", engine.conn)
        st.dataframe(users_df, use_container_width=True)

    with tab3:
        st.subheader("Global App Settings")
        with st.form("settings_form"):
            new_name = st.text_input("App Name", value=config['app_name'])
            new_color = st.color_picker("Theme Color", value=config['theme_color'])
            if st.form_submit_button("SAVE CHANGES"):
                engine.conn.cursor().execute("UPDATE settings SET app_name=?, theme_color=? WHERE id=1", (new_name, new_color))
                engine.conn.commit(); st.success("Updated! Please refresh."); st.rerun()

# --- 5. LOGIN LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.title("VIP LOGIN")
        u_in = st.text_input("Institutional Email")
        p_in = st.text_input("Security Key", type="password")
        if st.button("AUTHENTICATE"):
            h_in = hashlib.sha256(p_in.encode()).hexdigest()
            res = engine.conn.cursor().execute("SELECT role, expiry_date FROM users WHERE username=? AND password=?", (u_in, h_in)).fetchone()
            if res:
                if res[0] != 'ADMIN' and datetime.now() > datetime.strptime(res[1], '%Y-%m-%d'):
                    st.error("❌ Membership Expired.")
                else:
                    st.session_state.auth
