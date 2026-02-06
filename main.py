import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop Official ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. CSS FOR PROFESSIONAL DARK UI ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #333; }
    
    /* Header Status Cards (As per your screenshots) */
    .status-card-container { display: flex; gap: 10px; margin-bottom: 20px; }
    .status-card {
        padding: 12px 25px; border-radius: 8px; font-weight: bold; color: black; 
        display: flex; align-items: center; justify-content: center; min-width: 140px;
    }
    .bg-pending { background-color: #2ecc71; }   /* Green */
    .bg-ok { background-color: #f39c12; }        /* Orange */
    .bg-no-answer { background-color: #e74c3c; }  /* Red */
    
    .form-container { background-color: #1a1c23; padding: 25px; border-radius: 12px; border: 1px solid #444; }
    .sidebar-title { color: #e67e22; font-size: 26px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE MANAGEMENT (Fixes KeyErrors) ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state:
    # Adding one sample lead based on your screenshot data
    st.session_state.orders = [
        {"ID": "HS-1384", "Date": "2026-02-06", "Customer": "Sharanga Malaka", "Phone": "0702710550", 
         "Address": "69/3 Ragama Road, Kadawatha", "Status": "Pending", "Amount": 2950.0, "Pro Code": "VGLS0005"}
    ]
if 'stocks' not in st.session_state:
    st.session_state.stocks = [
        {"Product": "Hair Oil", "Code": "VGLS0005", "Price": 2950.0, "Available": 272, "Packed": 0},
        {"Product": "Crown 1", "Code": "VGLS0001", "Price": 2400.0, "Available": 50, "Packed": 0},
        {"Product": "Kalkaya", "Code": "VGLS0003", "Price": 2800.0, "Available": 624, "Packed": 0}
    ]

# --- 4. AUTHENTICATION ---
if st.session_state.user is None:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br><div class='form-container'><h2 style='text-align:center;'>Happy Shop ERP Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else: st.error("Invalid Credentials!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR NAVIGATION (With Happy Shop Branding) ---
    with st.sidebar:
        st.markdown(f"<div class='sidebar-title'>Happy Shop</div>", unsafe_allow_html=True)
        menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks", "🏷️ Products"])
        
        sub_menu = "Default"
        if menu == "🧾 Orders":
            sub_menu = st.radio("Order Actions", ["New Order", "View Lead", "Order Search", "Import Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"])
        elif menu == "🚚 Shipped Items":
            sub_menu = st.radio("Shipped Actions", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Courier Feedback", "Confirm Dispatch", "Print Dispatch Items", "Search Waybills", "Courier Feedback Summary"])
        elif menu == "📊 Stocks":
            sub_menu = st.radio("Stock Actions", ["View Stocks", "Stock Adjustment", "Stock Adjustment View", "Add Waste", "Stock Values"])
        elif menu == "↩️ Return":
            sub_menu = st.radio("Return Actions", ["Add Returns", "Returned Orders", "Pending Returns"])
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # --- 6. TOP STATUS BAR (Dynamic Summary) ---
    def get_count(status): return len([o for o in st.session_state.orders if o['Status'] == status])
    
    st.markdown(f"""
        <div class="status-card-container">
            <div class="status-card bg-pending">Pending | {get_count('Pending')}</div>
            <div class="status-card bg-ok">Ok | {get_count('Ok')}</div>
            <div class="status-card bg-no-answer">No Answer | {get_count('No Answer')}</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 7. CONTENT SECTIONS ---

    # DASHBOARD
    if menu == "🏠 Dashboard":
        st.subheader("Welcome to Happy Shop Dashboard")
        m1, m2, m3 = st.columns(3)
        # Fix for KeyError: checking if 'Amount' exists before summing
        total_rev = sum(float(o.get('Amount', 0)) for o in st.session_state.orders)
        m1.metric("Total Revenue", f"LKR {total_rev:,.2f}")
        m2.metric("Total Orders", len(st.session_state.orders))
        m3.metric("Shipped Orders", "0")
        
        st.markdown("### Recent Activity")
        st.table(pd.DataFrame(st.session_state.orders).tail(5))

    # NEW ORDER ENTRY
    elif menu == "🧾 Orders" and (sub_menu == "New Order" or sub_menu == "Add Lead"):
        st.subheader("Order Registration Form")
        with st.container():
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name *")
                addr = st.text_area("Address *")
                city = st.text_input("City")
                ph1 = st.text_input("Contact Number One *")
                source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "Tiktok", "Web"])
            with c2:
                prod = st.selectbox("Product", [s['Product'] for s in st.session_state.stocks])
                qty = st.number_input("Qty", min_value=1, value=1)
                amt = st.number_input("Sale Amount", min_value=0.0)
                courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto"])
                del_charge = st.number_input("Delivery Charge", min_value=0.0)
            
            if st.button("🚀 SUBMIT ORDER"):
                if name and ph1:
                    new_entry = {
                        "ID": f"HS-{1300 + len(st.session_state.orders) + 1}",
                        "Date": str(datetime.now().date()), "Customer": name, "Phone": ph1,
                        "Address": addr, "Status": "Pending", "Amount": amt + del_charge, "Pro Code": prod
                    }
                    st.session_state.orders.append(new_entry)
                    st.success("Order Processed Successfully!")
                    st.rerun()
                else: st.error("Please fill the mandatory fields (Name & Phone)!")

    # VIEW LEAD (Matching Table Style from Image 22)
    elif menu == "🧾 Orders" and sub_menu == "View Lead":
        st.subheader("Leads Management List")
        
        df_leads = pd.DataFrame(st.session_state.orders)
        st.dataframe(df_leads, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### ⚙️ Update Lead Status")
        col_id, col_stat, col_btn = st.columns([2, 2, 1])
        with col_id:
            sel_id = st.selectbox("Select Lead ID", df_leads['ID'])
        with col_stat:
            sel_stat = st.selectbox("Status", ["Pending", "Ok", "No Answer", "Confirmed", "Rejected", "Hold", "Canceled"])
        with col_btn:
            st.write(" ") 
            if st.button("UPDATE STATUS"):
                for order in st.session_state.orders:
                    if order['ID'] == sel_id:
                        order['Status'] = sel_stat
                        st.success(f"Status updated for {sel_id}")
                        st.rerun()

    # STOCKS VIEW (Matching Image 18)
    elif menu == "📊 Stocks":
        st.subheader(f"Stocks > {sub_menu}")
        if sub_menu == "View Stocks":
            st.table(pd.DataFrame(st.session_state.stocks))
        else:
            st.info(f"System is ready to process {sub_menu} data.")

    # PRODUCT SETTINGS (Matching Image 19)
    elif menu == "🏷️ Products":
        st.subheader("Product Inventory Configuration")
        with st.expander("Register New Product"):
            st.text_input("Product Name")
            st.text_input("Product Code")
            st.number_input("Sale Price")
            st.button("Save Product")
            
    # DEFAULT FOR OTHER SECTIONS
    else:
        st.subheader(f"{menu} > {sub_menu}")
        st.write("Data table loading...")
        st.dataframe(pd.DataFrame(st.session_state.orders))
