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

    /* Sidebar Styling */
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
        text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.4);
    }

    /* Metric Cards Styling */
    .metric-row { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 25px; }
    .card {
        background: rgba(255, 255, 255, 0.04);
        padding: 20px; border-radius: 15px; border-top: 4px solid #FFD700;
        min-width: 140px; flex: 1; text-align: center;
        transition: 0.3s;
    }
    .card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.08); }
    .card h4 { margin: 0; font-size: 11px; color: #aaa; text-transform: uppercase; }
    .card h2 { margin: 8px 0; font-size: 28px; font-weight: 700; }

    /* Custom Status Borders */
    .border-confirmed { border-top-color: #00ff88; color: #00ff88; }
    .border-pending { border-top-color: #00d4ff; color: #00d4ff; }
    .border-noanswer { border-top-color: #ffee00; color: #ffee00; }
    .border-cancel { border-top-color: #ff4d4d; color: #ff4d4d; }
    .border-fake { border-top-color: #888888; color: #888888; }
    .border-hold { border-top-color: #cc00ff; color: #cc00ff; }

    .glass-panel {
        background: rgba(255, 255, 255, 0.03);
        padding: 20px; border-radius: 20px; 
        border: 1px solid rgba(255,255,255,0.1);
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. DATA ENGINE
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
        "blacklist": load_db("blacklist.csv", ["phone", "reason", "date"])
    }

# =========================================================
# 3. SIDEBAR NAVIGATION
# =========================================================
with st.sidebar:
    st.markdown('<div class="brand-title">HAPPY SHOP</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#FFD700; font-size:12px;">ULTIMATE ERP v4.0</p>', unsafe_allow_html=True)
    st.divider()
    
    main_nav = st.selectbox("GO TO MODULE", ["🏠 Executive Dashboard", "🛒 Sales & Leads Management", "🚚 Logistics & Shipping", "📦 Inventory Pro", "💰 Finance & Accounting", "🔄 Returns Hub"])
    
    st.markdown("---")
    # Sub-menus based on main selection
    if main_nav == "🛒 Sales & Leads Management":
        sub_nav = st.radio("Actions", ["Add New Lead", "Order History", "Pending Confirmations", "Blacklist Manager"])
    elif main_nav == "🚚 Logistics & Shipping":
        sub_nav = st.radio("Actions", ["Dispatch Center", "Waybill Search", "Courier Performance"])
    elif main_nav == "📦 Inventory Pro":
        sub_nav = st.radio("Actions", ["Stock Levels", "GRN / PO", "Adjustment"])
    else:
        sub_nav = "General View"

# =========================================================
# 4. DASHBOARD IMPLEMENTATION
# =========================================================
if main_nav == "🏠 Executive Dashboard":
    st.markdown('<h2 style="color:#FFD700;">🚀 Business Performance Analytics</h2>', unsafe_allow_html=True)
    
    df = st.session_state.db['orders']
    
    # පින්තූරයේ තිබූ විදිහට Status Metrics
    st.markdown(f"""
    <div class="metric-row">
        <div class="card"><h4>TOTAL LEADS</h4><h2>{len(df)}</h2></div>
        <div class="card border-confirmed"><h4>CONFIRMED</h4><h2>{len(df[df['status']=='confirm'])}</h2></div>
        <div class="card border-pending"><h4>PENDING</h4><h2>{len(df[df['status']=='pending'])}</h2></div>
        <div class="card border-noanswer"><h4>NO ANSWER</h4><h2>{len(df[df['status']=='noanswer'])}</h2></div>
        <div class="card border-cancel"><h4>CANCELLED</h4><h2>{len(df[df['status']=='cancel'])}</h2></div>
        <div class="card border-fake"><h4>FAKE</h4><h2>{len(df[df['status']=='fake'])}</h2></div>
        <div class="card border-hold"><h4>ON HOLD</h4><h2>{len(df[df['status']=='hold'])}</h2></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        if not df.empty:
            fig = px.area(df, x='date', y='total', title="Revenue Stream (LKR)", 
                          color_discrete_sequence=['#FFD700'], template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        if not df.empty:
            # Donut Chart for Conversion
            fig_pie = px.pie(df, names='status', title="Conversion Ratio", hole=0.5,
                             color_discrete_sequence=px.colors.sequential.YlOrBr)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- SALES & LEADS (Add Lead Feature) ---
elif main_nav == "🛒 Sales & Leads Management":
    st.title(f"🔍 {sub_nav}")
    if sub_nav == "Add New Lead":
        with st.form("lead_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Customer Name")
            phone = col1.text_input("Contact Number")
            address = col1.text_area("Full Address")
            
            prod = col2.selectbox("Product Selection", st.session_state.db["stock"]["Product"])
            qty = col2.number_input("Quantity", 1)
            status = col2.selectbox("Set Status", ["pending", "confirm", "noanswer", "hold", "fake", "cancel"])
            
            if st.form_submit_button("🔥 ADD LEAD TO SYSTEM"):
                price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Price"].values[0]
                new_id = f"HSHOP-{uuid.uuid4().hex[:4].upper()}"
                new_entry = {"id": new_id, "date": str(date.today()), "name": name, "phone": phone, 
                            "address": address, "prod": prod, "qty": qty, "total": price*qty, "status": status, "staff": "Admin"}
                st.session_state.db["orders"] = pd.concat([st.session_state.db["orders"], pd.DataFrame([new_entry])], ignore_index=True)
                st.success("Lead Added and Dashboard Updated!")

    else:
        st.dataframe(st.session_state.db["orders"], use_container_width=True)

# --- OTHERS ---
else:
    st.warning("This section is under professional UI enhancement...")
    st.info("System is ready for data input.")

# =========================================================
# 5. DATA SYNC
# =========================================================
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
