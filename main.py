import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Full Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE INIT (Data Storage) ---
state_defaults = {
    'orders': [],
    'stocks': {"Kesharaja Hair Oil [VGLS0005]": 50, "Crown 1": 30, "Kalkaya": 25},
    'expenses': [],
    'returns': [],
    'grn_history': [],
    'products': [
        {"code": "VGLS0005", "name": "Kesharaja Hair Oil [VGLS0005]", "price": 2950.0},
        {"code": "HC001", "name": "Crown 1", "price": 3500.0}
    ],
    'authenticated': False
}

for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

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

# --- 4. PROFESSIONAL CSS & PRINTING ---
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
        .waybill-header { display: flex; justify-content: space-between; border-bottom: 2px solid black; padding-bottom: 5px; }
        .barcode-section { display: flex; border-bottom: 2px solid black; text-align: center; }
        .barcode-box { flex: 3; border-right: 2px solid black; padding: 10px; font-size: 30px; letter-spacing: 5px; }
        .qty-box { flex: 1; padding: 10px; font-weight: bold; font-size: 20px; }
        .waybill-table { width: 100%; border-collapse: collapse; }
        .waybill-table td, .waybill-table th { border: 1px solid black; padding: 6px; font-size: 12px; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- 6. DASHBOARD SECTION ---
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
    net_profit = total_rev - total_exp
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"LKR {total_rev:,.2f}")
    c2.metric("Total Expenses", f"LKR {total_exp:,.2f}", delta_color="inverse")
    c3.metric("Net Profit", f"LKR {net_profit:,.2f}")

    if st.session_state.orders:
        df = pd.DataFrame(st.session_state.orders)
        st.download_button("📥 Export Orders to Excel", df.to_csv(index=False).encode('utf-8'), "orders.csv", "text/csv")

# --- 7. PRODUCTS SECTION ---
elif menu == "🛍️ Products":
    st.subheader("🛍️ Product Management")
    with st.form("prod_form"):
        c1, c2, c3 = st.columns(3)
        p_code = c1.text_input("Product Code")
        p_name = c2.text_input("Product Name")
        p_price = c3.number_input("Retail Price", value=0.0)
        if st.form_submit_button("Save Product"):
            st.session_state.products.append({"code": p_code, "name": p_name, "price": p_price})
            if p_name not in st.session_state.stocks: st.session_state.stocks[p_name] = 0
            st.success("Product Added!")
    st.table(pd.DataFrame(st.session_state.products))

# --- 8. GRN SECTION ---
elif menu == "📦 GRN":
    st.subheader("📦 Goods Received Note (GRN)")
    with st.form("grn_form"):
        g_prod = st.selectbox("Select Product", [p['name'] for p in st.session_state.products])
        g_qty = st.number_input("Received Qty", min_value=1)
        g_sup = st.text_input("Supplier")
        if st.form_submit_button("Add Stock"):
            st.session_state.stocks[g_prod] += g_qty
            st.session_state.grn_history.append({"date": str(date.today()), "product": g_prod, "qty": g_qty, "supplier": g_sup})
            st.success("Stock Updated!")
    st.table(pd.DataFrame(st.session_state.grn_history))

# --- 9. EXPENSE SECTION ---
elif menu == "💰 Expense":
    st.subheader("💰 Expense Tracker")
    with st.form("exp_form"):
        e_cat = st.selectbox("Category", ["Marketing", "Salary", "Utility", "Packaging", "Other"])
        e_amt = st.number_input("Amount", min_value=0.0)
        e_desc = st.text_input("Description")
        if st.form_submit_button("Log Expense"):
            st.session_state.expenses.append({"date": str(date.today()), "category": e_cat, "amount": e_amt, "desc": e_desc})
            st.success("Expense Logged!")
    st.table(pd.DataFrame(st.session_state.expenses))

# --- 10. ORDERS SECTION ---
elif menu == "🧾 Orders":
    sub = st.radio("Order Menu", ["New Order", "View Lead"])
    if sub == "New Order":
        with st.form("order_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name *")
                phone = st.text_input("Phone *")
                addr = st.text_area("Address *")
            with c2:
                prod = st.selectbox("Product", list(st.session_state.stocks.keys()))
                qty = st.number_input("Qty", min_value=1, value=1)
                price = st.number_input("Price", value=2950.0)
                delivery = st.number_input("Delivery", value=350.0)
            if st.form_submit_button("Save Order"):
                oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                st.session_state.orders.append({
                    "id": oid, "name": name, "phone": phone, "addr": addr, "prod": prod, 
                    "qty": qty, "price": price, "delivery": delivery, "total": (price*qty)+delivery,
                    "status": "pending", "date": str(date.today())
                })
                st.success(f"Order {oid} Created!")
    else:
        for idx, o in enumerate(st.session_state.orders):
            with st.expander(f"{o['id']} - {o['name']} ({o['status']})"):
                cols = st.columns(4)
                if cols[0].button("Confirm ✅", key=f"c{idx}"): st.session_state.orders[idx]['status'] = 'confirm'; st.rerun()
                if cols[1].button("No Answer ☎", key=f"n{idx}"): st.session_state.orders[idx]['status'] = 'noanswer'; st.rerun()
                if cols[2].button("Cancel ❌", key=f"x{idx}"): st.session_state.orders[idx]['status'] = 'cancel'; st.rerun()
                if cols[3].button("Fake ⚠️", key=f"f{idx}"): st.session_state.orders[idx]['status'] = 'fake'; st.rerun()

# --- 11. DISPATCH & PRINT ---
elif menu == "🚚 Shipped Items":
    ready = [o for o in st.session_state.orders if o['status'] == 'confirm']
    for idx, ro in enumerate(ready):
        st.markdown(f"""
        <div class="print-area">
            <div class="waybill-header"><b>Herbal Crown Pvt Ltd</b><br>ID: {ro['id']}</div>
            <div class="barcode-section"><div class="barcode-box">||||||||||||||</div><div class="qty-box">QTY: {ro['qty']}</div></div>
            <table class="waybill-table">
                <tr><td><b>Customer:</b> {ro['name']}<br>{ro['addr']}<br>Tel: {ro['phone']}</td>
                <td><b>Summary:</b><br>Product: {ro['prod']}<br>Total: LKR {ro['total']:.2f}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Print & Ship {ro['id']}", key=f"p{idx}"):
            st.session_state.stocks[ro['prod']] -= ro['qty']
            for o in st.session_state.orders: 
                if o['id'] == ro['id']: o['status'] = 'shipped'
            st.components.v1.html("<script>window.print(); setTimeout(()=>window.location.reload(), 1000);</script>")

# --- 12. RETURN & STOCKS ---
elif menu == "🔄 Return":
    rid = st.text_input("Order ID to Return")
    if st.button("Process Return"):
        for o in st.session_state.orders:
            if o['id'] == rid:
                o['status'] = 'returned'
                st.session_state.stocks[o['prod']] += o['qty']
                st.success("Return Processed & Stock Updated!")
elif menu == "📊 Stocks":
    st.table(pd.DataFrame(st.session_state.stocks.items(), columns=["Product", "Quantity"]))
