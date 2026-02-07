import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import os
import plotly.express as px

# =========================================================
# 1. පද්ධතියේ පෙනුම (Professional Dark UI)
# =========================================================
st.set_page_config(page_title="HappyShop ERP v6.0", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .metric-card {
        background: #1a1c23; padding: 15px; border-radius: 10px;
        border-top: 4px solid #FFD700; text-align: center;
    }
    .metric-card h2 { color: #FFD700; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 2. දත්ත ගබඩාව (Reset & Load Logic)
# =========================================================
def load_data(file, cols):
    try:
        if os.path.exists(file):
            df = pd.read_csv(file)
            # තීරු වල නම් පරීක්ෂා කර නොතිබුණහොත් අලුතින් සාදයි
            for col in cols:
                if col not in df.columns:
                    return pd.DataFrame(columns=cols)
            return df
        return pd.DataFrame(columns=cols)
    except:
        return pd.DataFrame(columns=cols)

# පින්තූරවල තිබූ විදියට Column Names සකස් කිරීම
lead_cols = ["ID", "Date", "Customer", "Phone", "Location", "Product", "Qty", "Total", "Status", "Staff"]
stock_cols = ["Code", "Product", "Qty", "Price"]

if "db" not in st.session_state:
    st.session_state.db = {
        "leads": load_data("leads.csv", lead_cols),
        "stock": load_data("stock.csv", stock_cols)
    }

# ආරම්භක තොග (Default Stock)
if st.session_state.db["stock"].empty:
    st.session_state.db["stock"] = pd.DataFrame([
        {"Code": "KHO-01", "Product": "Kasharaja Hair Oil", "Qty": 225, "Price": 2950},
        {"Code": "HNC-02", "Product": "Herbal Night Cream", "Qty": 85, "Price": 1800}
    ])

# =========================================================
# 3. පද්ධතියේ ප්‍රධාන මෙනුව
# =========================================================
with st.sidebar:
    st.markdown("<h2 style='color: #FFD700;'>HAPPY SHOP ERP</h2>", unsafe_allow_html=True)
    menu = st.radio("Navigation", ["📊 Dashboard", "📝 Leads & Orders", "📦 Stock Manager"])
    
    st.divider()
    if st.button("🗑️ Reset All Data (Fix Errors)"):
        # Error එකක් එනවා නම් මේ බොත්තම එබූ විට පරණ CSV මැකී අලුත් ඒවා හැදේ
        for f in ["leads.csv", "stock.csv"]:
            if os.path.exists(f): os.remove(f)
        st.cache_data.clear()
        st.rerun()

# =========================================================
# 4. DASHBOARD (ඔයාගේ පින්තූරවල තිබූ විදියට)
# =========================================================
if menu == "📊 Dashboard":
    df = st.session_state.db["leads"]
    
    # Summary Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><h4>Total Leads</h4><h2>{len(df)}</h2></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><h4>Confirmed</h4><h2>{len(df[df["Status"]=="Confirmed"])}</h2></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><h4>No Answer</h4><h2>{len(df[df["Status"]=="No Answer"])}</h2></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><h4>On Hold</h4><h2>{len(df[df["Status"]=="Hold"])}</h2></div>', unsafe_allow_html=True)

    if not df.empty:
        fig = px.bar(df, x="Date", y="Total", color="Status", title="Sales Trend", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("තවම දත්ත ඇතුළත් කර නැත. 'Leads & Orders' වෙත ගොස් ඇතුළත් කරන්න.")

# =========================================================
# 5. LEADS & ORDERS (පින්තූරවල තිබූ විදියටම)
# =========================================================
elif menu == "📝 Leads & Orders":
    st.subheader("📝 Manage Leads & Orders")
    
    # Form to add new data
    with st.expander("➕ Add New Lead / Order"):
        with st.form("add_lead"):
            f1, f2 = st.columns(2)
            name = f1.text_input("Customer Name")
            phone = f1.text_input("Phone Number")
            loc = f1.text_input("Location (City)")
            prod = f2.selectbox("Product", st.session_state.db["stock"]["Product"])
            qty = f2.number_input("Quantity", 1)
            status = f2.selectbox("Status", ["Pending", "Confirmed", "No Answer", "Hold", "Cancelled"])
            
            if st.form_submit_button("Submit"):
                price = st.session_state.db["stock"].loc[st.session_state.db["stock"]["Product"] == prod, "Price"].values[0]
                new_id = f"HS-{uuid.uuid4().hex[:4].upper()}"
                new_data = {
                    "ID": new_id, "Date": str(date.today()), "Customer": name, "Phone": phone,
                    "Location": loc, "Product": prod, "Qty": qty, "Total": price*qty,
                    "Status": status, "Staff": "Admin"
                }
                st.session_state.db["leads"] = pd.concat([st.session_state.db["leads"], pd.DataFrame([new_data])], ignore_index=True)
                st.success("Data Saved!")
                st.rerun()

    st.dataframe(st.session_state.db["leads"], use_container_width=True)

# =========================================================
# 6. STOCK MANAGER
# =========================================================
elif menu == "📦 Stock Manager":
    st.subheader("📦 Inventory Levels")
    st.table(st.session_state.db["stock"])

# Save data
for key, df in st.session_state.db.items():
    df.to_csv(f"{key}.csv", index=False)
