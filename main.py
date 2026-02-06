import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Happy Shop | Pro ERP", layout="wide", initial_sidebar_state="expanded")

# --- 2. DATA LOADERS & SESSION STATE ---
districts = ["Ampara", "Anuradhapura", "Badulla", "Batticaloa", "Colombo", "Galle", "Gampaha", "Hambantota", "Jaffna", "Kalutara", "Kandy", "Kegalle", "Kilinochchi", "Kurunegala", "Mannar", "Matale", "Matara", "Moneragala", "Mullaitivu", "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee", "Vavuniya"]

# ප්‍රධාන නගර ලැයිස්තුව
cities = ["Colombo 01-15", "Dehiwala", "Mount Lavinia", "Nugegoda", "Maharagama", "Kottawa", "Pannipitiya", "Gampaha", "Negombo", "Kadawatha", "Kiribathgoda", "Wattala", "Ja-Ela", "Kandy", "Peradeniya", "Katugastota", "Galle", "Matara", "Kurunegala", "Ratnapura", "Kalutara", "Panadura", "Horana"]

if 'orders' not in st.session_state:
    st.session_state.orders = []
if 'last_reset_date' not in st.session_state:
    st.session_state.last_reset_date = date.today()

# --- 3. DAILY RESET LOGIC ---
# හැමදාම උදේට දත්ත 0 වෙන්න මෙතැනින් බලනවා
if st.session_state.last_reset_date != date.today():
    st.session_state.orders = []
    st.session_state.last_reset_date = date.today()

# --- 4. HELPER FUNCTIONS ---
def get_count(status_name):
    if status_name == "total": return len(st.session_state.orders)
    return len([o for o in st.session_state.orders if o['status'] == status_name])

# --- 5. PROFESSIONAL UI STYLING (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #e1e1e1; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; }
    
    /* Metric Buttons Styling */
    .metric-container { display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; margin-bottom: 25px; }
    .m-card {
        padding: 12px; border-radius: 10px; text-align: center; min-width: 125px;
        color: white; font-weight: bold; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    /* උඹ ඉල්ලපු පාටවල් ටික */
    .bg-pending { background: #6c757d; }  /* අළු පාට */
    .bg-confirm { background: #28a745; }  /* කොළ පාට */
    .bg-noanswer { background: #ffc107; color: black; } /* කහ පාට */
    .bg-cancel { background: #dc3545; }   /* රතු පාට */
    .bg-fake { background: #343a40; }     /* තද අළු/කළු */
    .bg-total { background: #007bff; }    /* නිල් පාට */
    .val { font-size: 26px; display: block; margin-top: 5px; }
    
    /* Table Headers */
    .header-text { color: #ffa500; font-weight: bold; border-bottom: 1px solid #30363d; padding-bottom: 10px; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 6. SIDEBAR MENU ---
with st.sidebar:
    st.markdown("<h1 style='color:#ffa500; text-align:center;'>HAPPY SHOP</h1>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN MENU", ["🏠 Dashboard", "📦 GRN", "💰 Expense", "🧾 Orders", "🚚 Shipped Items", "📊 Stocks"])
    
    sub_menu = "View Lead"
    if menu == "🧾 Orders":
        sub_menu = st.radio("Order Actions", ["New Order", "View Lead", "Add Lead", "Order History", "Search Waybills"])
    elif menu == "🚚 Shipped Items":
        sub_menu = st.radio("Shipped Actions", ["Ship", "Shipped List", "Delivery Summary", "Courier Feedback"])

    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()

# --- 7. TOP METRIC TILES (Dashboard සහ View Lead එකේදී පමණක් පෙනේ) ---
if menu == "🏠 Dashboard" or (menu == "🧾 Orders" and sub_menu == "View Lead"):
    st.markdown(f"""
        <div class="metric-container">
            <div class="m-card bg-pending">PENDING<span class="val">{get_count('pending')}</span></div>
            <div class="m-card bg-confirm">CONFIRMED<span class="val">{get_count('confirm')}</span></div>
            <div class="m-card bg-noanswer">NO ANSWER<span class="val">{get_count('noanswer')}</span></div>
            <div class="m-card bg-cancel">CANCEL/HOLD<span class="val">{get_count('cancel')}</span></div>
            <div class="m-card bg-fake">FAKE<span class="val">{get_count('fake')}</span></div>
            <div class="m-card bg-total">TOTAL LEADS<span class="val">{get_count('total')}</span></div>
        </div>
    """, unsafe_allow_html=True)

# --- 8. PAGE CONTENT ---

# 8.1 DASHBOARD
if menu == "🏠 Dashboard":
    st.title("Business Summary")
    st.info(f"System Online | Today: {date.today().strftime('%Y-%m-%d')}")

# 8.2 NEW ORDER / ADD LEAD (සම්පූර්ණ විස්තර සහිත පෝරමය)
elif menu == "🧾 Orders" and (sub_menu == "New Order" or sub_menu == "Add Lead"):
    st.subheader(f"📝 {sub_menu}")
    with st.form("full_order_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Customer Info**")
            name = st.text_input("Customer Name *")
            address = st.text_area("Address *")
            district = st.selectbox("Select District *", sorted(districts))
            city = st.selectbox("Select City *", sorted(cities))
            phone1 = st.text_input("Contact Number One *")
            phone2 = st.text_input("Contact Number Two")
            email = st.text_input("Email")
        
        with col2:
            st.markdown("**Product & Shipping**")
            product = st.selectbox("Product", ["Kesharaja Hair Oil [VGLS0005]", "Crown 1 [VGLS0001]", "Kalkaya [VGLS0003]"])
            qty = st.number_input("Qty", min_value=1, value=1)
            sale_amt = st.number_input("Sale Amount", min_value=0.0)
            p_note = st.text_area("Product Note")
            courier = st.selectbox("Courier Company", ["Any", "Koombiyo", "Domex", "Pronto"])
            del_charge = st.number_input("Delivery Charge", min_value=0.0)
            discount = st.number_input("Discount", min_value=0.0)
        
        if st.form_submit_button("🚀 SAVE RECORD"):
            if name and phone1 and address:
                new_id = len(st.session_state.orders) + 1
                st.session_state.orders.append({
                    "id": new_id,
                    "order_id": f"HS-{821384 + new_id}",
                    "customer": name,
                    "phone": phone1,
                    "status": "pending",
                    "total": (sale_amt * qty) + del_charge - discount
                })
                st.success("Record Saved Successfully!")
                st.rerun()
            else:
                st.error("Please fill required fields (*)")

# 8.3 VIEW LEAD (Interactive Table එක සහ real-time update බටන්)
elif menu == "🧾 Orders" and sub_menu == "View Lead":
    st.subheader("📋 Leads Management Table")
    
    if not st.session_state.orders:
        st.write("No leads added today.")
    else:
        # Table Header
        h1, h2, h3, h4, h5 = st.columns([1, 2, 2, 1.5, 3])
        h1.markdown("<div class='header-text'>ID</div>", unsafe_allow_html=True)
        h2.markdown("<div class='header-text'>Customer</div>", unsafe_allow_html=True)
        h3.markdown("<div class='header-text'>Phone</div>", unsafe_allow_html=True)
        h4.markdown("<div class='header-text'>Status</div>", unsafe_allow_html=True)
        h5.markdown("<div class='header-text'>Actions</div>", unsafe_allow_html=True)

        # Table Rows
        for idx, order in enumerate(st.session_state.orders):
            r1, r2, r3, r4, r5 = st.columns([1, 2, 2, 1.5, 3])
            
            r1.write(order['order_id'])
            r2.write(order['customer'])
            r3.write(order['phone'])
            
            # Status පාටවල්
            st_color = {"pending": "#6c757d", "confirm": "#28a745", "noanswer": "#ffc107", "cancel": "#dc3545", "fake": "#343a40"}
            r4.markdown(f'<span style="background:{st_color[order["status"]]}; padding:4px 8px; border-radius:5px; font-size:11px; color:{"black" if order["status"]=="noanswer" else "white"}; font-weight:bold;">{order["status"].upper()}</span>', unsafe_allow_html=True)
            
            # Action Buttons - මේවා එබූ සැනින් Python Variable update වේ
            b_cols = r5.columns(4)
            if b_cols[0].button("✔", key=f"c_{idx}", help="Confirm"):
                st.session_state.orders[idx]['status'] = "confirm"
                st.rerun()
            if b_cols[1].button("☎", key=f"n_{idx}", help="No Answer"):
                st.session_state.orders[idx]['status'] = "noanswer"
                st.rerun()
            if b_cols[2].button("✖", key=f"x_{idx}", help="Cancel/Hold"):
                st.session_state.orders[idx]['status'] = "cancel"
                st.rerun()
            if b_cols[3].button("⚠", key=f"f_{idx}", help="Fake"):
                st.session_state.orders[idx]['status'] = "fake"
                st.rerun()
            st.divider()

else:
    st.info(f"The section '{menu} > {sub_menu}' is being updated.")

