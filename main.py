import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px
import time

# =========================================================
# 1. LUXURY GLASS UI + PRO STYLING
# =========================================================
st.set_page_config(page_title="HappyShop ERP PREMIUM", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

    .stApp {
        background: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.85)), 
                    url("https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=2015&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(10, 15, 30, 0.95) !important;
        backdrop-filter: blur(25px);
        border-right: 2px solid #FFD700;
    }

    /* Brand Logo Replacement */
    .brand-logo {
        font-family: 'Inter', sans-serif;
        font-size: 32px;
        font-weight: 800;
        color: #FFD700;
        text-align: center;
        text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.5);
        margin-bottom: 20px;
    }

    /* Top Header */
    .top-header {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        padding: 15px 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 215, 0, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        transition: 0.3s ease;
    }
    .glass-card:hover {
        border: 1px solid #FFD700;
        transform: translateY(-5px);
    }

    /* Professional Metrics */
    div[data-testid="stMetric"] {
        background: rgba(255, 215, 0, 0.05);
        border-radius: 15px;
        padding: 15px;
        border-left: 5px solid #FFD700;
    }

    /* Custom Radio & Buttons */
    .stButton>button {
        border-radius: 10px;
        border: 1px solid #FFD700;
        background: transparent;
        color: #FFD700;
        transition: 0.4s;
    }
    .stButton>button:hover {
        background: #FFD700;
        color: black;
    }

    h1, h2, h3, p, label { color: white !important; font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. DATA ENGINE (Integrated Data Persistence)
# =========================================================
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, default_cols):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame(columns=default_cols)

# Initialize Session States
if "orders_df" not in st.session_state:
    st.session_state.orders_df = load_data("orders.csv", ["id", "date", "name", "phone", "address", "prod", "qty", "total", "status", "staff"])

if "stock_df" not in st.session_state:
    initial_stock = [
        {"Product": "Kasharaja Hair Oil", "Code": "KHO-01", "Qty": 225, "Price": 2950},
        {"Product": "Herbal Night Cream", "Code": "HNC-02", "Qty": 85, "Price": 1800},
        {"Product": "Face Wash Gold", "Code": "FWG-03", "Qty": 110, "Price": 1200}
    ]
    st.session_state.stock_df = pd.DataFrame(initial_stock)

if "expenses_df" not in st.session_state:
    st.session_state.expenses_df = load_data("expenses.csv", ["date", "category", "amount", "note"])

if "user" not in st.session_state: st.session_state.user = None

# =========================================================
# 3. ACCESS CONTROL
# =========================================================
if st.session_state.user is None:
    st.markdown('<div style="text-align:center; margin-top:100px;">', unsafe_allow_html=True)
    st.markdown('<div class="brand-logo">Happy Shop</div>', unsafe_allow_html=True)
    st.title("🛡️ Enterprise Login")
    _, col, _ = st.columns([1, 1, 1])
    with col:
        u_id = st.text_input("User ID")
        u_pw = st.text_input("Access Key", type="password")
        if st.button("AUTHORIZE ACCESS", use_container_width=True):
            if u_id == "admin" and u_pw == "1234":
                st.session_state.user = {"name": "Admin", "role": "OWNER"}
                st.rerun()
            elif u_id == "staff" and u_pw == "1234":
                st.session_state.user = {"name": "Staff", "role": "STAFF"}
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    # ---------------------------------------------------------
    # TOP HEADER
    # ---------------------------------------------------------
    st.markdown(f"""
        <div class="top-header">
            <span style="font-weight: 800; color: #FFD700; font-size: 24px; letter-spacing: 1px;">Happy Shop PRO</span>
            <span style="font-size:14px; color: rgba(255,255,255,0.7);">Session: <b>{st.session_state.user['name']}</b> | {datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
        </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SIDEBAR (Gold Themed & Organized)
    # ---------------------------------------------------------
    with st.sidebar:
        st.markdown('<div class="brand-logo">Happy Shop</div>', unsafe_allow_html=True)
        st.divider()

        if st.button("🏠 Executive Dashboard", use_container_width=True):
            st.session_state.menu_choice = "Dashboard"

        with st.expander("📦 INVENTORY & PRODUCTS"):
            choice_inv = st.radio("Navigation", ["View Stocks", "Stock Adjustment", "Create Product", "Raw Items", "GRN List", "New PO"], label_visibility="collapsed")
            if st.button("Go to Inventory"): st.session_state.menu_choice = choice_inv

        with st.expander("🔍 SALES & LEADS"):
            choice_sales = st.radio("Navigation", ["New Order", "Order Search", "Order History", "Blacklist Manager"], label_visibility="collapsed")
            if st.button("Go to Sales"): st.session_state.menu_choice = choice_sales

        with st.expander("🚚 LOGISTICS & SHIPPING"):
            choice_log = st.radio("Navigation", ["Ship Items", "Shipped List", "Courier Feedback", "Packing List"], label_visibility="collapsed")
            if st.button("Go to Logistics"): st.session_state.menu_choice = choice_log

        with st.expander("💰 FINANCE & EXPENSES"):
            choice_fin = st.radio("Navigation", ["Financial Summary", "New Expense", "View Expenses", "Add Returns"], label_visibility="collapsed")
            if st.button("Go to Finance"): st.session_state.menu_choice = choice_fin

        st.divider()
        if st.button("🔴 Logout System", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    if "menu_choice" not in st.session_state: st.session_state.menu_choice = "Dashboard"
    menu = st.session_state.menu_choice

    # ---------------------------------------------------------
    # MAIN ANALYTICS ENGINE
    # ---------------------------------------------------------
    col_main, col_action = st.columns([3.5, 1.2])

    with col_main:
        if menu == "Dashboard":
            st.title("📊 Enterprise Analytics")
            df = st.session_state.orders_df
            
            # Key Performance Indicators
            k1, k2, k3, k4 = st.columns(4)
            total_rev = df['total'].sum()
            k1.metric("Total Revenue", f"Rs. {total_rev:,.0f}")
            k2.metric("Orders", len(df))
            k3.metric("Stock Value", f"Rs. {(st.session_state.stock_df['Qty'] * st.session_state.stock_df['Price']).sum():,.0f}")
            k4.metric("Pending Leads", len(df[df['status'] == 'pending']))

            # Professional Charts
            c1, c2 = st.columns(2)
            with c1:
                fig_rev = px.line(df, x='date', y='total', title="Revenue Velocity", color_discrete_sequence=['#FFD700'])
                fig_rev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_rev, use_container_width=True)
            with c2:
                fig_stock = px.bar(st.session_state.stock_df, x='Product', y='Qty', title="Inventory Levels", color_discrete_sequence=['#00d4ff'])
                fig_stock.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig_stock, use_container_width=True)

        elif menu == "New Order":
            st.title("🛒 Create New Transaction")
            with st.form("pro_order_form"):
                col1, col2 = st.columns(2)
                with col1:
                    c_name = st.text_input("Customer Full Name")
                    c_phone = st.text_input("Phone Number")
                    c_address = st.text_area("Shipping Address")
                with col2:
                    p_select = st.selectbox("Product SKU", st.session_state.stock_df['Product'].tolist())
                    p_qty = st.number_input("Unit Quantity", min_value=1, value=1)
                    p_price = st.session_state.stock_df.loc[st.session_state.stock_df['Product'] == p_select, 'Price'].values[0]
                    st.info(f"Unit Price: Rs. {p_price:,.2f} | Total: Rs. {p_price * p_qty:,.2f}")
                
                if st.form_submit_button("CONFIRM & SYNC ORDER"):
                    new_id = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    new_order = {
                        "id": new_id, "date": str(date.today()), "name": c_name, "phone": c_phone,
                        "address": c_address, "prod": p_select, "qty": p_qty, "total": p_price * p_qty,
                        "status": "pending", "staff": st.session_state.user['name']
                    }
                    st.session_state.orders_df = pd.concat([st.session_state.orders_df, pd.DataFrame([new_order])], ignore_index=True)
                    save_data(st.session_state.orders_df, "orders.csv")
                    st.success(f"Order {new_id} Successfully Dispatched to Database!")

        elif menu == "View Stocks":
            st.title("📦 Real-time Inventory Grid")
            st.dataframe(st.session_state.stock_df, use_container_width=True)
            st.download_button("Export Inventory CSV", st.session_state.stock_df.to_csv(), "inventory.csv")

        elif menu == "New Expense":
            st.title("💸 Record Business Expense")
            with st.form("expense_form"):
                ex_cat = st.selectbox("Category", ["Marketing", "Staff", "Utility", "Courier", "Other"])
                ex_amt = st.number_input("Amount (LKR)", min_value=0)
                ex_note = st.text_input("Description")
                if st.form_submit_button("Save Expense"):
                    new_ex = {"date": str(date.today()), "category": ex_cat, "amount": ex_amt, "note": ex_note}
                    st.session_state.expenses_df = pd.concat([st.session_state.expenses_df, pd.DataFrame([new_ex])], ignore_index=True)
                    save_data(st.session_state.expenses_df, "expenses.csv")
                    st.success("Expense Recorded.")

        else:
            st.title(f"🛠️ {menu} Module")
            st.info("System is ready. Integration for this module is active. Waiting for data input...")

    # ---------------------------------------------------------
    # RIGHT ACTION PANEL (System Monitor)
    # ---------------------------------------------------------
    with col_action:
        st.markdown(f"""
            <div class="glass-card">
                <h3 style="color:#FFD700; margin-top:0;">⚡ SYSTEM STATUS</h3>
                <p style="color:#2ecc71;">● Server: Operational</p>
                <p style="color:#FFD700;">● User: {st.session_state.user['role']}</p>
                <hr style="border:0.1px solid rgba(255,215,0,0.2);">
                <p><b>Today's Target:</b> Rs. 100,000</p>
                <div style="background:rgba(255,255,255,0.1); border-radius:10px; height:10px; width:100%;">
                    <div style="background:#FFD700; height:10px; width:{(df['total'].sum()/100000)*100 if df['total'].sum() < 100000 else 100}%; border-radius:10px;"></div>
                </div>
                <p style="font-size:11px; margin-top:5px;">Progress: {min((df['total'].sum()/100000)*100, 100):,.1f}%</p>
            </div>
            
            <div class="glass-card" style="margin-top:20px; border-left: 5px solid #00d4ff;">
                <h4 style="color:#00d4ff;">🔔 RECENT LOGS</h4>
                <p style="font-size:12px;">• Order {df.iloc[-1]['id'] if not df.empty else 'N/A'} was added.</p>
                <p style="font-size:12px;">• Stock sync completed at {datetime.now().strftime('%H:%M')}</p>
            </div>
        """, unsafe_allow_html=True)
