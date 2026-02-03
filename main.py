import streamlit as st
import pandas as pd
from datetime import datetime

# පිටුවේ සැකසුම් (Page Config)
st.set_page_config(page_title="Crypto Signals Pro", layout="centered")

# --- සරල දත්ත ගබඩාවක් (දැනට පාවිච්චි කිරීමට) ---
if 'signals' not in st.session_state:
    st.session_state.signals = []

# --- LOGIN පද්ධතිය ---
def login():
    st.title("🚀 Crypto Signals Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if email == "ushan2008@gmail.com" and password == "2008":
            st.session_state.logged_in = True
            st.session_state.is_admin = True
            st.rerun()
        elif email != "" and password != "":
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.rerun()
        else:
            st.error("කරුණාකර විස්තර ඇතුළත් කරන්න")

# --- ADMIN PANEL ---
def admin_panel():
    st.header("⚡ Admin Control Panel")
    with st.form("signal_form"):
        pair = st.text_input("Coin Pair (e.g., BTC/USDT)")
        type = st.selectbox("Type", ["LONG", "SHORT"])
        entry = st.text_input("Entry Zone")
        tp = st.text_input("Take Profit")
        sl = st.text_input("Stop Loss")
        
        if st.form_submit_button("Post Signal"):
            new_signal = {
                "pair": pair.upper(),
                "type": type,
                "entry": entry,
                "tp": tp,
                "sl": sl,
                "time": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.signals.insert(0, new_signal)
            st.success(f"{pair} Signal එක සාර්ථකව පල කරා!")

# --- USER DASHBOARD ---
def user_dashboard():
    st.title("📈 Active Signals")
    
    if not st.session_state.signals:
        st.info("දැනට සක්‍රීය සිග්නල් කිසිවක් නැත.")
    else:
        for sig in st.session_state.signals:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"{sig['pair']} ({sig['type']})")
                    st.write(f"**Entry:** {sig['entry']} | **TP:** {sig['tp']} | **SL:** {sig['sl']}")
                with col2:
                    st.write(f"🕒 {sig['time']}")
                st.divider()

# --- RISK CALCULATOR ---
def risk_calculator():
    st.header("🧮 Risk Management Tool")
    balance = st.number_input("Wallet Balance ($)", min_value=0.0)
    risk_percent = st.slider("Risk (%)", 1, 10, 2)
    
    if balance > 0:
        risk_amount = balance * (risk_percent / 100)
        st.success(f"ඔබ මේ trade එකට උපරිම වැය කළ යුතු මුදල: **${risk_amount:.2f}**")

# --- ප්‍රධාන පාලනය (Main Control) ---
if 'logged_in' not in st.session_state:
    login()
else:
    menu = ["Signals", "Risk Calculator"]
    if st.session_state.is_admin:
        menu.insert(0, "Admin Panel")
        
    choice = st.sidebar.radio("Menu", menu)
    
    if st.sidebar.button("Logout"):
        del st.session_state.logged_in
        st.rerun()

    if choice == "Admin Panel":
        admin_panel()
    elif choice == "Signals":
        user_dashboard()
    elif choice == "Risk Calculator":
        risk_calculator()
