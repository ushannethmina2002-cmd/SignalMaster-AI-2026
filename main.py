import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE SETUP (වෙබ් එකට ගැලපෙන ලෙස) ---
st.set_page_config(
    page_title="HappyShop Official ERP", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. CSS STYLING (Screenshot එකේ පෙනුම ලබා ගැනීමට) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    [data-testid="stSidebar"] { background-color: #001f3f !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    .menu-header {
        background-color: #e67e22;
        padding: 10px;
        font-weight: bold;
        border-radius: 5px;
        margin: 10px 0px;
    }
    .section-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #e67e22;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN SYSTEM ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop ERP Login</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        email = st.text_input("Username / Email")
        password = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            if email == "happyshop@gmail.com" and password == "VLG0005":
                st.session_state.user = {"name": "Admin", "role": "OWNER"}
                st.rerun()
            elif email == "demo1@gmail.com" and password == "demo1":
                st.session_state.user = {"name": "Staff 01", "role": "STAFF"}
                st.rerun()
            elif email == "demo2@gmail.com" and password == "demo2":
                st.session_state.user = {"name": "Staff 02", "role": "STAFF"}
                st.rerun()
            else:
                st.error("Invalid Login!")

# --- 4. MAIN INTERFACE ---
if st.session_state.user is None:
    login()
else:
    # Sidebar - Hamburger Menu (ඉරි 3)
    with st.sidebar:
        st.markdown(f"### 🛒 HappyShop\nUser: {st.session_state.user['name']}")
        st.markdown("---")
        st.write("🏠 Dashboard")
        st.write("📦 GRN")
        st.write("💸 Expense")
        
        st.markdown("<div class='menu-header'>Orders</div>", unsafe_allow_html=True)
        choice = st.radio("Menu", [
            "New Order", "Pending Orders", "Order Search", 
            "Import Lead", "View Lead", "Add Lead", 
            "Order History", "Exchanging Orders", "Blacklist Manager"
        ], label_visibility="collapsed")
        
        st.markdown("<div class='menu-header'>Shipped Items</div>", unsafe_allow_html=True)
        st.markdown("<div class='menu-header'>Return</div>", unsafe_allow_html=True)
        
        if st.button("Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # New Order Form (ඔයා එවපු Screenshot එකේ තියෙන ඔක්කොම Fields මෙතන තියෙනවා)
    if choice == "New Order":
        st.markdown(f"## 📝 Customer / Waybill Entry")
        c1, c2 = st.columns([1.5, 1], gap="large")
        
        with c1:
            st.markdown("<div class='section-box'><b>Customer Details</b></div>", unsafe_allow_html=True)
            u_type = st.selectbox("Target User", ["All", "Registered", "Guest"])
            cust_name = st.text_input("Customer Name *")
            addr = st.text_area("Address *")
            city = st.selectbox("Select City *", ["Colombo", "Kandy", "Galle", "Matale"])
            dist = st.selectbox("Select District *", ["Colombo", "Gampaha", "Kandy", "Matale"])
            phone1 = st.text_input("Contact Number One *")
            phone2 = st.text_input("Contact Number Two")
            o_date = st.date_input("Due Date", value=datetime.now())
            source = st.selectbox("Order Source", ["FB Lead", "WhatsApp", "Web"])
            pay_method = st.selectbox("Payment Method", ["COD", "Bank Transfer"])

        with c2:
            st.markdown("<div class='section-box'><b>Product & Pricing</b></div>", unsafe_allow_html=True)
            prod = st.selectbox("Select Product *", [
                "Kesharaia Hair Oil [VGLS0005]", 
                "Herbal Crown: 1 [VGLS0001]", 
                "Maas Go Capsules [VGLS0006]"
            ])
            qty = st.number_input("Qty", min_value=1, value=1)
            amt = st.number_input("Sale Amount (Total Price)", min_value=0.0)
            note = st.text_area("Product Note")
            disc = st.number_input("Product Discount", min_value=0.0)
            
            st.markdown("<div class='section-box'><b>Courier & Charges</b></div>", unsafe_allow_html=True)
            courier = st.selectbox("Courier Company", ["Royal Express", "Koombiyo", "Domex"])
            del_charge = st.number_input("Delivery Charge", min_value=0.0)
            
            total = (amt - disc) + del_charge
            st.write(f"### Total Amount: Rs. {total:,.2f}")
            
            if st.button("🚀 SAVE & PROCESS ORDER", use_container_width=True):
                if cust_name and phone1 and addr:
                    st.success("Order Saved Successfully!")
                else:
                    st.error("Please fill required fields!")

    else:
        st.info(f"{choice} section is currently loading...")
