import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px  # Analytics සඳහා

# --- 0. DATA PERSISTENCE (ස්ථීරව දත්ත තබා ගැනීම) ---
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        return pd.read_csv(filename).to_dict('records')
    return []

# විශාල අංක කෙටි කර පෙන්වීමේ ශ්‍රිතය (Formatting Large Numbers)
def format_currency(num):
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    return f"{num:,.2f}"

# --- ලංකාවේ දිස්ත්‍රික්ක සහ නගර දත්ත ---
SL_DATA = {
    "Colombo": ["Colombo 1-15", "Dehiwala", "Mount Lavinia", "Nugegoda", "Maharagama", "Kottawa", "Malabe", "Battaramulla"],
    "Gampaha": ["Gampaha", "Negombo", "Kadawatha", "Kiribathgoda", "Wattala", "Ja-Ela", "Veyangoda"],
    "Kalutara": ["Kalutara", "Panadura", "Horana", "Beruwala", "Matugama"],
    "Kandy": ["Kandy", "Peradeniya", "Katugastota", "Gampola", "Nawalapitiya"],
    "Matale": ["Matale", "Dambulla", "Sigiriya"],
    "Nuwara Eliya": ["Nuwara Eliya", "Hatton", "Talawakele"],
    "Galle": ["Galle", "Hikkaduwa", "Ambalangoda", "Karapitiya"],
    "Matara": ["Matara", "Akuressa", "Weligama"],
    "Hambantota": ["Hambantota", "Tangalle", "Beliatta"],
    "Jaffna": ["Jaffna", "Chavakachcheri"],
    "Mannar": ["Mannar"],
    "Vavuniya": ["Vavuniya"],
    "Mullaitivu": ["Mullaitivu"],
    "Kilinochchi": ["Kilinochchi"],
    "Batticaloa": ["Batticaloa"],
    "Ampara": ["Ampara", "Kalmunai"],
    "Trincomalee": ["Trincomalee"],
    "Kurunegala": ["Kurunegala", "Kuliyapitiya", "Narammala", "Pannala"],
    "Puttalam": ["Puttalam", "Chilaw", "Marawila"],
    "Anuradhapura": ["Anuradhapura", "Eppawala", "Kekirawa"],
    "Polonnaruwa": ["Polonnaruwa"],
    "Badulla": ["Badulla", "Bandarawela", "Hali-Ela"],
    "Moneragala": ["Moneragala", "Wellawaya"],
    "Ratnapura": ["Ratnapura", "Embilipitiya", "Balangoda"],
    "Kegalle": ["Kegalle", "Mawanella", "Warakapola"]
}

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Full Enterprise ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE ---
if 'orders' not in st.session_state:
    st.session_state.orders = load_data('orders.csv')

if 'stocks' not in st.session_state:
    if os.path.exists('stocks.csv'):
        df_s = pd.read_csv('stocks.csv')
        st.session_state.stocks = dict(zip(df_s.Item, df_s.Qty))
    else:
        st.session_state.stocks = {"Kesharaja Hair Oil [VGLS0005]": 100, "Crown 1": 50, "Kalkaya": 75}
        save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')

if 'expenses' not in st.session_state:
    st.session_state.expenses = load_data('expenses.csv')

if 'grn_history' not in st.session_state:
    st.session_state.grn_history = load_data('grn.csv')

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
    
    .ship-header { background-color: #1f2937; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #374151; }
    .status-tab { padding: 5px 15px; border-radius: 5px; font-weight: bold; font-size: 12px; margin-right: 5px; color: white;}

    @media print {
        body * { visibility: hidden; }
        .print-area, .print-area * { visibility: visible !important; }
        .print-area { position: absolute; left: 0; top: 0; width: 100%; color: black !important; background: white !important; padding: 20px; }
        .bill-head { border-bottom: 2px solid black; padding-bottom: 10px; font-size: 24px; }
        .bc-box { border: 2px solid black; padding: 10px; font-size: 28px; text-align: center; margin: 10px 0; }
        .way-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .way-table td, .way-table th { border: 1px solid black; padding: 10px; font-size: 16px; text-align: left; color: black; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    sub = ""
    if menu == "🧾 Orders": 
        sub = st.radio("Order Menu", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"])
    elif menu == "🚚 Shipped Items": 
        sub = st.radio("Shipping Menu", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Courier Feedback", "Confirm Dispatch", "Print Dispatch Items", "Search Waybills", "Courier Feedback Summary"])
    elif menu == "📦 GRN": sub = st.radio("GRN Menu", ["New GRN", "GRN List"])
    elif menu == "📊 Stocks": sub = st.radio("Stock Menu", ["View Stocks", "Adjustment"])

# --- 6. DASHBOARD ---
if menu == "🏠 Dashboard":
    low_stock_items = [item for item, qty in st.session_state.stocks.items() if int(qty) < 10]
    if low_stock_items:
        st.error(f"⚠️ **Low Stock Alert:** {', '.join(low_stock_items)} are running low!")

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
    total_rev = sum([float(o['total']) for o in st.session_state.orders if o['status'] == 'shipped'])
    total_exp = sum([float(e['amount']) for e in st.session_state.expenses])
    net_profit = total_rev - total_exp
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue", f"LKR {format_currency(total_rev)}")
    c2.metric("Expenses", f"LKR {format_currency(total_exp)}")
    c3.metric("Net Profit", f"LKR {format_currency(net_profit)}")

    if st.session_state.orders:
        df_orders = pd.DataFrame(st.session_state.orders)
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.write("**Sales by District**")
            fig1 = px.pie(df_orders, names='dist', hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)
        with col_chart2:
            st.write("**Order Status Distribution**")
            fig2 = px.bar(df_orders, x='status', color='status')
            st.plotly_chart(fig2, use_container_width=True)

# --- 7. ORDERS ---
elif menu == "🧾 Orders":
    if sub in ["New Order", "Add Lead"]:
        st.subheader(f"📝 Happy Shop - {sub}")
        with st.form("full_order", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Customer Name *")
                phone = st.text_input("Contact Number 1 *")
                addr = st.text_area("Address *")
                dist = st.selectbox("District", list(SL_DATA.keys()))
                city = st.selectbox("City", SL_DATA[dist])
            with c2:
                prod = st.selectbox("Product", list(st.session_state.stocks.keys()))
                qty = st.number_input("Qty", min_value=1, value=1)
                price = st.number_input("Sale Amount", value=2950.0)
                delivery = st.number_input("Delivery Charge", value=350.0)
                discount = st.number_input("Discount", value=0.0)
                courier = st.selectbox("Courier Company", ["Koombiyo", "Domex", "Pronto", "Royal Express"])
            
            if st.form_submit_button("🚀 SAVE ORDER"):
                oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                st.session_state.orders.append({
                    "id": oid, "name": name, "phone": phone, "addr": addr, "city": city, "dist": dist,
                    "prod": prod, "qty": qty, "price": price, "delivery": delivery, "discount": discount,
                    "total": (price * qty) + delivery - discount, "status": "pending", "date": str(date.today()), "courier": courier, "printed": "No", "user": "Admin"
                })
                save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                st.success(f"Order {oid} Saved Successfully!")

    elif sub == "View Lead":
        st.markdown('<div class="ship-header"><h3>🔍 Leads Search</h3>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        s_status = fc1.selectbox("Status Filter", ["Any", "pending", "confirm", "noanswer", "cancel", "fake", "onhold"])
        s_user = fc2.selectbox("User Filter", ["Any", "Admin", "Staff 01"])
        s_name = fc3.text_input("Customer Name/Phone Search")
        
        fc4, fc5, fc6 = st.columns(3)
        s_start = fc4.date_input("Start Date", date.today())
        s_end = fc5.date_input("End Date", date.today())
        s_product = fc6.selectbox("Product Filter", ["Any"] + list(st.session_state.stocks.keys()))
        
        if st.button("Apply Search Filters"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Status Tabs Summary (ඡායාරූපය අනුව)
        def cnt(st_val): return len([o for o in st.session_state.orders if o.get('status') == st_val])
        st.markdown(f"""
            <div style="display:flex; flex-wrap:wrap; margin-bottom:20px;">
                <span class="status-tab" style="background:#4b5563;">Leads List: {len(st.session_state.orders)}</span>
                <span class="status-tab" style="background:#6c757d;">Pending: {cnt('pending')}</span>
                <span class="status-tab" style="background:#28a745;">Confirmed: {cnt('confirm')}</span>
                <span class="status-tab" style="background:#ffc107; color:black;">No Answer: {cnt('noanswer')}</span>
                <span class="status-tab" style="background:#dc3545;">Cancelled: {cnt('cancel')}</span>
                <span class="status-tab" style="background:#343a40;">Fake: {cnt('fake')}</span>
                <span class="status-tab" style="background:#d97706;">On Hold: {cnt('onhold')}</span>
            </div>
        """, unsafe_allow_html=True)

        # Filtering Logic
        filtered_orders = st.session_state.orders
        if s_status != "Any":
            filtered_orders = [o for o in filtered_orders if o['status'] == s_status]
        if s_name:
            filtered_orders = [o for o in filtered_orders if s_name.lower() in o['name'].lower() or s_name in str(o['phone'])]
        if s_product != "Any":
            filtered_orders = [o for o in filtered_orders if o['prod'] == s_product]

        if filtered_orders:
            # ඡායාරූපයේ ඇති Column පේළියට අනුව Table එක
            table_data = []
            for o in filtered_orders:
                table_data.append({
                    "Lead Date": o.get('date'),
                    "Customer Name": o.get('name'),
                    "Address": o.get('addr'),
                    "Contact #1": o.get('phone'),
                    "Product Code": o.get('prod'),
                    "Staff": o.get('user', 'Admin'),
                    "Status": o.get('status').upper(),
                    "Action": "Edit Below"
                })
            st.table(pd.DataFrame(table_data))

            st.write("### 🛠️ Lead Management Panel")
            for idx, o in enumerate(filtered_orders):
                with st.expander(f"ACTION: {o['id']} - {o['name']} ({o['phone']})"):
                    # පාරිභෝගිකයාගේ දත්ත ඇමතුමක් අතරතුර පහසුවෙන් වෙනස් කිරීමට
                    uc1, uc2 = st.columns(2)
                    new_name = uc1.text_input("Edit Name", value=o['name'], key=f"name_{idx}")
                    new_phone = uc1.text_input("Edit Phone", value=o['phone'], key=f"phone_{idx}")
                    new_addr = uc1.text_area("Edit Address", value=o['addr'], key=f"addr_{idx}")
                    
                    new_prod = uc2.selectbox("Edit Product", list(st.session_state.stocks.keys()), index=list(st.session_state.stocks.keys()).index(o['prod']), key=f"prod_{idx}")
                    new_qty = uc2.number_input("Edit Qty", value=int(o['qty']), key=f"qty_{idx}")
                    new_total = uc2.number_input("Edit Total Amount", value=float(o['total']), key=f"total_{idx}")

                    if st.button("Update Info 💾", key=f"save_{idx}"):
                        o['name'] = new_name
                        o['phone'] = new_phone
                        o['addr'] = new_addr
                        o['prod'] = new_prod
                        o['qty'] = new_qty
                        o['total'] = new_total
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        st.success("Updated!")
                        st.rerun()

                    st.write("---")
                    # Actions as requested in Photo: Confirm, No Answer, Cancel, Fake, Delete + Add Order
                    acols = st.columns(6)
                    if acols[0].button("Confirm ✅", key=f"c{idx}"): 
                        o['status'] = 'confirm'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if acols[1].button("No Answer ☎", key=f"n{idx}"): 
                        o['status'] = 'noanswer'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if acols[2].button("Cancel ❌", key=f"x{idx}"): 
                        o['status'] = 'cancel'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if acols[3].button("Fake ⚠️", key=f"f{idx}"): 
                        o['status'] = 'fake'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if acols[4].button("Delete 🗑️", key=f"d{idx}"): 
                        st.session_state.orders.remove(o)
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if acols[5].button("Add Order ➕", key=f"ao{idx}"):
                        # පවතින Lead එක අලුත් Order එකක් ලෙස පිටපත් කිරීම
                        new_o = o.copy()
                        new_o['id'] = f"HS-{uuid.uuid4().hex[:6].upper()}"
                        new_o['status'] = 'pending'
                        st.session_state.orders.append(new_o)
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        st.success("New Order Added from this Lead!")
        else:
            st.info("No leads found.")

    elif sub in ["Order Search", "Order Tracking"]:
        search = st.text_input("Search by Phone Number")
        if search:
            results = [o for o in st.session_state.orders if search in str(o['phone'])]
            if results: st.table(pd.DataFrame(results))
            else: st.warning("No records found.")

# --- 8. SHIPPED ITEMS ---
elif menu == "🚚 Shipped Items":
    if sub in ["Ship", "Shipping Dashboard"]:
        st.markdown('<div class="ship-header"><h3>🔍 Search orders for shipping</h3>', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.selectbox("User Search", ["Any", "Admin"])
        c2.selectbox("Date Range Filter", ["Disable", "Today", "Last 7 Days"])
        c3.selectbox("Courier Company", ["All", "Koombiyo", "Domex", "Pronto", "Royal Express"])
        c4.selectbox("Type", ["Only Company Orders"])
        st.button("Search Orders to Ship")
        
        ready_orders = [o for o in st.session_state.orders if o['status'] in ['confirm', 'ready_print']]
        st.info(f"{len(ready_orders)} items have to ship")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if ready_orders:
            df_ready = pd.DataFrame(ready_orders)
            st.dataframe(df_ready[['date', 'id', 'prod', 'qty', 'name', 'city', 'phone', 'status']], use_container_width=True)

    elif sub == "Confirm Dispatch":
        st.subheader("✅ Confirm Orders for Dispatch")
        ready_to_confirm = [o for o in st.session_state.orders if o['status'] == 'confirm']
        if not ready_to_confirm:
            st.info("No orders waiting for dispatch confirmation.")
        else:
            for idx, o in enumerate(ready_to_confirm):
                col1, col2 = st.columns([4, 1])
                col1.write(f"**{o['id']}** - {o['name']} | {o['city']} | {o['prod']} (x{o['qty']})")
                if col2.button("Ready to Print", key=f"conf_{idx}"):
                    o['status'] = 'ready_print'
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    st.rerun()

    elif sub in ["Print Dispatch Items", "Dispatch & Print"]:
        st.subheader("🖨️ Dispatch & Print Label")
        to_print = [o for o in st.session_state.orders if o['status'] == 'ready_print']
        for idx, ro in enumerate(to_print):
            st.markdown(f"**{ro['id']}** - {ro['name']}")
            if st.button(f"Print & Ship {ro['id']}", key=f"p_{idx}"):
                st.session_state.stocks[ro['prod']] -= int(ro['qty'])
                ro['status'] = 'shipped'
                save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                st.success(f"{ro['id']} moved to Shipped.")

# --- 9. GRN, EXPENSES & STOCKS ---
elif menu == "📦 GRN":
    if sub == "New GRN":
        with st.form("grn"):
            p = st.selectbox("Product", list(st.session_state.stocks.keys()))
            q = st.number_input("Received Qty", min_value=1)
            if st.form_submit_button("Add to Stock"):
                st.session_state.stocks[p] += q
                st.session_state.grn_history.append({"date": str(date.today()), "prod": p, "qty": q})
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                save_data(pd.DataFrame(st.session_state.grn_history), 'grn.csv')
                st.success("Stock Updated!")
    else: 
        if st.session_state.grn_history: st.table(pd.DataFrame(st.session_state.grn_history))

elif menu == "💰 Expense":
    with st.form("exp"):
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Category", ["Marketing", "Packaging", "Courier Fee", "Salary", "Rent", "Utility"])
        amt = c2.number_input("Amount")
        if st.form_submit_button("Log Expense"):
            st.session_state.expenses.append({"date": str(date.today()), "cat": cat, "amount": amt})
            save_data(pd.DataFrame(st.session_state.expenses), 'expenses.csv')
            st.success("Expense Logged!")
    if st.session_state.expenses: st.table(pd.DataFrame(st.session_state.expenses))

elif menu == "📊 Stocks":
    st.subheader("📈 Inventory Status")
    df_s = pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Available Qty"])
    st.table(df_s)

elif menu == "🛍️ Products":
    with st.form("p"):
        n = st.text_input("New Product Name")
        if st.form_submit_button("Add Product"):
            if n and n not in st.session_state.stocks:
                st.session_state.stocks[n] = 0
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                st.success(f"{n} Added!")
                st.rerun()
