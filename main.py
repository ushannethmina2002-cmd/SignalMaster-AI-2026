import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. PAGE SETUP & HAMBURGER MENU FOCUS ---
# initial_sidebar_state="collapsed" දැම්මම ඉබේම ඉරි 3 ඇතුළට මෙනු එක යනවා
st.set_page_config(page_title="HappyShop ERP", page_icon="🛒", layout="wide", initial_sidebar_state="collapsed")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* Sidebar එකේ පෙනුම (Dark Blue/Orange) */
            [data-testid="stSidebar"] { background-color: #001f3f !important; }
            [data-testid="stSidebar"] * { color: white !important; }
            .menu-category {
                background-color: #e67e22;
                padding: 10px;
                font-weight: bold;
                margin-top: 10px;
                border-radius: 5px;
            }
            
            /* Login Form එක මැදට ගැනීම */
            .login-box {
                background-color: #ffffff;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. DATABASE ---
conn = sqlite3.connect('happyshop_enterprise.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, address TEXT, 
            city TEXT, district TEXT, product TEXT, qty INTEGER, price REAL, 
            courier TEXT, status TEXT, staff_name TEXT, date TEXT)''')
conn.commit()

# --- 3. LOGIN LOGIC ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #f1c40f;'>HappyShop Login</h1>", unsafe_allow_html=True)
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        if st.button("Login to Dashboard", use_container_width=True):
            # Owner Login
            if email == "happyshop@gmail.com" and password == "VLG0005":
                st.session_state.user = {"email": email, "role": "OWNER", "name": "Admin"}
                st.rerun()
            # Staff 1 Login
            elif email == "demo1@gmail.com" and password == "demo1":
                st.session_state.user = {"email": email, "role": "STAFF", "name": "Staff 01"}
                st.rerun()
            # Staff 2 Login
            elif email == "demo2@gmail.com" and password == "demo2":
                st.session_state.user = {"email": email, "role": "STAFF", "name": "Staff 02"}
                st.rerun()
            else:
                st.error("Invalid Credentials!")

# --- 4. APP INTERFACE ---
if st.session_state.user is None:
    login()
else:
    # --- SIDEBAR (ඉරි 3 ක්ලික් කළාම එන මෙනු එක) ---
    with st.sidebar:
        st.markdown(f"### 🛒 HappyShop\n**Welcome, {st.session_state.user['name']}**")
        st.markdown("---")
        
        # Owner ට විතරක් පේන Dashboard එක
        if st.session_state.user['role'] == "OWNER":
            st.write("📊 Dashboard (Stats)")
        
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

    # --- CONTENT AREA ---
    if choice == "New Order":
        st.markdown(f"## 📝 New Order Entry - {st.session_state.user['name']}")
        l_col, r_col = st.columns([1.5, 1], gap="large")
        
        with l_col:
            st.markdown("<div style='background:#f8f9fa; padding:10px; border-left:5px solid #e67e22;'><b>Customer Details</b></div>", unsafe_allow_html=True)
            name = st.text_input("Customer Name *")
            address = st.text_area("Address *")
            city = st.selectbox("Select City *", ["Colombo", "Kandy", "Galle"])
            phone = st.text_input("Contact Number One *")
            o_date = st.date_input("Order Date", value=datetime.now())

        with r_col:
            st.markdown("<div style='background:#f8f9fa; padding:10px; border-left:5px solid #e67e22;'><b>Product & Pricing</b></div>", unsafe_allow_html=True)
            product = st.selectbox("Select Product *", ["Product A", "Product B"])
            qty = st.number_input("Qty", min_value=1)
            price = st.number_input("Sale Amount (Rs.)", min_value=0.0)
            courier = st.selectbox("Courier Company", ["Royal Express", "Koombiyo"])
            
            if st.button("🚀 SAVE ORDER", use_container_width=True):
                if name and phone and address:
                    c.execute("INSERT INTO orders (name, phone, address, city, product, qty, price, courier, status, staff_name, date) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                              (name, phone, address, city, product, qty, price, courier, 'Pending', st.session_state.user['name'], str(o_date)))
                    conn.commit()
                    st.success(f"Order Saved Successfully by {st.session_state.user['name']}!")
                else:
                    st.error("Please fill all required fields!")

    elif choice == "Pending Orders":
        st.header("⏳ Pending Orders List")
        # Owner ට ඔක්කොම පේනවා, Staff ට තමන්ගේ ඒවා විතරයි පේන්නේ (optional)
        df = pd.read_sql("SELECT * FROM orders WHERE status='Pending'", conn)
        st.dataframe(df, use_container_width=True)

    elif choice == "Blacklist Manager":
        st.header("🚫 Blacklist Manager")
        st.info("No blacklisted customers.")
