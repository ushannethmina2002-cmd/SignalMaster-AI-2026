import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- 1. SET PAGE CONFIG & REMOVE WATERMARKS ---
st.set_page_config(page_title="HappyShop Enterprise", page_icon="🛒", layout="centered")

# CSS එකෙන් Streamlit අංග සියල්ල හංගනවා
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* ඇප් එක ලෝඩ් වෙද්දී එන ලෝගෝ එක අයින් කිරීමට */
            div[data-testid="stStatusWidget"] {visibility: hidden;}
            
            /* මුළු Background එකම සුදු පාට කිරීමට (ඔයාගේ ෆොටෝ එකේ විදිහට) */
            .stApp {
                background-color: white;
            }
            
            /* Text Labels කළු පාට කිරීමට */
            label {
                color: #444 !important;
                font-weight: bold !important;
            }
            
            /* Login Button එකේ පෙනුම වෙනස් කිරීමට */
            .stButton>button {
                background-color: white;
                color: #444;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 10px 20px;
                width: 100%;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. DATABASE SETUP ---
class HappyShopDB:
    def __init__(self):
        self.conn = sqlite3.connect('happyshop_final.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT UNIQUE, password TEXT, role TEXT)''')
        # Owner Account (happyshop@gmail.com | VLG0005)
        h_pass = hashlib.sha256("VLG0005".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, 'OWNER')", ("happyshop@gmail.com", h_pass))
        self.conn.commit()

db = HappyShopDB()

# --- 3. LOGIN PAGE UI (ඔයාගේ ෆොටෝ එකේ විදිහට) ---
def login_page():
    # මැදට ලෝගෝ එක සහ ටයිටල් එක ගැනීම
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # HappyShop ලෝගෝ එක (ඔයාගේ ලෝගෝ එකේ ලින්ක් එක මෙතනට දාන්න)
    st.image("https://i.imgur.com/8K5yY7X.png", width=150) # මම තාවකාලික ලෝගෝ එකක් දැම්මා
    
    st.markdown("""
        <h1 style='text-align: center; color: #f1c40f; font-family: sans-serif; margin-bottom: 0;'>HappyShop</h1>
        <h1 style='text-align: center; color: #f1c40f; font-family: sans-serif; margin-top: 0;'>Login</h1>
    """, unsafe_allow_html=True)
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    if st.button("Login to Dashboard"):
        hp = hashlib.sha256(password.encode()).hexdigest()
        res = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND password=?", (email, hp)).fetchone()
        if res:
            st.session_state.user = {"email": email, "role": res[0]}
            st.rerun()
        else:
            st.error("Invalid Credentials!")

# --- 4. APP LOGIC ---
if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    login_page()
else:
    # මෙතනින් පස්සේ Dashboard එක පටන් ගන්නවා
    st.sidebar.success(f"Logged in as {st.session_state.user['role']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    st.write("# Welcome to HappyShop Dashboard")
    # කලින් දුන්න Dashboard කෝඩ් එක මෙතනට දාන්න...
