import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import requests
from datetime import datetime

# --- 1. ENGINE & DATA ARCHITECTURE ---
class HappyShopPro:
    def __init__(self):
        self.conn = sqlite3.connect('happyshop_enterprise_v4.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        # Leads & Delivery Table
        c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            customer_name TEXT, phone TEXT, address TEXT, city TEXT, 
            item_name TEXT, selling_price REAL, cost_price REAL, 
            status TEXT, tracking_id TEXT, staff_id TEXT, date TEXT)''')
        # User Management Table
        c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT UNIQUE, password TEXT, role TEXT)''')
        
        # Super Admin (Owner)
        owner_pass = hashlib.sha256("VLG0005".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, 'OWNER')", ("happyshop@gmail.com", owner_pass))
        self.conn.commit()

db = HappyShopPro()

# --- 2. THEME & STYLING ---
st.set_page_config(page_title="HappyShop Enterprise", layout="wide")
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .main-header { color: #ffcc00; font-size: 30px; font-weight: bold; border-bottom: 2px solid #30363d; margin-bottom: 20px; }
    .stat-card { background: #161b22; border: 1px solid #30363d; padding: 20px; border-radius: 10px; text-align: center; }
    .order-card { background: #1c2128; border-left: 5px solid #ffcc00; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .stButton>button { background-color: #238636 !important; color: white !important; border: none; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 3. CORE FUNCTIONS ---
def get_profit_stats():
    df = pd.read_sql("SELECT * FROM orders WHERE status='Delivered'", db.conn)
    if df.empty: return 0, 0
    total_revenue = df['selling_price'].sum()
    total_cost = df['cost_price'].sum()
    return total_revenue, (total_revenue - total_cost)

# --- 4. OWNER PANEL ---
def owner_view():
    st.markdown("<div class='main-header'>👑 OWNER MASTER CONSOLE</div>", unsafe_allow_html=True)
    
    # Analytics Row
    rev, profit = get_profit_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='stat-card'><h4>Total Revenue</h4><h2>Rs.{rev:,.0f}</h2></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='stat-card'><h4>Net Profit</h4><h2 style='color:#238636'>Rs.{profit:,.0f}</h2></div>", unsafe_allow_html=True)
    
    leads_count = pd.read_sql("SELECT count(*) FROM orders WHERE status='New'", db.conn).iloc[0,0]
    c3.markdown(f"<div class='stat-card'><h4>Pending Leads</h4><h2>{leads_count}</h2></div>", unsafe_allow_html=True)
    
    shipped_count = pd.read_sql("SELECT count(*) FROM orders WHERE status='Shipped'", db.conn).iloc[0,0]
    c4.markdown(f"<div class='stat-card'><h4>In Transit</h4><h2>{shipped_count}</h2></div>", unsafe_allow_html=True)

    st.divider()
    
    t1, t2 = st.tabs(["👥 Staff Control", "📜 Master Database"])
    with t1:
        st.subheader("Add New Staff Member")
        with st.form("staff_reg"):
            s_em = st.text_input("Staff Email")
            s_pw = st.text_input("Temporary Password")
            if st.form_submit_button("Register Staff"):
                h_pw = hashlib.sha256(s_pw.encode()).hexdigest()
                try:
                    db.conn.cursor().execute("INSERT INTO users VALUES (?,?,'STAFF')", (s_em, h_pw))
                    db.conn.commit(); st.success("Staff member added!")
                except: st.error("Email already exists!")

    with t2:
        st.subheader("All Orders (Live History)")
        all_df = pd.read_sql("SELECT * FROM orders ORDER BY id DESC", db.conn)
        st.dataframe(all_df, use_container_width=True)

# --- 5. STAFF PANEL ---
def staff_view():
    st.markdown("<div class='main-header'>📦 DISPATCH & PROCESSING HUB</div>", unsafe_allow_html=True)
    
    # Section: Confirmed Orders for Royal Dispatch
    st.subheader("🚀 Orders Ready for Royal Express")
    ready_df = pd.read_sql("SELECT * FROM orders WHERE status='Confirmed'", db.conn)
    
    if ready_df.empty:
        st.info("No orders ready for dispatch at the moment.")
    
    for i, row in ready_df.iterrows():
        with st.container():
            st.markdown(f"""<div class='order-card'>
                <b>ORDER #{row['id']}</b> | Customer: {row['customer_name']} | 📍 {row['city']}<br>
                <b>Product:</b> {row['item_name']} | <b>COD Amount:</b> Rs.{row['selling_price']}
            </div>""", unsafe_allow_html=True)
            
            if st.button(f"Generate Waybill & Dispatch to Royal", key=f"btn_{row['id']}"):
                # රෝයල් එකට ඩේටා යවන තැන (Simulation)
                fake_tracking = f"RE-CONF-{row['id']}778"
                db.conn.cursor().execute(
                    "UPDATE orders SET status='Shipped', tracking_id=? WHERE id=?", 
                    (fake_tracking, row['id'])
                )
                db.conn.commit()
                st.success(f"Success! Waybill Generated: {fake_tracking}")
                st.rerun()

    st.divider()
    # Section: Lead Entry (Manual/Sync)
    with st.expander("📝 Manual Lead Entry (Facebook Ad Data)"):
        with st.form("new_lead"):
            c1, c2 = st.columns(2)
            n = c1.text_input("Customer Name")
            p = c2.text_input("Phone Number")
            addr = st.text_area("Address")
            cty = st.text_input("City")
            itm = st.text_input("Item Name")
            sp = st.number_input("Selling Price (COD)", value=0.0)
            cp = st.number_input("Item Cost", value=0.0)
            
            if st.form_submit_button("Save & Confirm Later"):
                db.conn.cursor().execute(
                    "INSERT INTO orders (customer_name, phone, address, city, item_name, selling_price, cost_price, status, date) VALUES (?,?,?,?,?,?,?,?,?)",
                    (n, p, addr, cty, itm, sp, cp, 'New', datetime.now().strftime("%Y-%m-%d")))
                db.conn.commit(); st.success("Lead saved to Pending List!")

# --- 6. AUTHENTICATION ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6A3C2F98C0XF_CqMToO6_m-Fv0SjYw5Xpog&s", width=100) # Royal Express Style Logo
        st.title("HappyShop Login")
        e_in = st.text_input("Email")
        p_in = st.text_input("Password", type="password")
        if st.button("Login"):
            hp = hashlib.sha256(p_in.encode()).hexdigest()
            res = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND password=?", (e_in, hp)).fetchone()
            if res:
                st.session_state.user = {"email": e_in, "role": res[0]}
                st.rerun()
            else: st.error("Access Denied!")
else:
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
    
    if st.session_state.user['role'] == "OWNER": owner_view()
    else: staff_view()
