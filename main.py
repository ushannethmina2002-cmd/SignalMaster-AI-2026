import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import requests
from datetime import datetime, timedelta

# --- 1. CORE ENGINE (ALL COLUMNS INCLUDED) ---
class MasterEngineV11:
    def __init__(self):
        # අලුත්ම DB එකක් හදමු පරණ ලෙඩ අයින් කරන්න
        self.conn = sqlite3.connect('vip_master_v11.db', check_same_thread=False)
        self.init_db()
        self.ensure_defaults()

    def init_db(self):
        c = self.conn.cursor()
        # 1. Config Table
        c.execute('''CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, name TEXT, color TEXT, ann TEXT)''')
        # 2. Users Table (With Status & Expiry)
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, key TEXT, role TEXT, expiry DATE, status TEXT)''')
        # 3. Signals Table (With Full Logic)
        c.execute('''CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, entry TEXT, tp TEXT, sl TEXT, reason TEXT, chart TEXT, time TEXT)''')
        # 4. Intel Table (For News & Whale Alerts)
        c.execute('''CREATE TABLE IF NOT EXISTS intel (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, body TEXT, type TEXT, time TEXT)''')
        self.conn.commit()

    def ensure_defaults(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM config WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO config VALUES (1, 'ELITE VIP TERMINAL', '#f0b90b', 'Welcome to v11 Pro Terminal')")
        
        # Admin Seed
        admin_email = "ushannethmina2002@gmail.com"
        h = hashlib.sha256("192040090".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (email, key, role, expiry, status) VALUES (?,?,?,?,?)", 
                  (admin_email, h, 'ADMIN', '2099-12-31', 'ACTIVE'))
        self.conn.commit()

engine = MasterEngineV11()
config = pd.read_sql("SELECT * FROM config WHERE id=1", engine.conn).iloc[0]

# --- 2. GLOBAL STYLING ---
st.set_page_config(page_title=config['name'], layout="wide")
color = config['color']

st.markdown(f"""
<style>
    .stApp {{ background: #05070a; color: #e1e4e8; }}
    .card {{ background: rgba(255,255,255,0.03); border-radius: 12px; padding: 20px; border-left: 5px solid {color}; margin-bottom: 15px; }}
    .stButton>button {{ background: {color} !important; color: black !important; font-weight: bold; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. PROFESSIONAL TOOLS ---

def get_news():
    try:
        r = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN").json()
        return r['Data'][:5]
    except: return []

# --- 4. ADMIN PANEL (FULL CONTROL) ---
def admin_panel():
    st.title("🛡️ Institutional Admin v11")
    t1, t2, t3, t4 = st.tabs(["🚀 SIGNALS", "👥 MEMBERS", "📰 INTEL & ALERTS", "🎨 APP CONFIG"])

    with t1:
        with st.form("sig"):
            p = st.text_input("Asset Pair")
            t = st.selectbox("Type", ["LONG 🚀", "SHORT 🔴"])
            e, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
            r = st.text_area("Analysis / Chart Link")
            if st.form_submit_button("PUBLISH SIGNAL"):
                engine.conn.cursor().execute("INSERT INTO signals (pair, type, entry, tp, sl, reason, time) VALUES (?,?,?,?,?,?,?)",
                                            (p, t, e, tp, sl, r, datetime.now().strftime("%H:%M")))
                engine.conn.commit(); st.success("Signal Sent!")

    with t2:
        with st.form("usr"):
            u = st.text_input("User Email")
            k = st.text_input("Security Key")
            if st.form_submit_button("ADD VIP MEMBER"):
                hashed = hashlib.sha256(k.encode()).hexdigest()
                exp = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                engine.conn.cursor().execute("INSERT INTO users (email, key, role, expiry, status) VALUES (?,?,?,?,?)", (u, hashed, 'USER', exp, 'ACTIVE'))
                engine.conn.commit(); st.success(f"User {u} Added!")

    with t3:
        st.subheader("Send Manual Whale Alert / News")
        with st.form("intel"):
            title = st.text_input("Headline")
            body = st.text_area("Details")
            itype = st.selectbox("Type", ["WHALE ALERT 🐋", "BREAKING NEWS 📰"])
            if st.form_submit_button("PUSH ALERT"):
                engine.conn.cursor().execute("INSERT INTO intel (title, body, type, time) VALUES (?,?,?,?)", (title, body, itype, datetime.now().strftime("%H:%M")))
                engine.conn.commit(); st.success("Pushed!")

    with t4:
        with st.form("cfg"):
            name = st.text_input("App Name", value=config['name'])
            clr = st.color_picker("Theme Color", value=config['color'])
            if st.form_submit_button("SAVE APP SETTINGS"):
                engine.conn.cursor().execute("UPDATE config SET name=?, color=? WHERE id=1", (name, clr))
                engine.conn.commit(); st.rerun()

# --- 5. USER INTERFACE (ALL FEATURES) ---
def user_panel():
    st.markdown(f"<h1 style='color:{color}'>{config['name']}</h1>", unsafe_allow_html=True)
    
    t1, t2, t3, t4 = st.tabs(["🎯 VIP SIGNALS", "🌍 GLOBAL NEWS", "🐋 WHALE ALERTS", "📈 LIVE CHART"])
    
    with t1:
        sigs = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", engine.conn)
        for _, s in sigs.iterrows():
            st.markdown(f"<div class='card'><h3>{s['pair']} | {s['type']}</h3><p>Entry: {s['entry']} | TP: {s['tp']} | SL: {s['sl']}</p><p>{s['reason']}</p></div>", unsafe_allow_html=True)

    with t2:
        news = get_news()
        for n in news:
            st.markdown(f"<div class='card'><h4>{n['title']}</h4><p>{n['body'][:200]}...</p><a href='{n['url']}'>Read More</a></div>", unsafe_allow_html=True)

    with t3:
        alerts = pd.read_sql("SELECT * FROM intel ORDER BY id DESC", engine.conn)
        for _, a in alerts.iterrows():
            st.warning(f"🕒 {a['time']} | {a['type']} \n\n **{a['title']}**: {a['body']}")

    with t4:
        st.components.v1.html(f'<script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "240", "theme": "dark", "container_id": "tv"}});</script><div id="tv" style="height:500px;"></div>', height=510)

# --- 6. AUTHENTICATION ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.title("VIP ACCESS")
        u_id = st.text_input("Email")
        u_key = st.text_input("Security Key", type="password")
        if st.button("LOGIN"):
            h = hashlib.sha256(u_key.encode()).hexdigest()
            res = engine.conn.cursor().execute("SELECT role, expiry FROM users WHERE email=? AND key=?", (u_id, h)).fetchone()
            if res:
                if res[0] != 'ADMIN' and datetime.now() > datetime.strptime(res[1], '%Y-%m-%d'):
                    st.error("Access Expired.")
                else:
                    st.session_state.user = {"email": u_id, "role": res[0]}
                    st.rerun()
            else: st.error("Login Denied.")
else:
    if st.sidebar.button("Logout"): st.session_state.user = None; st.rerun()
    if st.session_state.user['role'] == 'ADMIN':
        m = st.sidebar.radio("Navigation
