import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import urllib.parse
from datetime import datetime

# --- 1. PAGE CONFIG & UI STYLING (WATERMARK REMOVAL) ---
st.set_page_config(page_title="HappyShop Enterprise ERP", page_icon="🛒", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            div[data-testid="stStatusWidget"] {visibility: hidden;}
            
            /* Sidebar Styling - Dark Blue/Orange */
            [data-testid="stSidebar"] { background-color: #001f3f; }
            [data-testid="stSidebar"] * { color: white !important; }
            .menu-category {
                background-color: #e67e22;
                padding: 8px 15px;
                font-weight: bold;
                color: white;
                margin-top: 10px;
            }

            /* Login Page Styling */
            .login-title {
                color: #f1c40f; 
                text-align: center; 
                font-size: 45px;
                font-weight: bold;
                line-height: 1.1;
            }
            
            /* Form Styling */
            .section-header {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                border-left: 5px solid #e67e22;
                margin-bottom: 15px;
                color: #333;
            }
            .stApp { background-color: white; }
            label { color: #333 !important; font-weight: bold !important; }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. DATABASE ENGINE ---
conn = sqlite3.connect('happyshop_ultimate.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, address TEXT, 
            city TEXT, district TEXT, product TEXT, qty INTEGER, price REAL, 
            courier TEXT, status TEXT, date TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT UNIQUE, password TEXT, role TEXT)''')
# Default Admin: happyshop@gmail.com | Pass: VLG0005
admin_pass = hashlib.sha256("VLG0005".encode()).hexdigest()
c.execute("INSERT OR IGNORE INTO users VALUES (?, ?, 'OWNER')", ("happyshop@gmail.com", admin_pass))
conn.commit()

# --- 3. LOGIN PAGE ---
def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1170/1170678.png", width=120)
        st.markdown("<div class='login-title'>HappyShop<br>Login</div>", unsafe_allow_html=True)
        
        email = st.text_input("Email", placeholder="Enter Email")
        password = st.text_input("Password", type="password", placeholder="Enter Password")
        
        if st.button("Login to Dashboard", use_container_width=True):
            hp = hashlib.sha256(password.encode()).hexdigest()
            res = c.execute("SELECT role FROM users WHERE email=? AND password=?", (email, hp)).fetchone()
            if res:
                st.session_state.user = {"email": email, "role": res[0]}
                st.rerun()
            else:
                st.error("Invalid Credentials")

# --- 4. SIDEBAR MENU ---
def sidebar_menu():
    with st.sidebar:
        st.markdown("### 🛒 HappyShop ERP")
        st.markdown("<hr style='margin:5px;'>", unsafe_allow_html=True)
        st.write("🏠 Dashboard")
        st.write("📦 GRN")
        st.write("💸 Expense")
        
        st.markdown("<div class='menu-category'>Orders</div>", unsafe_allow_html=True)
        choice = st.radio("Menu", [
            "New Order", "Pending Orders", "Order Search", 
            "Import Lead", "View Lead", "Add Lead", 
            "Order History", "Exchanging Orders", "Blacklist Manager"
        ], label_visibility="collapsed")
        
        st.markdown("<div class='menu-category'>Shipped Items</div>", unsafe_allow_html=True)
        st.markdown("<div class='menu-category'>Return</div>", unsafe_allow_html=True)
        
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()
        return choice

# --- 5. NEW ORDER FORM (SCREENSHOT MATCH) ---
def new_order_view():
    st.markdown("## 📝 New Order / Waybill Entry")
    col_left, col_right = st.columns([1.5, 1], gap="large")
    
    with col_left:
        st.markdown("<div class='section-header'>Customer Details</div>", unsafe_allow_html=True)
        user_type = st.selectbox("User", ["All", "Registered", "Guest"])
        name = st.text_input("Customer Name *")
        address = st.text_area("Address *", height=80)
        city = st.selectbox("Select City *", ["Colombo", "Kandy", "Galle", "Gampaha", "Other"])
        district = st.selectbox("Select District *", ["Colombo", "Gampaha", "Kalutara", "Kandy", "Galle"])
        
        c1, c2 = st.columns(2)
        phone1 = c1.text_input("Contact Number One *")
        phone2 = c2.text_input("Contact Number Two")
        
        email = st.text_input("Email")
        o_date = st.date_input("Order Date", value=datetime.now())
        source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "Web", "Direct"])
        payment = st.selectbox("Payment Method", ["COD", "Bank Transfer"])

    with col_right:
        st.markdown("<div class='section-header'>Product & Pricing</div>", unsafe_allow_html=True)
        product = st.selectbox("Select Product *", ["Item A", "Item B", "Item C"])
        qty = st.number_input("Qty", min_value=1, value=1)
        price = st.number_input("Sale Amount (Rs.)", min_value=0.0)
        note = st.text_area("Product Note")
        discount = st.number_input("Product Discount", min_value=0.0)
        
        st.markdown("<div class='section-header'>Courier Info</div>", unsafe_allow_html=True)
        courier = st.selectbox("Courier Company", ["Royal Express", "Koombiyo", "Domex"])
        ref_no = st.text_input("Reference No")
        weight = st.number_input("Pkg Weight (kgs)", value=0.5)
        
        st.divider()
        st.write(f"### Total: Rs. {price - discount:,.2f}")
        
        if st.button("🚀 SAVE & PROCESS ORDER", use_container_width=True):
            if name and phone1 and address:
                c.execute("INSERT INTO orders (name, phone, address, city, district, product, qty, price, courier, status, date) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                          (name, phone1, address, city, district, product, qty, price, courier, 'Pending', str(o_date)))
                conn.commit()
                st.success("Order Saved and Ready for Dispatch!")
            else:
                st.error("Please fill required fields (*)")

# --- 6. MAIN APP LOGIC ---
if 'user' not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    login_page()
else:
    page = sidebar_menu()
    if page == "New Order":
        new_order_view()
    elif page == "Pending Orders":
        st.subheader("⏳ Pending Orders List")
        pending_df = pd.read_sql("SELECT * FROM orders WHERE status='Pending'", conn)
        st.dataframe(pending_df, use_container_width=True)
    elif page == "Blacklist Manager":
        st.subheader("🚫 Blacklist Manager")
        st.warning("No customers blacklisted yet.")
    else:
        st.info(f"The '{page}' section is being updated.")

