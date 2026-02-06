import streamlit as st
from datetime import date, datetime
import uuid

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Happy Shop | Enterprise ERP",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# SESSION STATE INIT
# --------------------------------------------------
if "orders" not in st.session_state:
    st.session_state.orders = {}

if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "Kesharaja Hair Oil [VGLS0005]": 100,
        "Crown 1": 50,
        "Kalkaya": 75
    }

if "print_order" not in st.session_state:
    st.session_state.print_order = None

# --------------------------------------------------
# CSS
# --------------------------------------------------
st.markdown("""
<style>
.stApp { background:#0d1117; color:#c9d1d9; }
[data-testid=stSidebar] { background:#161b22; }

.metric-container {
    display:flex; gap:10px; flex-wrap:wrap;
    position:sticky; top:0; z-index:999;
}
.m-card {
    padding:12px; border-radius:10px;
    min-width:130px; text-align:center;
    font-weight:bold; color:white;
}
.bg-pending{background:#6c757d;}
.bg-confirm{background:#28a745;}
.bg-noanswer{background:#ffc107;color:black;}
.bg-cancel{background:#dc3545;}
.bg-fake{background:#343a40;}
.bg-shipped{background:#0dcaf0;}
.bg-total{background:#007bff;}
.val{font-size:24px;}

@media print {
 body * { visibility:hidden; }
 .print-area, .print-area * {
   visibility:visible;
 }
 .print-area {
   position:absolute;
   left:0; top:0;
   width:500px;
   background:white; color:black;
   padding:15px;
   border:2px solid black;
 }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
def count_status(s):
    return len([o for o in st.session_state.orders.values() if o["order"]["status"] == s])

def new_order_id():
    return "HS-" + uuid.uuid4().hex[:8].upper()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.markdown("<h2 style='color:#ffa500;text-align:center'>HAPPY SHOP</h2>", unsafe_allow_html=True)
    menu = st.selectbox("MAIN MENU", [
        "🏠 Dashboard",
        "🧾 Orders",
        "🚚 Dispatch",
        "📦 Stocks",
        "🔍 Tracking"
    ])

    sub = ""
    if menu == "🧾 Orders":
        sub = st.radio("Orders", ["New Order", "View Leads"])
    if menu == "🚚 Dispatch":
        sub = "Dispatch"

# --------------------------------------------------
# METRICS
# --------------------------------------------------
st.markdown(f"""
<div class="metric-container">
 <div class="m-card bg-pending">Pending<span class="val">{count_status("pending")}</span></div>
 <div class="m-card bg-confirm">Confirmed<span class="val">{count_status("confirm")}</span></div>
 <div class="m-card bg-noanswer">No Answer<span class="val">{count_status("noanswer")}</span></div>
 <div class="m-card bg-cancel">Cancel<span class="val">{count_status("cancel")}</span></div>
 <div class="m-card bg-fake">Fake<span class="val">{count_status("fake")}</span></div>
 <div class="m-card bg-shipped">Shipped<span class="val">{count_status("shipped")}</span></div>
 <div class="m-card bg-total">Total<span class="val">{len(st.session_state.orders)}</span></div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# NEW ORDER
# --------------------------------------------------
if sub == "New Order":
    st.subheader("📝 New Order")

    with st.form("order_form", clear_on_submit=True):
        c1, c2 = st.columns(2)

        with c1:
            name = st.text_input("Customer Name *")
            phone = st.text_input("Phone *")
            address = st.text_area("Address *")
            city = st.text_input("City")

        with c2:
            product = st.selectbox("Product", list(st.session_state.stocks.keys()))
            qty = st.number_input("Qty", min_value=1, value=1)
            price = st.number_input("Price", value=2950.0)
            delivery = st.number_input("Delivery", value=350.0)
            discount = st.number_input("Discount", value=0.0)

        submit = st.form_submit_button("SAVE ORDER")

    if submit:
        if not name or not phone:
            st.error("Name & Phone required")
        elif any(o["customer"]["phone"] == phone for o in st.session_state.orders.values()):
            st.warning("Duplicate Lead Detected")
        else:
            oid = new_order_id()
            st.session_state.orders[oid] = {
                "customer": {
                    "name": name,
                    "phone": phone,
                    "address": address,
                    "city": city
                },
                "order": {
                    "product": product,
                    "qty": qty,
                    "price": price,
                    "delivery": delivery,
                    "discount": discount,
                    "total": price * qty + delivery - discount,
                    "status": "pending"
                },
                "history": [
                    {"status": "pending", "time": str(datetime.now())}
                ],
                "date": str(date.today())
            }
            st.success(f"Order {oid} created")
            st.rerun()

# --------------------------------------------------
# VIEW LEADS
# --------------------------------------------------
elif sub == "View Leads":
    st.subheader("📋 Leads")

    for oid, o in st.session_state.orders.items():
        with st.expander(f"{oid} | {o['customer']['name']} ({o['order']['status']})"):
            st.write(o["customer"])

            c = st.columns(4)
            if c[0].button("Confirm", key=f"c{oid}"):
                o["order"]["status"] = "confirm"
            if c[1].button("No Answer", key=f"n{oid}"):
                o["order"]["status"] = "noanswer"
            if c[2].button("Cancel", key=f"x{oid}"):
                o["order"]["status"] = "cancel"
            if c[3].button("Fake", key=f"f{oid}"):
                o["order"]["status"] = "fake"

# --------------------------------------------------
# DISPATCH & PRINT
# --------------------------------------------------
elif menu == "🚚 Dispatch":
    st.subheader("🚚 Dispatch & Print")

    for oid, o in st.session_state.orders.items():
        if o["order"]["status"] == "confirm":
            st.markdown(f"""
            <div class="print-area">
                <h3>Herbal Crown Pvt Ltd</h3>
                <hr>
                <b>Order:</b> {oid}<br>
                <b>Date:</b> {o['date']}<br><br>

                <b>Customer</b><br>
                {o['customer']['name']}<br>
                {o['customer']['address']}<br>
                {o['customer']['phone']}<br><br>

                <b>Product:</b> {o['order']['product']}<br>
                <b>Qty:</b> {o['order']['qty']}<br>
                <b>Total:</b> LKR {o['order']['total']:.2f}
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"🖨 Print & Ship {oid}", key=f"p{oid}"):
                st.session_state.print_order = oid
                st.rerun()

# --------------------------------------------------
# PRINT TRIGGER
# --------------------------------------------------
if st.session_state.print_order:
    oid = st.session_state.print_order
    st.session_state.orders[oid]["order"]["status"] = "shipped"
    st.session_state.stocks[
        st.session_state.orders[oid]["order"]["product"]
    ] -= st.session_state.orders[oid]["order"]["qty"]

    st.components.v1.html("""
    <script>
      setTimeout(()=>{ window.print(); }, 500);
    </script>
    """, height=0)

    st.session_state.print_order = None

# --------------------------------------------------
# STOCKS
# --------------------------------------------------
elif menu == "📦 Stocks":
    st.subheader("📦 Stock Levels")
    st.table(st.session_state.stocks)

# --------------------------------------------------
# TRACKING
# --------------------------------------------------
elif menu == "🔍 Tracking":
    st.subheader("🔍 Order Tracking")
    q = st.text_input("Enter Phone Number")

    if q:
        for oid, o in st.session_state.orders.items():
            if q in o["customer"]["phone"]:
                st.success(f"{oid} → {o['order']['status'].upper()}")
