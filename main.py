import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px

# =========================================================
# 1. ADVANCED UI & THEME CONFIGURATION
# =========================================================
st.set_page_config(page_title="HappyShop ERP PRO", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: white;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.8) !important;
        backdrop-filter: blur(15px);
        border-right: 2px solid #FFD700;
    }

    .brand-title {
        font-size: 35px;
        font-weight: 800;
        color: #FFD700;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 10px rgba(255, 215, 0, 0.3);
    }

    /* Professional Metric Cards */
    .metric-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 20px;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 12px;
        border-left: 5px solid #FFD700;
        min-width: 160px;
        flex: 1;
        text-align: center;
    }

    .metric-card h4 { margin: 0; font-size: 14px; color: #ccc; }
    .metric-card h2 { margin: 5px 0; font-size: 24px; color: #FFD700; }

    /* Custom Status Colors */
    .status-confirmed { border-left-color: #2ecc71; }
    .status-pending { border-left-color: #3498db; }
    .status-noanswer { border-left-color: #f1c40f; }
    .status-cancel { border-left-color: #e74c3c; }
    .status-fake { border-left-color: #95a5a6; }
    .status-hold { border-left-color: #9b59b6; }

    .top-nav {
        background: rgba(255, 255, 255, 0.03);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid rgba(255, 215, 0, 0.2);
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. ADVANCED DATA ENGINE (CSV DATABASE)
# =========================================================
def load_db(file, columns):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

if "db" not in st.session_state:
    st.session_state.db = {
        "orders": load_db("orders.csv", ["id", "date", "name", "phone", "address", "prod", "qty", "total", "status", "staff"]),
        "stock": load_db("stock.csv", ["Code", "Product", "Qty", "Price", "Value", "Type"]),
        "expenses": load_db("expenses.csv", ["date", "type", "category", "amount", "note"]),
        "logistics": load_db("logistics.csv", ["order_id", "waybill", "courier", "status", "dispatch_date"]),
        "returns": load_db("returns.csv", ["order_id", "date", "reason", "status"]),
        "grn_po": load_db("grn_po.csv", ["type", "id", "date", "supplier", "items", "total", "status"])
    }

if st.session_state.db["stock"].empty:
    st.session_state.db["stock"] = pd.DataFrame([
        {"Code": "KHO-01", "Product": "Kasharaja Hair Oil", "Qty": 100, "Price": 2950, "Value": 295000, "Type": "Finished"},
        {"Code": "HNC-02", "Product": "Herbal Night Cream", "Qty": 50, "Price": 1800, "Value": 90000, "Type": "Finished"}
    ])

# =========================================================
# 3. SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown('<div class="brand-title">Happy Shop</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-size:12px;">ENTERPRISE RESOURCE PLANNING</p>', unsafe_allow_html=True)
    st.divider()
    
    nav = st.radio("MAIN MENU", ["🏠 Dashboard", "📦 Inventory Control", "🛒 Sales & Leads", "🚚 Logistics", "💰 Finance", "🔄 Returns"])
    
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.info("System Session Ended.")

# =========================================================
# 4. MODULES IMPLEMENTATION
# =========================================================

# --- DASHBOARD (BUSINESS ANALYTICS) ---
if nav == "🏠 Dashboard":
    st.markdown('<div class="top-nav"><h3>📊 Executive Business Dashboard</h3></div>', unsafe_allow_html=True)
    
    orders = st.session_state.db['orders']
    
    # දත්ත ගණනය කිරීම (Calculations)
    total_leads = len(orders)
    confirmed = len(orders[orders['status'] == 'confirm'])
    pending = len(orders[orders['status'] == 'pending'])
    no_answer = len(orders[orders['status'] == 'noanswer'])
    cancel = len(orders[orders['status'] == 'cancel'])
    fake = len(orders[orders['status'] == 'fake'])
    hold = len(orders[orders['status'] == 'hold'])
    
    # 1. Row of Status Metrics (From Images)
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-card"><h4>TOTAL LEADS</h4><h2>{total_leads}</h2></div>
        <div class="metric-card status-confirmed"><h4>CONFIRMED</h4><h2>{confirmed}</h2></div>
        <div class="metric-card status-pending"><h4>PENDING</h4><h2>{pending}</h2></div>
        <div class="metric-card status-noanswer"><h4>NO ANSWER</h4><h2>{no_answer}</h2></div>
        <div class="metric-card status-cancel"><h4>CANCEL</h4><h2>{cancel}</h2></div>
        <div class="metric-card status-fake"><h4>FAKE</h4><h2>{fake}</h2></div>
        <div class="metric-card status-hold"><h4>HOLD</h4><h2>{hold}</h2></div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Financial Metrics
    col_f1, col_f2, col_f3 = st.columns(3)
    col_f1.metric("Total Sales Revenue", f"Rs. {orders['total'].sum():,.0f}")
    col_f2.metric("Net Profit (Est.)", f"Rs. {orders['total'].sum() * 0.4:,.0f}", delta="40% Margin")
    col_f3.metric("Inventory Value", f"Rs. {st.session_state.db['stock']['Value'].sum():,.0f}")

    st.divider()

    # 3. Charts
    c1, c2 = st.columns([2, 1])
    with c1:
        if not orders.empty:
            fig = px.area(orders, x='date', y='total', title="📈 Revenue Growth Trend", 
                          color_discrete_sequence=['#FFD700'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        if not orders.empty:
            fig_pie = px.pie(orders, names='status', title="🎯 Order Conversion",
                             color_discrete_map={'confirm':'#2ecc71','pending':'#3498db','cancel':'#e74c3c'})
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig_pie, use_container_width=True)

# --- INVENTORY CONTROL ---
elif nav == "📦 Inventory Control":
    tab1, tab2, tab3, tab4 = st.tabs(["📊 View Stocks", "⚙️ Stock Adjustment", "📝 GRN & PO", "🎨 Product Management"])
    with tab1:
        st.subheader("Inventory Grid")
        st.dataframe(st.session_state.db["stock"], use_container_width=True)
    with tab2:
        p_code = st.selectbox("Select Product", st.session_state.db["stock"]["Code"])
        adj_qty = st.number_input("Adjustment Quantity", value=0)
        if st.button("Apply Adjustment"):
            st.session_state.db["stock"].loc[st.session_state.db["stock"]["Code"] == p_code, "Qty"] += adj_qty
            st.success("Updated Successfully!")
    with tab3:
        st.button("➕ Create New GRN")
        st.dataframe(st.session_state.db["grn_po"], use_container_width=True)
    with tab4:
        with st.form("prod_form"):
            st.text_input("Product Name")
            st.number_input("Unit Price")
            st.form_submit_button("Save Product")

# --- SALES & LEADS ---
elif nav == "🛒 Sales & Leads":
    tab1, tab2, tab3 = st.tabs(["➕ New Lead", "🔍 Order Search", "🚫 Blacklist"])
    with tab1:
        with st.form("sale_f"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Customer Name")
            phone = c1.text_input("Mobile")
            prod = c2.selectbox("Product", st.session_state.db["stock"]["Product"])
            qty = c2.number_input("Qty", 1)
            status = st.selectbox("Initial Status", ["pending", "confirm", "noanswer", "hold", "fake", "cancel"])
            if st.form_submit_button("Save Lead"):
                price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Price"].values[0]
                new_o = {"id": f"ORD-{uuid.uuid4().hex[:5].upper()}", "date": str(date.today()), "name": name, 
                         "phone": phone, "address": "", "prod": prod, "qty": qty, "total": price*qty, 
                         "status": status, "staff": "Admin"}
                st.session_state.db["orders"] = pd.concat([st.session_state.db["orders"], pd.DataFrame([new_o])], ignore_index=True)
                st.success("Lead Synced to Dashboard!")
    with tab2:
        st.dataframe(st.session_state.db["orders"], use_container_width=True)

# --- LOGISTICS ---
elif nav == "🚚 Logistics":
    st.title("Logistics Center")
    col1, col2 = st.columns(2)
    col1.button("🚢 Confirm Shipments")
    col2.button("🏷️ Print All Waybills")
    st.dataframe(st.session_state.db["logistics"], use_container_width=True)

# --- FINANCE ---
elif nav == "💰 Finance":
    st.title("Financial Overview")
    st.metric("Total Expenses", f"Rs. {st.session_state.db['expenses']['amount'].sum():,.0f}")
    st.dataframe(st.session_state.db["expenses"], use_container_width=True)

# --- RETURNS ---
elif nav == "🔄 Returns":
    st.title("Returns Management")
    st.dataframe(st.session_state.db["returns"], use_container_width=True)

# =========================================================
# 5. AUTO-SAVE ENGINE
# =========================================================
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
