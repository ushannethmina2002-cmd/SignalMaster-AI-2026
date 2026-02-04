import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. CONFIG & DB ---
def init_db():
    conn = sqlite3.connect('crypto_empire_ultimate_v15.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, msg TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    
    defaults = [('app_name', 'CRYPTO ELITE PRO'), ('theme_color', '#f0b90b'), ('admin_pw', '2008')]
    for k, v in defaults:
        c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)', (k, v))
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. ADVANCED UI CSS (ULTRA MODERN) ---
def apply_style():
    main_color = "#f0b90b"
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        * {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background: radial-gradient(circle at 0% 0%, #1e2329 0%, #0b0e11 100%); color: #ffffff; }}
        
        /* Glassmorphism Cards */
        .glass-card {{
            background: rgba(255, 255, 255, 0.03); border-radius: 20px;
            padding: 20px; border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px); margin-bottom: 20px;
        }}
        
        .signal-item {{
            background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
            border-radius: 15px; padding: 15px; border: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 15px; transition: 0.3s ease;
        }}
        .signal-item:hover {{ border-color: {main_color}; transform: translateY(-3px); }}
        
        /* Custom Sidebar */
        [data-testid="stSidebar"] {{ background: rgba(11, 14, 17, 0.95) !important; border-right: 1px solid rgba(255,255,255,0.05); }}
        
        /* Stats Styling */
        .stat-val {{ color: {main_color}; font-size: 24px; font-weight: bold; }}
        </style>
    """, unsafe_allow_html=True)

# --- 3. UI COMPONENTS (LIVE ELEMENTS) ---
def top_ticker():
    components.html("""
        <div style="height:62px; background-color: transparent;">
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
        {
          "symbols": [
            {"proName": "BINANCE:BTCUSDT", "title": "BTC/USDT"},
            {"proName": "BINANCE:ETHUSDT", "title": "ETH/USDT"},
            {"proName": "BINANCE:SOLUSDT", "title": "SOL/USDT"},
            {"proName": "BINANCE:BNBUSDT", "title": "BNB/USDT"},
            {"proName": "BINANCE:DOGEUSDT", "title": "DOGE/USDT"}
          ],
          "showSymbolLogo": true, "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
        }
        </script></div>
    """, height=70)

def market_cards():
    col1, col2, col3 = st.columns(3)
    pairs = [("BTC", "BTCUSDT"), ("ETH", "ETHUSDT"), ("SOL", "SOLUSDT")]
    cols = [col1, col2, col3]
    
    for i, (name, symbol) in enumerate(pairs):
        with cols[i]:
            st.markdown(f"""<div class="glass-card"><small style="color:#848e9c;">{name}/USDT</small></div>""", unsafe_allow_html=True)
            components.html(f"""
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
                {{
                  "symbol": "BINANCE:{symbol}", "width": "100%", "height": 150, "locale": "en",
                  "dateRange": "12M", "colorTheme": "dark", "isTransparent": true, "autosize": true, "largeChartUrl": ""
                }}
                </script>
            """, height=160)

# --- 4. PANELS ---
def admin_panel():
    st.sidebar.title("💎 ADMIN PRO")
    mode = st.sidebar.radio("Navigation", ["Overview", "Signals", "Settings"])
    
    if mode == "Overview":
        st.title("⚡ PLATFORM OVERVIEW")
        st.markdown('<div class="glass-card"><h3>Global Analytics</h3><p>User engagement is up 24% this week.</p></div>', unsafe_allow_html=True)
        df = pd.read_sql("SELECT * FROM signals", db_conn)
        st.dataframe(df, use_container_width=True)
        
    elif mode == "Signals":
        st.title("📢 SIGNAL MANAGER")
        with st.form("new_sig"):
            p = st.text_input("Pair"); s = st.selectbox("Side", ["LONG", "SHORT"])
            en = st.text_input("Entry"); tp = st.text_input("TP"); sl = st.text_input("SL")
            if st.form_submit_button("PUBLISH"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)",
                                         (p,s,en,tp,sl,"Active",datetime.now().strftime("%H:%M")))
                db_conn.commit(); st.rerun()

def user_panel():
    st.sidebar.title("🚀 EXPLORE")
    u_menu = st.sidebar.selectbox("Jump to", ["🏠 Dashboard", "🎯 VIP Signals", "📊 Advanced Charts", "💬 Community"])

    top_ticker()

    if u_menu == "🏠 Dashboard":
        st.markdown("<h1>MARKET OVERVIEW</h1>", unsafe_allow_html=True)
        market_cards()
        st.markdown("### 🔥 Trending Signals")
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' LIMIT 2", db_conn)
        for _, r in df.iterrows():
            st.markdown(f'<div class="signal-item"><b>{r["pair"]}</b> - {r["side"]} @ {r["entry"]}</div>', unsafe_allow_html=True)

    elif u_menu == "🎯 VIP Signals":
        st.title("🎯 PREMIUM SIGNALS")
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        for _, r in df.iterrows():
            color = "#2ebd85" if r['side']=="LONG" else "#f6465d"
            st.markdown(f"""
                <div class="glass-card">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:{color}; font-weight:bold;">{r['side']}</span>
                        <small>{r['time']}</small>
                    </div>
                    <h2 style="margin:5
