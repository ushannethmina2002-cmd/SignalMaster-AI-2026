import streamlit as st
import pandas as pd
from datetime import datetime, date
import streamlit.components.v1 as components

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Pro ERP", layout="wide")

# --- 2. DATA & SESSION STATE ---
if 'orders' not in st.session_state:
    st.session_state.orders = [
        {"id": 1, "order_id": "HS-1001", "customer": "Sharanga Malaka", "phone": "0702710550", "status": "pending"}
    ]

# --- 3. LOGIC FOR STATUS UPDATES (From Table Buttons) ---
# Query params හරහා එන දත්ත වලින් status එක update කිරීම
query_params = st.query_params
if "update_id" in query_params and "new_status" in query_params:
    u_id = int(query_params["update_id"])
    u_status = query_params["new_status"]
    
    for order in st.session_state.orders:
        if order['id'] == u_id:
            order['status'] = u_status
    
    # Query params අයින් කරලා පිරිසිදු කරනවා (නැත්නම් දිගටම refresh වෙනවා)
    st.query_params.clear()
    st.rerun()

# --- 4. HELPER FUNCTIONS ---
def get_count(status_name):
    if status_name == "total": return len(st.session_state.orders)
    return len([o for o in st.session_state.orders if o['status'] == status_name])

# --- 5. CSS FOR COLORS & UI ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    .metric-container { display: flex; gap: 10px; justify-content: center; margin-bottom: 25px; }
    .m-card {
        padding: 15px; border-radius: 10px; text-align: center; min-width: 130px;
        color: white; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    /* Specific Colors based on your request */
    .bg-pending { background: #6c757d; }  /* අළු පාට */
    .bg-confirm { background: #28a745; }  /* කොළ පාට */
    .bg-noanswer { background: #ffc107; color: black; } /* කහ පාට */
    .bg-cancel { background: #dc3545; }   /* රතු පාට */
    .bg-total { background: #007bff; }
    .val { font-size: 24px; display: block; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MENU", ["🏠 Dashboard", "🧾 Orders"])
    sub_menu = "View Lead"
    if menu == "🧾 Orders":
        sub_menu = st.radio("Actions", ["View Lead", "Add Lead"])

# --- 7. TOP METRIC CARDS ---
# Dashboard හෝ View Lead පිටුවලදී පමණක් පෙන්වයි
if menu == "🏠 Dashboard" or sub_menu == "View Lead":
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL/HOLD<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-total">TOTAL LEADS<span class="val">{get_count('total')}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 8. PAGE CONTENT ---
if sub_menu == "Add Lead":
    st.subheader("Add New Lead")
    with st.form("add_form"):
        name = st.text_input("Customer Name")
        phone = st.text_input("Phone Number")
        if st.form_submit_button("Save"):
            new_id = len(st.session_state.orders) + 1
            st.session_state.orders.append({"id": new_id, "order_id": f"HS-{1000+new_id}", "customer": name, "phone": phone, "status": "pending"})
            st.rerun()

elif sub_menu == "View Lead":
    st.subheader("Leads Management Table")
    
    rows_html = ""
    for order in st.session_state.orders:
        # පේළියේ පසුබිම් වර්ණය Status එක අනුව වෙනස් කිරීම
        row_style = ""
        if order['status'] == 'confirm': row_style = "background: rgba(40,167,69,0.15);"
        elif order['status'] == 'noanswer': row_style = "background: rgba(255,193,7,0.15);"
        elif order['status'] == 'cancel': row_style = "background: rgba(220,53,69,0.15);"

        rows_html += f"""
        <tr style="{row_style}">
            <td>{order['order_id']}</td>
            <td>{order['customer']}</td>
            <td>{order['phone']}</td>
            <td><span class="badge {order['status']}">{order['status'].upper()}</span></td>
            <td>
                <a href="?update_id={order['id']}&new_status=confirm" target="_self"><button class="btn-s btn-confirm">✔</button></a>
                <a href="?update_id={order['id']}&new_status=noanswer" target="_self"><button class="btn-s btn-noanswer">☎</button></a>
                <a href="?update_id={order['id']}&new_status=cancel" target="_self"><button class="btn-s btn-cancel">✖</button></a>
            </td>
        </tr>
        """

    html_table = f"""
    <html><head><style>
        table {{ width:100%; border-collapse:collapse; color:white; font-family:sans-serif; background:#161b22; }}
        th, td {{ padding:12px; border:1px solid #30363d; text-align:left; }}
        th {{ background:#21262d; color:#ffa500; font-size:12px; }}
        .badge {{ padding:4px 8px; border-radius:5px; font-size:10px; font-weight:bold; }}
        .pending {{ background:#6c757d; }} .confirm {{ background:#28a745; }} .noanswer {{ background:#ffc107; color:black; }} .cancel {{ background:#dc3545; }}
        .btn-s {{ border:none; padding:8px 12px; border-radius:4px; cursor:pointer; font-weight:bold; color:white; margin-right:5px; text-decoration:none; }}
        .btn-confirm {{ background:#28a745; }} .btn-noanswer {{ background:#ffc107; color:black; }} .btn-cancel {{ background:#dc3545; }}
    </style></head>
    <body>
        <table>
            <thead><tr><th>ID</th><th>Customer</th><th>Phone</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </body></html>
    """
    components.html(html_table, height=500, scrolling=True)
