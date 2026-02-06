import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. පේජ් සැකසුම් ---
st.set_page_config(
    page_title="HappyShop Official ERP", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- 2. CSS STYLING (ලස්සන Professional පෙනුම සහ සුදු ඉරි කෑලි 3) ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    
    /* ☰ Hamburger Menu Icon එක සුදු පාට කිරීම */
    [data-testid="stHeader"] button svg {
        fill: white !important;
        color: white !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #001f3f !important;
        min-width: 280px !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Orange Headers for Sections */
    .menu-header {
        background-color: #e67e22;
        padding: 8px;
        font-weight: bold;
        border-radius: 5px;
        margin-top: 10px;
        text-align: center;
        font-size: 14px;
    }

    /* Section Boxes */
    .section-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        border-left: 6px solid #e67e22;
        margin-bottom: 20px;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION DATA (ඩේටා තාවකාලිකව තබා ගැනීමට) ---
if 'orders' not in st.session_state: st.session_state.orders = []
if 'user' not in st.session_state: st.session_state.user = None

# LOGIN FUNCTION
def login():
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
            else: st.error("වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.user is None:
    login()
else:
    # --- 4. මෙනු බාර් එක (SIDEBAR) - උඹ එවපු පින්තූරවල තිබුණු විදිහටම ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>MANAGER</h2>", unsafe_allow_html=True)
        
        menu = st.radio("MAIN MENU", [
            "🏠 Dashboard", "📦 GRN", "💸 Expense", "🛒 Orders", 
            "🚚 Shipped Items", "🔄 Return", "📊 Stocks", "🏷️ Products"
        ])

        if menu == "📦 GRN":
            sub_menu = st.selectbox("GRN Options", ["New GRN", "GRN List", "Reorder List", "New PO", "PO List", "Packing"])
        elif menu == "🛒 Orders":
            sub_menu = st.selectbox("Order Options", ["New Order", "Pending Orders", "Order Search", "Import Lead", "Order History", "Blacklist Manager"])
        elif menu == "🚚 Shipped Items":
            sub_menu = st.selectbox("Shipping Options", ["Ship", "Shipped List", "Delivery Summary", "Confirm Dispatch"])
        elif menu == "📊 Stocks":
            sub_menu = st.selectbox("Stock Options", ["View Stocks", "Stock Adjustment", "Stock Values"])
        elif menu == "🏷️ Products":
            sub_menu = st.selectbox("Product Options", ["Create Product", "View Products", "Raw Items"])
        else:
            sub_menu = "Default"

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- 5. පේජ් වලට අදාළ වැඩ කොටස ---
    
    # NEW ORDER PAGE
    if menu == "🛒 Orders" and sub_menu == "New Order":
        st.markdown("## 📝 New Order Entry")
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("<div class='section-box'><b>👤 Customer Details</b>", unsafe_allow_html=True)
            name = st.text_input("Customer Name *")
            address = st.text_area("Address *")
            phone = st.text_input("Phone Number *")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='section-box'><b>📦 Product Info</b>", unsafe_allow_html=True)
            item = st.selectbox("Select Product", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go"])
            price = st.number_input("Price", min_value=0.0)
            if st.button("🚀 Save Order", use_container_width=True):
                st.session_state.orders.append({"Date": str(datetime.now().date()), "Name": name, "Phone": phone, "Item": item, "Total": price})
                st.success("සාර්ථකව සේව් කළා!")
            st.markdown("</div>", unsafe_allow_html=True)

    # ORDER SEARCH PAGE (Screenshot එකේ තිබුණ විදිහට)
    elif menu == "🛒 Orders" and sub_menu == "Order Search":
        st.markdown("## 🔍 Order Search")
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.selectbox("User", ["Any", "Admin"])
        with col2: st.text_input("Customer Name")
        with col3: st.date_input("Start Date")
        if st.button("Search"):
            st.write("Searching...")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.session_state.orders:
            st.table(pd.DataFrame(st.session_state.orders))
        else: st.info("දත්ත කිසිවක් නැත.")

    # අනෙකුත් පේජ් සඳහා (Coming Soon)
    else:
        st.header(f"{menu} - {sub_menu}")
        st.warning("මෙම අංශය දැනට සැකසෙමින් පවතී.")
