import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. THE GOD ENGINE (SCALABLE ARCHITECTURE) ---
class GodEngineV13:
    def __init__(self):
        # අලුත්ම ඩේටාබේස් එකක් (v13)
        self.conn = sqlite3.connect('master_v13_ultimate.db', check_same_thread=False)
        self.init_db()
        self.seed_configs()

    def init_db(self):
        c = self.conn.cursor()
        # සෙටින්ග්ස් 20ක් සඳහා වන ටේබල් එක
        c.execute('''CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY, app_name TEXT, theme_color TEXT, welcome_msg TEXT, 
            logo_url TEXT, maintenance INTEGER, support_url TEXT, default_pair TEXT,
            whale_min TEXT, signal_expiry INTEGER, allow_registration INTEGER,
            font_size TEXT, sidebar_state TEXT, academy_link TEXT, news_api_key TEXT,
            chart_height INTEGER, telegram_bot_token TEXT, footer_text TEXT,
            max_users INTEGER, security_level TEXT, auto_delete_old_signals INTEGER
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, key TEXT, role TEXT, expiry DATE)''')
        c.execute('''CREATE TABLE IF NOT EXISTS signals (id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT, type TEXT, entry TEXT, tp TEXT, sl TEXT, reason TEXT, time TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS intel (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, body TEXT, type TEXT, time TEXT)''')
        self.conn.commit()

    def seed_configs(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM config WHERE id=1")
        if not c.fetchone():
            c.execute("""INSERT INTO config VALUES (
                1, 'ELITE MASTER v13', '#00d4ff', 'Welcome, Institutional Member',
                'https://cryptologos.cc/logos/bitcoin-btc-logo.png', 0, 'https://t.me/admin',
                'BINANCE:BTCUSDT', '100 BTC', 30, 1, '16px', 'expanded', 'https://academy.com',
                '', 500, '', '© 2026 Elite Master VIP', 500, 'High', 1
            )""")
        # Admin Account
        h = hashlib.sha256("192040090".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users (email, key, role, expiry) VALUES (?,?,?,?)", 
                  ('ushannethmina2002@gmail.com', h, 'ADMIN', '2099-12-31'))
        self.conn.commit()

db = GodEngineV13()
cfg = pd.read_sql("SELECT * FROM config WHERE id=1", db.conn).iloc[0]

# --- 2. THEME & ADVANCED CSS ---
st.set_page_config(page_title=cfg['app_name'], layout="wide", initial_sidebar_state=cfg['sidebar_state'])
main_color = cfg['theme_color']

st.markdown(f"""
<style>
    .stApp {{ background: #010409; color: #e1e4e8; font-size: {cfg['font_size']}; }}
    .nav-card {{ background: rgba(255,255,255,0.03); border: 1px solid {main_color}44; padding: 15px; border-radius: 12px; margin-bottom: 10px; }}
    .stButton>button {{ background: {main_color} !important; color: black !important; font-weight: bold; border-radius: 8px; border: none; }}
    .admin-box {{ background: #0d1117; border: 1px solid #30363d; padding: 20px; border-radius: 10px; }}
</style>
""", unsafe_allow_html=True)

# --- 3. ADMIN SETTINGS (THE 20 CONTROLS) ---
def render_master_settings():
    st.header("⚙️ Master System Controls (20 Options)")
    with st.form("big_settings"):
        col1, col2, col3 = st.columns(3)
        # 1-3: Identity
        new_name = col1.text_input("1. App Name", cfg['app_name'])
        new_color = col2.color_picker("2. Theme Color", cfg['theme_color'])
        new_logo = col3.text_input("3. Logo URL", cfg['logo_url'])
        
        # 4-6: Access & Maintenance
        new_mnt = col1.selectbox("4. Maintenance Mode", [0, 1], index=cfg['maintenance'])
        new_reg = col2.selectbox("5. Allow Public Signups", [0, 1], index=cfg['allow_registration'])
        new_sec = col3.selectbox("6. Security Level", ["Low", "Medium", "High"], index=0)
        
        # 7-9: Content Defaults
        new_pair = col1.text_input("7. Default Chart", cfg['default_pair'])
        new_whale = col2.text_input("8. Whale Min. Limit", cfg['whale_min'])
        new_msg = col3.text_input("9. Welcome Message", cfg['welcome_msg'])
        
        # 10-12: Links & API
        new_sup = col1.text_input("10. Support URL", cfg['support_url'])
        new_acad = col2.text_input("11. Academy Link", cfg['academy_link'])
        new_api = col3.text_input("12. News API Key (Optional)", cfg['news_api_key'])
        
        # 13-15: UI & UX
        new_font = col1.selectbox("13. Font Size", ["14px", "16px", "18px"], index=1)
        new_side = col2.selectbox("14. Sidebar Default", ["expanded", "collapsed"], index=0)
        new_hgt = col3.slider("15. Chart Height", 300, 800, cfg['chart_height'])
        
        # 16-18: Advanced
        new_bot = col1.text_input("16. Telegram Bot Token", cfg['telegram_bot_token'])
        new_exp = col2.number_input("17. Signal Expiry (Days)", value=cfg['signal_expiry'])
        new_max = col3.number_input("18. Max User Limit", value=cfg['max_users'])
        
        # 19-20: System
        new_auto = col1.checkbox("19. Auto-Delete Old Signals", value=cfg['auto_delete_old_signals'])
        new_foot = col2.text_input("20. Footer Copyright Text", cfg['footer_text'])
        
        if st.form_submit_button("🔥 SAVE ALL MASTER CONFIGURATIONS"):
            db.conn.cursor().execute("""UPDATE config SET 
                app_name=?, theme_color=?, logo_url=?, maintenance=?, allow_registration=?, 
                security_level=?, default_pair=?, whale_min=?, welcome_msg=?, support_url=?,
                academy_link=?, news_api_key=?, font_size=?, sidebar_state=?, chart_height=?,
                telegram_bot_token=?, signal_expiry=?, max_users=?, auto_delete_old_signals=?, footer_text=?
                WHERE id=1""", (new_name, new_color, new_logo, new_mnt, new_reg, new_sec, new_pair, new_whale, 
                                 new_msg, new_sup, new_acad, new_api, new_font, new_side, new_hgt, new_bot, 
                                 new_exp, new_max, new_auto, new_foot))
            db.conn.commit(); st.success("System Rebooted with New Settings!"); st.rerun()

# --- 4. MODULAR DASHBOARDS ---
def user_panel():
    # Sidebar Navigation (150+ features easily addable here)
    st.sidebar.image(cfg['logo_url'], width=80)
    menu = st.sidebar.radio("Main Menu", ["🎯 Signals", "📰 Intel", "🐋 Whale Alerts", "🎓 Academy", "📞 Support"])
    
    # පින්තූරයේ තිබුණු විදියටම Header එක
    st.markdown(f"<h1 style='color:{main_color}'>{cfg['app_name']}</h1>", unsafe_allow_html=True)
    st.write(cfg['welcome_msg'])

    if menu == "🎯 Signals":
        sigs = pd.read_sql("SELECT * FROM signals ORDER BY id DESC", db.conn)
        for _, s in sigs.iterrows():
            st.markdown(f"<div class='nav-card'><h3>{s['pair']} - {s['type']}</h3><p>Entry: {s['entry']} | TP: {s['tp']} | SL: {s['sl']}</p></div>", unsafe_allow_html=True)
    
    elif menu == "📰 Intel":
        st.components.v1.html(f'<script src="https://s3.tradingview.com/tv.js"></script><script>new TradingView.widget({{"autosize": true, "symbol": "{cfg['default_pair']}", "interval": "240", "theme": "dark", "container_id": "tv"}});</script><div id="tv" style="height:{cfg['chart_height']}px;"></div>', height=cfg['chart_height']+10)

def admin_panel():
    st.sidebar.warning("🛡️ ADMIN MODE ACTIVE")
    admin_menu = st.sidebar.selectbox("Admin Action", ["Dashboard Settings", "Manage Signals", "Manage Users", "Database Audit"])
    
    if admin_menu == "Dashboard Settings":
        render_master_settings()
    elif admin_menu == "Manage Signals":
        with st.form("sig"):
            p, t = st.text_input("Pair"), st.selectbox("Type", ["LONG", "SHORT"])
            e, tp, sl = st.text_input("Entry"), st.text_input("TP"), st.text_input("SL")
            if st.form_submit_button("Post Signal"):
                db.conn.cursor().execute("INSERT INTO signals (pair, type, entry, tp, sl, time) VALUES (?,?,?,?,?,?)", (p, t, e, tp, sl, datetime.now().strftime("%H:%M")))
                db.conn.commit(); st.success("Published!")

# --- 5. AUTH FLOW ---
if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.title("SECURE LOGIN")
        e_in = st.text_input("Email")
        k_in = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            h = hashlib.sha256(k_in.encode()).hexdigest()
            res = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND key=?", (e_in, h)).fetchone()
            if res:
                st.session_state.auth = {"role": res[0]}
                st.rerun()
            else: st.error("Access Denied")
else:
    if st.sidebar.button("Logout"): st.session_state.auth = None; st.rerun()
    
    if st.session_state.auth['role'] == 'ADMIN':
        mode = st.sidebar.toggle("Switch to User View", value=False)
        if mode: user_panel()
        else: admin_panel()
    else: user_panel()

st.sidebar.markdown(f"<div style='position: fixed; bottom: 10px;'>{cfg['footer_text']}</div>", unsafe_allow_html=True)
