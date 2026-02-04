import streamlit as st
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. ENTERPRISE SECURITY & DB ARCHITECT ---
class CryptoSecurity:
    @staticmethod
    def hash_password(password):
        return hashlib.sha256(str.encode(password)).hexdigest()

    @staticmethod
    def init_vault():
        conn = sqlite3.connect('enterprise_core.db', check_same_thread=False)
        c = conn.cursor()
        # Identity Tables
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, 
            password TEXT, role TEXT, status TEXT, last_login TEXT)''')
        # Intelligence Tables
        c.execute('''CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY, pair TEXT, side TEXT, entry TEXT, 
            tp TEXT, sl TEXT, confidence TEXT, timestamp TEXT)''')
        # Seed Admin (Password: Admin@2026)
        admin_h = CryptoSecurity.hash_password("Admin@2026")
        c.execute("INSERT OR IGNORE INTO users (username, password, role, status) VALUES (?,?,?,?)",
                  ('ushan2008@gmail.com', admin_h, 'ADMIN', 'ACTIVE'))
        conn.commit()
        return conn

db_conn = CryptoSecurity.init_vault()

# --- 2. WORLD-CLASS UI DESIGN SYSTEM ---
def apply_institutional_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    :root { --primary: #f0b90b; --bg-dark: #080a0c; --glass: rgba(255, 255, 255, 0.03); }
    .stApp { background: var(--bg-dark); color: #e1e1e1; font-family: 'Inter', sans-serif; }
    
    /* Premium Glassmorphism */
    .glass-card {
        background: var(--glass); border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px; padding: 25px; backdrop-filter: blur(10px); margin-bottom: 20px;
    }
    
    .status-badge {
        padding: 4px 12px; border-radius: 50px; font-size: 10px; font-weight: 800; text-transform: uppercase;
        border: 1px solid var(--primary); color: var(--primary);
    }
    
    /* Sidebar & Navigation */
    [data-testid="stSidebar"] { background-color: #0c0e12; border-right: 1px solid rgba(255,255,255,0.05); }
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), #ffca28) !important;
        color: black !important; font-weight: 800 !important; border-radius: 12px !important; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CORE MODULES (MARKET INTELLIGENCE) ---
def render_intelligence_module():
    st.title("🌍 Market Intelligence")
    
    # Fear & Greed / Volatility Row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="glass-card"><small>SENTIMENT</small><h2 style="color:#00ff88;">GREED (68)</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="glass-card"><small>VOLATILITY</small><h2 style="color:#f0b90b;">MEDIUM</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="glass-card"><small>BTC DOMINANCE</small><h2>52.4%</h2></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Market Analytics", "🎯 Premium Signals", "🎓 Education"])
    
    with tab1:
        st.markdown("### Technical Pulse")
        components.html("""
            <div style="height:400px;"><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
            {"interval": "4h", "width": "100%", "isTransparent": true, "height": "100%", "symbol": "BINANCE:BTCUSDT", "showIntervalTabs": true, "colorTheme": "dark"}
            </script></div>""", height=400)

    with tab2:
        st.markdown("### 🔔 Signal Aggregator")
        st.info("⚠️ NOT FINANCIAL ADVICE: For informational and educational purposes only.")
        signals = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", db_conn)
        for _, s in signals.iterrows():
            st.markdown(f"""
            <div class="glass-card">
                <div style="display:flex; justify-content:space-between;">
                    <b>{s['pair']}</b> <span class="status-badge">{s['side']}</span>
                </div>
                <div style="margin-top:10px; display:grid; grid-template-columns:1fr 1fr 1fr; text-align:center;">
                    <div><small>ENTRY</small><br><b>{s['entry']}</b></div>
                    <div><small style="color:#00ff88;">TARGET</small><br><b>{s['tp']}</b></div>
                    <div><small style="color:#ff3b3b;">CONFIDENCE</small><br><b>{s['confidence']}</b></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("### 📚 Crypto Academy")
        st.markdown("""
        <div class="glass-card">
            <h4>1. What is Crypto Intelligence?</h4>
            <p>Crypto intelligence is the process of using data, analysis, and market metrics to make informed decisions rather than emotional guesses.</p>
        </div>
        """, unsafe_allow_html=True)

# --- 4. ADMIN CONTROL CENTER ---
def render_admin_module():
    st.title("🛡️ Command Center")
    menu = st.sidebar.selectbox("Admin Menu", ["User Management", "Publish Signals", "System Logs"])
    
    if menu == "User Management":
        st.subheader("Manage Enterprise Access")
        with st.form("create_user"):
            new_u = st.text_input("Gmail Address")
            new_p = st.text_input("Temporary Password", type="password")
            if st.form_submit_button("Create Institutional Account"):
                h_pw = CryptoSecurity.hash_password(new_p)
                db_conn.cursor().execute("INSERT INTO users (username, password, role, status) VALUES (?,?,?,?)",
                                         (new_u, h_pw, 'USER', 'ACTIVE'))
                db_conn.commit()
                st.success(f"Account for {new_u} created.")
        
        st.divider()
        users_df = pd.read_sql("SELECT id, username, role, status FROM users", db_conn)
        st.table(users_df)

# --- 5. LOGIN & SESSION LOGIC ---
apply_institutional_theme()
if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    _, col, _ = st.columns([1,1.5,1])
    with col:
        st.markdown("<br><br><h1 style='text-align:center;'>ELITE ACCESS</h1>", unsafe_allow_html=True)
        u = st.text_input("Email")
        p = st.text_input("Password", type="password")
        if st.button("AUTHENTICATE"):
            hashed = CryptoSecurity.hash_password(p)
            res = db_conn.cursor().execute("SELECT role FROM users WHERE username=? AND password=?", (u, hashed)).fetchone()
            if res:
                st.session_state.auth = {'user': u, 'role': res[0]}
                st.rerun()
            else: st.error("Access Denied: Invalid Credentials")
else:
    if st.sidebar.button("Secure Logout"):
        st.session_state.auth = None
        st.rerun()
    
    if st.session_state.auth['role'] == 'ADMIN':
        render_admin_module()
    else:
        render_intelligence_module()
