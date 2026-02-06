import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="HappyShop Official ERP", 
    page_icon="🛒", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# --- 2. CSS STYLING (Hamburger Icon White + Styling) ---
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
        min-width: 260px !important;
    }
    [data-testid="stSidebar"] * { color: white !important; }

    .menu-header {
        background-color: #e67e22;
        padding: 10px;
        font-weight: bold;
        border-radius: 8px;
        margin-top: 15px;
        text-align: center;
    }

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

# --- 3. DATA STORAGE (Temporary) ---
if 'orders_list' not in st.session_state:
    st.session_state.orders_list = [
        {"Date": "2026-02-06", "Name": "Wasantha Bandara", "Phone": "0773411920", "Address": "Matale", "Product": "Kesharaia Hair Oil", "Status": "Pending", "Total": 2500.0},
        {"Date": "2026-02-05", "Name": "Nethmina", "Phone": "0712345678", "Address": "Kandy", "Product": "Herbal Crown", "Status": "Shipped", "Total": 3200.0}
    ]

# --- 4. LOGIN SYSTEM ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login_view():
    st.markdown("<br><br><h1 style='text-align: center; color: #f1c40f;'>HappyShop ERP Login</h1>", unsafe_allow_html=True)
    _, col2, _ = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='section-box'>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Log In", use_container_width=True):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.error("Login Details වැරදියි!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 5. MAIN INTERFACE ---
if st.session_state.user is None:
    login_view()
else:
    # --- SIDEBAR MENU ---
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>🛒 HappyShop</h2>", unsafe_allow_html=True)
        st.markdown("<div class='menu-header'>ORDERS</div>", unsafe_allow_html=True)
        choice = st.radio("Nav", [
            "New Order", "Pending Orders", "Order Search", 
            "Order History", "Blacklist Manager"
        ], label_visibility="collapsed")
        
        st.markdown("<div class='menu-header'>SYSTEM</div>", unsafe_allow_html=True)
        sub_choice = st.selectbox("Logs", ["Shipped Items", "Return Orders"])
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # --- PAGE LOGIC ---
    df = pd.DataFrame(st.session_state.orders_list)

    if choice == "New Order":
        st.markdown("## 📝 New Order Entry")
        c1, c2 = st.columns([1.6, 1], gap="large")
        with c1:
            st.markdown("<div class='section-box'><b>👤 Customer Details</b>", unsafe_allow_html=True)
            name = st.text_input("Customer Name *")
            addr = st.text_area("Address *")
            phone = st.text_input("Phone Number *")
            st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='section-box'><b>📦 Product</b>", unsafe_allow_html=True)
            prod = st.selectbox("Item", ["Kesharaia Hair Oil", "Herbal Crown", "Maas Go"])
            amt = st.number_input("Price", min_value=0.0)
            if st.button("🚀 SAVE", use_container_width=True):
                new_data = {"Date": str(datetime.now().date()), "Name": name, "Phone": phone, "Address": addr, "Product": prod, "Status": "Pending", "Total": amt}
                st.session_state.orders_list.append(new_data)
                st.success("සාර්ථකව සේව් කළා!")
            st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "Pending Orders":
        st.header("⏳ Pending Orders")
        pending_df = df[df["Status"] == "Pending"]
        st.dataframe(pending_df, use_container_width=True)

    elif choice == "Order Search":
        st.header("🔍 Search Orders")
        q = st.text_input("නම හෝ දුරකථනය ඇතුළත් කරන්න")
        if q:
            results = df[df.apply(lambda row: q.lower() in str(row).lower(), axis=1)]
            st.dataframe(results, use_container_width=True)
        else:
            st.info("සෙවීමට විස්තර ඇතුළත් කරන්න.")

    elif choice == "Order History":
        st.header("📜 Order History")
        st.dataframe(df, use_container_width=True)

    elif choice == "Blacklist Manager":
        st.header("🚫 Blacklist Manager")
        st.warning("දැනට කිසිදු පාරිභෝගිකයෙකු කළු ලැයිස්තුගත කර නැත.")
