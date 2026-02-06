import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. පේජ් සැකසුම් (SIDEBAR එක සැමවිටම පේන්න පවත්වයි) ---
st.set_page_config(
    page_title="HappyShop Official ERP",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"  # මේකෙන් තමයි මෙනු එක ස්ථිරවම එළියට දාලා තියන්නේ
)

# --- 2. CSS STYLING (පින්තූරවල තිබුණු Layout එකම ලබාගැනීමට) ---
st.markdown("""
    <style>
    /* මුළු App එකේම පසුබිම */
    .stApp { background-color: #0d1117; color: white; }
    
    /* වම් පැත්තේ Sidebar එකේ පෙනුම */
    [data-testid="stSidebar"] {
        background-color: #001529 !important;
        min-width: 250px !important;
    }
    
    /* Sidebar අකුරු සුදු පාට කිරීම */
    [data-testid="stSidebar"] * { color: white !important; font-size: 16px; }

    /* Hamburger Icon (ඉරි 3) සුදු පාට කිරීම */
    [data-testid="stHeader"] button svg { fill: white !important; }

    /* මෙනු Header එක (Orange Color) */
    .menu-header {
        background-color: #e67e22;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        border-radius: 5px;
        margin: 10px 0;
    }

    /* Section Boxes */
    .section-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    
    /* අනවශ්‍ය Streamlit Label අයින් කිරීම */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN SESSION ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. DATA ---
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 5. LOGIN VIEW ---
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center; color: #f1c40f;'>HappyShop ERP Login</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.error("වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 6. ස්ථිර මෙනු බාර් එක (SIDEBAR MENU) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>MANAGER</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        # උඹ එවපු පින්තූරවල තිබුණු ඒ විදිහටම මෙනු එක
        main_menu = st.radio("Main Navigation", [
            "🏠 Dashboard", "📦 GRN", "💸 Expense", "🛒 Orders", 
            "🚚 Shipped Items", "🔄 Return", "📊 Stocks", "🏷️ Products"
        ])
        
        # එක එක මෙනු එකට අදාළ Sub Options
        if "Orders" in main_menu:
            sub_menu = st.selectbox("Order Actions", [
                "New Order", "Pending Orders", "Order Search", 
                "Import Lead", "View Lead", "Add Lead", 
                "Order History", "Exchanging Orders", "Blacklist Manager"
            ])
        elif "GRN" in main_menu:
            sub_menu = st.selectbox("GRN Actions", ["New GRN", "GRN List", "Reorder List", "New PO", "PO List", "Packing"])
        elif "Shipped" in main_menu:
            sub_menu = st.selectbox("Shipping Actions", ["Ship", "Shipped List", "Delivery Summary", "Confirm Dispatch"])
        elif "Stocks" in main_menu:
            sub_menu = st.selectbox("Stock Actions", ["View Stocks", "Stock Adjustment", "Stock Values"])
        elif "Products" in main_menu:
            sub_menu = st.selectbox("Product Actions", ["Create Product", "View Products", "Raw Items"])
        else:
            sub_menu = "Home"

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- 7. පේජ් වල අන්තර්ගතය ---
    
    # NEW ORDER PAGE (පින්තූරේ තිබුණු විදිහට)
    if main_menu == "🛒 Orders" and sub_menu == "New Order":
        st.markdown("## 📝 New Order Entry")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("<div class='section-box'><b>👤 Customer Details</b>", unsafe_allow_html=True)
            st.text_input("Customer Name *")
            st.text_area("Address *")
            st.text_input("Phone Number *")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='section-box'><b>📦 Product & Pricing</b>", unsafe_allow_html=True)
            st.selectbox("Select Product", ["Kesharaia Hair Oil", "Herbal Crown"])
            st.number_input("Qty", value=1)
            st.number_input("Sale Amount", value=0.0)
            st.button("Save Order", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ORDER SEARCH PAGE (පින්තූරේ තිබුණු විදිහට)
    elif main_menu == "🛒 Orders" and sub_menu == "Order Search":
        st.markdown("## 🔍 Order Search")
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.selectbox("User", ["Any", "Admin"])
        with col2: st.text_input("Customer Name")
        with col3: st.date_input("Start Date")
        st.button("Search")
        st.markdown("</div>", unsafe_allow_html=True)
        st.info("මෙහි දත්ත සෙවීමේ ප්‍රතිඵල පෙන්වයි.")

    # DASHBOARD
    elif "Dashboard" in main_menu:
        st.header("🏠 Welcome to Dashboard")
        st.info("පද්ධතියේ දත්ත සාරාංශය මෙහි පෙන්වයි.")

    # අනෙකුත් සියලුම පේජ් සඳහා
    else:
        st.header(f"{main_menu} - {sub_menu}")
        st.warning("මෙම කොටස සඳහා දත්ත ඇතුළත් කරමින් පවතී.")
