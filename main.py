import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Ultimate ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE ---
if 'orders' not in st.session_state:
    st.session_state.orders = []

# --- 3. DISTRICTS & CITIES (ලංකාවේ දත්ත) ---
districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]
cities = ["Colombo 01-15", "Dehiwala", "Mount Lavinia", "Nugegoda", "Maharagama", "Kottawa", "Pannipitiya", "Gampaha", "Negombo", "Kadawatha", "Kiribathgoda", "Wattala", "Ja-Ela", "Kandy", "Peradeniya", "Katugastota", "Galle", "Matara", "Kurunegala", "Ratnapura", "Kalutara", "Panadura", "Horana"]

# --- 4. PROFESSIONAL CSS & PRINTING ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    
    /* Metrics */
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card { padding: 12px; border-radius: 10px; text-align: center; min-width: 120px; color: white; font-weight: bold; }
    .bg-pending { background: #6c757d; } .bg-confirm { background: #28a745; } 
    .bg-noanswer { background: #ffc107; color: black; } .bg-cancel { background: #dc3545; } 
    .bg-fake { background: #343a40; } .bg-total { background: #007bff; }
    .val { font-size: 24px; display: block; }

    /* WAYBILL DESIGN (පින්තූරයේ පරිදිම) */
    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { position: absolute; left: 0; top: 0; width: 380px; color: black !important; background: white !important; padding: 15px; border: 2px solid black; font-family: 'Inter', sans-serif; }
        .waybill-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .waybill-table td, .waybill-table th { border: 1px solid black; padding: 6px; font-size: 13px; text-align: left; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped & Prints", "📦 GRN", "💰 Expense", "📊 Stocks"])
    sub_menu = "View Lead"
    if menu == "🧾 Orders":
        sub_menu = st.radio("Actions", ["New Order", "View Lead", "Order Tracking", "Add Lead"])
    elif menu == "🚚 Shipped & Prints":
        sub_menu = st.radio("Actions", ["Dispatch & Print", "Shipped List"])

# --- 6. TOP METRIC CARDS ---
def get_count(s): return len([o for o in st.session_state.orders if o['status'] == s])
if menu == "🏠 Dashboard" or "Lead" in sub_menu or "Order" in sub_menu:
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-fake">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-card bg-total">TOTAL<span class="val">{len(st.session_state.orders)}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 7. NEW ORDER / ADD LEAD (සම්පූර්ණ විස්තර සහිත පෝරමය) ---
if sub_menu in ["New Order", "Add Lead"]:
    st.subheader("📝 Customer & Order Entry Form")
    with st.form("full_order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Customer Name *")
            phone1 = st.text_input("Contact Number 1 *")
            phone2 = st.text_input("Contact Number 2")
            address = st.text_area("Address *")
            district = st.selectbox("District *", sorted(districts))
            city = st.selectbox("City *", sorted(cities))
        with col2:
            email = st.text_input("Email")
            prod = st.selectbox("Product", ["Kesharaja Hair Oil", "Crown 1", "Kalkaya"])
            qty = st.number_input("Qty", min_value=1, value=1)
            price = st.number_input("Sale Amount", value=2950.0)
            delivery = st.number_input("Delivery Charge", value=350.0)
            discount = st.number_input("Discount", value=0.0)
            courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto"])
            source = st.selectbox("Order Source", ["Facebook", "WhatsApp", "TikTok"])
            note = st.text_area("Order Note")
        
        if st.form_submit_button("🚀 SAVE RECORD"):
            if name and phone1 and address:
                st.session_state.orders.append({
                    "id": f"HS-{len(st.session_state.orders)+821380}",
                    "name": name, "phone1": phone1, "phone2": phone2, "addr": address, 
                    "dist": district, "city": city, "prod": prod, "qty": qty, 
                    "total": (price * qty) + delivery - discount, "status": "pending",
                    "courier": courier, "date": str(date.today())
                })
                st.success("Record Saved!")
                st.rerun()

# --- 8. VIEW LEAD (බටන් ඔක්කොම සහිතව) ---
elif sub_menu == "View Lead":
    st.subheader("📋 Leads Management Table")
    if not st.session_state.orders:
        st.write("No leads found.")
    else:
        for idx, o in enumerate(st.session_state.orders):
            with st.expander(f"{o['id']} - {o['name']} ({o['status'].upper()})"):
                st.write(f"📞 {o['phone1']} | 📍 {o['addr']}, {o['city']}")
                c1, c2, c3, c4, c5 = st.columns(5)
                if c1.button("Confirm ✅", key=f"c_{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
                if c2.button("No Answer ☎", key=f"n_{idx}"): st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
                if c3.button("Cancel ❌", key=f"x_{idx}"): st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
                if c4.button("Fake ⚠", key=f"f_{idx}"): st.session_state.orders[idx]['status'] = 'fake'; st.rerun()
                if c5.button("Dispatch 🚚", key=f"d_{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()

# --- 9. DISPATCH & WAYBILL (HERBAL CROWN Pvt Ltd Design) ---
elif sub_menu == "Dispatch & Print":
    st.subheader("🚚 Waybill Printing")
    confirm_orders = [o for o in st.session_state.orders if o['status'] == 'confirm']
    
    if not confirm_orders:
        st.warning("No confirmed orders to print.")
    else:
        for idx, co in enumerate(confirm_orders):
            st.info(f"Ready: {co['id']} - {co['name']}")
            
            # පින්තූරයේ තිබූ ආකාරයටම බිල් එකේ ලේඅවුට් එක
            bill_html = f"""
            <div class="print-area">
                <div style="text-align:center; border-bottom: 2px solid black; padding-bottom:5px;">
                    <h2 style="margin:0;">Herbal Crown Pvt Ltd</h2>
                    <p style="font-size:11px; margin:0;">0766066789 | Quality Herbal Care</p>
                </div>
                <table class="waybill-table">
                    <tr><td><b>Date:</b> {co['date']}</td><td><b>Order ID:</b> {co['id']}</td></tr>
                    <tr><td><b>Courier:</b> {co['courier']}</td><td><b>Status:</b> CONFIRM</td></tr>
                </table>
                <div style="text-align:center; padding:10px;">
                    <p style="font-size:30px; letter-spacing:8px; margin:0;">|||||||||||||||||</p>
                    <p style="font-size:11px; margin:0;">(01) {co['id']} (21) 567512</p>
                </div>
                <table class="waybill-table">
                    <tr><th style="width:55%;">Customer Details</th><th>Payment Summary</th></tr>
                    <tr>
                        <td>
                            <b>{co['name']}</b><br>
                            {co['addr']}<br>
                            {co['city']}, {co['dist']}<br>
                            <b>Tel:</b> {co['phone1']}
                        </td>
                        <td>
                            Item: {co['prod']}<br>
                            Qty: {co['qty']}<br><br>
                            <b style="font-size:15px;">TOTAL: LKR {co['total']:.2f}</b>
                        </td>
                    </tr>
                </table>
                <p style="font-size:10px; text-align:center; margin-top:10px;">Thank You for Shopping with Happy Shop!</p>
            </div>
            """
            st.markdown(bill_html, unsafe_allow_html=True)
            
            if st.button(f"Print & Dispatch {co['id']}", key=f"p_{idx}"):
                for order in st.session_state.orders:
                    if order['id'] == co['id']: order['status'] = 'shipped'
                st.components.v1.html("<script>window.print();</script>", height=0)
                st.rerun()

# --- 10. SEARCH & TRACKING ---
elif sub_menu == "Order Tracking":
    st.subheader("🔍 Order Tracking")
    q = st.text_input("Enter Phone Number to track")
    if q:
        res = [o for o in st.session_state.orders if q in o['phone1']]
        if res:
            for o in res:
                st.info(f"Order {o['id']} Status: {o['status'].upper()}")
                st.toast(f"Status Updated: {o['status'].upper()}")
        else: st.error("No order found.")
