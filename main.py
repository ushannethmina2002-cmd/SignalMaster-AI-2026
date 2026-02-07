electbox("Courier Company", ["Koombiyo", "Domex", "Pronto", "Royal Express"])
                
                if st.form_submit_button("🚀 SAVE ENTRY"):
                    oid = f"HS-{uuid.uuid4().hex[:6].upper()}"
                    st.session_state.orders.append({
                        "id": oid, "name": name, "phone": phone, "addr": addr, "city": city, "dist": dist,
                        "prod": prod, "qty": qty, "price": price, "delivery": delivery, "discount": discount,
                        "total": (price * qty) + delivery - discount, "status": "pending", "date": str(date.today()), 
                        "courier": courier, "staff": st.session_state.current_user
                    })
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    st.success(f"Order {oid} Saved Successfully!")
        else: st.error("Staff access restricted for this action.")

    elif sub in ["View Lead", "Order Search"]:
        st.markdown('<div class="ship-header"><h3>🔍 Leads Search & Filter</h3>', unsafe_allow_html=True)
        fc1, fc2, fc3, fc4 = st.columns(4)
        s_status = fc1.selectbox("Filter Status", ["Any", "pending", "confirm", "noanswer", "rejected", "fake", "cancelled"])
        s_user = fc2.selectbox("Filter User", ["Any", "Admin", "demo1", "demo2", "demo3", "demo4", "demo5"])
        s_name = fc3.text_input("Search Name/Phone")
        s_range = fc4.date_input("Date Range", [date.today() - timedelta(days=30), date.today()])
        
        if st.button("Apply Advanced Filter", type="primary"): st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Status Tabs Summary
        def cnt_st(s): return len([o for o in st.session_state.orders if o.get('status') == s])
        st.markdown(f"""
            <div style="margin-bottom:20px;">
                <span class="status-tab" style="background:#4b5563;">Leads: {len(st.session_state.orders)}</span>
                <span class="status-tab" style="background:#6c757d;">Pending: {cnt_st('pending')}</span>
                <span class="status-tab" style="background:#28a745;">Confirm: {cnt_st('confirm')}</span>
                <span class="status-tab" style="background:#ffc107; color:black;">No Answer: {cnt_st('noanswer')}</span>
            </div>
        """, unsafe_allow_html=True)

        df = pd.DataFrame(st.session_state.orders)
        if not df.empty:
            if s_status != "Any": df = df[df['status'] == s_status]
            if s_user != "Any": df = df[df['staff'] == s_user]
            if s_name: df = df[df['name'].str.contains(s_name, case=False) | df['phone'].astype(str).str.contains(s_name)]
            
            # Action UI
            for idx, row in df.iterrows():
                with st.expander(f"📦 {row['id']} | {row['name']} | Status: {row['status'].upper()}"):
                    col1, col2, col3, col4, col5 = st.columns(5)
                    if col1.button("✅ OK", key=f"ok_{idx}"):
                        st.session_state.orders[idx]['status'] = 'confirm'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if col2.button("☎ Call", key=f"cl_{idx}"):
                        st.session_state.orders[idx]['status'] = 'noanswer'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if col3.button("🚫 Cancel", key=f"cn_{idx}"):
                        st.session_state.orders[idx]['status'] = 'cancelled'
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
                    if col4.button("🗑️ Delete", key=f"dl_{idx}"):
                        st.session_state.orders.pop(idx)
                        save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
            st.dataframe(df, use_container_width=True)

# --- 8. LOGISTICS (SHIPPED ITEMS) ---
elif menu == "🚚 Shipped Items":
    if sub == "Confirm Dispatch":
        st.subheader("✅ Confirm Orders for Dispatch")
        ready = [o for o in st.session_state.orders if o['status'] == 'confirm']
        if ready:
            for idx, o in enumerate(ready):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{o['id']}** - {o['name']} | {o['city']} | {o['prod']}")
                if c2.button("Ready to Print", key=f"pr_{idx}"):
                    o['status'] = 'ready_print'
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv'); st.rerun()
        else: st.info("No confirmed orders to dispatch.")

    elif sub == "Print Dispatch Items":
        st.subheader("🖨️ Printing & Shipping")
        to_ship = [o for o in st.session_state.orders if o['status'] == 'ready_print']
        if to_ship:
            for idx, o in enumerate(to_ship):
                st.markdown(f"**{o['id']}** - {o['name']} - {o['courier']}")
                if st.button(f"Mark as Shipped {o['id']}", key=f"ship_{idx}"):
                    # Stock Deduction
                    if o['prod'] in st.session_state.stocks:
                        st.session_state.stocks[o['prod']] -= int(o['qty'])
                    o['status'] = 'shipped'
                    save_data(pd.DataFrame(st.session_state.orders), 'orders.csv')
                    save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                    st.success(f"Waybill Generated for {o['id']}")
                    st.rerun()

# --- 9. GRN, EXPENSES & STOCKS ---
elif menu == "📦 GRN":
    st.subheader("📦 Goods Receive Note")
    with st.form("grn_new"):
        p = st.selectbox("Select Product", list(st.session_state.stocks.keys()))
        q = st.number_input("Received Quantity", min_value=1)
        if st.form_submit_button("Add to Inventory"):
            st.session_state.stocks[p] += q
            st.session_state.grn_history.append({"date": str(date.today()), "prod": p, "qty": q})
            save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
            save_data(pd.DataFrame(st.session_state.grn_history), 'grn.csv')
            st.success(f"Stock updated for {p}!")

elif menu == "💰 Expense":
    st.subheader("💰 Financial Tracking")
    with st.form("expense_entry"):
        c1, c2 = st.columns(2)
        cat = c1.selectbox("Category", ["Marketing", "FB Ads", "Salary", "Rent", "Packaging", "Courier"])
        amt = c2.number_input("Amount (LKR)", min_value=0.0)
        if st.form_submit_button("Log Expense"):
            st.session_state.expenses.append({"date": str(date.today()), "cat": cat, "amount": amt})
            save_data(pd.DataFrame(st.session_state.expenses), 'expenses.csv')
            st.success("Expense logged.")
    st.table(pd.DataFrame(st.session_state.expenses))

elif menu == "📊 Stocks":
    st.subheader("📈 Inventory Status Dashboard")
    df_stock = pd.DataFrame(st.session_state.stocks.items(), columns=["Product Name", "Available Qty"])
    st.table(df_stock)
    
    # Low Stock Alert
    low = df_stock[df_stock['Available Qty'] < 10]
    if not low.empty:
        st.warning(f"Critical Stock: {', '.join(low['Product Name'].tolist())}")

elif menu == "🛍️ Products":
    st.subheader("🛍️ Product Master Data")
    with st.form("new_product"):
        n_p = st.text_input("New Product Name")
        if st.form_submit_button("Create Product"):
            if n_p and n_p not in st.session_state.stocks:
                st.session_state.stocks[n_p] = 0
                save_data(pd.DataFrame(st.session_state.stocks.items(), columns=["Item", "Qty"]), 'stocks.csv')
                st.rerun()

# --- FOOTER & LOGOUT ---
st.sidebar.markdown("---")
if st.sidebar.button("🔓 Logout System"):
    st.session_state.authenticated = False
    st.rerun()
