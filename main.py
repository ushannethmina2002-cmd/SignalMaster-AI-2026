import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import re
import streamlit.components.v1 as components

# --- 1. CONFIGURATION & DATABASE ---
def init_db():
    conn = sqlite3.connect('crypto_empire_final_pro.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    defaults = [('app_name', 'CRYPTO EMPIRE PRO'), ('theme_color', '#f0b90b'), ('admin_pw', '2008')]
    for k, v in defaults:
        c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)', (k, v))
    conn.commit()
    return conn

db_conn = init_db()

def get_cfg(key):
    res = db_conn.cursor().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return res[0] if res else ""

# --- 2. ADVANCED CSS (GLASSMORPHISM) ---
def apply_style():
    main_color = get_cfg('theme_color')
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
        * {{ font-family: 'Poppins', sans-serif; }}
        .stApp {{ background: radial-gradient(circle at top right, #1e2329, #0b0e11); color: #ffffff; }}
        [data-testid="stSidebar"] {{ background: rgba(30, 35, 41, 0.8) !important; backdrop-filter: blur(10px); }}
        .signal-card {{
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px; padding: 20px; margin-bottom: 15px; transition: 0.3s;
        }}
        .signal-card:hover {{ border-color: {main_color}; transform: translateY(-5px); background: rgba(255, 255, 255, 0.05); }}
        .stButton>button {{ background: {main_color} !important; color: black !important; font-weight: 600; border-radius: 12px; width: 100%; border:none; }}
        .stMetric {{ background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 15px; border-left: 5px solid {main_color}; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. ADMIN INTERFACE ---
def admin_panel():
    st.markdown(f"<h1 style='color:{get_cfg('theme_color')};'>⚡ CONTROL CENTER</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📢 Signals", "⚙️ Config"])
    
    with tab1:
        st.subheader("Platform Stats")
        df_all = pd.read_sql("SELECT * FROM signals", db_conn)
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Signals", len(df_all))
        c2.metric("Active Now", len(df_all[df_all['status'] == 'Active']))
        c3.metric("System Health", "100%")
        st.dataframe(df_all, use_container_width=True)

    with tab2:
        st.subheader("Post New Signal")
        with st.form("new_sig"):
            pair = st.text_input("Pair (e.g. BTC/USDT)")
            side = st.selectbox("Side", ["LONG", "SHORT"])
            entry = st.text_input("Entry Price")
            tp = st.text_input("Target Price (TP)")
            sl = st.text_input("Stop Loss (SL)")
            if st.form_submit_button("PUBLISH SIGNAL"):
                db_conn.cursor().execute("INSERT INTO signals (pair, side, entry, tp, sl, status, time) VALUES (?,?,?,?,?,?,?)",
                                         (pair, side, entry, tp, sl, "Active", datetime.now().strftime("%Y-%m-%d %H:%M")))
                db_conn.commit()
                st.success("Signal Published Successfully!")

    with tab3:
        st.subheader("Global Settings")
        new_name = st.text_input("Change App Name", get_cfg('app_name'))
        new_color = st.color_picker("Change Brand Color", get_cfg('theme_color'))
        if st.button("Apply New Changes"):
            db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='app_name'", (new_name,))
            db_conn.commit()
            st.rerun()

# --- 4. USER INTERFACE ---
def user_panel():
    st.sidebar.markdown(f"<h2 style='color:{get_cfg('theme_color')};'>{get_cfg('app_name')}</h2>", unsafe_allow_html=True)
    menu = st.sidebar.selectbox("Category", ["🎯 VIP Signals", "📊 Live Markets", "🧮 Calculator"])

    if menu == "🎯 VIP Signals":
        st.markdown(f"<h1>VIP SIGNALS</h1>", unsafe_allow_html=True)
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        if df.empty:
            st.info("Waiting for next pro signal...")
        for _, r in df.iterrows():
            badge = "#2ebd85" if r['side'] == "LONG" else "#f6465d"
            st.markdown(f"""
                <div class="signal-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="background:{badge}; color:white; padding:3px 12px; border-radius:5px; font-weight:600;">{r['side']}</span>
                        <small style="color:#848e9c;">{r['time']}</small>
                    </div>
                    <h2 style="margin:10px 0;">{r['pair']}</h2>
                    <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:10px;">
                        <div><small style="color:#848e9c;">ENTRY</small><br><b>{r['entry']}</b></div>
                        <div><small style="color:#848e9c;">TARGET</small><br><b style="color:#2ebd85;">{r['tp']}</b></div>
                        <div><small style="color:#848e9c;">STOP LOSS</small><br><b style="color:#f6465d;">{r['sl']}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    elif menu == "📊 Live Markets":
        st.title("Market Hub")
        components.html('<div id="c" style="height:500px;"><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize":true,"symbol":"BINANCE:BTCUSDT","theme":"dark","container_id":"c"});</script></div>', height=500)

# --- 5. SYSTEM LOGIC ---
apply_style()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, login_col, _ = st.columns([1, 1.5, 1])
    with login_col:
        st.markdown(f"<h1 style='text-align:center;'>{get_cfg('app_name')}</h1>", unsafe_allow_html=True)
        email = st.text_input("Gmail Address").lower()
        pw = st.text_input("Password", type="password")
        if st.button("UNLOCk ACCESS"):
            if email == "ushan2008@gmail.com" and pw == get_cfg('admin_pw'):
                st.session_state.update({"logged_in": True, "is_admin": True, "user_email": email})
                st.rerun()
            elif "@gmail.com" in email:
                st.session_state.update({"logged_in": True, "is_admin": False, "user_email": email})
                st.rerun()
else:
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    if st.session_state.is_admin:
        admin_panel()
    else:
        user_panel()
