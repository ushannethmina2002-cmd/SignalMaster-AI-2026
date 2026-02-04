import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('crypto_v16_final.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)')
    defaults = [('app_name', 'CRYPTO ELITE PRO'), ('theme_color', '#f0b90b'), ('admin_pw', '2008')]
    for k, v in defaults:
        c.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?,?)', (k, v))
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. PREMIUM UI CSS ---
def apply_pro_style():
    main_col = "#f0b90b"
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    * {{ font-family: 'Inter', sans-serif; }}
    .stApp {{ background: #0b0e11; color: #ffffff; }}
    
    /* Neon Glow Card */
    .premium-card {{
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}
    
    .stButton>button {{
        background: linear-gradient(90deg, {main_col}, #ffca28) !important;
        color: black !important;
        font-weight: bold;
        border-radius: 10px;
        border: none;
    }}
    
    /* Live Price Ticker Overlay */
    .price-box {{
        background: rgba(240, 185, 11, 0.1);
        border-left: 4px solid {main_col};
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DYNAMIC WIDGETS ---
def show_live_tape():
    components.html("""
        <div style="background:transparent;">
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
        {
          "symbols": [
            {"proName": "BINANCE:BTCUSDT", "title": "BTC"},
            {"proName": "BINANCE:ETHUSDT", "title": "ETH"},
            {"proName": "BINANCE:SOLUSDT", "title": "SOL"}
          ],
          "colorTheme": "dark", "isTransparent": true, "displayMode": "adaptive", "locale": "en"
        }
        </script></div>
    """, height=50)

# --- 4. ADMIN PANEL ---
def admin_portal():
    st.sidebar.subheader("💎 ADMIN CONTROL")
    choice = st.sidebar.radio("Go to", ["Dashboard", "Post Signal", "Settings"])
    
    if choice == "Dashboard":
        st.title("📊 Platform Performance")
        df = pd.read_sql("SELECT * FROM signals", db_conn)
        st.dataframe(df, use_container_width=True)
        
    elif choice == "Post Signal":
        st.title("📢 New VIP Signal")
        with st.form("sig_form"):
            p = st.text_input("Pair (e.g. BTC/USDT)")
            s = st.selectbox("Direction", ["LONG", "SHORT"])
            en = st.text_input("Entry")
            tp = st.text_input("Take Profit")
            sl = st.text_input("Stop Loss")
            if st.form_submit_button("PUBLISH NOW"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)",
                                         (p,s,en,tp,sl,"Active",datetime.now().strftime("%H:%M")))
                db_conn.commit()
                st.success("Signal Live!")

# --- 5. USER PANEL ---
def user_portal():
    show_live_tape()
    st.sidebar.subheader("🚀 NAVIGATION")
    u_menu = st.sidebar.selectbox("Category", ["🏠 Home", "🎯 Signals", "📊 Market"])

    if u_menu == "🏠 Home":
        st.title("🚀 Market Intelligence")
        st.markdown('<div class="price-box">💡 Welcome! Check out the top trending pairs below.</div>', unsafe_allow_html=True)
        
        # Mini Chart Card
        components.html("""
            <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
            {"symbol": "BINANCE:BTCUSDT", "width": "100%", "height": 200, "locale": "en", "dateRange": "12M", "colorTheme": "dark", "isTransparent": true}
            </script>
        """, height=210)

    elif u_menu == "🎯 Signals":
        st.title("🎯 VIP Trading Signals")
        df = pd.read_sql("SELECT * FROM signals WHERE status='Active' ORDER BY id DESC", db_conn)
        if df.empty:
            st.info("Searching for next quality entry...")
        for _, r in df.iterrows():
            st.markdown(f"""
            <div class="premium-card">
                <div style="display:flex; justify-content:space-between;">
                    <b style="color:#f0b90b; font-size:1.2em;">{r['pair']}</b>
                    <span style="color:#2ebd85;">{r['side']}</span>
                </div>
                <hr style="opacity:0.1;">
                Entry: {r['entry']} | TP: {r['tp']} | SL: {r['sl']}
            </div>
            """, unsafe_allow_html=True)

# --- 6. MAIN SYSTEM ---
apply_pro_style()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.title("Elite Login")
        e = st.text_input("Email").lower()
        p = st.text_input("Password", type="password")
        if st.button("SIGN IN"):
            st.session_state.update({"logged_in": True, "is_admin": (e=="ushan2008@gmail.com"), "user_email": e})
            st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()
    if st.session_state.is_admin: admin_portal()
    else: user_portal()
