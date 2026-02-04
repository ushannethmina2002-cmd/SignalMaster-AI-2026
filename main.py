import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('crypto_elite_v22.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, side TEXT, entry TEXT, tp TEXT, sl TEXT, status TEXT, time TEXT)')
    conn.commit()
    return conn

db_conn = init_db()

# --- 2. ULTRA-PREMIUM UI CSS (MATCHING YOUR PHOTOS) ---
def apply_ultra_premium_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    .stApp { background: #0b0e11; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    /* Premium Glass Card Style */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(4px);
    }
    
    /* Neon Text & Badges */
    .neon-green { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
    .neon-red { color: #ff3b3b; text-shadow: 0 0 10px rgba(255, 59, 59, 0.3); }
    
    .status-badge {
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
    }
    .buy-bg { background: rgba(0, 255, 136, 0.15); color: #00ff88; border: 1px solid #00ff88; }
    .sell-bg { background: rgba(255, 59, 59, 0.15); color: #ff3b3b; border: 1px solid #ff3b3b; }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #f0b90b, #ffca28) !important;
        color: #000 !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: bold !important;
        height: 48px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. PHOTO-SPECIFIC WIDGETS ---
def draw_market_header():
    # පින්තූරවල තියෙන Market Overview කොටස
    st.markdown("### 📊 Global Market Dashboard")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('''<div class="glass-card" style="text-align:center;">
            <small style="color:#848e9c;">Fear & Greed Index</small>
            <h2 style="color:#f0b90b; margin:0;">62 <span style="font-size:14px; color:#848e9c;">Greed</span></h2>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.markdown('''<div class="glass-card" style="text-align:center;">
            <small style="color:#848e9c;">Market Sentiment</small>
            <h2 class="neon-green" style="margin:0;">BULLISH</h2>
        </div>''', unsafe_allow_html=True)

# --- 4. NAVIGATION LOGIC ---
def user_interface():
    st.markdown("<h2 style='text-align:center; font-weight:800; color:#f0b90b;'>CRYPTO ELITE PRO</h2>", unsafe_allow_html=True)
    
    # 1. Live Ticker Tape (පින්තූරවල තියෙන එක)
    components.html("""
        <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
        {"symbols": [{"proName": "BINANCE:BTCUSDT", "title": "BTC"}, {"proName": "BINANCE:ETHUSDT", "title": "ETH"}, {"proName": "BINANCE:SOLUSDT", "title": "SOL"}], "colorTheme": "dark", "isTransparent": true}
        </script>""", height=50)

    # 2. Market Overview
    draw_market_header()
    
    # 3. Signals Section (පින්තූරයේ තියෙන විදියටම)
    st.markdown("### 🎯 VIP Trading Signals")
    df = pd.read_sql("SELECT * FROM signals ORDER BY id DESC LIMIT 5", db_conn)
    
    if df.empty:
        st.markdown('<div class="glass-card" style="text-align:center; color:#848e9c;">Waiting for high-probability setups...</div>', unsafe_allow_html=True)
    else:
        for _, r in df.iterrows():
            badge_class = "buy-bg" if r['side'] == "LONG" else "sell-bg"
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:18px; font-weight:700;">{r['pair']}</span>
                    <span class="status-badge {badge_class}">{r['side']}</span>
                </div>
                <div style="margin-top:15px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:5px; text-align:center;">
                    <div><small style="color:#848e9c;">Entry</small><br><b>{r['entry']}</b></div>
                    <div><small style="color:#848e9c;">Target</small><br><b class="neon-green">{r['tp']}</b></div>
                    <div><small style="color:#848e9c;">Stop Loss</small><br><b class="neon-red">{r['sl']}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 4. Top Assets List (පින්තූරයේ තියෙන විදියටම)
    st.markdown("### 📈 Top Assets (Live)")
    st.markdown("""
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span><b style="color:#f0b90b;">BTC</b> Bitcoin</span> <span class="neon-green">$96,432.10 (+2.4%)</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <span><b style="color:#f0b90b;">ETH</b> Ethereum</span> <span class="neon-green">$2,845.50 (+1.8%)</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span><b style="color:#f0b90b;">SOL</b> Solana</span> <span class="neon-red">$142.12 (-0.5%)</span>
        </div>
    </div>
    <br><br>
    """, unsafe_allow_html=True)

# --- 5. MAIN APP ---
apply_ultra_premium_style()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center; color:#f0b90b;'>ELITE</h1>", unsafe_allow_html=True)
        u = st.text_input("GMAIL ADDRESS")
        p = st.text_input("PASSWORD", type="password")
        if st.button("UNLOCK PRO ACCESS"):
            st.session_state.update({"logged_in": True, "is_admin": (u=="ushan2008@gmail.com")})
            st.rerun()
else:
    if st.sidebar.button("Logout"): st.session_state.clear(); st.rerun()
    
    if st.session_state.is_admin:
        st.title("👨‍💻 Admin Control Hub")
        with st.form("new_sig"):
            pair = st.text_input("Pair (e.g. BTC/USDT)"); side = st.selectbox("Side", ["LONG", "SHORT"])
            ent = st.text_input("Entry Price"); tp = st.text_input("TP Price"); sl = st.text_input("SL Price")
            if st.form_submit_button("PUBLISH SIGNAL"):
                db_conn.cursor().execute("INSERT INTO signals (pair,side,entry,tp,sl,status,time) VALUES (?,?,?,?,?,?,?)",
                                         (pair,side,ent,tp,sl,"Active",datetime.now().strftime("%H:%M")))
                db_conn.commit(); st.success("Signal is now Live!")
    else:
        user_interface()
