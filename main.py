import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. PAGE CONFIG & SIDEBAR FORCING ---
st.set_page_config(page_title="HappyShop ERP", page_icon="🛒", layout="wide", initial_sidebar_state="expanded")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            
            /* Sidebar එක Mobile වලත් පේන්න සැලැස්වීම */
            [data-testid="stSidebarNav"] {display: none;}
            [data-testid="stSidebar"] {
                background-color: #001f3f !important;
                min-width: 250px !important;
            }
            [data-testid="stSidebar"] * { color: white !important; }
            
            /* මෙනු කැටගරි Styling */
            .menu-category {
                background-color: #e67e22;
                padding: 10px;
                font-weight: bold;
                color: white;
                margin-top: 10px;
                border-radius: 5px;
            }
            
            /* ලොගින් පේජ් එක මැදට ගැනීම */
            .login-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 2. DATABASE ---
conn = sqlite3.connect('happyshop_final_v7.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, address TEXT, 
            city TEXT, district TEXT, product TEXT, qty INTEGER, price REAL, 
            courier TEXT, status TEXT, date TEXT)''')
conn.commit()

# --- 3. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_view():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #f1c40f;'>HappyShop Login</h1>", unsafe_allow_html=True)
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login to Dashboard", use_container_width=True):
            if email == "happyshop@gmail.com" and password == "VLG0005":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Email හෝ Password වැරදියි!")

# --- 4. MAIN APP ---
if not st.session_state.logged_in:
    login_view()
else:
    # --- SIDEBAR MENU (මෙහි තමයි මෙනු එක තියෙන්නේ) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>HappyShop</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.write("🏠 Dashboard")
        st.write("📦 GRN")
        st.write("💸 Expense")
        
        st.markdown("<div class='menu-category'>Orders</div>", unsafe_allow_html=True)
        # Radio button එක මෙනු එකක් විදිහට පාවිච්චි කිරීම
        choice = st.radio("Select Action", [
            "New Order", "Pending Orders", "Order Search", 
            "Import Lead", "View Lead", "Add Lead", 
            "Order History", "Exchanging Orders", "Blacklist Manager"
        ], label_visibility="collapsed")
        
        st.markdown("<div class='menu-category'>Shipped Items</div>", unsafe_allow_html=True)
        st.markdown("<div class='menu-category'>Return</div>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # --- CONTENT AREA ---
    if choice == "New Order":
        st.markdown("## 📝 New Order / Waybill Entry")
        col_left, col_right = st.columns([1.5, 1], gap="large")
        
        with col_left:
            st.markdown("<div style='background:#f8f9fa; padding:10px; border-left:5px solid #e67e22;'><b>Customer Details</b></div>", unsafe_allow_html=True)
            st.selectbox("User", ["All", "Registered", "Guest"])
            name = st.text_input("Customer Name *")
            address = st.text_area("Address *")
            st.selectbox("Select City *", ["Colombo", "Kandy", "Galle"])
            st.text_input("Contact Number One *")
            st.date_input("Order Date", value=datetime.now())

        with col_right:
            st.markdown("<div style='background:#f8f9fa; padding:10px; border-left:5px solid #e67e22;'><b>Product & Pricing</b></div>", unsafe_allow_html=True)
            st.selectbox("Select Product *", ["Product A", "Product B"])
            qty = st.number_input("Qty", min_value=1)
            price = st.number_input("Sale Amount (Rs.)", min_value=0.0)
            st.selectbox("Courier Company", ["Royal Express", "Koombiyo"])
            
            if st.button("🚀 SAVE ORDER", use_container_width=True):
                st.success("Order Saved!")

    elif choice == "Blacklist Manager":
        st.header("🚫 Blacklist Manager")
        st.info("No blacklisted users yet.")
