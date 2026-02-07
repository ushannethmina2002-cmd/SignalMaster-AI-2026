import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px

# =========================================================
# 1. ADVANCED UI & THEME CONFIGURATION
# =========================================================
st.set_page_config(page_title="HappyShop ERP ADVANCED", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* Professional Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.7) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid #FFD700;
    }

    .brand-title {
        font-size: 35px;
        font-weight: 800;
        color: #FFD700;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 10px rgba(255, 215, 0, 0.3);
    }

    /* Glassmorphism Cards */
    .data-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 215, 0, 0.1);
        margin-bottom: 20px;
    }

    .top-nav {
        display: flex;
        justify-content: space-between;
        padding: 15px;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        margin-bottom: 25px;
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        padding: 15px;
        border-radius: 10px;
        border-bottom: 3px solid #FFD700;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. ADVANCED DATA ENGINE (CSV DATABASE)
# =========================================================
def load_db(file, columns):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

# Initialize All Databases from Images
if "db" not in st.session_state:
    st.session_state.db = {
        "orders": load_db("orders.csv", ["id", "date", "name", "phone", "address", "prod", "qty", "total", "status", "staff"]),
        "stock": load_db("stock.csv", ["Code", "Product", "Qty", "Price", "Value", "Type"]),
        "expenses": load_db("expenses.csv", ["date", "type", "category", "amount", "note"]),
        "logistics": load_db("logistics.csv", ["order_id", "waybill", "courier", "status", "dispatch_date"]),
        "returns": load_db("returns.csv", ["order_id", "date", "reason", "status"]),
        "grn_po": load_db("grn_po.csv", ["type", "id", "date", "supplier", "items", "total", "status"])
    }

# Default Stock if empty
if st.session_state.db["stock"].empty:
    st.session_state.db["stock"] = pd.DataFrame([
        {"Code": "KHO-01", "Product": "Kasharaja Hair Oil", "Qty": 100, "Price": 2950, "Value": 295000, "Type": "Finished"},
        {"Code": "HNC-02", "Product": "Herbal Night Cream", "Qty": 50, "Price": 1800, "Value": 90000, "Type": "Finished"}
    ])

# =========================================================
# 3. SIDEBAR NAVIGATION (Mapped to your Images)
# =========================================================
with st.sidebar:
    st.markdown('<div class="brand-title">Happy Shop</div>', unsafe_allow_html=True)
    
    nav = st.radio("MAIN MENU", ["🏠 Dashboard", "📦 Inventory Control", "🛒 Sales & Leads", "🚚 Logistics", "💰 Finance", "🔄 Returns"])
    
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.write("Logged out")

# =========================================================
# 4. MODULES IMPLEMENTATION
# =========================================================

# --- DASHBOARD ---
if nav == "🏠 Dashboard":
    st.markdown('<div class="top-nav"><h3>🚀 Executive Overview</h3></div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Sales", f"Rs. {st.session_state.db['orders']['total'].sum():,.0f}")
    m2.metric("Pending Orders", len(st.session_state.db['orders'][st.session_state.db['orders']['status']=='pending']))
    m3.metric("Stock Value", f"Rs. {st.session_state.db['stock']['Value'].sum():,.0f}")
    m4.metric("Active Returns", len(st.session_state.db['returns']))
    
    fig = px.area(st.session_state.db['orders'], x='date', y='total', title="Sales Trend Analysis")
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig, use_container_width=True)

# --- INVENTORY CONTROL (Image 1, 2, 4) ---
elif nav == "📦 Inventory Control":
    tab1, tab2, tab3, tab4 = st.tabs(["View Stocks", "Stock Adjustment", "GRN & PO", "Product Management"])
    
    with tab1:
        st.subheader("📊 Current Inventory")
        st.dataframe(st.session_state.db["stock"], use_container_width=True)
        st.metric("Total Stock Items", st.session_state.db["stock"]["Qty"].sum())

    with tab2:
        st.subheader("⚙️ Stock Adjustment & Waste")
        with st.expander("Add Waste / Adjustment"):
            p_code = st.selectbox("Product Code", st.session_state.db["stock"]["Code"])
            adj_qty = st.number_input("Adjustment Qty (+/-)", value=0)
            if st.button("Apply Adjustment"):
                st.session_state.db["stock"].loc[st.session_state.db["stock"]["Code"] == p_code, "Qty"] += adj_qty
                st.success("Adjustment Updated!")

    with tab3:
        st.subheader("📝 GRN & Purchase Orders")
        col1, col2 = st.columns(2)
        with col1: st.button("➕ New GRN")
        with col2: st.button("📝 New PO")
        st.dataframe(st.session_state.db["grn_po"], use_container_width=True)

    with tab4:
        st.subheader("🎨 Product & Raw Items")
        with st.form("new_prod"):
            n_code = st.text_input("Product Code")
            n_name = st.text_input("Product Name")
            n_price = st.number_input("Selling Price", min_value=0)
            n_type = st.selectbox("Item Type", ["Finished Product", "Raw Material"])
            if st.form_submit_button("Create Product"):
                new_p = {"Code": n_code, "Product": n_name, "Qty": 0, "Price": n_price, "Value": 0, "Type": n_type}
                st.session_state.db["stock"] = pd.concat([st.session_state.db["stock"], pd.DataFrame([new_p])], ignore_index=True)
                st.success("New Item Added to System")

# --- SALES & LEADS (Image 3) ---
elif nav == "🛒 Sales & Leads":
    tab1, tab2, tab3 = st.tabs(["New Order / Lead", "Order Search", "Blacklist Manager"])
    
    with tab1:
        with st.form("order_form"):
            c_name = st.text_input("Customer Name")
            c_phone = st.text_input("Phone Number")
            c_prod = st.selectbox("Product", st.session_state.db["stock"]["Product"])
            c_qty = st.number_input("Qty", min_value=1)
            if st.form_submit_button("Submit Order"):
                price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == c_prod, "Price"].values[0]
                oid = f"ORD-{uuid.uuid4().hex[:5].upper()}"
                new_o = {"id": oid, "date": str(date.today()), "name": c_name, "phone": c_phone, "address": "N/A", "prod": c_prod, "qty": c_qty, "total": price*c_qty, "status": "pending", "staff": "Admin"}
                st.session_state.db["orders"] = pd.concat([st.session_state.db["orders"], pd.DataFrame([new_o])], ignore_index=True)
                st.success(f"Order {oid} Placed Successfully!")

    with tab2:
        st.subheader("🔍 Order History & Search")
        search_q = st.text_input("Search by Phone or ID")
        df_o = st.session_state.db["orders"]
        if search_q:
            df_o = df_o[df_o['phone'].contains(search_q) | df_o['id'].contains(search_q)]
        st.dataframe(df_o, use_container_width=True)

# --- LOGISTICS (Image 7) ---
elif nav == "🚚 Logistics":
    st.subheader("📦 Dispatch & Courier Management")
    col1, col2, col3 = st.columns(3)
    col1.button("🚢 Confirm Dispatch")
    col2.button("🏷️ Print Packing List")
    col3.button("🛰️ Search Waybills")
    
    st.dataframe(st.session_state.db["logistics"], use_container_width=True)

# --- FINANCE (Image 6) ---
elif nav == "💰 Finance":
    st.subheader("💸 Expense & POS Manager")
    with st.expander("➕ Add New Expense"):
        e_cat = st.selectbox("Category", ["Marketing", "Courier", "Salaries", "Utility"])
        e_amt = st.number_input("Amount", min_value=0)
        if st.button("Save Expense"):
            new_e = {"date": str(date.today()), "type": "General", "category": e_cat, "amount": e_amt, "note": ""}
            st.session_state.db["expenses"] = pd.concat([st.session_state.db["expenses"], pd.DataFrame([new_e])], ignore_index=True)
            st.success("Expense Recorded")
    
    st.dataframe(st.session_state.db["expenses"], use_container_width=True)

# --- RETURNS (Image 5) ---
elif nav == "🔄 Returns":
    st.subheader("🔙 Return Order Management")
    tab1, tab2 = st.tabs(["Add Return", "Pending Returns"])
    with tab1:
        rid = st.text_input("Order ID for Return")
        reason = st.selectbox("Reason", ["Damage", "Wrong Item", "Customer Refused"])
        if st.button("Process Return"):
            new_r = {"order_id": rid, "date": str(date.today()), "reason": reason, "status": "Pending"}
            st.session_state.db["returns"] = pd.concat([st.session_state.db["returns"], pd.DataFrame([new_r])], ignore_index=True)
            st.warning("Return Logged and Pending Approval")
    with tab2:
        st.dataframe(st.session_state.db["returns"], use_container_width=True)

# =========================================================
# 5. AUTO-SAVE ENGINE
# =========================================================
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
