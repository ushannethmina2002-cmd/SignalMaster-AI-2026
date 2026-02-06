import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. පේජ් එකේ මූලික සැකසුම් ---
st.set_page_config(
    page_title="HappyShop Official ERP", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- 2. CSS STYLING (Sidebar එක පින්තූරවල තියෙන විදිහටම හැදීම) ---
st.markdown("""
    <style>
    /* මුළු App එකේම පසුබිම */
    .stApp { background-color: #0d1117; color: white; }
    
    /* වම් පැත්තේ Sidebar එකේ පෙනුම */
    [data-testid="stSidebar"] {
        background-color: #001529 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Sidebar එකේ අයිකන් සහ අකුරු සුදු පාට කිරීම */
    [data-testid="stSidebar"] * {
        color: white !important;
        font-weight: 500;
    }

    /* මෙනු එක තේරූ විට ලැබෙන පාට (Orange/Blue) */
    .st-emotion-cache-10o0f9z { background-color: #e67e22 !important; }

    /* පින්තූරවල තිබුණු වැනි කොටු (Section Boxes) */
    .section-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }

    /* Hamburger Menu Button (සුදු පාට කිරීම) */
    header[data-testid="stHeader"] button svg {
        fill: white !important;
    }
    
    /* අනවශ්‍ය Streamlit අංග අයින් කිරීම */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. දත්ත කළමනාකරණය (Session State) ---
if 'orders' not in st.session_state:
    st.session_state.orders = [
        {"Date": "2026-02-06", "Name": "Sharanga Malaka", "Address": "69/3 Ragama Road", "Contact": "0702710550", "Product": "Kesharaia Hair Oil", "Status": "Pending"}
    ]
if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. LOGIN SYSTEM ---
def login_page():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop ERP Login</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        u = st.text_input("Username / Email")
        p = st.text_input("Password", type="password")
        if st.button("Enter System", use_container_width=True):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.error("විස්තර වැරදියි! Username: happyshop@gmail.com")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MAIN SYSTEM INTERFACE ---
if st.session_state.user is None:
    login_page()
else:
    # --- සයිඩ් බාර් එක (SIDEBAR MENU) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>MANAGER</h2>", unsafe_allow_html=True)
        st.write(f"Logged in as: **{st.session_state.user}**")
        st.markdown("---")
        
        # උඹ එවපු පින්තූරවල තියෙන මෙනු ටික
        main_choice = st.radio("MAIN MENU", [
            "🏠 Dashboard", "📦 GRN", "💸 Expense", "🛒 Orders", 
            "🚚 Shipped Items", "🔄 Return", "📊 Stocks", "🏷️ Products"
        ])

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- මෙනු එකට අදාළ පේජ් (Dynamic Pages) ---
    
    # --- ORDERS SECTION ---
    if "Orders" in main_choice:
        sub_choice = st.selectbox("Action", [
            "New Order", "Pending Orders", "Order Search", "Import Lead", 
            "Order History", "Exchanging Orders", "Blacklist Manager"
        ])

        if sub_choice == "New Order":
            st.markdown("## 📝 New Order Entry")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("<div class='section-box'><b>👤 Customer Details</b><br><br>", unsafe_allow_html=True)
                name = st.text_input("Customer Name *")
                addr = st.text_area("Address *")
                phone = st.text_input("Phone Number *")
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div class='section-box'><b>📦 Product Info</b><br><br>", unsafe_allow_html=True)
                prod = st.selectbox("Item", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go"])
                qty = st.number_input("Qty", min_value=1, value=1)
                price = st.number_input("Price", min_value=0.0)
                if st.button("Save Order", use_container_width=True):
                    new_order = {"Date": str(datetime.now().date()), "Name": name, "Address": addr, "Contact": phone, "Product": prod, "Status": "Pending"}
                    st.session_state.orders.append(new_order)
                    st.success("ඕඩර් එක සාර්ථකව සේව් කළා!")
                st.markdown("</div>", unsafe_allow_html=True)

        elif sub_choice == "Order Search":
            st.markdown("## 🔍 Leads / Order Search")
            st.markdown("<div class='section-box'>", unsafe_allow_html=True)
            sc1, sc2, sc3 = st.columns(3)
            with sc1: st.selectbox("User", ["Any", "Admin"])
            with sc2: st.text_input("Customer Name Search")
            with sc3: st.date_input("Start Date")
            st.button("Search Now")
            st.markdown("</div>", unsafe_allow_html=True)
            
            df = pd.DataFrame(st.session_state.orders)
            st.table(df) # පින්තූරේ තිබුණු විදිහටම ලිස්ට් එක පෙන්වයි

    # --- STOCKS SECTION ---
    elif "Stocks" in main_choice:
        st.header("📊 Stock Management")
        st.selectbox("Stock Action", ["View Stocks", "Stock Adjustment", "Stock Values"])
        st.info("Stock දත්ත මෙතැනින් කළමනාකරණය කරන්න.")

    # --- PRODUCTS SECTION ---
    elif "Products" in main_choice:
        st.header("🏷️ Products")
        st.selectbox("Product Action", ["Create Product", "View Products", "Raw Items"])
        st.info("නව නිෂ්පාදන ඇතුළත් කිරීම මෙතැනින් සිදු කරන්න.")

    # --- අනෙක් හැම එකක් සඳහාම ---
    else:
        st.header(main_choice)
        st.warning("මෙම අංශය සඳහා දත්ත සකසමින් පවතී (Coming Soon).")
