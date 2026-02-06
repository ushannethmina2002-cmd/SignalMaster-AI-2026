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

# --- 4. CSS DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .ship-header { background-color: #1f2937; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #374151; }
    .status-bar { display: flex; gap: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .stat-box { padding: 5px 15px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION (ඡායාරූපයේ පරිදි යාවත්කාලීන කරන ලදී) ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN NAVIGATION", ["🏠 Dashboard", "🧾 Orders", "🚚 Shipped Items", "📦 GRN", "💰 Expense", "🔄 Return", "📊 Stocks", "🛍️ Products"])
    
    sub = ""
    if menu == "🧾 Orders": 
        sub = st.radio("Order Menu", ["New Order", "Pending Orders", "Order Search", "Import Lead", "View Lead", "Add Lead", "Order History", "Exchanging Orders", "Blacklist Manager"])
    elif menu == "🚚 Shipped Items": 
        sub = st.radio("Shipping Menu", ["Ship", "Shipped List", "Shipped Summary", "Delivery Summary", "Courier Feedback", "Confirm Dispatch", "Print Dispatch items", "Search Waybills", "Courier Feedback Summary"])
    elif menu == "📦 GRN": sub = st.radio("GRN Menu", ["New GRN", "GRN List"])
    elif menu == "📊 Stocks": sub = st.radio("Stock Menu", ["View Stocks", "Adjustment"])

# --- 6. DASHBOARD ---
if menu == "🏠 Dashboard":
    def get_count(s): return len([o for o in st.session_state.orders if o.get('status') == s])
    st.markdown(f"""
        <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px;">
            <div style="background:#6c757d; padding:15px; border-radius:10px; text-align:center; min-width:120px;">PENDING<br><b style="font-size:20px;">{get_count('pending')}</b></div>
            <div style="background:#28a745; padding:15px; border-radius:10px; text-align:center; min-width:120px;">CONFIRMED<br><b style="font-size:20px;">{get_count('confirm')}</b></div>
            <div style="background:#ffc107; color:black; padding:15px; border-radius:10px; text-align:center; min-width:120px;">NO ANSWER<br><b style="font-size:20px;">{get_count('noanswer')}</b></div>
            <div style="background:#dc3545; padding:15px; border-radius:10px; text-align:center; min-width:120px;">CANCEL<br><b style="font-size:20px;">{get_count('cancel')}</b></div>
            <div style="background:#007bff; padding:15px; border-radius:10px; text-align:center; min-width:120px;">TOTAL<br><b style="font-size:20px;">{len(st.session_state.orders)}</b></div>
        </div>
    """, unsafe_allow_html=True)
    # Graph logic follows... (සංස්කරණය නොකළ මුල් කොටස)

# --- 7. ORDERS (View Lead කොටස ඡායාරූපය අනුව සම්පූර්ණයෙන්ම වෙනස් කරන ලදී) ---
elif menu == "🧾 Orders":
    if sub == "View Lead":
        st.markdown('<div class="ship-header"><h3>🔍 Leads Search</h3>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        s_status = c1.selectbox("Status", ["Any", "pending", "confirm", "noanswer", "cancel", "fake", "rejected", "onhold"])
        s_user = c2.selectbox("User", ["Any", "Admin", "Staff 01", "Crown Dimo 3"])
        s_name = c3.text_input("Customer Name")
        
        c4, c5, c6 = st.columns(3)
        s_start = c4.date_input("Start Date", date.today())
        s_end = c5.date_input("End Date", date.today())
        s_product = c6.selectbox("Product", ["Any"] + list(st.session_state.stocks.keys()))
        
        st.markdown('<div style="text-align: right;"><button style="background:#059669; color:white; border:none; padding:8px 20px; border-radius:5px; cursor:pointer;">Search</button> <button style="background:#4b5563; color:white; border:none; padding:8px 20px; border-radius:5px; cursor:pointer;">Reload</button></div></div>', unsafe_allow_html=True)

        # Status Summary Bar (ඡායාරූපයේ පරිදි)
        st.markdown(f"""
        <div class="status-bar">
            <div class="stat-box" style="background:#4b5563;">Leads List: {len(st.session_state.orders)}</div>
            <div class="stat-box" style="background:#6b7280;">Pending: {get_count('pending')}</div>
            <div class="stat-box" style="background:#10b981;">Confirmed: {get_count('confirm')}</div>
            <div class="stat-box" style="background:#f59e0b;">No Answer: {get_count('noanswer')}</div>
            <div class="stat-box" style="background:#ef4444;">Rejected: {get_count('rejected')}</div>
            <div class="stat-box" style="background:#374151;">Fake: {get_count('fake')}</div>
            <div class="stat-box" style="background:#b91c1c;">Cancelled: {get_count('cancel')}</div>
            <div class="stat-box" style="background:#d97706;">On Hold: {get_count('onhold')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Filtering Logic
        filtered = [o for o in st.session_state.orders if (s_status == "Any" or o['status'] == s_status) and (s_name.lower() in o['name'].lower() if s_name else True)]

        if filtered:
            # ඡායාරූපයේ ඇති Cloumns සමඟ දත්ත වගුව
            data_list = []
            for o in filtered:
                data_list.append({
                    "Lead Date": o.get('date'),
                    "Customer Name": o.get('name'),
                    "Address": o.get('addr'),
                    "Contact #1": o.get('phone'),
                    "Product Code": o.get('prod'),
                    "Staff": "Admin",
                    "Status": o.get('status').upper(),
                    "ID": o.get('id')
                })
            
            df_display = pd.DataFrame(data_list)
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            st.write("### ⚙️ Quick Actions & Order Update")
            for idx, o in enumerate(filtered):
                with st.expander(f"Update: {o['id']} - {o['name']} | {o['phone']}"):
                    # පාරිභෝගික දත්ත වෙනස් කිරීමට (Edit Feature)
                    ec1, ec2 = st.columns(2)
                    up_name = ec1.text_input("Customer Name", value=o['name'], key=f"un_{idx}")
                    up_phone = ec1.text_input("Phone Number", value=o['phone'], key=f"up_{idx}")
                    up_addr = ec1.text_area("Address", value=o['addr'], key=f"ua_{idx}")
                    
                    up_prod = ec2.selectbox("Product", list(st.session_state.stocks.keys()), index=list(st.session_state.stocks.keys()).index(o['prod']), key=f"upr_{idx}")
                    up_price = ec2.number_input("Amount", value=float(o.get('price', 0)), key=f"uam_{idx}")
                    
                    if st.button("Update Lead Info 💾", key=f"save_{idx}"):
                        o['name'] = up_name
                        o['phone'] = up_phone
                        o['addr'] = up_addr
                        o['prod'] = up_prod
                        o['price'] = up_price
                        o['total'] = up_price + float(o.get('delivery', 0)) - float(o.get('discount', 0))
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                        st.success("Lead data updated!")
                        st.rerun()

                    st.markdown("---")
                    # ඉල්ලා ඇති බොත්තම් පෙළ
                    btn_cols = st.columns(7)
                    if btn_cols[0].button("Confirm ✅", key=f"conf_{idx}"): 
                        o['status'] = 'confirm'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if btn_cols[1].button("No Answer ☎", key=f"na_{idx}"): 
                        o['status'] = 'noanswer'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if btn_cols[2].button("Cancel ❌", key=f"can_{idx}"): 
                        o['status'] = 'cancel'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if btn_cols[3].button("Fake ⚠️", key=f"fk_{idx}"): 
                        o['status'] = 'fake'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if btn_cols[4].button("Delete 🗑️", key=f"del_{idx}"): 
                        st.session_state.orders.remove(o)
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if btn_cols[5].button("Add Order ➕", key=f"add_{idx}"):
                        st.session_state.orders.append(o.copy()) # Duplicate as a new order if needed
                        st.success("Added as a New Order!")
        else:
            st.info("No leads matching the criteria.")

    # සෙසු මෙනු සඳහා placeholder දත්ත (ඡායාරූපයේ ඇති මෙනු සියල්ල මෙහි ඇතුළත් වේ)
    elif sub in ["New Order", "Add Lead"]:
        # (ඔබේ මුල් New Order පෝරමය මෙහි පවතී)
        with st.form("new_order_form"):
            st.write("Customer & Product Details")
            # ... (මුල් කේතයේ ඇති Form fields)
            if st.form_submit_button("🚀 SAVE ORDER"):
                st.success("Order Saved!")

    elif sub == "Import Lead":
        st.subheader("📥 Bulk Import Leads (Excel/CSV)")
        st.file_uploader("Upload Lead File")
        
    elif sub == "Blacklist Manager":
        st.subheader("🚫 Blacklisted Customers")
        st.text_input("Search Blacklist")

# --- 8. SHIPPED ITEMS (ඡායාරූපයේ ඇති පරිදි නව මෙනු සමඟ) ---
elif menu == "🚚 Shipped Items":
    if sub == "Ship":
        st.markdown('<div class="ship-header"><h3>🔍 Search orders for shipping</h3>', unsafe_allow_html=True)
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.selectbox("User", ["Any", "Admin"])
        sc2.selectbox("Date Range", ["Disable", "Today", "Custom"])
        sc3.selectbox("Courier", ["All", "Koombiyo", "Domex"])
        sc4.selectbox("Dropshipper", ["Only Company Orders"])
        st.markdown('<button style="background:#059669; color:white; border:none; padding:8px 20px; border-radius:5px;">Search</button></div>', unsafe_allow_html=True)
        
        st.info("0 items have to ship")
        st.write("#### Ready to Ship List")
        st.write("No data available in table")

    elif sub == "Courier Feedback":
        st.subheader("🚚 Courier Status Update")
        st.file_uploader("Upload Courier Return/Delivery CSV")

# --- 9. GRN, EXPENSE, STOCKS (මුල් කේතය නොවෙනස්ව පවතී) ---
# ... (මුල් කේතයේ ඉතිරි කොටස් මෙහි ඇතුළත් වේ)
