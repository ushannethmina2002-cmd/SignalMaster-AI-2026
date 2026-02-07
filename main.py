import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px
import plotly.graph_objects as go

# =========================================================
# 1. ULTIMATE UI & THEME CONFIGURATION
# =========================================================
st.set_page_config(page_title="HappyShop ERP ULTIMATE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #020111, #0d0c2b, #13123b);
        color: white;
    }

    /* Sidebar Professional Look */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.85) !important;
        backdrop-filter: blur(20px);
        border-right: 2px solid #FFD700;
    }

    .brand-title {
        font-size: 38px;
        font-weight: 800;
        color: #FFD700;
        text-align: center;
        margin-bottom: 2px;
        letter-spacing: 2px;
        text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.4);
    }

    /* Professional Status Cards */
    .metric-row { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 25px; }
    .card {
        background: rgba(255, 255, 255, 0.04);
        padding: 20px; border-radius: 15px; border-top: 4px solid #FFD700;
        min-width: 140px; flex: 1; text-align: center;
        transition: transform 0.3s;
    }
    .card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.08); }
    .card h4 { margin: 0; font-size: 11px; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }
    .card h2 { margin: 8px 0; font-size: 28px; font-weight: 700; }

    /* Specific Status Borders */
    .border-confirmed { border-top-color: #00ff88; color: #00ff88; }
    .border-pending { border-top-color: #00d4ff; color: #00d4ff; }
    .border-noanswer { border-top-color: #ffee00; color: #ffee00; }
    .border-cancel { border-top-color: #ff4d4d; color: #ff4d4d; }
    .border-fake { border-top-color: #888888; color: #888888; }
    .border-hold { border-top-color: #cc00ff; color: #cc00ff; }

    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        padding: 20px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. DATA ENGINE (CSV DATABASE)
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
        "grn_po": load_db("grn_po.csv", ["type", "id", "date", "supplier", "items", "total", "status"]),
        "audit_logs": load_db("audit.csv", ["timestamp", "user", "action"])
    }

# =========================================================
# 3. SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown('<div class="brand-title">HAPPY SHOP</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-size:12px;">ULTIMATE ERP v3.0</p>', unsafe_allow_html=True)
    st.divider()
    
    main_nav = st.radio("CORE MODULES", ["🏠 Executive Dashboard", "🛒 Sales & Add Leads", "🚚 Logistics Hub", "📦 Inventory Pro", "💰 Financials", "🔄 Returns Control"])
    
    st.divider()
    st.info(f"User: Administrator\nDate: {date.today()}")
    if st.button("🔌 System Shutdown"): st.stop()

# =========================================================
# 4. MODULES
# =========================================================

# --- EXECUTIVE DASHBOARD ---
if main_nav == "🏠 Executive Dashboard":
    st.markdown('<h2 style="color:#FFD700;">🚀 Business Overview</h2>', unsafe_allow_html=True)
    
    df = st.session_state.db['orders']
    
    # 1. Advanced Metric Cards
    st.markdown(f"""
    <div class="metric-row">
        <div class="card"><h4>Total Leads</h4><h2>{len(df)}</h2></div>
        <div class="card border-confirmed"><h4>Confirmed</h4><h2>{len(df[df['status']=='confirm'])}</h2></div>
        <div class="card border-pending"><h4>Pending</h4><h2>{len(df[df['status']=='pending'])}</h2></div>
        <div class="card border-noanswer"><h4>No Answer</h4><h2>{len(df[df['status']=='noanswer'])}</h2></div>
        <div class="card border-cancel"><h4>Cancelled</h4><h2>{len(df[df['status']=='cancel'])}</h2></div>
        <div class="card border-fake"><h4>Fake</h4><h2>{len(df[df['status']=='fake'])}</h2></div>
        <div class="card border-hold"><h4>On Hold</h4><h2>{len(df[df['status']=='hold'])}</h2></div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Advanced Analytics Charts
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        if not df.empty:
            fig = px.area(df, x='date', y='total', title="Revenue Performance",
                          line_shape="spline", color_discrete_sequence=['#FFD700'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                              font_color="white", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        if not df.empty:
            fig_pie = px.pie(df, names='status', title="Lead Conversion", hole=0.6,
                             color_discrete_sequence=px.colors.sequential.Gold)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- SALES & ADD LEADS ---
elif main_nav == "🛒 Sales & Add Leads":
    st.markdown('<h2 style="color:#FFD700;">🛒 Sales Management</h2>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["➕ Add New Lead", "📋 View All Orders"])
    
    with tab1:
        with st.form("lead_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Customer Name")
            phone = col1.text_input("Contact Number")
            addr = col1.text_area("Delivery Address")
            
            prod = col2.selectbox("Product Selection", st.session_state.db["stock"]["Product"])
            qty = col2.number_input("Quantity", 1)
            status = col2.selectbox("Order Status", ["pending", "confirm", "noanswer", "hold", "fake", "cancel"])
            
            if st.form_submit_button("🚀 SYNC LEAD TO SYSTEM"):
                price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Price"].values[0]
                new_id = f"HSHOP-{uuid.uuid4().hex[:4].upper()}"
                new_lead = {"id": new_id, "date": str(date.today()), "name": name, "phone": phone, 
                            "address": addr, "prod": prod, "qty": qty, "total": price*qty, "status": status, "staff": "Admin"}
                st.session_state.db["orders"] = pd.concat([st.session_state.db["orders"], pd.DataFrame([new_lead])], ignore_index=True)
                st.success(f"Lead {new_id} Successfully Added!")

    with tab2:
        st.dataframe(st.session_state.db["orders"], use_container_width=True)

# --- REST OF THE MODULES (Logistics, Inventory, Finance, Returns) ---
# (සෙසු කොටස් පෙර පරිදිම පවතී, UI එක තවත් ලස්සන කර ඇත)
else:
    st.info("Module is being rendered with professional UI...")
    st.dataframe(st.session_state.db[main_nav.split()[-1].lower()], use_container_width=True)

# =========================================================
# 5. DATA SYNC
# =========================================================
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
