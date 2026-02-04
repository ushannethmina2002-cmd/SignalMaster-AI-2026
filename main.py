import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Crypto Pro Hub", layout="wide")

# --- 1. CONNECTION SETUP ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ Secrets Setup එකේ ප්‍රශ්නයක් තියෙනවා. කරුණාකර URL එක පරීක්ෂා කරන්න.")

# --- 2. LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():
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

# --- 3. ADMIN PANEL ---
def admin_panel():
    st.title("👨‍💼 Admin Panel")
    with st.form("new_sig"):
        p = st.text_input("Pair")
        s = st.selectbox("Side", ["LONG", "SHORT"])
        en, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
        if st.form_submit_button("Broadcast"):
            try:
                df = conn.read(worksheet="Sheet1")
                new_row = pd.DataFrame([{"Pair": p.upper(), "Side": s, "Entry": en, "TP": tp, "SL": sl, "Status": "Active", "Time": datetime.now().strftime("%H:%M")}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.success("✅ Success! Sheet එකට දත්ත එකතු වුණා.")
            except:
                st.error("❌ Sheet එක සොයාගත නොහැක. ටැබ් එකේ නම 'Sheet1' ද කියා බලන්න.")

# --- 4. USER DASHBOARD ---
def user_dashboard():
    st.title("🚀 Live Signals")
    try:
        df = conn.read(worksheet="Sheet1")
        active_sigs = df[df['Status'] == "Active"]
        if not active_sigs.empty:
            for i, row in active_sigs.iterrows():
                st.info(f"📊 {row['Pair']} | {row['Side']} | Entry: {row['Entry']}")
        else:
            st.write("දැනට සිග්නල් නැත.")
    except:
        st.warning("⚠️ දත්ත කියවීමට නොහැක. Admin ලොග් වී පළමු සිග්නල් එක ඇතුළත් කරන්න.")

# --- MAIN ---
if not st.session_state.logged_in:
    login()
else:
    mode = st.sidebar.radio("Menu", ["Admin", "Signals"]) if st.session_state.is_admin else "Signals"
    if mode == "Admin": admin_panel()
    else: user_dashboard()
