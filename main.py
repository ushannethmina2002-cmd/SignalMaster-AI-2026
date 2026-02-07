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

    /* Search Bar in Header */
    .header-search {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        color: white;
        border-radius: 20px;
        padding: 5px 15px;
        outline: none;
    }

    /* Status Cards (Horizontal Labels from Image) */
    .status-badge {
        padding: 5px 15px;
        border-radius: 5px;
        font-size: 13px;
        font-weight: bold;
        color: white;
        margin-right: 5px;
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

    /* Metrics Styling */
    div[data-testid="stMetricValue"] { color: #00d4ff !important; font-size: 24px !important; }
    
    h1, h2, h3, p, label { color: white !important; font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. DATA ENGINE
# =========================================================
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename).to_dict("records")
    return []

# Session States
if "orders" not in st.session_state: st.session_state.orders = load_data("orders.csv")
if "stocks" not in st.session_state: st.session_state.stocks = {"Hair Oil": 150, "Cream": 85, "Face Wash": 110}
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
    # TOP HEADER (Image Features)
    # ---------------------------------------------------------
    st.markdown(f"""
        <div class="top-header">
            <span style="font-weight: bold; color: #00d4ff;">🚀 HAPPYSHOP ERP PRO</span>
            <input type="text" class="header-search" placeholder="Search Phone / Customer / Waybill">
            <span style="font-size:12px;">Welcome, <b>{st.session_state.user['name']}</b> | {date.today()}</span>
        </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SIDEBAR (Slim & Pinned as requested)
    # ---------------------------------------------------------
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>📊</h2>", unsafe_allow_html=True) # Logo Icon
        st.divider()
        # Radio buttons with icons for a clean look
        menu = st.radio("SELECT MODULE", [
            "🏠 Dashboard", 
            "🔍 Leads Search", 
            "🧾 Order Entry", 
            "🚚 Logistics",
            "📊 Stocks",
            "💰 Finance"
        ], label_visibility="collapsed")
        
        st.divider()
        if st.button("🔴 Logout"):
            st.session_state.user = None
            st.rerun()

    # ---------------------------------------------------------
    # MAIN CONTENT & ACTION PANEL
    # ---------------------------------------------------------
    col_main, col_action = st.columns([3.6, 1])

    with col_main:
        # --- MODULE: LEADS SEARCH (පින්තූරයේ තිබූ ආකාරයට) ---
        if menu == "🔍 Leads Search":
            st.subheader("🔍 Leads Search & Management")
            
            # Filter Row
            with st.container():
                f1, f2, f3, f4 = st.columns(4)
                f1.selectbox("Status", ["Any", "Pending", "Confirmed", "No Answer", "Fake"])
                f2.selectbox("Staff User", ["Any", "Admin", "Staff 01", "Staff 02"])
                f3.date_input("Start Date", date.today())
                f4.date_input("End Date", date.today())
                
                if st.button("Search Database", use_container_width=True):
                    st.toast("Filtering data...")

            st.divider()

            # Horizontal Status Counters (From Image)
            st.markdown("""
                <div style="display:flex; margin-bottom:20px;">
                    <span class="status-badge" style="background:#3498db;">Pending: 12</span>
                    <span class="status-badge" style="background:#2ecc71;">Ok: 45</span>
                    <span class="status-badge" style="background:#e67e22;">No Answer: 8</span>
                    <span class="status-badge" style="background:#e74c3c;">Rejected: 2</span>
                    <span class="status-badge" style="background:#95a5a6;">Fake: 1</span>
                </div>
            """, unsafe_allow_html=True)

            # Lead List Table
            df = pd.DataFrame(st.session_state.orders)
            if not df.empty:
                st.dataframe(df, use_container_width=True)
                
                # Action Buttons inside Expanders
                for idx, row in df.iterrows():
                    with st.expander(f"Action: {row['id']} - {row['name']} ({row['status']})"):
                        c1, c2, c3, c4 = st.columns(4)
                        if c1.button("Confirm ✅", key=f"c{idx}"):
                            st.session_state.orders[idx]['status'] = 'confirm'; save_data(pd.DataFrame(st.session_state.orders), "orders.csv"); st.rerun()
                        if c2.button("No Answer 📞", key=f"n{idx}"):
                            st.session_state.orders[idx]['status'] = 'noanswer'; save_data(pd.DataFrame(st.session_state.orders), "orders.csv"); st.rerun()
                        if c3.button("Fake 🚫", key=f"f{idx}"):
                            st.session_state.orders[idx]['status'] = 'fake'; save_data(pd.DataFrame(st.session_state.orders), "orders.csv"); st.rerun()
                        if c4.button("Delete 🗑️", key=f"d{idx}"):
                            st.session_state.orders.pop(idx); save_data(pd.DataFrame(st.session_state.orders), "orders.csv"); st.rerun()
            else:
                st.info("No leads found in the system.")

        # --- MODULE: DASHBOARD ---
        elif menu == "🏠 Dashboard":
            st.title("📈 Intelligence Overview")
            df_d = pd.DataFrame(st.session_state.orders)
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Leads", len(df_d))
            m2.metric("Revenue", f"LKR {df_d['total'].sum() if not df_d.empty else 0:,.0f}")
            m3.metric("Stock Items", sum(st.session_state.stocks.values()))
            if not df_d.empty:
                st.line_chart(df_d.groupby('date').size())

        # --- MODULE: ORDER ENTRY ---
        elif menu == "🧾 Order Entry":
            st.title("📝 New Lead Submission")
            with st.form("entry_form"):
                name = st.text_input("Customer Name")
                phone = st.text_input("Contact Number")
                prod = st.selectbox("Product SKU", list(st.session_state.stocks.keys()))
                qty = st.number_input("Quantity", 1)
                if st.form_submit_button("SAVE ORDER"):
                    oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.orders.append({"id": oid, "name": name, "phone": phone, "prod": prod, "qty": qty, "total": qty*1500, "status": "pending", "date": str(date.today())})
                    save_data(pd.DataFrame(st.session_state.orders), "orders.csv")
                    st.success("Lead Recorded!")

        # --- OTHER MODULES ---
        elif menu == "🚚 Logistics": st.title("🚚 Courier Management")
        elif menu == "📊 Stocks": st.table(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]))
        elif menu == "💰 Finance": st.title("💰 Financial Summary")

    # ---------------------------------------------------------
    # RIGHT ACTION PANEL
    # ---------------------------------------------------------
    with col_action:
        st.markdown(f"""
            <div class="glass-card">
                <h4 style="color:#00d4ff; font-size:16px;">⚡ QUICK CONSOLE</h4>
                <hr style="border:0.1px solid rgba(255,255,255,0.1);">
                <p style="font-size:13px;">Status: <b>System Live 🟢</b></p>
                <p style="font-size:13px;">User: <b>{st.session_state.user['role']}</b></p>
                <p style="font-size:13px;">Database: <b>Connected</b></p>
                <br>
                <p style="font-size:14px;">📝 <b>Internal Notes:</b></p>
                <textarea style="width:100%; height:120px; background:rgba(0,0,0,0.3); border:1px solid #333; color:white; border-radius:10px; padding:10px;"></textarea>
            </div>
            
            <div class="glass-card" style="border-left: 4px solid #ff4b4b;">
                <h4 style="color:#ff4b4b; font-size:15px;">🔔 SYSTEM ALERTS</h4>
                <p style="font-size:12px;">• 3 Leads are pending for 24h</p>
                <p style="font-size:12px;">• Low stock alert: Hair Oil</p>
            </div>
        """, unsafe_allow_html=True)

# =========================================================
# END OF CODE
# =========================================================
