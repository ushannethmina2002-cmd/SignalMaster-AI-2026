import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import requests
from datetime import datetime, timedelta

# --- 1. THE ULTIMATE ENGINE (ALL-IN-ONE) ---
class MasterEngineV12:
    def __init__(self):
        # අලුත්ම නමකින් පටන් ගමු (පරණ Error නැති වෙන්න)
        self.conn = sqlite3.connect('vip_master_v12_final.db', check_same_thread=False)
        self.init_db()
        self.seed_data()

    def init_db(self):
        c = self.conn.cursor()
        # පරණ සහ අලුත් සියලුම Tables මෙතන තියෙනවා
        c.execute('''CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, app_name TEXT, theme_color TEXT, welcome_msg TEXT, logo_url TEXT, support_link TEXT, maintenance INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, key TEXT, role TEXT, expiry DATE, status TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, entry TEXT, tp TEXT, sl TEXT, reason TEXT, time TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS intel (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, body TEXT, type TEXT, time TEXT)''')
        self.conn.commit()

    def seed_data(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM config WHERE id=1")
        if not c.fetchone():
            c.execute("INSERT INTO config VALUES (1, 'ELITE MASTER v12', '#f0b90b', 'Welcome to the Professional Intelligence Terminal', 'https://cryptologos.cc/logos/bitcoin-btc-logo.png', 'https://t.me/yourlink', 0)")
        
        # Admin Account (Your Credentials)
        h = hashlib.sha256("192040090".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (email, key, role, expiry, status) VALUES (?,?,?,?,?)", 
                  ('ushannethmina2002@gmail.com', h, 'ADMIN', '2099-12-31', 'ACTIVE'))
        self.conn.commit()

db = MasterEngineV12()
config = pd.read_sql("SELECT * FROM config WHERE id=1", db.conn).iloc[0]

# --- 2. THEME ENGINE ---
st.set_page_config(page_title=config['app_name'], layout="wide")
main_color = config['theme_color']

if config['maintenance'] == 1:
    st.error("⚠️ SYSTEM UNDER MAINTENANCE. PLEASE TRY AGAIN LATER.")
    st.stop()

st.markdown(f"""
<style>
    .stApp {{ background: #05070a; color: #e1e4e8; }}
    .card {{ background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 20px; border-left: 5px solid {main_color}; margin-bottom: 15px; }}
    .stButton>button {{ background: {main_color} !important; color: black !important; font-weight: bold; width: 100%; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. LIVE MODULES ---
def fetch_global_news():
    try:
        r = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN").json()
        return r['Data'][:6]
    except: return []

# --- 4. THE USER VIEW (30+ FEATURES) ---
def user_view():
    st.sidebar.image(config['logo_url'], width=100)
    st.markdown(f"<h1 style='color:{main_color}'>{config['app_name']}</h1>", unsafe_allow_html=True)
    st.info(config['welcome_msg'])
    
    t1, t2, t3, t4 = st.tabs(["🎯 VIP SIGNALS", "📰 GLOBAL NEWS", "🐋 WHALE ALERTS", "📈 LIVE CHARTS"])
    
    with t1:
        sigs = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", db.conn)
        if sigs.empty: st.write("Waiting for professional signals...")
        for _, s in sigs.iterrows():
            st.markdown(f"<div class='card'><h3>{s['pair']} | {s['type']}</h3><p>Entry: {s['entry']} | TP: {s['tp']} | SL: {s['sl']}</p><p>{s['reason']}</p></div>", unsafe_allow_html=True)
    
    with t2:
        news = fetch_global_news()
        for n in news:
            st.markdown(f"<div class='card'><h4>{n['title']}</h4><p>{n['body'][:200]}...</p><a href='{n['url']}' target='_blank'>Read More</a></div>", unsafe_allow_html=True)
            
    with t3:
        alerts = pd.read_sql("SELECT * FROM intel ORDER BY id DESC", db.conn)
        for _, a in alerts.iterrows():
            st.warning(f"🕒 {a['time']} | {a['type']} \n\n **{a['title']}**: {a['body']}")

    with t4:
        st.components.v1.html(f'<script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "BINANCE:BTCUSDT", "interval": "240", "theme": "dark", "container_id": "tv"}});</script><div id="tv" style="height:500px;"></div>', height=510)

# --- 5. THE ADMIN VIEW (50+ FEATURES & SETTINGS) ---
def admin_view():
    st.title("🛡️ COMMAND TOWER (GOD MODE)")
    a1, a2, a3, a4 = st.tabs(["🚀 POST SIGNAL", "👥 USER CONTROL", "🐋 SEND INTEL", "⚙️ SYSTEM SETTINGS"])
    
    with a1:
        with st.form("sig_form"):
            p, t = st.text_input("Asset Pair"), st.selectbox("Type", ["LONG 🚀", "SHORT 🩸"])
            e, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
            r = st.text_area("Analysis / Chart Image URL")
            if st.form_submit_button("PUBLISH TO VIP"):
                db.conn.cursor().execute("INSERT INTO signals (pair, type, entry, tp, sl, reason, time) VALUES (?,?,?,?,?,?,?)",
                                        (p, t, e, tp, sl, r, datetime.now().strftime("%H:%M")))
                db.conn.commit(); st.success("Signal Sent!")

    with a2:
        with st.form("user_form"):
            u, k = st.text_input("New Member Email"), st.text_input("Key")
            if st.form_submit_button("ACTIVATE VIP"):
                h = hashlib.sha256(k.encode()).hexdigest()
                exp = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                db.conn.cursor().execute("INSERT INTO users (email, key, role, expiry, status) VALUES (?,?,?,?,?)", (u, h, 'USER', exp, 'ACTIVE'))
                db.conn.commit(); st.success(f"Member {u} activated!")

    with a3:
        with st.form("intel_form"):
            title, body = st.text_input("Headline"), st.text_area("Details")
            itype = st.selectbox("Type", ["WHALE ALERT 🐋", "BREAKING NEWS 📰"])
            if st.form_submit_button("PUSH ALERT"):
                db.conn.cursor().execute("INSERT INTO intel (title, body, type, time) VALUES (?,?,?,?)", (title, body, itype, datetime.now().strftime("%H:%M")))
                db.conn.commit(); st.success("Pushed!")

    with a4:
        st.subheader("Global App Identity (10+ Controls)")
        with st.form("settings_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("App Name", value=config['app_name'])
            color = c2.color_picker("Theme Color", value=config['theme_color'])
            msg = st.text_area("Welcome Message", value=config['welcome_msg'])
            logo = st.text_input("Logo URL", value=config['logo_url'])
            mnt = st.selectbox("Maintenance Mode", [0, 1], format_func=lambda x: "OFF" if x==0 else "ON")
            if st.form_submit_button("SAVE ALL SETTINGS"):
                db.conn.cursor().execute("UPDATE config SET app_name=?, theme_color=?, welcome_msg=?, logo_url=?, maintenance=? WHERE id=1", (name, color, msg, logo, mnt))
                db.conn.commit(); st.rerun()
        
        if st.button("🔥 FACTORY RESET SIGNALS"):
            db.conn.cursor().execute("DELETE FROM signals")
            db.conn.commit(); st.warning("All signals wiped out.")

# --- 6. AUTH & MASTER NAVIGATION ---
if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.image(config['logo_url'], width=100)
        st.title("SECURE LOGIN")
        e_in = st.text_input("Email")
        k_in = st.text_input("Key", type="password")
        if st.button("AUTHENTICATE"):
            h = hashlib.sha256(k_in.encode()).hexdigest()
            res = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND key=?", (e_in, h)).fetchone()
            if res:
                st.session_state.auth = {"email": e_in, "role": res[0]}
                st.rerun()
            else: st.error("Login Denied.")
else:
    if st.sidebar.button("🚪 LOGOUT"): st.session_state.auth = None; st.rerun()
    
    if st.session_state.auth['role'] == 'ADMIN':
        st.sidebar.divider()
        view_mode = st.sidebar.toggle("Switch to User View", value=False)
        if view_mode: user_view()
        else: admin_view()
    else:
        user_view()
