import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- 1. DATA ENGINE ---
class HappyShopEngine:
    def __init__(self):
        self.conn = sqlite3.connect('happyshop_leads.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        # Leads Table
        c.execute('''CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            name TEXT, phone TEXT, product TEXT, status TEXT, time TEXT)''')
        # Users Table
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            email TEXT UNIQUE, password TEXT, role TEXT)''')
        
        # Owner Account Seed (ඔයා ඉල්ලපු විදියට)
        owner_email = "happyshop@gmail.com"
        owner_pass = hashlib.sha256("VLG0005".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, 'OWNER')", (owner_email, owner_pass))
        self.conn.commit()

db = HappyShopEngine()

# --- 2. THEME & UI ---
st.set_page_config(page_title="HappyShop Lead Manager", layout="wide")
st.markdown("""
<style>
    .stApp { background: #0d1117; color: #c9d1d9; }
    .lead-card { background: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 6px solid #1877F2; }
    .owner-card { background: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #238636; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 3. OWNER DASHBOARD ---
def owner_panel():
    st.title("👨‍💼 HappyShop Owner Dashboard")
    
    t1, t2, t3 = st.tabs(["📊 Analytics", "👥 Manage Staff", "📝 All Leads"])
    
    with t1:
        col1, col2, col3 = st.columns(3)
        total = pd.read_sql("SELECT count(*) FROM leads", db.conn).iloc[0,0]
        conf = pd.read_sql("SELECT count(*) FROM leads WHERE status='Confirmed'", db.conn).iloc[0,0]
        
        col1.markdown(f"<div class='owner-card'><h3>Total Leads</h3><h1>{total}</h1></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='owner-card' style='border-color:#1877F2'><h3>Confirmed</h3><h1>{conf}</h1></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='owner-card' style='border-color:#d73a49'><h3>Pending</h3><h1>{total-conf}</h1></div>", unsafe_allow_html=True)

    with t2:
        st.subheader("Create New Staff Account")
        with st.form("add_staff"):
            s_email = st.text_input("Staff Email")
            s_pass = st.text_input("Staff Password", type="password")
            if st.form_submit_button("Create Account"):
                h_pass = hashlib.sha256(s_pass.encode()).hexdigest()
                try:
                    db.conn.cursor().execute("INSERT INTO users VALUES (?,?, 'STAFF')", (s_email, h_pass))
                    db.conn.commit()
                    st.success(f"Staff account for {s_email} created!")
                except: st.error("Email already exists!")

    with t3:
        all_leads = pd.read_sql("SELECT * FROM leads ORDER BY id DESC", db.conn)
        st.dataframe(all_leads, use_container_width=True)

# --- 4. STAFF DASHBOARD ---
def staff_panel():
    st.title("🎧 Staff Processing Hub")
    
    # Facebook එකෙන් දත්ත එන තැන (Manual Entry for Testing)
    with st.expander("➕ Add Lead Manually (Testing)"):
        with st.form("test_lead"):
            n = st.text_input("Customer Name")
            p = st.text_input("Phone Number")
            pr = st.text_input("Product")
            if st.form_submit_button("Add to System"):
                db.conn.cursor().execute("INSERT INTO leads (name, phone, product, status, time) VALUES (?,?,?,?,?)",
                                        (n, p, pr, 'New', datetime.now().strftime("%Y-%m-%d %H:%M")))
                db.conn.commit(); st.rerun()

    st.subheader("New Facebook Leads")
    new_leads = pd.read_sql("SELECT * FROM leads WHERE status='New' ORDER BY id DESC", db.conn)
    
    if new_leads.empty:
        st.info("No new leads to process.")
    
    for i, row in new_leads.iterrows():
        st.markdown(f"""<div class='lead-card'>
            <b style='color:#58a6ff;'>NEW FACEBOOK LEAD</b><br>
            <h3 style='margin:5px 0;'>{row['name']}</h3>
            <b>Phone:</b> {row['phone']} | <b>Product:</b> {row['product']}<br>
            <small>Received: {row['time']}</small>
        </div>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 4])
        if c1.button("✅ Confirm Order", key=f"c_{row['id']}"):
            db.conn.cursor().execute("UPDATE leads SET status='Confirmed' WHERE id=?", (row['id'],))
            db.conn.commit(); st.rerun()

# --- 5. LOGIN LOGIC ---
if 'auth' not in st.session_state: st.session_state.auth = None

if not st.session_state.auth:
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        st.title("HappyShop Login")
        login_em = st.text_input("Email")
        login_pw = st.text_input("Password", type="password")
        if st.button("Access System"):
            h_pw = hashlib.sha256(login_pw.encode()).hexdigest()
            res = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND password=?", (login_em, h_pw)).fetchone()
            if res:
                st.session_state.auth = {"email": login_em, "role": res[0]}
                st.rerun()
            else: st.error("Invalid Credentials!")
else:
    if st.sidebar.button("Logout"):
        st.session_state.auth = None
        st.rerun()
    
    if st.session_state.auth['role'] == "OWNER":
        owner_panel()
    else:
        staff_panel()
