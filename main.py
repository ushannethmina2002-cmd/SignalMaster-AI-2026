import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG & DB ---
def init_db():
    conn = sqlite3.connect('crypto_ultra_v13.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    defaults = [('app_name', 'CRYPTO EMPIRE PRO'), ('theme_color', '#f0b90b')]
    c.executemany("INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)", defaults)
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. THE SECRET SAUCE: ULTRA UI CSS ---
def apply_ultra_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
        
        * { font-family: 'Inter', sans-serif; }

        /* Main App Background */
        .stApp {
            background: radial-gradient(circle at top right, #1e2329, #0b0e11);
            color: #ffffff;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(30, 35, 41, 0.7) !important;
            backdrop-filter: blur(15px);
            border-right: 1px solid rgba(255,255,255,0.1);
        }

        /* Professional Signal Cards */
        .signal-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(4px);
            transition: 0.4s ease;
        }
        
        .signal-card:hover {
            border-color: #f0b90b;
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.05);
        }

        /* Glowing Buttons */
        .stButton>button {
            background: linear-gradient(90deg, #f0b90b, #fcd535) !important;
            color: #000 !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 15px rgba(240, 185, 11, 0.3);
        }

        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 10px 20px;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

# --- 3. UI COMPONENTS ---
apply_ultra_style()

# Session State
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def user_ui():
    st.sidebar.markdown("### 💎 PREMIUM ACCESS")
    menu = st.sidebar.selectbox("MENU", ["🎯 Signals", "📈 Market", "🧮 Tools"])

    if menu == "🎯 Signals":
        st.markdown("<h1 style='text-align: center; color: #f0b90b;'>🎯 ACTIVE SIGNALS</h1>", unsafe_allow_html=True)
        
        # Example Signal Card
        st.markdown("""
            <div class="signal-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 style="margin:0; color:#f0b90b;">BTC / USDT</h2>
                    <span style="background:#2ebd85; color:white; padding:5px 15px; border-radius:50px; font-weight:bold;">LONG</span>
                </div>
                <hr style="opacity:0.1; margin:15px 0;">
                <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; text-align:center;">
                    <div><small style="color:#848e9c;">ENTRY</small><br><b style="font-size:1.2em;">42,500</b></div>
                    <div><small style="color:#848e9c;">TARGET</small><br><b style="font-size:1.2em; color:#2ebd85;">45,000</b></div>
                    <div><small style="color:#848e9c;">STOP LOSS</small><br><b style="font-size:1.2em; color:#f6465d;">41,200</b></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    elif menu == "📈 Market":
        st.title("📈 Real-Time Insight")
        components.html('<div id="chart" style="height:500px;"><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize": true,"symbol": "BINANCE:BTCUSDT","theme": "dark","container_id": "chart"});</script></div>', height=500)

def login_page():
    st.markdown("<div style='text-align:center; padding:50px;'>", unsafe_allow_html=True)
    st.image("https://cryptologos.cc/logos/binance-coin-bnb-logo.png", width=80)
    st.title("Crypto Empire Login")
    email = st.text_input("GMAIL")
    pw = st.text_input("PASSWORD", type="password")
    if st.button("SIGN IN"):
        st.session_state.logged_in = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# --- EXECUTION ---
if not st.session_state.logged_in:
    login_page()
else:
    user_ui()
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
