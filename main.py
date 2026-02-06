import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- 1. SYSTEM ENGINE ---
class OrderSystem:
    def __init__(self):
        self.conn = sqlite3.connect('order_management.db', check_same_thread=False)
        self.init_db()

    def init_db(self):
        c = self.conn.cursor()
        # Leads table
        c.execute('''CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            customer_name TEXT, 
            phone TEXT, 
            product_interest TEXT, 
            status TEXT, 
            assigned_to TEXT, 
            created_at TEXT)''')
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT UNIQUE, key TEXT, role TEXT)''')
        
        # Admin Seed
        h = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users VALUES (?,?,?)", ("owner@business.com", h, "OWNER"))
        # Staff Seed
        h_staff = hashlib.sha256("staff123".encode()).hexdigest()
        c.execute("INSERT OR IGNORE INTO users VALUES (?,?,?)", ("staff1@business.com", h_staff, "STAFF"))
        self.conn.commit()

db = OrderSystem()

# --- 2. THEME ---
st.set_page_config(page_title="LEAD-TO-ORDER SYSTEM", layout="wide")
st.markdown("""<style>.stApp { background: #0e1117; color: white; } .card { background: #1b1e23; padding: 20px; border-radius: 10px; border-left: 5px solid #00d4ff; }</style>""", unsafe_allow_html=True)

# --- 3. DASHBOARDS ---

def owner_dashboard():
    st.title("👨‍💼 Owner Strategy Center")
    col1, col2, col3 = st.columns(3)
    
    total_leads = pd.read_sql("SELECT count(*) FROM leads", db.conn).iloc[0,0]
    confirmed = pd.read_sql("SELECT count(*) FROM leads WHERE status='Confirmed'", db.conn).iloc[0,0]
    
    col1.metric("Total Leads", total_leads)
    col2.metric("Confirmed Orders", confirmed)
    col3.metric("Conversion Rate", f"{(confirmed/total_leads*100 if total_leads>0 else 0):.1f}%")

    st.subheader("All System Leads")
    all_data = pd.read_sql("SELECT * FROM leads ORDER BY id DESC", db.conn)
    st.dataframe(all_data, use_container_width=True)

def staff_dashboard():
    st.title("🎧 Staff Processing Hub")
    
    # Lead එකක් Manual ඇඩ් කරන්න (Facebook Webhook නැති වෙලාවට)
    with st.expander("➕ Add New Lead Manually"):
        with st.form("manual_lead"):
            name = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
            prod = st.text_input("Product")
            if st.form_submit_button("Add Lead"):
                db.conn.cursor().execute("INSERT INTO leads (customer_name, phone, product_interest, status, created_at) VALUES (?,?,?,?,?)",
                                        (name, phone, prod, "New", datetime.now().strftime("%Y-%m-%d %H:%M")))
                db.conn.commit()
                st.success("Lead Added!")

    st.subheader("Pending Leads to Confirm")
    pending = pd.read_sql("SELECT * FROM leads WHERE status='New'", db.conn)
    
    for _, row in pending.iterrows():
        with st.container():
            st.markdown(f"""<div class='card'>
                <h4>{row['customer_name']} - {row['phone']}</h4>
                <p>Interested in: {row['product_interest']}</p>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Confirm Order #{row['id']}"):
                db.conn.cursor().execute("UPDATE leads SET status='Confirmed' WHERE id=?", (row['id'],))
                db.conn.commit()
                st.rerun()

# --- 4. LOGIN ---
if 'user' not in st.session_state: st.session_state.user = None

if not st.session_state.user:
    st.title("Order Management System")
    em = st.text_input("Email")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        h = hashlib.sha256(pw.encode()).hexdigest()
        res = db.conn.cursor().execute("SELECT role FROM users WHERE email=? AND key=?", (em, h)).fetchone()
        if res:
            st.session_state.user = {"email": em, "role": res[0]}
            st.rerun()
        else: st.error("Wrong details")
else:
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()
        
    if st.session_state.user['role'] == "OWNER":
        owner_dashboard()
    else:
        staff_dashboard()
