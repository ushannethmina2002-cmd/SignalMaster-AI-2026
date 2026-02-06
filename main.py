import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop Official ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. CSS FOR PROFESSIONAL UI ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #111 !important; border-right: 1px solid #333; }
    .sidebar-title { color: #e67e22; font-size: 26px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    
    /* Status Header Cards */
    .status-card-container { display: flex; gap: 10px; margin-bottom: 20px; }
    .status-card {
        padding: 12px 20px; border-radius: 8px; font-weight: bold; color: black; 
        display: flex; align-items: center; justify-content: center; min-width: 140px;
    }
    .bg-green { background-color: #2ecc71; }
    .bg-orange { background-color: #f39c12; }
    .bg-red { background-color: #e74c3c; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if 'user' not in st.session_state: st.session_state.user = None
if 'orders' not in st.session_state:
    st.session_state.orders = [
        {"id": 1, "order_id": "HS-1384", "customer": "Sharanga Malaka", "phone": "0702710550", "status": "pending"}
    ]

# --- 4. AUTHENTICATION ---
if st.session_state.user is None:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<br><br><h2 style='text-align:center;'>Happy Shop Login</h2>", unsafe_allow_html=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("LOGIN"):
            if u == "happyshop@gmail.com" and p == "VLG0005":
                st.session_state.user = "Admin"
                st.rerun()
            else: st.error("Invalid Credentials!")
else:
    # --- 5. SIDEBAR ---
    with st.sidebar:
        st.markdown(f"<div class='sidebar-title'>Happy Shop</div>", unsafe_allow_html=True)
        menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "↩️ Return", "📊 Stocks", "🏷️ Products"])
        
        sub_menu = "Default"
        if menu == "🧾 Orders":
            sub_menu = st.radio("Order Actions", ["New Order", "View Lead", "Order Search", "Import Lead", "Order History"])
        elif menu == "🚚 Shipped Items":
            sub_menu = st.radio("Shipped Actions", ["Shipped List", "Courier Feedback", "Search Waybills"])
        elif menu == "📊 Stocks":
            sub_menu = st.radio("Stock Actions", ["View Stocks", "Stock Adjustment"])
        
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # --- 6. TOP STATUS BAR ---
    st.markdown(f"""
        <div class="status-card-container">
            <div class="status-card bg-green">Pending | {len(st.session_state.orders)}</div>
            <div class="status-card bg-orange">Ok | 0</div>
            <div class="status-card bg-red">No Answer | 0</div>
        </div>
    """, unsafe_allow_html=True)

    # --- 7. CONTENT ---
    if menu == "🏠 Dashboard":
        st.subheader("Business Summary")
        st.info("Welcome to Happy Shop Management System. All systems operational.")

    elif menu == "🧾 Orders" and sub_menu == "View Lead":
        st.subheader("Interactive Order Status System")

        # --- HTML/CSS/JS INTEGRATION ---
        # Generating rows dynamically from session state
        rows_html = ""
        for order in st.session_state.orders:
            rows_html += f"""
            <tr class="status-{order['status']}" id="row{order['id']}">
              <td>{order['order_id']}</td>
              <td>{order['customer']}</td>
              <td>{order['phone']}</td>
              <td><span class="badge {order['status']}" id="status{order['id']}">{order['status'].capitalize()}</span></td>
              <td class="actions">
                <button class="btn-confirm" onclick="setStatus({order['id']},'confirm')">✔</button>
                <button class="btn-hold" onclick="setStatus({order['id']},'hold')">⏸</button>
                <button class="btn-noanswer" onclick="setStatus({order['id']},'noanswer')">☎✖</button>
                <button class="btn-cancel" onclick="setStatus({order['id']},'cancel')">✖</button>
                <button class="btn-fake" onclick="setStatus({order['id']},'fake')">⚠</button>
              </td>
            </tr>
            """

        html_code = f"""
        <!DOCTYPE html>
        <html>
        <head>
        <style>
            table{{ width:100%; border-collapse:collapse; background:#fff; font-family: sans-serif; }}
            th, td{{ padding:12px; border:1px solid #ddd; text-align:left; font-size:14px; color: #333; }}
            th{{ background:#222; color:#fff; }}
            .status-pending{{ background:#fff; }}
            .status-confirm{{ background:#d4edda; }}
            .status-hold{{ background:#fff3cd; }}
            .status-noanswer{{ background:#f8d7da; }}
            .status-cancel{{ background:#f5c6cb; }}
            .status-fake{{ background:#d6d8db; }}
            .actions button{{ border:none; padding:8px 12px; margin:2px; cursor:pointer; border-radius:4px; font-weight:bold; }}
            .btn-confirm{{ background:#28a745; color:#fff; }}
            .btn-hold{{ background:#ffc107; }}
            .btn-noanswer{{ background:#dc3545; color:#fff; }}
            .btn-cancel{{ background:#bd2130; color:#fff; }}
            .btn-fake{{ background:#6c757d; color:#fff; }}
            .badge{{ padding:5px 10px; border-radius:4px; font-size:12px; color:#fff; text-transform: uppercase; }}
            .pending{{ background:#6c757d; }}
            .confirm{{ background:#28a745; }}
            .hold{{ background:#ffc107; color:#000; }}
            .noanswer{{ background:#dc3545; }}
            .cancel{{ background:#bd2130; }}
            .fake{{ background:#343a40; }}
        </style>
        </head>
        <body>
        <table>
            <thead>
                <tr>
                    <th>Order ID</th><th>Customer</th><th>Phone</th><th>Status</th><th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        <script>
            function setStatus(id, status){{
                const row = document.getElementById("row"+id);
                const badge = document.getElementById("status"+id);
                row.className = "status-" + status;
                badge.className = "badge " + status;
                badge.innerText = status.toUpperCase();
            }}
        </script>
        </body>
        </html>
        """
        components.html(html_code, height=400, scrolling=True)

    elif menu == "🧾 Orders" and sub_menu == "New Order":
        st.subheader("Add New Lead")
        with st.form("new_order"):
            c_name = st.text_input("Customer Name")
            c_phone = st.text_input("Phone Number")
            if st.form_submit_button("Save Order"):
                new_id = len(st.session_state.orders) + 1
                st.session_state.orders.append({
                    "id": new_id, "order_id": f"HS-{1384+new_id}", 
                    "customer": c_name, "phone": c_phone, "status": "pending"
                })
                st.success("Order saved!")
                st.rerun()

    else:
        st.subheader(f"{menu} > {sub_menu}")
        st.write("Section is ready for data entry.")
