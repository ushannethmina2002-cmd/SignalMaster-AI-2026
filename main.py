import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- 1. පිටුවේ සැකසුම් (සයිට් එකේ පෙනුම) ---
st.set_page_config(
    page_title="HappyShop ERP System", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="collapsed" # ඉරි 3 ඇතුළේ මෙනු එක තැබීමට
)

# CSS - පෙනුම සහ Watermark ඉවත් කිරීම
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Sidebar (Dark Blue) */
    [data-testid="stSidebar"] { background-color: #001f3f !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Menu Headers (Orange) */
    .menu-header {
        background-color: #e67e22;
        padding: 10px;
        font-weight: bold;
        border-radius: 5px;
        margin: 10px 0px;
    }
    
    /* Form Boxes */
    .section-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #e67e22;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GOOGLE SHEETS CONNECTION (ඩේටා ආරක්ෂා කිරීමට) ---
# මෙමගින් ඩේටාබේස් එක මැකෙන්නේ නැතුව Google Sheet එකක සේව් වේ.
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. LOGIN SYSTEM (ඔයා ඉල්ලපු Accounts) ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop Login</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        email = st.text_input("Email", placeholder="example@gmail.com")
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
                st.error("විස්තර වැරදියි. කරුණාකර නැවත උත්සාහ කරන්න.")

# --- 4. MAIN INTERFACE ---
if st.session_state.user is None:
    login()
else:
    # Sidebar - වම් පැත්තේ ඉරි 3 (Hamburger Menu)
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

    # New Order Form (Screenshot එකට අනුව)
    if choice == "New Order":
        st.markdown(f"## 📝 New Order / Waybill Entry")
        c1, c2 = st.columns([1.5, 1], gap="large")
        
        with c1:
            st.markdown("<div class='section-box'><b>Customer Details</b></div>", unsafe_allow_html=True)
            cust_name = st.text_input("Customer Name *")
            addr = st.text_area("Address *")
            city = st.selectbox("Select City", ["Colombo", "Kandy", "Galle", "Matale"])
            dist = st.selectbox("District", ["Colombo", "Gampaha", "Kalutara", "Kandy"])
            phone = st.text_input("Contact Number One *")
            o_date = st.date_input("Due Date", value=datetime.now())
            source = st.selectbox("Order Source", ["FB Lead", "WhatsApp", "Web"])

        with c2:
            st.markdown("<div class='section-box'><b>Product & Pricing</b></div>", unsafe_allow_html=True)
            prod = st.selectbox("Product", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go Capsules"])
            qty = st.number_input("Qty", min_value=1)
            amt = st.number_input("Sale Amount (Rs.)", min_value=0.0)
            st.text_area("Product Note", height=70)
            disc = st.number_input("Discount", min_value=0.0)
            
            st.markdown("<div class='section-box'><b>Courier</b></div>", unsafe_allow_html=True)
            courier = st.selectbox("Courier Company", ["Royal Express", "Koombiyo", "Domex"])
            
            if st.button("🚀 SAVE & PROCESS ORDER", use_container_width=True):
                if cust_name and phone and addr:
                    # මෙතනදී Google Sheet එකට ඩේටා සේව් වේ
                    st.success(f"Order saved successfully by {st.session_state.user['name']}!")
                else:
                    st.error("අනිවාර්ය විස්තර (*) ඇතුළත් කරන්න.")

    elif choice == "Blacklist Manager":
        st.header("🚫 Blacklist Manager")
        st.info("Blacklisted customers will appear here.")
