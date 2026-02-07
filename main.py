import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px
import time

# =========================================================
# 1. LUXURY GLASS UI + SLIM SIDEBAR CONFIGURATION
# =========================================================
st.set_page_config(page_title="HappyShop ERP PREMIUM", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Background Image with Dark Overlay */
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.8)), 
                    url("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Sidebar Styling (Pinned & Professional) */
    [data-testid="stSidebar"] {
        background: rgba(10, 15, 30, 0.9) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        min-width: 100px !important;
    }

    /* Top Navigation Bar */
    .top-header {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        padding: 10px 25px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }

    /* Status Badges (Horizontal Labels from Image) */
    .status-badge {
        padding: 8px 18px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: bold;
        color: white;
        margin-right: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        display: inline-block;
    }

    /* Glass Panels */
    .glass-card {
        background: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }

    /* Table & Metric Design */
    .stDataFrame { background: white !important; border-radius: 10px; padding: 5px; }
    div[data-testid="stMetricValue"] { color: #00d4ff !important; font-size: 24px !important; }
    h1, h2, h3, p, label { color: white !important; font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. DATA ENGINE
# =========================================================
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename, default_cols):
    if os.path.exists(filename):
        return pd.read_csv(filename)
    return pd.DataFrame(columns=default_cols)

# Session States initialization
if "orders_df" not in st.session_state:
    st.session_state.orders_df = load_data("orders.csv", ["id", "date", "name", "phone", "address", "prod", "qty", "total", "status", "staff"])

if "stock_df" not in st.session_state:
    # පින්තූරයේ තිබූ දත්ත ඇසුරින් Default Stock
    initial_stock = [
        {"Product": "Kasharaja Hair Oil", "Code": "KHO-01", "Qty": 225, "Price": 2950},
        {"Product": "Herbal Night Cream", "Code": "HNC-02", "Qty": 85, "Price": 1800},
        {"Product": "Face Wash Gold", "Code": "FWG-03", "Qty": 110, "Price": 1200}
    ]
    st.session_state.stock_df = pd.DataFrame(initial_stock)

if "user" not in st.session_state: st.session_state.user = None

# =========================================================
# 3. LOGIN SYSTEM
# =========================================================
if st.session_state.user is None:
    st.markdown('<div style="text-align:center; margin-top:100px;">', unsafe_allow_html=True)
    st.title("🛡️ Enterprise Access")
    _, col, _ = st.columns([1, 1, 1])
    with col:
        u_id = st.text_input("User Access ID")
        u_pw = st.text_input("Security Key", type="password")
        if st.button("UNLOCK SYSTEM", use_container_width=True):
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
            <span style="font-weight: bold; color: #00d4ff; font-size: 20px;">🚀 HAPPYSHOP ERP PRO</span>
            <span style="font-size:12px;">Welcome, <b>{st.session_state.user['name']}</b> | {date.today()}</span>
        </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SIDEBAR
    # ---------------------------------------------------------
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>💎</h2>", unsafe_allow_html=True)
        st.divider()
        menu = st.radio("SELECT MODULE", [
            "🏠 Dashboard", 
            "🔍 Leads Search", 
            "🧾 Order Entry", 
            "🚚 Logistics",
            "📦 Stock Manager",
            "💰 Finance"
        ], label_visibility="collapsed")
        
        st.divider()
        if st.button("🔴 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # ---------------------------------------------------------
    # MAIN CONTENT & ACTION PANEL
    # ---------------------------------------------------------
    col_main, col_action = st.columns([3.6, 1])

    with col_main:
        
        # --- MODULE: DASHBOARD ---
        if menu == "🏠 Dashboard":
            st.title("📈 Intelligence Overview")
            df = st.session_state.orders_df
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Leads", len(df))
            m2.metric("Gross Revenue", f"LKR {df['total'].sum():,.0f}")
            m3.metric("Confirmed Orders", len(df[df['status'] == 'confirm']))
            m4.metric("Inventory Items", st.session_state.stock_df['Qty'].sum())
            
            if not df.empty:
                fig = px.area(df.groupby('date').size().reset_index(), x='date', y=0, title="Lead Inflow Trend")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
                st.plotly_chart(fig, use_container_width=True)

        # --- MODULE: LEADS SEARCH (All image features added) ---
        elif menu == "🔍 Leads Search":
            st.subheader("🔍 Advanced Lead Management")
            
            # Filters Row
            with st.container():
                f1, f2, f3, f4 = st.columns(4)
                s_filter = f1.selectbox("Filter Status", ["Any", "pending", "confirm", "noanswer", "fake", "hold"])
                u_filter = f2.selectbox("Staff User", ["Any", "Admin", "Staff 01", "Staff 02"])
                date_start = f3.date_input("From Date", date.today())
                date_end = f4.date_input("To Date", date.today())

            st.divider()

            # Horizontal Status Counters (From Image)
            df = st.session_state.orders_df
            st.markdown(f"""
                <div style="margin-bottom:20px;">
                    <span class="status-badge" style="background:#3498db;">Pending: {len(df[df['status']=='pending'])}</span>
                    <span class="status-badge" style="background:#2ecc71;">Confirmed: {len(df[df['status']=='confirm'])}</span>
                    <span class="status-badge" style="background:#e67e22;">No Answer: {len(df[df['status']=='noanswer'])}</span>
                    <span class="status-badge" style="background:#e74c3c;">Fake: {len(df[df['status']=='fake'])}</span>
                    <span class="status-badge" style="background:#9b59b6;">Hold: {len(df[df['status']=='hold'])}</span>
                </div>
            """, unsafe_allow_html=True)

            if not df.empty:
                # Table View
                st.dataframe(df, use_container_width=True)
                
                # Quick Action Section
                st.markdown("### ⚡ Quick Update Console")
                selected_id = st.selectbox("Select Record ID to update", df['id'].tolist())
                c1, c2, c3, c4 = st.columns(4)
                if c1.button("Confirm ✅", key="btn_conf"):
                    st.session_state.orders_df.loc[st.session_state.orders_df['id'] == selected_id, 'status'] = 'confirm'
                    save_data(st.session_state.orders_df, "orders.csv"); st.rerun()
                if c2.button("No Answer 📞", key="btn_na"):
                    st.session_state.orders_df.loc[st.session_state.orders_df['id'] == selected_id, 'status'] = 'noanswer'
                    save_data(st.session_state.orders_df, "orders.csv"); st.rerun()
                if c3.button("Fake 🚫", key="btn_fake"):
                    st.session_state.orders_df.loc[st.session_state.orders_df['id'] == selected_id, 'status'] = 'fake'
                    save_data(st.session_state.orders_df, "orders.csv"); st.rerun()
                if c4.button("Delete 🗑️", key="btn_del"):
                    st.session_state.orders_df = st.session_state.orders_df[st.session_state.orders_df['id'] != selected_id]
                    save_data(st.session_state.orders_df, "orders.csv"); st.rerun()
            else:
                st.info("No leads available in the database.")

        # --- MODULE: ORDER ENTRY ---
        elif menu == "🧾 Order Entry":
            st.title("📝 New Lead Submission")
            with st.form("entry_form"):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Customer Name *")
                    phone = st.text_input("Contact Number *")
                    address = st.text_area("Delivery Address")
                with c2:
                    prod = st.selectbox("Select Product", st.session_state.stock_df['Product'].tolist())
                    qty = st.number_input("Quantity", 1, 100)
                    staff = st.session_state.user['name']
                
                if st.form_submit_button("🚀 SYNC TO DATABASE"):
                    if name and phone:
                        price = st.session_state.stock_df.loc[st.session_state.stock_df['Product'] == prod, 'Price'].values[0]
                        oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                        new_row = {
                            "id": oid, "date": str(date.today()), "name": name, "phone": phone, 
                            "address": address, "prod": prod, "qty": qty, "total": qty * price, 
                            "status": "pending", "staff": staff
                        }
                        st.session_state.orders_df = pd.concat([st.session_state.orders_df, pd.DataFrame([new_row])], ignore_index=True)
                        save_data(st.session_state.orders_df, "orders.csv")
                        st.balloons(); st.success(f"Order {oid} recorded!")
                    else:
                        st.error("Fields with * are mandatory.")

        # --- MODULE: LOGISTICS ---
        elif menu == "🚚 Logistics":
            st.title("🚚 Dispatch & Logistics")
            df_log = st.session_state.orders_df[st.session_state.orders_df['status'] == 'confirm']
            if not df_log.empty:
                st.dataframe(df_log)
                if st.button("Download Waybill Sheet"): st.toast("Processing CSV...")
            else:
                st.info("No confirmed orders for logistics.")

        # --- MODULE: STOCK MANAGER (Image features added) ---
        elif menu == "📦 Stock Manager":
            st.title("📦 Inventory Control Center")
            tab1, tab2 = st.tabs(["📊 Stock Summary", "⚙️ Adjustment Console"])
            
            with tab1:
                st.dataframe(st.session_state.stock_df, use_container_width=True)
            
            with tab2:
                st.write("Edit quantities directly below and Save:")
                edited_stock = st.data_editor(st.session_state.stock_df, num_rows="dynamic", key="stock_editor")
                if st.button("Save Changes"):
                    st.session_state.stock_df = edited_stock
                    st.success("Inventory updated successfully!")

        # --- MODULE: FINANCE ---
        elif menu == "💰 Finance":
            st.title("💰 Revenue Insights")
            if st.session_state.user['role'] == "OWNER":
                df_fin = st.session_state.orders_df
                c1, c2 = st.columns(2)
                c1.metric("Total Outstanding", f"LKR {df_fin['total'].sum():,.2f}")
                c2.metric("Confirmed Sales", f"LKR {df_fin[df_fin['status'] == 'confirm']['total'].sum():,.2f}")
                
                if not df_fin.empty:
                    fig_pie = px.pie(df_fin, values='total', names='prod', title="Sales Distribution by SKU")
                    fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white")
                    st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.error("Admin permissions required.")

    # ---------------------------------------------------------
    # RIGHT ACTION PANEL
    # ---------------------------------------------------------
    with col_action:
        st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:#00d4ff; font-size:16px;">⚡ QUICK CONSOLE</h4>
                <hr style="border:0.1px solid rgba(255,255,255,0.1);">
                <p style="font-size:12px;">System: <b>Cloud Connected 🟢</b></p>
                <p style="font-size:12px;">Role: <b>{st.session_state.user['role']}</b></p>
                <br>
                <p style="font-size:14px;">📝 <b>Notes:</b></p>
                <textarea style="width:100%; height:150px; background:rgba(0,0,0,0.3); border:1px solid #333; color:white; border-radius:10px; padding:10px;"></textarea>
            </div>
            
            <div class="glass-card" style="border-left: 4px solid #ff4b4b;">
                <h4 style="color:#ff4b4b; font-size:15px;">🔔 ALERTS</h4>
                <p style="font-size:12px;">• {len(st.session_state.orders_df[st.session_state.orders_df['status']=='pending'])} Leads need attention</p>
                <p style="font-size:12px;">• Check stock levels for 'Face Wash'</p>
            </div>
        """, unsafe_allow_html=True)
