import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE SETUP (ලස්සනට සහ මෙනු එක පේන්න) ---
st.set_page_config(
    page_title="HappyShop Official ERP", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="expanded" # මෙනු එක හැමවෙලේම ඇරිලා තියෙන්න
)

# --- 2. ADVANCED CSS (ලස්සන Dark/Orange Theme එකක්) ---
st.markdown("""
    <style>
    /* මුළු පිටුවම Dark Mode කිරීම */
    .stApp { background-color: #0d1117; color: white; }
    
    /* මෙනු බාර් එකේ පෙනුම (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: #001f3f !important;
        min-width: 260px !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* මෙනු එකේ කැටගරි (Orange Headers) */
    .menu-header {
        background-color: #e67e22;
        padding: 12px;
        font-weight: bold;
        border-radius: 8px;
        margin: 15px 0px 5px 0px;
        text-align: center;
    }

    /* Form Boxes (ලස්සනට කොටු කිරීම) */
    .section-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        border-left: 6px solid #e67e22;
        margin-bottom: 25px;
    }

    /* Input Fields ලස්සන කිරීම */
    input, textarea, select {
        background-color: #0d1117 !important;
        color: white !important;
        border: 1px solid #30363d !important;
    }

    /* අනවශ්‍ය දේවල් අයින් කිරීම */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN SESSION ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop Web Portal</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        email = st.text_input("Username / Email")
        pwd = st.text_input("Password", type="password")
        if st.button("Log In to System", use_container_width=True):
            if email == "happyshop@gmail.com" and pwd == "VLG0005":
                st.session_state.user = {"name": "Admin", "role": "OWNER"}
                st.rerun()
            elif (email == "demo1@gmail.com" and pwd == "demo1") or (email == "demo2@gmail.com" and pwd == "demo2"):
                st.session_state.user = {"name": email.split('@')[0], "role": "STAFF"}
                st.rerun()
            else:
                st.error("විස්තර වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. MAIN INTERFACE ---
if st.session_state.user is None:
    login()
else:
    # --- SIDEBAR MENU (මෙන්න මේක තමයි ඔයා ඉල්ලපු මෙනු එක) ---
    with st.sidebar:
        st.markdown(f"<h2 style='text-align:center;'>🛒 HappyShop</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>User: <b>{st.session_state.user['name']}</b></p>", unsafe_allow_html=True)
        st.markdown("---")
        
        st.button("🏠 Dashboard", use_container_width=True)
        st.button("📦 GRN", use_container_width=True)
        st.button("💸 Expense", use_container_width=True)
        
        st.markdown("<div class='menu-header'>ORDERS</div>", unsafe_allow_html=True)
        choice = st.radio("Nav", [
            "New Order", "Pending Orders", "Order Search", 
            "Import Lead", "View Lead", "Add Lead", 
            "Order History", "Exchanging Orders", "Blacklist Manager"
        ], label_visibility="collapsed")
        
        st.markdown("<div class='menu-header'>SHIPPED & RETURN</div>", unsafe_allow_html=True)
        st.button("🚚 Shipped Items", use_container_width=True)
        st.button("🔄 Return Orders", use_container_width=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", color="red"):
            st.session_state.user = None
            st.rerun()

    # --- CONTENT AREA (ORDER FORM) ---
    if choice == "New Order":
        st.markdown("## 📝 Customer / Waybill Entry")
        
        col_main, col_side = st.columns([1.6, 1], gap="large")
        
        with col_main:
            st.markdown("<div class='section-box'><b>👤 Customer Details</b>", unsafe_allow_html=True)
            st.selectbox("Target User", ["All", "Registered", "Guest"])
            st.text_input("Customer Name *", placeholder="Enter full name")
            st.text_area("Address *", placeholder="Enter delivery address")
            
            c1, c2 = st.columns(2)
            c1.selectbox("Select City *", ["Colombo", "Kandy", "Galle", "Matale"])
            c2.selectbox("Select District *", ["Colombo", "Gampaha", "Kalutara", "Kandy"])
            
            p1, p2 = st.columns(2)
            p1.text_input("Contact Number One *")
            p2.text_input("Contact Number Two")
            
            st.date_input("Due Date", value=datetime.now())
            st.selectbox("Order Source", ["FB Lead", "WhatsApp", "Web", "Call"])
            st.selectbox("Payment Method", ["COD (Cash on Delivery)", "Bank Transfer"])
            st.markdown("</div>", unsafe_allow_html=True)

        with col_side:
            st.markdown("<div class='section-box'><b>📦 Product & Pricing</b>", unsafe_allow_html=True)
            st.selectbox("Select Product *", [
                "Kesharaia Hair Oil [VGLS0005]", 
                "Herbal Crown: 1 [VGLS0001]", 
                "Maas Go Capsules [VGLS0006]"
            ])
            st.number_input("Qty", min_value=1, value=1)
            st.number_input("Sale Amount (LKR)", min_value=0.0)
            st.text_area("Product Note", height=80)
            st.number_input("Discount", min_value=0.0)
            
            st.markdown("<b>🚚 Courier Info</b>", unsafe_allow_html=True)
            st.selectbox("Courier Company", ["Royal Express", "Koombiyo", "Domex"])
            st.number_input("Delivery Charge", min_value=0.0)
            
            st.divider()
            st.markdown("<h3 style='text-align:right;'>Total: Rs. 0.00</h3>", unsafe_allow_html=True)
            
            if st.button("🚀 SAVE & PROCESS ORDER", use_container_width=True):
                st.success("Order Saved!")
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info(f"The '{choice}' section is coming soon.")
