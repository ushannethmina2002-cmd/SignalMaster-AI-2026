import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('signals_pro_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS signals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, 
                  status TEXT, time TEXT)''')
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
    st.title("🔐 Pro Trading Hub Login")
    email = st.text_input("Gmail Address").lower()
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if email == "ushan2008@gmail.com" and password == "2008":
            st.session_state.logged_in, st.session_state.is_admin, st.session_state.user_email = True, True, email
            st.rerun()
        elif "@gmail.com" in email:
            st.session_state.logged_in, st.session_state.is_admin, st.session_state.user_email = True, False, email
            st.rerun()

# --- 3. ADMIN PAGES ---

# Dashboard Page
def admin_dashboard_summary():
    st.title("📊 Admin Dashboard")
    col1, col2, col3 = st.columns(3)
    
    total_sigs = pd.read_sql("SELECT COUNT(*) FROM signals", db_conn).values[0][0]
    active_sigs = pd.read_sql("SELECT COUNT(*) FROM signals WHERE status='Active'", db_conn).values[0][0]
    total_users_actions = pd.read_sql("SELECT COUNT(*) FROM user_activity", db_conn).values[0][0]
    
    col1.metric("මුළු සිග්නල්", total_sigs)
    col2.metric("දැනට Active", active_sigs)
    col3.metric("යූසර්ලගේ ප්‍රතිචාර", total_users_actions)
    
    st.subheader("පසුගිය යූසර් ක්‍රියාකාරකම්")
    df_logs = pd.read_sql("SELECT * FROM user_activity ORDER BY id DESC LIMIT 5", db_conn)
    st.table(df_logs)

# Signal Management Page
def admin_signal_manager():
    st.title("📢 Signal Management")
    with st.expander("නව සිග්නල් එකක් පල කරන්න"):
        with st.form("sig_form", clear_on_submit=True):
            p = st.text_input("Pair")
            s = st.selectbox("Side", ["LONG", "SHORT"])
            en, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
            if st.form_submit_button("Broadcast"):
                db_conn.cursor().execute("INSERT INTO signals (pair, side, entry, tp, sl, status, time) VALUES (?,?,?,?,?,?,?)",
                                         (p.upper(), s, en, tp, sl, "Active", datetime.now().strftime("%Y-%m-%d %H:%M")))
                db_conn.commit()
                st.success("පල කළා!")

    st.subheader("පවතින සිග්නල් පාලනය")
    df_sigs = pd.read_sql("SELECT * FROM signals", db_conn)
    edited = st.data_editor(df_sigs, num_rows="dynamic")
    if st.button("Save Changes"):
        edited.to_sql('signals', db_conn, if_exists='replace', index=False)
        st.success("යාවත්කාලීන වුණා!")

# --- 4. USER VIEW ---
def user_view():
    st.title("🚀 Active Signals")
    df = pd.read_sql("SELECT * FROM signals WHERE status='Active'", db_conn)
    for i, row in df.iterrows():
        st.info(f"📊 {row['side']} {row['pair']} | Entry: {row['entry']}")

# --- 5. MAIN NAVIGATION ---
if not st.session_state.logged_in:
    login()
else:
    st.sidebar.title("Crypto Pro Hub")
    
    if st.session_state.is_admin:
        # මෙන්න මෙතනට තමයි අලුත් ඔප්ෂන් ටික එකතු කළේ
        menu = st.sidebar.radio("Admin Menu", [
            "🏠 Dashboard", 
            "📢 Signal Manager", 
            "📊 User Analytics", 
            "⚙️ App Settings"
        ])
        
        if menu == "🏠 Dashboard": admin_dashboard_summary()
        elif menu == "📢 Signal Manager": admin_signal_manager()
        elif menu == "📊 User Analytics": st.title("Analytics Coming Soon...")
        elif menu == "⚙️ App Settings": st.title("Settings Coming Soon...")
        
    else:
        user_view()
        
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

