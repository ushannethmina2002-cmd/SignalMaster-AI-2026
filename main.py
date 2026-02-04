import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('crypto_elite_v17.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    defaults = [('app_name', 'CRYPTO ELITE PRO'), ('admin_pw', '2008')]
    for k, v in defaults:
        c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)', (k, v))
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. THE "PHOTO-MATCH" UI DESIGN (CSS) ---
def apply_neon_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
    
    .stApp { background-color: #0b0e11; color: #ffffff; }
    
    /* Neon App Headers */
    .app-title {
        font-family: 'Orbitron', sans-serif;
        color: #00ff88;
        text-align: center;
        letter-spacing: 2px;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
    }

    /* Professional Signal Cards */
    .neon-card {
        background: #161a1e;
        border-radius: 25px;
        padding: 20px;
        border: 1px solid #2d3339;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    .signal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }

    .badge-long {
        background: #00ff88;
        color: #000;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 12px;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.4);
    }

    .badge-short {
        background: #ff3b3b;
        color: #fff;
        padding: 5px 15px;
        border-radius: 50px;
        font-weight: bold;
        font-size: 12px;
        box-shadow: 0 0 15px rgba(255, 59, 59, 0.4);
    }

    /* Floating Navigation Style */
    [data-testid="stSidebar"] {
        background: #0b0e11 !important;
        border-right: 1px solid #2d3339;
    }

    /* Neon Buttons */
    .stButton>button {
        background: #ffffff !important;
        color: #000 !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        border: none !important;
        height: 45px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(255,255,255,0.2);
    }
    
    /* Ticker Tape Style */
    .ticker-wrap { background: #161a1e; border-radius: 15px; padding: 5px; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. COMPONENTS ---
def draw_ticker():
    components.html("""
    <div style="background:transparent;">
    <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
    {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}], "colorTheme": "dark", "isTransparent": true}
    </script></div>""", height=50)

# --- 4. PANELS ---
def admin_hub():
    st.markdown("<h1 class='app-title'>ADMIN HUB</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📊 Performance", "🎯 Post Signal"])
    
    with tab1:
        df = pd.read_sql("SELECT * FROM signals", db_conn)
        st.dataframe(df, use_container_width=True)
        
    with tab2:
        with st.form("new_signal"):
            p = st.text_input("Asset Pair")
            s = st.selectbox("Position", ["LONG", "SHORT"])
            en = st.text_input("Entry Price")
            tp = st.text_input("Take Profit")
            sl = st.text_input("Stop Loss")
            if st.form_submit_button("PUBLISH TO VIP"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)",
                                         (p,s,en,tp,sl,"Active",datetime.now().strftime("%H:%M")))
                db_conn.commit()
                st.success("Signal Published!")

def user_hub():
    st.markdown("<h2 class='app-title'>CRYPTO ELITE PRO</h2>", unsafe_allow_html=True)
    draw_ticker()
    
    menu = st.sidebar.radio("Navigation", ["🎯 Signals", "📈 Markets", "📓 Journals"])
    
    if menu == "🎯 Signals":
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        if df.empty:
            st.info("No Active Signals. Stay Tuned!")
        for _, r in df.iterrows():
            badge_class = "badge-long" if r['side'] == "LONG" else "badge-short"
            st.markdown(f"""
            <div class="neon-card">
                <div class="signal-header">
                    <span style="font-size:1.2em; font-weight:bold;">{r['pair']}</span>
                    <span class="{badge_class}">{r['side']}</span>
                </div>
                <div style="display:flex; justify-content:space-between; opacity:0.8;">
                    <span>Entry: <b>{r['entry']}</b></span>
                    <span style="color:#00ff88;">TP: {r['tp']}</span>
                    <span style="color:#ff3b3b;">SL: {r['sl']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    elif menu == "📈 Markets":
        components.html('<div id="chart" style="height:500px;"><script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({"autosize":true,"symbol":"BINANCE:BTCUSDT","theme":"dark","container_id":"chart"});</script></div>', height=500)

# --- 5. LOGIC ---
apply_neon_style()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 style='text-align:center;'>Welcome</h1>", unsafe_allow_html=True)
        email = st.text_input("Email").lower()
        pw = st.text_input("Password", type="password")
        if st.button("NEON LOGIN"):
            st.session_state.update({"logged_in": True, "is_admin": (email == "ushan2008@gmail.com"), "user_email": email})
            st.rerun()
else:
    if st.sidebar.button("LOGOUT"): st.session_state.clear(); st.rerun()
    admin_hub() if st.session_state.is_admin else user_hub()

