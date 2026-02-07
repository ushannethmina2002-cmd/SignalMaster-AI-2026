import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid

# ==========================================
# 1. පද්ධති සැකසුම් (UI)
# ==========================================
st.set_page_config(page_title="Pro Order System", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .main-card { background: #1a1c23; padding: 20px; border-radius: 10px; border: 1px solid #333; }
    .stock-card { background: #161b22; padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #00d4ff; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Database Logic (SQL එකට සමානව)
# ==========================================
if "products" not in st.session_state:
    st.session_state.products = pd.DataFrame([
        {'id': 1, 'name': 'Kesharaja Hair Oil', 'code': 'VGLS0005', 'price': 2950, 'stock': 228},
        {'id': 2, 'name': 'Herbal Crown', 'code': 'VGLS0001', 'price': 1800, 'stock': 53},
        {'id': 3, 'name': 'Medahani Kalkaya', 'code': 'VGLS0003', 'price': 1200, 'stock': 597},
        {'id': 4, 'name': 'Maas Go Capsules', 'code': 'VGLS0006', 'price': 2500, 'stock': 90}
    ])

if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame(columns=["id", "customer", "contact", "city", "address", "payment", "total", "items"])

# ==========================================
# 3. ප්‍රධාන පාලක පුවරුව (Main Layout)
# ==========================================
st.title("📦 Advanced Order & Stock System")

col1, col2 = st.columns([1.2, 0.8])

# --- වම් පස: නව ඇණවුම (New Order) ---
with col1:
    st.subheader("🛒 New Order Form")
    with st.container():
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        c_name = st.text_input("Customer Name")
        c_contact = st.text_input("Contact Number")
        
        col_a, col_b = st.columns(2)
        c_city = col_a.text_input("City")
        c_pay = col_b.selectbox("Payment Method", ["COD", "Card"])
        c_address = st.text_area("Address")

        st.markdown("---")
        st.write("🛍️ **Order Items**")
        
        # අයිතම කිහිපයක් ඇඩ් කිරීමේ පහසුකම (Multi-item logic)
        if "temp_items" not in st.session_state:
            st.session_state.temp_items = []

        selected_p = st.selectbox("Select Product", st.session_state.products['name'])
        p_qty = st.number_input("Quantity", min_value=1, value=1)
        
        if st.button("+ Add to List"):
            p_data = st.session_state.products[st.session_state.products['name'] == selected_p].iloc[0]
            st.session_state.temp_items.append({
                "name": selected_p,
                "qty": p_qty,
                "price": p_data['price'],
                "subtotal": p_data['price'] * p_qty
            })

        # දැනට ලිස්ට් එකේ තියෙන බඩු පෙන්වීම
        if st.session_state.temp_items:
            item_df = pd.DataFrame(st.session_state.temp_items)
            st.table(item_df)
            grand_total = item_df['subtotal'].sum()
            st.metric("Grand Total (LKR)", f"{grand_total:,.2f}")

            if st.button("🚀 Save Complete Order"):
                order_id = len(st.session_state.orders) + 1
                new_order = {
                    "id": order_id,
                    "customer": c_name,
                    "contact": c_contact,
                    "city": c_city,
                    "address": c_address,
                    "payment": c_pay,
                    "total": grand_total,
                    "items": str(st.session_state.temp_items)
                }
                
                # Stock Update කිරීම (PHP Code එකේ තිබූ Update Logic එක)
                for item in st.session_state.temp_items:
                    st.session_state.products.loc[st.session_state.products['name'] == item['name'], 'stock'] -= item['qty']
                
                st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_order])], ignore_index=True)
                st.session_state.temp_items = [] # Reset list
                st.success("Order Saved Successfully and Stock Updated!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- දකුණු පස: තොග පාලනය (Stock Adjustment) ---
with col2:
    st.subheader("⚙️ Stock Adjustment")
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    for index, row in st.session_state.products.iterrows():
        st.markdown(f'''
        <div class="stock-card">
            <small>{row['code']}</small><br>
            <b>{row['name']}</b><br>
            Current Stock: {row['stock']}
        </div>
        ''', unsafe_allow_html=True)
        new_s = st.number_input(f"Update {row['name']}", value=int(row['stock']), key=f"stock_{row['id']}")
        st.session_state.products.at[index, 'stock'] = new_s

    if st.button("Update All Stock"):
        st.success("Stock levels updated manually!")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. ඇණවුම් ලේඛනය (Orders Table)
# ==========================================
st.divider()
st.subheader("📜 Recent Orders")
st.dataframe(st.session_state.orders, use_container_width=True)
