import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import uuid
import os
import plotly.express as px
import plotly.graph_objects as go
import time
import re

# --- 0. DATA PERSISTENCE ---
def save_data(df, filename):
    df.to_csv(filename, index=False)

def load_data(filename):
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        return df.to_dict('records')
    return []

def format_currency(num):
    if num >= 1_000_000_000: return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000: return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000: return f"{num / 1_000:.1f}K"
    return f"{num:,.2f}"

# --- SRI LANKA GEO-DATA (RE-ADDED) ---
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
    "Mannar": ["Mannar"], "Vavuniya": ["Vavuniya"], "Mullaitivu": ["Mullaitivu"], "Kilinochchi": ["Kilinochchi"],
    "Batticaloa": ["Batticaloa"], "Ampara": ["Ampara", "Kalmunai"], "Trincomalee": ["Trincomalee"],
    "Kurunegala": ["Kurunegala", "Kuliyapitiya", "Narammala", "Pannala"],
    "Puttalam": ["Puttalam", "Chilaw", "Marawila"],
    "Anuradhapura": ["Anuradhapura", "Eppawala", "Kekirawa"], "Polonnaruwa": ["Polonnaruwa"],
    "Badulla": ["Badulla", "Bandarawela", "Hali-Ela"], "Moneragala": ["Moneragala", "Wellawaya"],
    "Ratnapura": ["Ratnapura", "Embilipitiya", "Balangoda"], "Kegalle": ["Kegalle", "Mawanella", "Warakapola"]
}

# --- 1. SESSION STATE & DB ---
if 'orders' not in st.session_state: st.session_state.orders = load_data('orders.csv')
if 'stocks' not in st.session_state:
    if os.path.exists('stocks.csv'):
        df_s = pd.read_csv('stocks.csv')
        st.session_state.stocks = dict(zip(df_s.Item, df_s.Qty))
    else:
        st.session_state.stocks = {"Kesharaja Hair Oil": 100, "Crown 1": 50, "Kalkaya": 75}
if 'expenses' not in st.session_state: st.session_state.expenses = load_data('expenses.csv')
if 'audit_logs' not in st.session_state: st.session_state.audit_logs = load_data('audit.csv')
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'user_role' not in st.session_state: st.session_state.user_role = None

# Admin-Controlled Staff Permissions (Permanent Fix)
if 'staff_perms' not in st.session_state:
    st.session_state.staff_perms = {"Add_Order": True, "View_Leads": True, "Print_Labels": True, "Finance": False}

# --- 2. LOGIN SYSTEM ---
def check_auth(u, p):
    if u == "happyshop@gmail.com" and p == "happy123":
        return True, "Owner", "Admin"
    for i in range(1, 6):
        if u == f"demo{i}@gmail.com" and p == f"demo{i}":
            return True, "Staff", f"Staff_{i}"
    return False, None, None

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center; color: #ffa500;'>HAPPY SHOP ENTERPRISE LOGIN</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("Username (Email)")
        pw = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            auth, role, name = check_auth(user, pw)
            if auth:
                st.session_state.authenticated, st.session_state.user_role, st.session_state.current_user = True, role, name
                st.rerun()
            else: st.error("Invalid Login Details")
    st.stop()

# --- 3. PAGE CONFIG & CSS ---
st.set_page_config(page_title="Happy Shop | Ultimate Enterprise", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .m-card { padding: 15px; border-radius: 12px; text-align: center; color: white; font-weight: bold; border: 1px solid #30363d; }
    .bg-p { background: linear-gradient(135deg, #6c757d, #495057); } 
    .bg-c { background: linear-gradient(135deg, #28a745, #1e7e34); } 
    .bg-n { background: linear-gradient(135deg, #ffc107, #e0a800); color: black; } 
    .bg-x { background: linear-gradient(135deg, #dc3545, #bd2130); } 
    .bg-t { background: linear-gradient(135deg, #007bff, #0062cc); }
    .wa-btn { background-color: #25D366; color: white; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR & PERMISSION MANAGER ---
with st.sidebar:
    st.markdown(f"👤 **{st.session_state.current_user}** ({st.session_state.user_role})")
    
    if st.session_state.user_role == "Owner":
        with st.expander("🛠️ Master Admin Controls"):
            st.session_state.staff_perms["Add_Order"] = st.checkbox("Staff: Add New Orders", value=st.session_state.staff_perms["Add_Order"])
            st.session_state.staff_perms["View_Leads"] = st.checkbox("Staff: Lead Manager", value=st.session_state.staff_perms["View_Leads"])
            st.session_state.staff_perms["Print_Labels"] = st.checkbox("Staff: Print/Dispatch", value=st.session_state.staff_perms["Print_Labels"])
            st.session_state.staff_perms["Finance"] = st.checkbox("Staff: View Payroll", value=st.session_state.staff_perms["Finance"])
        
        staff_list = ["Admin"] + [f"Staff_{i}" for i in range(1, 6)]
        switch_to = st.selectbox("Ghost Switch View:", staff_list)
        if st.button("Instant Switch"):
            st.session_state.current_user = switch_to
            st.rerun()

    menu = st.selectbox("Main Menu", ["Dashboard", "Orders", "Inventory", "Finance & Payroll"])
    sub = ""
    if menu == "Orders":
        sub = st.radio("Actions", ["New Order", "Lead Manager", "RTS/Returns"])

# --- 5. DASHBOARD (ALL ORIGINAL CHARTS RE-ADDED) ---
if menu == "Dashboard":
    st.title(f"🚀 Business Control Center")
    df_orders = pd.DataFrame(st.session_state.orders)
    
    def get_count(s): return len([o for o in st.session_state.orders if o.get('status') == s])
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f'<div class="m-card bg-p">PENDING<br><span style="font-size:24px">{get_count("pending")}</span></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="m-card bg-c">CONFIRMED<br><span style="font-size:24px">{get_count("confirm")}</span></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="m-card bg-n">NO ANSWER<br><span style="font-size:24px">{get_count("noanswer")}</span></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="m-card bg-x">CANCELLED<br><span style="font-size:24px">{get_count("cancel")}</span></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="m-card bg-t">TOTAL LEADS<br><span style="font-size:24px">{len(st.session_state.orders)}</span></div>', unsafe_allow_html=True)

    if not df_orders.empty:
        col_lg, col_sm = st.columns([2, 1])
        with col_lg:
            fig = px.bar(df_orders, x='date', color='status', title="Order Trends", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        with col_sm:
            st.subheader("🏆 Staff Performance")
            st.dataframe(df_orders['staff'].value_counts(), use_container_width=True)

# --- 6. ORDERS SYSTEM (WITH PERMISSIONS) ---
elif menu == "Orders":
    if sub == "New Order":
        if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Add_Order"]:
            st.subheader("✨ Intelligent Order Entry")
            # Smart Parser (New Feature)
            with st.expander("📋 Smart Paste WhatsApp Text"):
                raw_text = st.text_area("Paste here...")
                if st.button("Extract"):
                    phone_m = re.search(r'(\d{10})', raw_text)
                    st.session_state.p_name = raw_text.split('\n')[0] if raw_text else ""
                    st.session_state.p_phone = phone_m.group(1) if phone_m else ""
                    st.success("Extracted!")

            with st.form("entry_form"):
                col1, col2 = st.columns(2)
                c_name = col1.text_input("Customer Name", value=st.session_state.get('p_name', ""))
                c_phone = col1.text_input("Mobile", value=st.session_state.get('p_phone', ""))
                addr = col1.text_area("Address")
                dist = col2.selectbox("District", list(SL_DATA.keys()))
                city = col2.selectbox("City", SL_DATA[dist])
                prod = col2.selectbox("Product", list(st.session_state.stocks.keys()))
                price = col2.number_input("Value (LKR)", value=2500)
                
                if st.form_submit_button("Submit & Lock"):
                    oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.orders.append({
                        "id": oid, "name": c_name, "phone": c_phone, "addr": addr, "dist": dist, "city": city,
                        "prod": prod, "total": price, "status": "pending", "date": str(date.today()),
                        "staff": st.session_state.current_user, "notes": "", "dispatch": "No"
                    })
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    st.balloons()
        else:
            st.error("Access Denied: Owner has disabled order entry for staff.")

    elif sub == "Lead Manager":
        if st.session_state.user_role == "Owner" or st.session_state.staff_perms["View_Leads"]:
            st.subheader("📋 Advanced Lead Management")
            df = pd.DataFrame(st.session_state.orders)
            search = st.text_input("🔍 Search Leads")
            if not df.empty:
                if search: df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
                for idx, row in df.iterrows():
                    with st.expander(f"{row['id']} | {row['name']} | {row['status']}"):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        new_status = c1.selectbox("Status", ["pending", "confirm", "noanswer", "cancel", "shipped"], key=f"s_{idx}")
                        
                        if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Print_Labels"]:
                            if c2.button(f"🖨️ Print Label", key=f"p_{idx}"): st.write("Label Printing...")
                            if c3.button(f"🚚 Mark Dispatch", key=f"d_{idx}"): 
                                st.session_state.orders[idx]['dispatch'] = "Yes"
                                st.toast("Dispatched!")

                        if st.button("Update Ledger", key=f"b_{idx}"):
                            st.session_state.orders[idx]['status'] = new_status
                            save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                            st.rerun()

# --- 7. FINANCE & PAYROLL ---
elif menu == "Finance & Payroll":
    if st.session_state.user_role == "Owner" or st.session_state.staff_perms["Finance"]:
        st.title("💰 Finance & Payroll")
        df = pd.DataFrame(st.session_state.orders)
        if not df.empty:
            staff_stats = df[df['status'] == 'confirm'].groupby('staff').size().reset_index(name='Confirms')
            staff_stats['Payable'] = 30000 + (staff_stats['Confirms'] * 50)
            st.table(staff_stats)
    else:
        st.error("Access Denied: Only Admin can view Finance.")

# --- 8. INVENTORY (RE-ADDED) ---
elif menu == "Inventory":
    st.title("📊 Inventory Status")
    st.table(pd.DataFrame(st.session_state.stocks.items(), columns=["Product", "Qty"]))

if st.sidebar.button("🔓 Logout"):
    st.session_state.authenticated = False
    st.rerun()
