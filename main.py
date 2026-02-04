import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- PAGE SETUP ---
st.set_page_config(page_title="Crypto Pro Hub", layout="wide")

# Google Sheet එකට සම්බන්ධ වීම
conn = st.connection("gsheets", type=GSheetsConnection)

# --- LOGIN SYSTEM ---
def login():
    if 'logged_in' not in st.session_state:
        st.title("🔐 Crypto Pro Login")
        email = st.text_input("Gmail Address")
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
    return st.session_state.get('logged_in', False)

# --- ADMIN PANEL (MANAGE DATA) ---
def admin_panel():
    st.title("👨‍💼 Admin Control Center")
    tab1, tab2 = st.tabs(["📢 Add New Signal", "🛠️ Manage & Delete Signals"])

    with tab1:
        with st.form("new_sig"):
            pair = st.text_input("Pair (BTC/USDT)")
            side = st.selectbox("Side", ["LONG", "SHORT"])
            entry = st.text_input("Entry")
            tp = st.text_input("TP")
            sl = st.text_input("SL")
            if st.form_submit_button("Broadcast Signal"):
                # දැනට තියෙන දත්ත කියවීම
                df = conn.read(worksheet="Sheet1")
                new_row = pd.DataFrame([{
                    "Pair": pair.upper(), "Side": side, "Entry": entry, 
                    "TP": tp, "SL": sl, "Status": "Active", 
                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M")
                }])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("Signal Saved to Google Sheet!")

    with tab2:
        st.subheader("Edit or Delete from App")
        df = conn.read(worksheet="Sheet1")
        # මෙතනදී ඔයාට ඇප් එක ඇතුළෙම Sheet එකේ දත්ත Edit කරන්න හෝ පේළි මකන්න පුළුවන්
        edited_df = st.data_editor(df, num_rows="dynamic")
        
        if st.button("Save Changes to Sheet"):
            conn.update(worksheet="Sheet1", data=edited_df)
            st.success("Google Sheet Updated Successfully!")

# --- USER DASHBOARD ---
def user_dashboard():
    st.title("🚀 Active Crypto Signals")
    # Sheet එකේ තියෙන සිග්නල් කියවීම
    df = conn.read(worksheet="Sheet1")
    
    if not df.empty:
        for index, row in df.iterrows():
            if row['Status'] == "Active":
                color = "#00ffcc" if row['Side'] == "LONG" else "#ff4b4b"
                with st.container():
                    st.markdown(f"""
                    <div style="background:#1e2329; padding:20px; border-radius:10px; border-left:5px solid {color}; margin-bottom:10px;">
                        <h3 style="color:{color};">{row['Side']} {row['Pair']}</h3>
                        <p>Entry: {row['Entry']} | TP: {row['TP']} | SL: {row['SL']}</p>
                        <small>Posted: {row['Time']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"✅ I'm In ({row['Pair']})", key=f"btn_{index}"):
                        st.balloons()
                        st.success("Trade Joined! Admin will be notified.")
    else:
        st.info("No active signals at the moment.")

# --- MAIN LOGIC ---
if login():
    st.sidebar.title("Crypto Pro")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.is_admin:
        choice = st.sidebar.radio("Menu", ["Admin Panel", "User View"])
        if choice == "Admin Panel": admin_panel()
        else: user_dashboard()
    else:
        user_dashboard()

