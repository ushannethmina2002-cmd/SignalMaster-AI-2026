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

# --- 2. CSS: සුදු මෙනු බාර් එක සහ Sidebar එක හැඩ ගැන්වීම ---
st.markdown("""
    <style>
    /* මුළු පසුබිම */
    .stApp { background-color: #0d1117; color: white; padding-top: 60px; }

    /* --- WHITE HEADER (උඹ එවපු HTML එකේ විදියට) --- */
    .custom-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background-color: #ffffff;
        padding: 12px 25px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        z-index: 1000;
    }
    .menu-logo { font-weight: bold; font-size: 20px; color: #000; }
    .menu-links a {
        margin-left: 20px;
        text-decoration: none;
        color: #333;
        font-weight: 600;
        font-family: 'Arial', sans-serif;
    }

    /* --- SIDEBAR සැකසුම් --- */
    [data-testid="stSidebar"] {
        background-color: #001529 !important;
        padding-top: 60px; /* Header එකට ඉඩ තැබීමට */
    }
    [data-testid="stSidebar"] * { color: white !important; }

    /* Hamburger Icon (ඉරි 3) කළු පාට කිරීම (සුදු පසුබිමේ පේන්න) */
    [data-testid="stHeader"] button svg { 
        fill: #000000 !important; 
        width: 30px;
        height: 30px;
    }
    
    /* Section Boxes */
    .section-box {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        border-left: 5px solid #e67e22;
    }

    /* Streamlit ගේ සාමාන්‍ය Header එක අයින් කිරීම */
    header[data-testid="stHeader"] { background-color: transparent; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    
    <div class="custom-header">
        <div class="menu-logo">HappyShop Official ERP</div>
        <div class="menu-links">
            <a href="#">Home</a>
            <a href="#">Odds</a>
            <a href="#">VIP</a>
            <a href="#">Contact</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. SESSION DATA & LOGIN ---
if 'user' not in st.session_state:
    st.session_state.user = None
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 4. LOGIN INTERFACE ---
if st.session_state.user is None:
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>System Login</h1>", unsafe_allow_html=True)
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
                st.error("විස්තර වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR (ස්ථිරවම පවතින මෙනු එක) ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>MANAGER</h2>", unsafe_allow_html=True)
        st.markdown("---")
        
        main_choice = st.radio("Navigation", [
            "🏠 Dashboard", "📦 GRN", "💸 Expense", "🛒 Orders", 
            "🚚 Shipped Items", "🔄 Return", "📊 Stocks", "🏷️ Products"
        ])

        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- 6. පේජ් වලට අදාළ ඩේටා ---
    if "Orders" in main_choice:
        sub = st.selectbox("Order Section", ["New Order", "Order Search", "Pending Orders"])
        
        if sub == "New Order":
            st.markdown("### 📝 Create New Order")
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown("<div class='section-box'><b>👤 Customer</b>", unsafe_allow_html=True)
                name = st.text_input("Customer Name")
                phone = st.text_input("Phone")
                st.markdown("</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div class='section-box'><b>📦 Pricing</b>", unsafe_allow_html=True)
                amt = st.number_input("Amount", min_value=0.0)
                if st.button("Save", use_container_width=True):
                    st.session_state.orders.append({"Date": str(datetime.now().date()), "Name": name, "Phone": phone, "Total": amt})
                    st.success("Saved!")
                st.markdown("</div>", unsafe_allow_html=True)
        
        elif sub == "Order Search":
            st.markdown("### 🔍 Leads / Order Search")
            df = pd.DataFrame(st.session_state.orders)
            st.table(df)

    else:
        st.header(main_choice)
        st.info("මෙම කොටස සකස් කරමින් පවතී.")
