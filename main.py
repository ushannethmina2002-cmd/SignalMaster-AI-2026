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
            border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px;
            transition: 0.3s ease;
        }}
        .signal-card:hover {{ border-color: {color}; transform: scale(1.01); }}
        .vip-badge {{ background: linear-gradient(90deg, #f0b90b, #ffea00); color: black; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. ADMIN FEATURES ---
def admin_portal():
    st.sidebar.title("💎 ELITE ADMIN")
    task = st.sidebar.selectbox("System Tasks", ["Dashboard", "Signal Manager", "User Access", "App Settings"])
    
    if task == "Dashboard":
        st.title("📊 Platform Oversight")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Users", "1.2k")
        c2.metric("Win Rate", "88%")
        c3.metric("Server", "Optimal")
        st.write("### Recent Activity")
        st.table(pd.read_sql("SELECT * FROM signals ORDER BY id DESC LIMIT 5", db_conn))

    elif task == "App Settings":
        st.title("⚙️ Global Configuration")
        with st.form("global_settings"):
            name = st.text_input("App Name", "CRYPTO EMPIRE VIP")
            color = st.color_picker("Brand Theme Color", "#f0b90b")
            ann = st.text_area("Live Announcement", "New Signals coming soon!")
            if st.form_submit_button("Update Platform"):
                db_conn.cursor().execute("UPDATE settings SET value=? WHERE key='app_name'", (name,))
                db_conn.commit()
                st.rerun()

# --- 4. USER FEATURES ---
def user_portal():
    st.sidebar.title("🚀 NAVIGATOR")
    menu = st.sidebar.radio("Categories", ["🏠 Home", "📊 Markets", "🎓 Academy", "📓 My Journal", "💬 Support"])

    if menu == "🏠 Home":
        st.title("🎯 Premium Signals")
        # Live Gauge Widget
        components.html('<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-tickers.js" async>{"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}], "colorTheme": "dark"}</script>', height=80)
        
        df = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", db_conn)
        for _, r in df.iterrows():
            st.markdown(f"""
            <div class="signal-card">
                <div style="display:flex; justify-content:space-between;">
                    <span class="vip-badge">{r['type']}</span>
                    <small>{r['time']}</small>
                </div>
                <h2 style="margin:10px 0;">{r['pair']} <span style="color:#2ebd85;">{r['side']}</span></h2>
                <p>Entry: {r['entry']} | TP: {r['tp']} | SL: {r['sl']}</p>
            </div>
            """, unsafe_allow_html=True)

    elif menu == "📊 Markets":
        st.title("📊 Market Analysis")
        tab1, tab2 = st.tabs(["Charts", "News Calendar"])
        with tab1:
            components.html('<div id="tv" style="height:450px;"><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize":true,"symbol":"BINANCE:BTCUSDT","theme":"dark","container_id":"tv"});</script></div>', height=450)
        with tab2:
            st.subheader("Economic Calendar")
            components.html('<iframe src="https://sslecal2.forexprostools.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&category=_all&importance=1,2,3&features=datepicker,timezone&countries=25,32,6,37,7,22,5,10,35,43,36,110,11,26,12,4,8&calType=week&timeZone=8&lang=1" width="100%" height="500"></iframe>', height=500)

    elif menu == "📓 My Journal":
        st.title("📓 Personal Trade Journal")
        note = st.text_area("Record your trade thoughts...")
        if st.button("Save Note"):
            db_conn.cursor().execute("INSERT INTO journal (email, note, time) VALUES (?,?,?)", (st.session_state.user_email, note, datetime.now().strftime("%Y-%m-%d")))
            db_conn.commit()
            st.success("Note Saved!")

# --- 5. MAIN LOGIC ---
apply_ultra_ui()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 ELITE ACCESS")
    e = st.text_input("Email")
    p = st.text_input("Password", type="password")
    if st.button("ENTER"):
        st.session_state.update({"logged_in": True, "is_admin": (e == "ushan2008@gmail.com"), "user_email": e})
        st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()
    if st.session_state.is_admin: admin_portal()
    else: user_portal()
