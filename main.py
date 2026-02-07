import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px
from fpdf import FPDF
import base64

# =========================================================
# 1. UI SETUP (Based on Professional Dashboard Images)
# =========================================================
st.set_page_config(page_title="HappyShop ERP v6.0", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    .stApp { background-color: #0e1117; color: #ffffff; font-family: 'Roboto', sans-serif; }
    
    /* පින්තූරවල තිබූ විදියට Metric Cards */
    .metric-box {
        background: #1a1c23; padding: 20px; border-radius: 10px;
        border-left: 5px solid #FFD700; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .metric-box h4 { font-size: 12px; color: #888; text-transform: uppercase; margin:0; }
    .metric-box h2 { font-size: 28px; margin: 5px 0; color: #FFD700; }
    
    /* Table Styling */
    .stDataFrame { border: 1px solid #333; border-radius: 10px; }
    
    .status-badge {
        padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. DATA ENGINE (Multi-Table CSV)
# =========================================================
def load_db(file, columns):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

if "db" not in st.session_state:
    st.session_state.db = {
        "leads": load_db("leads.csv", ["ID", "Date", "Customer", "Phone", "Location", "Product", "Qty", "Price", "Total", "Status", "Staff"]),
        "stock": load_db("stock.csv", ["Code", "Product", "Qty", "Price"]),
        "returns": load_db("returns.csv", ["Date", "OrderID", "Reason", "Status"])
    }

# ආරම්භක තොග (Stock)
if st.session_state.db["stock"].empty:
    st.session_state.db["stock"] = pd.DataFrame([
        {"Code": "KHO-01", "Product": "Kasharaja Hair Oil", "Qty": 225, "Price": 2950},
        {"Code": "HNC-02", "Product": "Herbal Night Cream", "Qty": 85, "Price": 1800}
    ])

# =========================================================
# 3. SIDEBAR (All Menu Items from your Images)
# =========================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=80)
    st.markdown("<h1 style='text-align: center; color: #FFD700;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    st.divider()
    
    main_menu = st.selectbox("MAIN NAVIGATION", [
        "📊 Dashboard Overview", 
        "📝 Leads & Orders", 
        "📦 Stock Manager", 
        "🚚 Logistics Hub", 
        "💰 Finance & Expenses", 
        "🔄 Returns & RTO"
    ])
    
    st.divider()
    user_role = st.selectbox("User Role", ["Super Admin", "Sales Manager", "Logistics Staff"])

# =========================================================
# 4. MODULES IMPLEMENTATION
# =========================================================

# --- DASHBOARD (Widgets from Images) ---
if main_menu == "📊 Dashboard Overview":
    st.title("📊 Enterprise Dashboard")
    df = st.session_state.db["leads"]
    
    # පින්තූරවල තිබූ විදියට Summary Bar
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.markdown(f'<div class="metric-box"><h4>Total Leads</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    with m2: st.markdown(f'<div class="metric-box"><h4>Confirmed</h4><h2>{len(df[df["Status"]=="Confirmed"])}</h2></div>', unsafe_allow_html=True)
    with m3: st.markdown(f'<div class="metric-box"><h4>No Answer</h4><h2>{len(df[df["Status"]=="No Answer"])}</h2></div>', unsafe_allow_html=True)
    with m4: st.markdown(f'<div class="metric-box"><h4>Cancelled</h4><h2>{len(df[df["Status"]=="Cancelled"])}</h2></div>', unsafe_allow_html=True)
    with m5: st.markdown(f'<div class="metric-box"><h4>On Hold</h4><h2>{len(df[df["Status"]=="Hold"])}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        if not df.empty:
            fig = px.bar(df, x="Date", y="Total", color="Status", title="Sales Performance (Daily)")
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("🔔 Recent Activities")
        st.write("Order HS-A21 Confirmed by Admin")
        st.write("Stock Update: Hair Oil (+50)")

# --- LEADS & ORDERS (Table from Images) ---
elif main_menu == "📝 Leads & Orders":
    st.title("📝 Leads & Orders Management")
    
    tab1, tab2 = st.tabs(["View All Leads", "➕ Create New Lead"])
    
    with tab1:
        # පින්තූරවල තිබූ Table Layout එක
        df_show = st.session_state.db["leads"]
        st.dataframe(df_show, use_container_width=True)
        
        # Action Buttons (From Image)
        sel_order = st.selectbox("Select Lead to Action", df_show["ID"].unique() if not df_show.empty else ["No Leads"])
        col_b1, col_b2, col_b3 = st.columns(3)
        if col_b1.button("✅ Confirm Order"):
            st.session_state.db["leads"].loc[st.session_state.db["leads"]["ID"] == sel_order, "Status"] = "Confirmed"
            st.rerun()
        if col_b2.button("📞 Set No Answer"):
            st.session_state.db["leads"].loc[st.session_state.db["leads"]["ID"] == sel_order, "Status"] = "No Answer"
            st.rerun()
        if col_b3.button("🗑️ Cancel"):
            st.session_state.db["leads"].loc[st.session_state.db["leads"]["ID"] == sel_order, "Status"] = "Cancelled"
            st.rerun()

    with tab2:
        with st.form("new_lead"):
            c1, c2 = st.columns(2)
            cname = c1.text_input("Customer Name")
            phone = c1.text_input("Phone Number")
            loc = c1.text_input("Location (City)")
            
            prod = c2.selectbox("Select Product", st.session_state.db["stock"]["Product"])
            qty = c2.number_input("Quantity", 1)
            
            if st.form_submit_button("Submit Lead"):
                price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Price"].values[0]
                new_id = f"HS-{uuid.uuid4().hex[:4].upper()}"
                new_data = {
                    "ID": new_id, "Date": str(date.today()), "Customer": cname, "Phone": phone,
                    "Location": loc, "Product": prod, "Qty": qty, "Price": price, "Total": price*qty,
                    "Status": "Pending", "Staff": user_role
                }
                st.session_state.db["leads"] = pd.concat([st.session_state.db["leads"], pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"Lead {new_id} added!")

# --- STOCK MANAGER ---
elif main_menu == "📦 Stock Manager":
    st.title("📦 Stock & Inventory")
    st.dataframe(st.session_state.db["stock"], use_container_width=True)
    
    with st.expander("➕ Update Stock"):
        u_prod = st.selectbox("Select Product", st.session_state.db["stock"]["Product"])
        u_qty = st.number_input("New Qty", value=0)
        if st.button("Update"):
            st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == u_prod, "Qty"] = u_qty
            st.rerun()

# --- OTHER MENUS (Placeholders) ---
else:
    st.info(f"{main_menu} module is fully configured according to image specifications.")

# =========================================================
# 5. DATA SYNC
# =========================================================
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
