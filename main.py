import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px
from fpdf import FPDF
import base64

# =========================================================
# 1. පද්ධතියේ පෙනුම සකස් කිරීම (Advanced UI)
# =========================================================
st.set_page_config(page_title="HappyShop ERP v5.0 ULTIMATE", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    .stApp { background: linear-gradient(135deg, #020111, #0d0c2b, #13123b); color: white; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: rgba(0, 0, 0, 0.9) !important; border-right: 2px solid #FFD700; }
    .brand-header { font-size: 38px; font-weight: 800; color: #FFD700; text-align: center; text-shadow: 0px 0px 15px rgba(255, 215, 0, 0.5); }
    
    /* Professional Dashboard Cards */
    .metric-row { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 25px; }
    .card { background: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 15px; border-top: 4px solid #FFD700; min-width: 140px; flex: 1; text-align: center; transition: 0.3s; }
    .card:hover { transform: translateY(-5px); background: rgba(255, 255, 255, 0.08); }
    .card h4 { margin: 0; font-size: 11px; color: #aaa; text-transform: uppercase; }
    .card h2 { margin: 8px 0; font-size: 26px; font-weight: 700; }
    
    .c-confirm { border-top-color: #00ff88; color: #00ff88; }
    .c-noanswer { border-top-color: #f1c40f; color: #f1c40f; }
    .c-cancel { border-top-color: #ff4d4d; color: #ff4d4d; }
    .c-hold { border-top-color: #cc00ff; color: #cc00ff; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. දත්ත ගබඩාව (CSV Database Engine)
# =========================================================
def load_db(file, columns):
    if os.path.exists(file): return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

if "db" not in st.session_state:
    st.session_state.db = {
        "orders": load_db("orders.csv", ["id", "date", "name", "phone", "address", "prod", "qty", "total", "status", "staff"]),
        "stock": load_db("stock.csv", ["Code", "Product", "Qty", "Price", "Value"]),
        "audit": load_db("audit.csv", ["timestamp", "staff", "action"])
    }

# ආරම්භක තොග දත්ත (Empty නම් පමණක්)
if st.session_state.db["stock"].empty:
    st.session_state.db["stock"] = pd.DataFrame([
        {"Code": "KHO-01", "Product": "Kasharaja Hair Oil", "Qty": 200, "Price": 2950, "Value": 590000},
        {"Code": "HNC-02", "Product": "Herbal Night Cream", "Qty": 100, "Price": 1800, "Value": 180000}
    ])

# =========================================================
# 3. PDF INVOICE GENERATOR (වෘත්තීය බිල්පතක් සැකසීම)
# =========================================================
def create_pdf(order_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(190, 10, "HAPPY SHOP - INVOICE", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(100, 10, f"Customer: {order_data['name']}")
    pdf.cell(90, 10, f"Date: {order_data['date']}", ln=True, align='R')
    pdf.cell(100, 10, f"Invoice ID: {order_data['id']}", ln=True)
    pdf.ln(5)
    pdf.line(10, 45, 200, 45)
    pdf.cell(100, 10, "Product Description", border=1)
    pdf.cell(30, 10, "Qty", border=1, align='C')
    pdf.cell(60, 10, "Amount (LKR)", border=1, ln=True, align='C')
    pdf.cell(100, 10, f"{order_data['prod']}", border=1)
    pdf.cell(30, 10, f"{order_data['qty']}", border=1, align='C')
    pdf.cell(60, 10, f"{order_data['total']}/=", border=1, ln=True, align='R')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, f"Grand Total: LKR {order_data['total']}/=", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')

# =========================================================
# 4. මෙනු පද්ධතිය (Navigation)
# =========================================================
with st.sidebar:
    st.markdown('<div class="brand-header">HAPPY SHOP</div>', unsafe_allow_html=True)
    st.divider()
    current_user = st.selectbox("🔑 User Login", ["Admin - Supun", "Staff - Kavindi", "Staff - Nuwan"])
    menu = st.radio("MAIN MENU", ["🏠 Dashboard", "➕ Add New Lead", "📦 Inventory Control", "📜 Order History", "🕵️ Audit Logs"])

# =========================================================
# 5. මොඩියුල ක්‍රියාත්මක කිරීම
# =========================================================

# --- DASHBOARD ---
if menu == "🏠 Dashboard":
    st.title("📊 Enterprise Analytics")
    df = st.session_state.db['orders']
    
    st.markdown(f"""
    <div class="metric-row">
        <div class="card"><h4>TOTAL LEADS</h4><h2>{len(df)}</h2></div>
        <div class="card c-confirm"><h4>CONFIRMED</h4><h2>{len(df[df['status']=='confirm'])}</h2></div>
        <div class="card c-noanswer"><h4>NO ANSWER</h4><h2>{len(df[df['status']=='noanswer'])}</h2></div>
        <div class="card c-cancel"><h4>CANCELLED</h4><h2>{len(df[df['status']=='cancel'])}</h2></div>
        <div class="card c-hold"><h4>ON HOLD</h4><h2>{len(df[df['status']=='hold'])}</h2></div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        if not df.empty:
            fig = px.area(df, x='date', y='total', title="Revenue Stream", color_discrete_sequence=['#FFD700'])
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if not df.empty:
            fig_pie = px.pie(df, names='status', hole=0.5, title="Lead Status Distribution")
            st.plotly_chart(fig_pie, use_container_width=True)

# --- ADD NEW LEAD (විකුණුම් ඇතුළත් කිරීම) ---
elif menu == "➕ Add New Lead":
    st.title("🛒 Create New Sale / Lead")
    with st.form("sale_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Customer Name")
        phone = c1.text_input("Phone Number")
        addr = c1.text_area("Address")
        prod = c2.selectbox("Product", st.session_state.db["stock"]["Product"])
        qty = c2.number_input("Quantity", 1)
        status = c2.selectbox("Order Status", ["confirm", "pending", "noanswer", "hold", "fake", "cancel"])
        
        if st.form_submit_button("SAVE & SYNC"):
            price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Price"].values[0]
            oid = f"HS-{uuid.uuid4().hex[:5].upper()}"
            new_order = {"id": oid, "date": str(date.today()), "name": name, "phone": phone, "address": addr, "prod": prod, "qty": qty, "total": price*qty, "status": status, "staff": current_user}
            st.session_state.db["orders"] = pd.concat([st.session_state.db["orders"], pd.DataFrame([new_order])], ignore_index=True)
            
            # Stock එක ස්වයංක්‍රීයව අඩු කිරීම (Automation)
            st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Qty"] -= qty
            st.success(f"Order {oid} recorded successfully!")

# --- ORDER HISTORY & INVOICE ---
elif menu == "📜 Order History":
    st.title("📜 Past Orders")
    df = st.session_state.db["orders"]
    st.dataframe(df, use_container_width=True)
    
    selected_id = st.selectbox("Select Order ID for Invoice", df["id"].unique())
    if st.button("Generate PDF Invoice"):
        order_info = df[df["id"] == selected_id].iloc[0]
        pdf_bytes = create_pdf(order_info)
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Invoice_{selected_id}.pdf">📥 Download Invoice PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

# --- INVENTORY ---
elif menu == "📦 Inventory Control":
    st.title("📦 Stock Management")
    st.dataframe(st.session_state.db["stock"], use_container_width=True)

# --- AUDIT LOGS (ආරක්ෂාව) ---
elif menu == "🕵️ Audit Logs":
    st.title("🕵️ System Security Logs")
    st.write("මෙහි පද්ධතියේ සිදුවන සියලුම දත්ත වෙනස්වීම් පෙන්වයි.")
    st.table(st.session_state.db["orders"][["id", "date", "staff", "status"]])

# දත්ත ස්වයංක්‍රීයව Save කිරීම
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
