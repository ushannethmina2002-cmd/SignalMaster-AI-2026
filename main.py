import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. ADVANCED CSS FOR UI MATCHING ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #333; }
    
    /* Header Status Cards (From your screenshots) */
    .status-card-container { display: flex; gap: 10px; margin-bottom: 20px; }
    .status-card {
        padding: 10px 20px; border-radius: 8px; font-weight: bold; color: black; 
        display: flex; align-items: center; justify-content: center; min-width: 120px;
    }
    .bg-pending { background-color: #2ecc71; } /* Green */
    .bg-ok { background-color: #f39c12; }      /* Orange */
    .bg-no-answer { background-color: #e74c3c; } /* Red */
    
    .form-container { background-color: #1a1c23; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    .stMetric { background-color: #1a1c23; padding: 15px; border-radius: 10px; border-left: 5px solid #e67e22; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE MANAGEMENT (Fixes KeyErrors) ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state:
    st.session_state.orders = [
        {"ID": "HS-1001", "Date": "2026-02-06", "Customer": "Sample User", "Phone": "0771234567", "Status": "Pending", "Amount": 2950.0}
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
        st.markdown("<br><br><div class='form-container'><h2 style='text-align:center;'>Happy Shop ERP</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else: st.error("Invalid Credentials!")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # --- 5. SIDEBAR NAVIGATION (Matching All Your Screenshots) ---
    with st.sidebar:
        st.markdown(f"<h2 style='color:#e67e22;'>Sandun</h2>", unsafe_allow_html=True)
        menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks", "🏷️ Products"])
        
        sub_menu = "Default"
        if menu == "🧾 Orders":
            sub_menu = st.radio("Order Actions", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Order History", "Blacklist Manager"])
        elif menu == "🚚 Shipped Items":
            sub_menu = st.radio("Shipped Actions", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Courier Feedback", "Confirm Dispatch", "Search Waybills"])
        elif menu == "📊 Stocks":
            sub_menu = st.radio("Stock Actions", ["View Stocks", "Stock Adjustment", "Add Waste", "Stock Values"])
        elif menu == "↩️ Return":
            sub_menu = st.radio("Return Actions", ["Add Returns", "Returned Orders", "Pending Returns"])
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # --- 6. TOP STATUS BAR (Dynamic Count) ---
    pending_count = len([o for o in st.session_state.orders if o['Status'] == 'Pending'])
    st.markdown(f"""
        <div class="status-card-container">
            <div class="status-card bg-pending">Pending | {pending_count}</div>
            <div class="status-card bg-ok">Ok | 0</div>
            <div class="status-card bg-no-answer">No Answer | 0</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 7. CONTENT SECTIONS ---

    # DASHBOARD
    if menu == "🏠 Dashboard":
        st.subheader("Business Summary")
        m1, m2, m3 = st.columns(3)
        total_rev = sum(o.get('Amount', 0) for o in st.session_state.orders)
        m1.metric("Total Sales", f"LKR {total_rev:,.2f}")
        m2.metric("Total Orders", len(st.session_state.orders))
        m3.metric("Shipped", "0")
        st.dataframe(pd.DataFrame(st.session_state.orders), use_container_width=True)

    # NEW ORDER FORM
    elif menu == "🧾 Orders" and sub_menu == "New Order":
        st.subheader("New Order Entry")
        with st.container():
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name *")
                address = st.text_area("Address *")
                city = st.text_input("City")
                phone = st.text_input("Contact Number One *")
                source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "Tiktok"])
            with c2:
                item = st.selectbox("Product", [s['Product'] for s in st.session_state.stocks])
                qty = st.number_input("Qty", min_value=1)
                price = st.number_input("Sale Amount", min_value=0.0)
                courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto"])
                del_charge = st.number_input("Delivery Charge", min_value=0.0)
            
            if st.button("🚀 Submit Order"):
                if name and phone:
                    new_order = {
                        "ID": f"HS-{1000 + len(st.session_state.orders) + 1}",
                        "Date": str(datetime.now().date()), "Customer": name,
                        "Phone": phone, "Status": "Pending", "Amount": price + del_charge
                    }
                    st.session_state.orders.append(new_order)
                    st.success("Order Saved Successfully!")
                else: st.error("Please fill required fields!")

    # VIEW STOCKS (As per Image 18)
    elif menu == "📊 Stocks" and sub_menu == "View Stocks":
        st.subheader("Current Inventory Status")
        st.table(pd.DataFrame(st.session_state.stocks))

    # IMPORT LEAD / VIEW LEAD (As per Image 14, 15)
    elif menu == "🧾 Orders" and (sub_menu == "Import Lead" or sub_menu == "View Lead"):
        st.subheader(f"{sub_menu} Management")
        st.info("Leads are synced from Order Sources. You can update statuses below.")
        df_leads = pd.DataFrame(st.session_state.orders)
        
        # Status Update Logic
        selected_id = st.selectbox("Select Lead/Order ID", df_leads['ID'])
        new_stat = st.selectbox("Update Status", ["Pending", "Ok", "No Answer", "Rejected", "Canceled"])
        if st.button("Update Status Now"):
            for o in st.session_state.orders:
                if o['ID'] == selected_id:
                    o['Status'] = new_stat
                    st.success(f"ID {selected_id} updated to {new_stat}")
                    st.rerun()
        st.dataframe(df_leads, use_container_width=True)

    # PRODUCTS (As per Image 19)
    elif menu == "🏷️ Products":
        st
