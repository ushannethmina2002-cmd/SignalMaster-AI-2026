import streamlit as st
import pandas as pd
import os
import uuid
from datetime import datetime

# ==========================================
# 1. පද්ධති සැකසුම් (Professional Sidebar UI)
# ==========================================
st.set_page_config(page_title="HappyShop Ultimate ERP", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #333; }
    /* සයිඩ්බාර් එකේ පෙනුම ඔයාගේ CSS එකට අනුව */
    [data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #ddd;
    }
    .nav-item {
        display: block; padding: 10px 15px;
        text-decoration: none; color: #333;
        font-size: 14px; border-radius: 5px;
        margin-bottom: 2px;
    }
    .nav-item:hover { background-color: #f2f2f2; }
    .main-content { margin-left: 20px; padding: 20px; }
    .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. Database Logic (Menus, Products, Orders)
# ==========================================

# මෙනු දත්ත ගබඩාව (ඔයා එවපු INSERT INTO ටික)
if "menus" not in st.session_state:
    initial_menus = [
        {'id': 1, 'title': 'Dashboard', 'link': 'Dashboard', 'icon': '📊'},
        {'id': 2, 'title': 'New Order', 'link': 'New Order', 'icon': '📝'},
        {'id': 3, 'title': 'Stock', 'link': 'Stock', 'icon': '📦'},
        {'id': 4, 'title': 'WhatsApp', 'link': 'WhatsApp', 'icon': '💬'},
        {'id': 5, 'title': 'Profit', 'link': 'Profit', 'icon': '💰'},
        {'id': 6, 'title': 'Menu Manager', 'link': 'Menu Manager', 'icon': '⚙️'}
    ]
    # මෙහි ඔයා එවපු අනෙක් මෙනු 40ම පද්ධතියට ඇතුළත් කළ හැක.
    st.session_state.menus = pd.DataFrame(initial_menus)

# නිෂ්පාදන දත්ත (SQL INSERT INTO ටික)
if "products" not in st.session_state:
    st.session_state.products = pd.DataFrame([
        {'id': 1, 'name': 'Kesharaja Hair Oil', 'code': 'VGLS0005', 'price': 2950, 'stock': 228},
        {'id': 2, 'name': 'Herbal Crown', 'code': 'VGLS0001', 'price': 1800, 'stock': 53},
        {'id': 3, 'name': 'Medahani Kalkaya', 'code': 'VGLS0003', 'price': 1200, 'stock': 597},
        {'id': 4, 'name': 'Maas Go Capsules', 'code': 'VGLS0006', 'price': 2500, 'stock': 90}
    ])

if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame(columns=["id", "customer", "total", "payment", "date"])

# ==========================================
# 3. Dynamic Sidebar (ඔයා එවපු PHP Logic එක)
# ==========================================
with st.sidebar:
    st.markdown("### 🛒 ORDER SYSTEM")
    st.divider()
    
    # මෙනු ලැයිස්තුව පෙන්වීම
    selection = "Dashboard" # Default
    for index, row in st.session_state.menus.iterrows():
        if st.button(f"{row['icon']} {row['title']}", key=f"menu_{row['id']}", use_container_width=True):
            st.session_state.current_page = row['link']
    
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"

# ==========================================
# 4. පද්ධතියේ පිටු (Pages)
# ==========================================
page = st.session_state.current_page

# --- MENU MANAGER (ඔයාගේ PHP CRUD Logic එක) ---
if page == "Menu Manager":
    st.title("⚙️ Menu Manager")
    
    # Add Menu Form
    with st.expander("➕ Add New Menu Item"):
        with st.form("add_menu"):
            m_title = st.text_input("Title")
            m_link = st.text_input("Link Name")
            m_icon = st.text_input("Icon (Emoji)")
            if st.form_submit_button("Add Menu"):
                new_id = st.session_state.menus['id'].max() + 1
                new_row = {'id': new_id, 'title': m_title, 'link': m_link, 'icon': m_icon}
                st.session_state.menus = pd.concat([st.session_state.menus, pd.DataFrame([new_row])], ignore_index=True)
                st.rerun()

    # Menu Table & Delete
    st.table(st.session_state.menus)
    del_id = st.number_input("Enter Menu ID to Delete", min_value=1, step=1)
    if st.button("Delete Menu"):
        st.session_state.menus = st.session_state.menus[st.session_state.menus['id'] != del_id]
        st.rerun()

# --- DASHBOARD ---
elif page == "Dashboard":
    st.title("📊 Business Dashboard")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", len(st.session_state.orders))
    col2.metric("Total Revenue", f"Rs. {st.session_state.orders['total'].sum():,.2f}")
    col3.metric("Low Stock Items", len(st.session_state.products[st.session_state.products['stock'] < 100]))
    
    st.divider()
    st.subheader("Recent Orders")
    st.dataframe(st.session_state.orders, use_container_width=True)

# --- NEW ORDER ---
elif page == "New Order":
    st.title("📝 Create New Order")
    with st.form("order_form"):
        c_name = st.text_input("Customer Name")
        c_contact = st.text_input("Contact")
        c_city = st.text_input("City")
        c_pay = st.selectbox("Payment Method", ["COD", "Card"])
        
        # Multi-product Selection
        selected_p = st.multiselect("Select Products", st.session_state.products['name'])
        
        if st.form_submit_button("Save Order"):
            total_price = 0
            for p_name in selected_p:
                price = st.session_state.products.loc[st.session_state.products['name'] == p_name, 'price'].values[0]
                total_price += price
                # Stock Update
                st.session_state.products.loc[st.session_state.products['name'] == p_name, 'stock'] -= 1
            
            new_order = {
                "id": len(st.session_state.orders) + 1,
                "customer": c_name,
                "total": total_price,
                "payment": c_pay,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_order])], ignore_index=True)
            st.success("Order Created Successfully!")

# --- STOCK ---
elif page == "Stock":
    st.title("📦 Stock Inventory")
    st.dataframe(st.session_state.products, use_container_width=True)

# --- අනෙකුත් පිටු (Placeholders) ---
else:
    st.title(f"{page}")
    st.info(f"This is the {page} module. You can add specific logic here.")
