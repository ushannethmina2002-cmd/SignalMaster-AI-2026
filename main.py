import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE ---
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 3. PROFESSIONAL CSS (PRINT & UI) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    /* Metric Cards */
    .metric-container { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card {
        padding: 15px; border-radius: 12px; text-align: center; min-width: 140px;
        color: white; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .bg-pending { background: #6c757d; } 
    .bg-confirm { background: #28a745; } 
    .bg-noanswer { background: #ffc107; color: black; } 
    .bg-cancel { background: #dc3545; }
    .bg-shipped { background: #007bff; }
    .val { font-size: 28px; display: block; margin-top: 5px; }

    /* Print Formatting */
    @media print {
        body * { visibility: hidden; }
        .print-section, .print-section * { visibility: visible; }
        .print-section { position: absolute; left: 0; top: 0; width: 100%; color: black !important; background: white !important; padding: 30px; border: 1px solid #000; }
        .no-print { display: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR (ALL YOUR REQUESTED MENUS) ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    sub_menu = ""
    if menu == "🧾 Orders":
        sub_menu = st.radio("Order Actions", ["New Order", "Pending Orders", "Order Search", "View Lead", "Add Lead", "Order History"])
    elif menu == "🚚 Shipped Items":
        sub_menu = st.radio("Shipping Actions", ["Ship", "Shipped List", "Print Waybills"])
    elif menu == "📦 GRN": sub_menu = "GRN List"
    elif menu == "💰 Expense": sub_menu = "View Expenses"
    elif menu == "📊 Stocks": sub_menu = "View Stocks"

# --- 5. DASHBOARD METRICS ---
def get_count(s): return len([o for o in st.session_state.orders if o['status'] == s])

if menu == "🏠 Dashboard" or "Lead" in sub_menu or "Order" in sub_menu:
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-shipped">SHIPPED<span class="val">{get_count('shipped')}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 6. NEW ORDER FORM (FULL DETAILS) ---
if sub_menu in ["New Order", "Add Lead"]:
    st.subheader("📝 Customer & Order Entry Form")
    with st.form("order_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Customer Name *")
            addr = st.text_area("Address *")
            city = st.text_input("City")
            phone = st.text_input("Phone Number *")
        with c2:
            prod = st.selectbox("Product", ["Kesharaja Hair Oil", "Crown 1", "Kalkaya"])
            amt = st.number_input("Sale Amount", value=2950.0)
            ship = st.number_input("Delivery Charge", value=350.0)
            note = st.text_area("Order Note")
        
        if st.form_submit_button("SAVE ORDER"):
            if name and phone:
                st.session_state.orders.append({
                    "id": f"HS-{len(st.session_state.orders)+101}",
                    "name": name, "phone": phone, "addr": addr, "prod": prod,
                    "total": amt + ship, "status": "pending", "date": str(date.today())
                })
                st.success("Order Saved!")
                st.rerun()

# --- 7. ORDER TRACKING (SEARCH) ---
elif sub_menu == "Order Search":
    st.subheader("🔍 Order Tracking")
    q = st.text_input("Enter Phone Number")
    if q:
        res = [o for o in st.session_state.orders if q in o['phone']]
        if res:
            for o in res:
                st.info(f"Order {o['id']} is currently: {o['status'].upper()}")
        else: st.error("No order found!")

# --- 8. FIX: PRINTING WAYBILL ---
elif sub_menu == "Ship":
    st.subheader("🚚 Ready for Dispatch")
    confirmed = [o for o in st.session_state.orders if o['status'] == 'confirm' or o['status'] == 'pending']
    
    if not confirmed:
        st.warning("No orders to print.")
    else:
        for idx, o in enumerate(confirmed):
            with st.expander(f"Order: {o['id']} - {o['name']}"):
                # මෙතන තමයි බිල් එක නිර්මාණය වෙන්නේ
                waybill_html = f"""
                <div class="print-section">
                    <h2 style="text-align:center;">HAPPY SHOP - WAYBILL</h2>
                    <hr>
                    <p><b>ORDER ID:</b> {o['id']}</p>
                    <p><b>CUSTOMER:</b> {o['name']}</p>
                    <p><b>ADDRESS:</b> {o['addr']}</p>
                    <p><b>PHONE:</b> {o['phone']}</p>
                    <p><b>ITEM:</b> {o['prod']}</p>
                    <h3 style="text-align:right;">COD AMOUNT: LKR {o['total']:.2f}</h3>
                    <hr>
                    <p style="font-size:10px; text-align:center;">Thank you for your order!</p>
                </div>
                """
                st.markdown(waybill_html, unsafe_allow_html=True)
                
                # බිල් එක ප්‍රින්ට් කරන බටන් එක
                if st.button(f"🖨️ Print Waybill & Dispatch", key=f"btn_{idx}"):
                    # Status එක Shipped වලට මාරු කරනවා
                    for order in st.session_state.orders:
                        if order['id'] == o['id']:
                            order['status'] = 'shipped'
                    
                    # JavaScript හරහා බ්‍රවුසර් එකේ Print window එක ඕපන් කරනවා
                    st.components.v1.html(f"<script>window.print();</script>", height=0)
                    st.success(f"Order {o['id']} dispatched!")
                    st.rerun()

# --- 9. PLACEHOLDERS FOR OTHER MENUS ---
else:
    st.title(f"{menu} > {sub_menu}")
    st.info("Section under development...")
