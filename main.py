import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. DATABASE SETUP (ඇප් එක ඇතුළෙම ඩේටාබේස් එක සැකසීම) ---
def init_db():
    conn = sqlite3.connect('crypto_signals.db', check_same_thread=False)
    c = conn.cursor()
    # සිග්නල් ගබඩා කරන ටේබල් එක
    c.execute('''CREATE TABLE IF NOT EXISTS signals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, 
                  status TEXT, time TEXT)''')
    # යූසර්ලා ලොග් කරන ටේබල් එක
    c.execute('''CREATE TABLE IF NOT EXISTS user_activity 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  email TEXT, pair TEXT, action_time TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. LOGIN LOGIC ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Crypto Pro Secure Login")
    email = st.text_input("Gmail Address").lower()
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email == "ushan2008@gmail.com" and password == "2008":
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.session_state.user_email = email
            st.rerun()
        elif "@gmail.com" in email:
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("විස්තර වැරදියි. නැවත උත්සාහ කරන්න.")

# --- 3. ADMIN PANEL ---
def admin_panel():
    st.title("👨‍💼 Admin Control Panel")
    tab1, tab2 = st.tabs(["📢 Post Signal", "🛠️ Manage All Data"])
    
    with tab1:
        with st.form("add_signal_form", clear_on_submit=True):
            p = st.text_input("Pair (e.g. BTC/USDT)")
            s = st.selectbox("Side", ["LONG", "SHORT"])
            en, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
            if st.form_submit_button("Broadcast Signal"):
                c = db_conn.cursor()
                c.execute("INSERT INTO signals (pair, side, entry, tp, sl, status, time) VALUES (?,?,?,?,?,?,?)",
                          (p.upper(), s, en, tp, sl, "Active", datetime.now().strftime("%Y-%m-%d %H:%M")))
                db_conn.commit()
                st.success("Signal එක ඇප් එකේ Database එකට සේව් වුණා!")

    with tab2:
        st.subheader("Current Data in Database")
        df_sigs = pd.read_sql("SELECT * FROM signals", db_conn)
        # ඩේටා මකන්න හෝ එඩිට් කරන්න මෙතනින් පුළුවන්
        edited_df = st.data_editor(df_sigs, num_rows="dynamic", key="data_editor")
        if st.button("Save Changes"):
            edited_df.to_sql('signals', db_conn, if_exists='replace', index=False)
            st.success("Database එක යාවත්කාලීන වුණා!")

# --- 4. USER DASHBOARD ---
def user_dashboard():
    st.title("🚀 Live Crypto Signals")
    # Database එකෙන් දත්ත කියවීම
    df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
    
    if not df.empty:
        for i, row in df.iterrows():
            color = "#00ffcc" if row['side'] == "LONG" else "#ff4b4b"
            st.markdown(f"""
            <div style="background:#1e2329; padding:20px; border-radius:10px; border-left:5px solid {color}; margin-bottom:10px;">
                <h3 style="color:{color};">{row['side']} {row['pair']}</h3>
                <p>Entry: {row['entry']} | TP: {row['tp']} | SL: {row['sl']}</p>
                <small>Time: {row['time']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"✅ I'm In ({row['pair']})", key=f"btn_{row['id']}"):
                c = db_conn.cursor()
                c.execute("INSERT INTO user_activity (email, pair, action_time) VALUES (?,?,?)",
                          (st.session_state.user_email, row['pair'], datetime.now().strftime("%H:%M:%S")))
                db_conn.commit()
                st.success("Admin notified! Good luck.")
    else:
        st.info("දැනට සක්‍රීය සිග්නල් කිසිවක් නැත.")

# --- NAVIGATION ---
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("Pro Trading Hub")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.is_admin:
        mode = st.sidebar.radio("Navigation", ["Admin Panel", "Signals View"])
        if mode == "Admin Panel": admin_panel()
        else: user_dashboard()
    else:
        user_dashboard()
