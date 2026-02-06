import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Full Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE (Data Stability) ---
if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'stocks' not in st.session_state:
    st.session_state.stocks = {"Kesharaja Hair Oil [VGLS0005]": 100, "Crown 1": 50, "Kalkaya": 75}
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'grn_history' not in st.session_state:
    st.session_state.grn_history = []
if 'products' not in st.session_state:
    st.session_state.products = [
        {"code": "VGLS0005", "name": "Kesharaja Hair Oil [VGLS0005]", "price": 2950.0},
        {"code": "C1", "name": "Crown 1", "price": 3500.0}
    ]
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- 3. LOGIN SYSTEM ---
if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #ffa500;'>HAPPY SHOP LOGIN</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if user == "admin" and pw == "happy123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Username or Password")
    st.stop()

# --- 4. CSS & PRINTING DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    .metric-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card { padding: 12px; border-radius: 10px; text-align: center; min-width: 120px; color: white; font-weight: bold; }
    .bg-p { background: #6c757d; } .bg-c { background: #28a745; } .bg-n { background: #ffc107; color: black; } 
    .bg-x { background: #dc3545; } .bg-f { background: #343a40; } .bg-t { background: #007bff; }
    .val { font-size: 24px; display: block; }
    
    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible; }
        .print-area { position: absolute; left: 0; top: 0; width: 500px; color: black !important; background: white !important; padding: 15px; border: 2px solid black; }
        .bill-head { display: flex; justify-content: space-between; border-bottom: 2px solid black; padding-bottom: 5px; }
        .bc-box { flex: 3; border-right: 2px solid black; padding: 10px; font-size: 30px; letter-spacing: 5px; text-align: center; }
        .qty-box { flex: 1; padding: 10px; font-weight: bold; font-size: 22px; text-align: center; }
        .way-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .way-table td, .way-table th { border: 1px solid black; padding: 6px; font-size: 13px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    sub = ""
    if menu == "🧾 Orders": sub = st.radio("Order Menu", ["New Order", "View Lead", "Order Tracking", "Add Lead"])
    elif menu == "🚚 Shipped Items": sub = st.radio("Shipping Menu", ["Dispatch & Print", "Shipped List", "Delivery Summary"])
    elif menu == "📦 GRN": sub = st.radio("GRN Menu", ["New GRN", "GRN List"])
    elif menu == "📊 Stocks": sub = st.radio("Stock Menu", ["View Stocks", "Adjustment"])

# --- 6. DASHBOARD (Metrics & Financials) ---
if menu == "🏠 Dashboard":
    def get_count(s): return len([o for o in st.session_state.orders if o.get('status') == s])
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-p">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-c">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-n">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-x">CANCEL<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-f">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-card bg-t">TOTAL<span class="val">{len(st.session_state.orders)}</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 Profit & Loss Overview")
    total_rev = sum([o['total'] for o in st.session_state.orders if o['status'] == 'shipped'])
    total_exp = sum([e['amount'] for e in st.session_state.expenses])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Shipped Revenue", f"LKR {total_rev:,.2f}")
    c2.metric("Total Expenses", f"LKR {total_exp:,.2f}")
    c3.metric("Net Profit", f"LKR {total_rev - total_exp:,.2f}")

    if st.session_state.orders:
        df = pd.DataFrame(st.session_state.orders)
        st.download_button("📥 Export Orders (CSV)", df.to_csv(index=False).encode('utf-8'), "happy_shop_orders.csv")

# --- 7. ORDERS (View Lead & Tracking Integrated) ---
elif menu == "🧾 Orders":
    if sub in ["New Order", "Add Lead"]:
        st.subheader(f"📝 {sub}")
        with st.form("full_order", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name *")
                phone = st.text_input("Contact Number 1 *")
                addr = st.text_area("Address *")
                city = st.text_input("City")
                district = st.selectbox("District", ["Colombo", "Gampaha", "Kandy", "Galle", "Other"])
            with c2:
                prod = st.selectbox("Product", list(st.session_state.stocks.keys()))
                qty = st.number_input("Qty", min_value=1, value=1)
                price = st.number_input("Sale Amount", value=2950.0)
                delivery = st.number_input("Delivery Charge", value=350.0)
                discount = st.number_input("Discount", value=0.0)
                courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto"])
            
            if st.form_submit_button("🚀 SAVE ORDER"):
                oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                st.session_state.orders.append({
                    "id": oid, "name": name, "phone": phone, "addr": addr, "city": city, "dist": district,
                    "prod": prod, "qty": qty, "price": price, "delivery": delivery, "discount": discount,
                    "total": (price * qty) + delivery - discount, "status": "pending", "date": str(date.today()), "courier": courier
                })
                st.success(f"Order {oid} Saved!")

    elif sub == "View Lead":
        st.subheader("📋 Lead List")
        for idx, o in enumerate(st.session_state.orders):
            with st.expander(f"{o['id']} - {o['name']} ({o['status'].upper()})"):
                st.write(f"📞 {o['phone']} | 📍 {o['addr']}, {o['city']}")
                cols = st.columns(5)
                if cols[0].button("Confirm ✅", key=f"c{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
                if cols[1].button("No Answer ☎", key=f"n{idx}"): st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
                if cols[2].button("Cancel ❌", key=f"x{idx}"): st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
                if cols[3].button("Fake ⚠️", key=f"f{idx}"): st.session_state.orders[idx]['status'] = 'fake'; st.rerun()
                if cols[4].button("Delete 🗑️", key=f"d{idx}"): st.session_state.orders.pop(idx); st.rerun()

    elif sub == "Order Tracking":
        search = st.text_input("Search by Phone Number")
        if search:
            results = [o for o in st.session_state.orders if search in o['phone']]
            for r in results:
                st.info(f"ID: {r['id']} | Status: {r['status'].upper()} | Total: {r['total']}")

# --- 8. SHIPPED ITEMS (Print & History) ---
elif menu == "🚚 Shipped Items":
    if sub == "Dispatch & Print":
        ready = [o for o in st.session_state.orders if o['status'] == 'confirm']
        for idx, ro in enumerate(ready):
            st.markdown(f"""
            <div class="print-area">
                <div class="bill-head"><b>Herbal Crown Pvt Ltd</b><br>ID: {ro['id']}</div>
                <div style="display:flex; border-bottom:2px solid black;">
                    <div class="bc-box">||||||||||||||||</div>
                    <div class="qty-box">QTY: {ro['qty']}</div>
                </div>
                <table class="way-table">
                    <tr><th>Customer Details</th><th>Order Details</th></tr>
                    <tr>
                        <td><b>{ro['name']}</b><br>{ro['addr']}<br>Tel: {ro['phone']}</td>
                        <td>{ro['prod']} (x{ro['qty']})<br><b>Total: LKR {ro['total']:.2f}</b></td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Print & Ship {ro['id']}", key=f"p{idx}"):
                st.session_state.stocks[ro['prod']] -= ro['qty']
                for o in st.session_state.orders: 
                    if o['id'] == ro['id']: o['status'] = 'shipped'
                st.components.v1.html("<script>window.print(); setTimeout(()=>window.location.reload(), 1000);</script>")

    elif sub == "Shipped List":
        shipped = [o for o in st.session_state.orders if o['status'] == 'shipped']
        st.table(pd.DataFrame(shipped) if shipped else "No shipped items.")

# --- 9. GRN & EXPENSES & RETURNS ---
elif menu == "📦 GRN":
    if sub == "New GRN":
        with st.form("grn"):
            p = st.selectbox("Product", list(st.session_state.stocks.keys()))
            q = st.number_input("Received Qty", min_value=1)
            if st.form_submit_button("Add to Stock"):
                st.session_state.stocks[p] += q
                st.session_state.grn_history.append({"date": str(date.today()), "prod": p, "qty": q})
                st.success("Updated!")
    else: st.table(pd.DataFrame(st.session_state.grn_history))

elif menu == "💰 Expense":
    with st.form("exp"):
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Category", ["Marketing", "Packaging", "Courier Fee", "Salary"])
        amt = c2.number_input("Amount")
        if st.form_submit_button("Log Expense"):
            st.session_state.expenses.append({"date": str(date.today()), "cat": cat, "amount": amt})
    st.table(pd.DataFrame(st.session_state.expenses))

elif menu == "🔄 Return":
    rid = st.text_input("Enter Order ID to Return (RTS)")
    if st.button("Confirm RTS"):
        for o in st.session_state.orders:
            if o['id'] == rid:
                o['status'] = 'returned'
                st.session_state.stocks[o['prod']] += o['qty']
                st.success("Stock Added Back & Status Updated.")

elif menu == "📊 Stocks":
    st.table(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Available Qty"]))

elif menu == "🛍️ Products":
    with st.form("p"):
        n = st.text_input("Product Name")
        if st.form_submit_button("Add Product"):
            st.session_state.stocks[n] = 0
            st.success("New Product Ready!")
