
import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime
import re

# --- 1. CONFIGURATION (ටෙලිග්‍රෑම් විස්තර) ---
BOT_TOKEN = "8526792641:AAHEyboZTc9-lporhmcAGekEVO-Z-D-pvb8"
CHANNEL_ID = "-1003662013328"

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('crypto_ultimate_sync.db', check_same_thread=False)
    c = conn.cursor()
    # සිග්නල් ටේබල් එක (msg_id එක Unique දමා ඇත්තේ එකම මැසේජ් එක දෙපාරක් වැටීම වැළැක්වීමටයි)
    c.execute('''CREATE TABLE IF NOT EXISTS signals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, 
                  tp TEXT, sl TEXT, status TEXT, pnl TEXT, img_url TEXT, time TEXT, msg_id TEXT UNIQUE)''')
    c.execute('CREATE TABLE IF NOT EXISTS user_activity (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, pair TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    
    # Default Settings
    defaults = [('app_name', 'Crypto Pro VIP Hub'), ('admin_pw', '2008')]
    c.executemany("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", defaults)
    conn.commit()
    return conn

db_conn = init_db()

def get_setting(key):
    res = db_conn.cursor().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return res[0] if res else ""

# --- 3. TELEGRAM AUTO-SYNC LOGIC ---
def sync_from_telegram():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url).json()
        if response.get("ok"):
            for result in response.get("result", []):
                msg = result.get("channel_post", {})
                if str(msg.get("chat", {}).get("id")) == CHANNEL_ID:
                    text = msg.get("text", "")
                    msg_id = str(msg.get("message_id"))
                    
                    check = db_conn.cursor().execute("SELECT id FROM signals WHERE msg_id=?", (msg_id,)).fetchone()
                    if not check and text:
                        # ඉතා සරල Parsing logic එකක් - මෙය චැනල් එකේ මැසේජ් එක අනුව වෙනස් විය හැක
                        side = "LONG" if any(x in text.upper() for x in ["BUY", "LONG"]) else "SHORT"
                        pair_match = re.search(r'([A-Z0-9]{2,10}/?[A-Z0-9]{2,10})', text.upper())
                        pair = pair_match.group(1) if pair_match else "NEW SIGNAL"
                        
                        c = db_conn.cursor()
                        curr_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                        c.execute("""INSERT INTO signals (pair, side, entry, tp, sl, status, pnl, img_url, time, msg_id) 
                                     VALUES (?,?,?,?,?,?,?,?,?,?)""",
                                  (pair, side, "Market", "See Chart", "See Chart", "Active", "0", "", curr_time, msg_id))
                        db_conn.commit()
                        st.toast(f"Telegram Sync: {pair} Added!")
    except:
        pass

# --- 4. NEWS FETCH ---
def get_crypto_news():
    try:
        res = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN").json()
        return res['Data'][:5]
    except: return []

# --- 5. LOGIN SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def login():
    st.title(f"🔐 {get_setting('app_name')} Login")
    email = st.text_input("Gmail Address").lower()
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if email == "ushan2008@gmail.com" and pw == get_setting('admin_pw'):
            st.session_state.logged_in, st.session_state.is_admin, st.session_state.user_email = True, True, email
            st.rerun()
        elif "@gmail.com" in email:
            st.session_state.logged_in, st.session_state.is_admin, st.session_state.user_email = True, False, email
            st.rerun()

# --- 6. ADMIN PANEL ---
def admin_panel():
    st.sidebar.title("Admin Menu")
    menu = st.sidebar.radio("Go to", ["🏠 Dashboard", "📢 Signal Manager", "👥 User Logs", "⚙️ Settings"])
    
    if menu == "🏠 Dashboard":
        st.title("📊 Platform Overview")
        c1, c2, c3 = st.columns(3)
        total_s = pd.read_sql("SELECT COUNT(*) FROM signals", db_conn).values[0][0]
        active_s = pd.read_sql("SELECT COUNT(*) FROM signals WHERE status='Active'", db_conn).values[0][0]
        
        c1.metric("Total Signals", total_s)
        c2.metric("Active Now", active_s)
        
        # Profit Tracker Graph
        df_pnl = pd.read_sql("SELECT time, pnl FROM signals WHERE status='Closed'", db_conn)
        if not df_pnl.empty:
            st.subheader("Profit Growth")
            st.line_chart(df_pnl.set_index('time'))

    elif menu == "📢 Signal Manager":
        st.title("📢 Manage Signals")
        # Manual Entry
        with st.expander("Post Manual Signal"):
            with st.form("man_sig"):
                p = st.text_input("Pair")
                s = st.selectbox("Side", ["LONG", "SHORT"])
                en, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
                img = st.text_input("Chart Image URL")
                if st.form_submit_button("Post"):
                    db_conn.cursor().execute("INSERT INTO signals (pair, side, entry, tp, sl, status, pnl, img_url, time) VALUES (?,?,?,?,?,?,?,?,?)",
                                             (p.upper(), s, en, tp, sl, "Active", "0", img, datetime.now().strftime("%Y-%m-%d")))
                    db_conn.commit()
                    st.success("Posted!")

        st.subheader("All Signals (Edit/Delete/Close)")
        df_all = pd.read_sql("SELECT * FROM signals", db_conn)
        edited = st.data_editor(df_all, num_rows="dynamic")
        if st.button("Save Changes"):
            edited.to_sql('signals', db_conn, if_exists='replace', index=False)
            st.rerun()

    elif menu == "⚙️ Settings":
        st.title("⚙️ App Settings")
        new_name = st.text_input("App Name", get_setting('app_name'))
        new_pw = st.text_input("Admin Password", get_setting('admin_pw'))
        if st.button("Update Settings"):
            db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='app_name'", (new_name,))
            db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='admin_pw'", (new_pw,))
            db_conn.commit()
            st.success("Updated!")

# --- 7. USER DASHBOARD ---
def user_dashboard():
    st.title(f"🚀 {get_setting('app_name')}")
    sync_from_telegram() # ඇප් එක ලෝඩ් වනවිට Telegram Sync වේ
    
    t1, t2 = st.tabs(["🎯 Live Signals", "📰 Market News"])
    
    with t1:
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        if not df.empty:
            for i, row in df.iterrows():
                color = "#00ffcc" if row['side'] == "LONG" else "#ff4b4b"
                with st.container():
                    st.markdown(f"""
                    <div style="background:#1e2329; padding:20px; border-radius:15px; border-left:8px solid {color}; margin-bottom:15px;">
                        <h2 style="color:{color}; margin:0;">{row['side']} {row['pair']}</h2>
                        <p><b>Entry:</b> {row['entry']} | <b>TP:</b> {row['tp']} | <b>SL:</b> {row['sl']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if row['img_url']: st.image(row['img_url'], use_container_width=True)
                    if st.button(f"Join Trade ({row['pair']})", key=f"btn_{row['id']}"):
                        db_conn.cursor().execute("INSERT INTO user_activity (email, pair, time) VALUES (?,?,?)",
                                                 (st.session_state.user_email, row['pair'], datetime.now().strftime("%H:%M")))
                        db_conn.commit()
                        st.balloons()
        else: st.info("No active signals yet.")

    with t2:
        for n in get_crypto_news():
            st.subheader(n['title'])
            st.write(n['body'][:150] + "...")
            st.markdown(f"[Read More]({n['url']})")
            st.divider()

# --- MAIN ---
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.is_admin: admin_panel()
    else: user_dashboard()
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
