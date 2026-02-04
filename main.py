import streamlit as st
import sqlite3
import pandas as pd
import requests
from datetime import datetime

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('crypto_pro_v3.db', check_same_thread=False)
    c = conn.cursor()
    # සිග්නල් ටේබල් එක
    c.execute('''CREATE TABLE IF NOT EXISTS signals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, 
                  status TEXT, pnl TEXT, img_url TEXT, time TEXT)''')
    # යූසර්ලාගේ ක්‍රියාකාරකම්
    c.execute('CREATE TABLE IF NOT EXISTS user_activity (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, pair TEXT, time TEXT)')
    # ඇප් සැකසුම්
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    
    # Default Settings ඇතුළත් කිරීම
    defaults = [('app_name', 'Crypto Pro VIP'), ('admin_pw', '2008')]
    c.executemany("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", defaults)
    conn.commit()
    return conn

db_conn = init_db()

def get_setting(key):
    res = db_conn.cursor().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return res[0] if res else ""

# --- 2. NEWS FETCH FUNCTION ---
def get_crypto_news():
    try:
        # CryptoCompare API එකෙන් අලුත්ම පුවත් ගැනීම
        res = requests.get("https://min-api.cryptocompare.com/data/v2/news/?lang=EN").json()
        return res['Data'][:5] 
    except: return []

# --- 3. LOGIN SYSTEM ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

def login():
    st.title(f"🔐 {get_setting('app_name')} Login")
    email = st.text_input("Gmail Address").lower()
    pw = st.text_input("Password", type="password")
    if st.button("Login Now"):
        if email == "ushan2008@gmail.com" and pw == get_setting('admin_pw'):
            st.session_state.logged_in, st.session_state.is_admin, st.session_state.user_email = True, True, email
            st.rerun()
        elif "@gmail.com" in email:
            st.session_state.logged_in, st.session_state.is_admin, st.session_state.user_email = True, False, email
            st.rerun()
        else:
            st.error("Invalid Credentials!")

# --- 4. ADMIN PANEL ---
def admin_panel():
    st.sidebar.subheader("Admin Control")
    menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "📢 Signal Manager", "⚙️ App Settings"])
    
    if menu == "📊 Dashboard":
        st.title("📊 Platform Dashboard")
        
        # Profit Tracker Graph
        df_pnl = pd.read_sql("SELECT time, pnl FROM signals WHERE status='Closed'", db_conn)
        if not df_pnl.empty:
            st.subheader("Profit/Loss Performance")
            st.line_chart(df_pnl.set_index('time'))
        
        st.subheader("Recent User Activity")
        st.dataframe(pd.read_sql("SELECT * FROM user_activity ORDER BY id DESC LIMIT 10", db_conn), use_container_width=True)

    elif menu == "📢 Signal Manager":
        st.title("📢 Signal Management")
        with st.expander("Create New VIP Signal"):
            with st.form("sig_form", clear_on_submit=True):
                p = st.text_input("Pair (e.g. BTC/USDT)")
                s = st.selectbox("Side", ["LONG", "SHORT"])
                col1, col2, col3 = st.columns(3)
                en = col1.text_input("Entry")
                tp = col2.text_input("TP")
                sl = col3.text_input("SL")
                img = st.text_input("Analysis Image URL (Optional)")
                if st.form_submit_button("Publish Signal"):
                    db_conn.cursor().execute("INSERT INTO signals (pair, side, entry, tp, sl, status, pnl, img_url, time) VALUES (?,?,?,?,?,?,?,?,?)",
                                             (p.upper(), s, en, tp, sl, "Active", "0", img, datetime.now().strftime("%Y-%m-%d")))
                    db_conn.commit()
                    st.success("Signal Published Successfully!")

        st.subheader("Edit or Close Signals")
        df_all = pd.read_sql("SELECT * FROM signals", db_conn)
        edited = st.data_editor(df_all, num_rows="dynamic", use_container_width=True)
        if st.button("Apply Database Changes"):
            edited.to_sql('signals', db_conn, if_exists='replace', index=False)
            st.rerun()

    elif menu == "⚙️ App Settings":
        st.title("⚙️ General Settings")
        new_name = st.text_input("Application Name", get_setting('app_name'))
        new_pw = st.text_input("Admin Password", get_setting('admin_pw'))
        if st.button("Save Changes"):
            db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='app_name'", (new_name,))
            db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='admin_pw'", (new_pw,))
            db_conn.commit()
            st.success("Settings Updated!")

# --- 5. USER DASHBOARD ---
def user_dashboard():
    st.title(f"🚀 {get_setting('app_name')}")
    t1, t2 = st.tabs(["🎯 Active Signals", "🌍 Market News"])
    
    with t1:
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        if not df.empty:
            for i, row in df.iterrows():
                color = "#00ffcc" if row['side'] == "LONG" else "#ff4b4b"
                with st.container():
                    st.markdown(f"""
                    <div style="background:#1e2329; padding:20px; border-radius:15px; border-left:8px solid {color}; margin-bottom:15px;">
                        <h2 style="color:{color}; margin:0;">{row['side']} {row['pair']}</h2>
                        <p style="font-size:18px;"><b>Entry:</b> {row['entry']} | <b>TP:</b> {row['tp']} | <b>SL:</b> {row['sl']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if row['img_url']:
                        st.image(row['img_url'], caption=f"{row['pair']} Technical Analysis", use_container_width=True)
                    
                    if st.button(f"🚀 I'm In ({row['pair']})", key=f"user_{row['id']}"):
                        db_conn.cursor().execute("INSERT INTO user_activity (email, pair, time) VALUES (?,?,?)",
                                                 (st.session_state.user_email, row['pair'], datetime.now().strftime("%H:%M")))
                        db_conn.commit()
                        st.balloons()
                        st.toast("Admin has been notified!")
                st.divider()
        else:
            st.info("No active signals at the moment. Please wait for Admin updates.")

    with t2:
        st.subheader("Latest Crypto News")
        news_list = get_crypto_news()
        for news in news_list:
            st.markdown(f"### {news['title']}")
            st.write(news['body'][:200] + "...")
            st.markdown(f"[Read Full Story]({news['url']})")
            st.caption(f"Source: {news['source']} | {datetime.fromtimestamp(news['published_on']).strftime('%Y-%m-%d')}")
            st.divider()

# --- MAIN NAVIGATION ---
if not st.session_state.logged_in:
    login()
else:
    if st.session_state.is_admin:
        admin_panel()
    else:
        user_dashboard()
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
