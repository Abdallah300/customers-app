import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import qrcode
from io import BytesIO
import base64

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================
st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; }
    .report-table th { background-color: #28a745; color: white; }
    .warning-row { background-color: #ffcccc !important; color: black !important; }
    .qr-box { border: 2px dashed #28a745; padding: 15px; text-align: center; background: #f0fff0; border-radius: 10px; margin: 10px; }
    .client-card { border: 2px solid #28a745; padding: 15px; border-radius: 10px; margin: 10px 0; background: #f9fff9; }
    .balance-positive { color: green; font-weight: bold; }
    .balance-negative { color: red; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# إدارة ملفات البيانات
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f: 
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)

# تأمين حساب المدير
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# دالة لإنشاء QR code كصورة base64
def generate_qr_code(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="green", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# ================== 2. نظام الدخول ==================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "qr_scanned" not in st.session_state: st.session_state.qr_scanned = None

if not st.session_state.logged_in:
    st.title("💧 Power Life Ultra - دخول")
    u_in = st.text_input("اسم المستخدم")
    p_in = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else: st.error("بيانات غير صحيحة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    
    menu = ["📋 قائمة العملاء", "➕ إضافة عميل", "🛠️ إضافة صيانة", "🔍 بحث وتعديل", "💰 أرباح الشركة"]
    if user_now['role'] == "admin":
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    menu.append("📱 مسح باركود العميل")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- 1. إضافة عميل (بالمميزات الجديدة والباركود) ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد - بيانات تفصيلية")
        with st.form("new_c_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم العميل", required=True)
                phone = st.text_input("رقم الهاتف", required=True)
                gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
                center = st.text_input("المركز")
            with col2:
                village = st.text_input("البلد/القرية")
                ctype = st.selectbox("نوع الجهاز/العميل", ["جهاز جديد", "جهاز قديم", "عميل شركة"])
                loc = st.text_input("الإحداثيات (30.1, 31.2)")
                balance = st.number_input("الرصيد الابتدائي", value=0.0)
            
            if st.form_submit_button("حفظ العميل وإصدار الباركود"):
                if name and phone:
                    new_id = len(customers) + 1
                    c_data = {
                        "id": new_id, 
                        "name": name, 
                        "phone": phone, 
                        "gov": gov,
                        "center": center, 
                        "village": village, 
                        "type": ctype,
                        "location": loc, 
                        "history": [],
                        "initial_balance": balance,
                        "current_balance": balance,
                        "created_at": str(datetime.now().date()),
                        "qr_code": f"PL-{new_id}-{datetime.now().strftime('%Y%m%d')}"
                    }
                    customers.append(c_data)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success(f"✅ تم الحفظ بنجاح للعميل رقم: {new_id}")
                    
                    # إنشاء وعرض QR code
                    qr_data = f"POWERLIFE_CLIENT_ID:{new_id},NAME:{name},PHONE:{phone}"
                    qr_img = generate_qr_code(qr_data)
                    
                    col_qr1, col_qr2 = st.columns(2)
                    with col_qr1:
                        st.markdown(f"""
                        <div class='qr-box'>
                            <h4>🤳 باركود العميل: {name}</h4>
                            <img src="data:image/png;base64,{qr_img}" width="200">
                            <p><strong>كود العميل: PL-{new_id}</strong></p>
                            <p>رقم الهاتف: {phone}</p>
                            <p>تاريخ التسجيل: {datetime.now().date()}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_qr2:
                        st.markdown("""
                        ### 📋 تعليمات استخدام الباركود:
                        1. يمكن مسح الباركود من خلال تطبيق الكاميرا
                        2. أو استخدام تطبيق ماسح الباركود
                        3. البيانات ستظهر مباشرة في نظام المسح
                        4. حفظ الباركود للعميل للاستخدام المستقبلي
                        """)
                else:
                    st.error("⚠️ يرجى ملء اسم العميل ورقم الهاتف")

    # --- 2. قائمة العملاء (تقرير شامل مع الباركود) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 جميع العملاء المسجلين")
        
        # فلترة وعرض
        search_term = st.text_input("🔍 بحث في قائمة العملاء")
        filtered_customers = customers
        if search_term:
            filtered_customers = [c for c in customers if search_term.lower() in c['name'].lower() or search_term in c['phone']]
        
        if filtered_customers:
            st.info(f"📊 عدد العملاء: {len(filtered_customers)}")
            
            # عرض العملاء في شبكة
            cols_per_row = 3
            for i in range(0, len(filtered_customers), cols_per_row):
                cols = st.columns(cols_per_row)
                for j in range(cols_per_row):
                    if i + j < len(filtered_customers):
                        client = filtered_customers[i + j]
                        with cols[j]:
                            # حساب إجمالي المدفوعات
                            total_paid = sum(h['التكلفة'] for h in client.get('history', []))
                            balance_status = "🟢" if client.get('current_balance', 0) >= 0 else "🔴"
                            
                            # إنشاء QR code للعميل
                            qr_data = f"POWERLIFE_CLIENT_ID:{client['id']},NAME:{client['name']},PHONE:{client['phone']}"
                            qr_img = generate_qr_code(qr_data)
                            
                            st.markdown(f"""
                            <div class='client-card'>
                                <h4>{balance_status} {client['name']}</h4>
                                <p><strong>📞:</strong> {client['phone']}</p>
                                <p><strong>📍:</strong> {client['gov']}</p>
                                <p><strong>💳 الرصيد:</strong> <span class="{'balance-positive' if client.get('current_balance', 0) >= 0 else 'balance-negative'}">{client.get('current_balance', 0)} جنيه</span></p>
                                <p><strong>💰 المدفوع:</strong> {total_paid} جنيه</p>
                                <div style="text-align:center; margin:10px 0">
                                    <img src="data:image/png;base64,{qr_img}" width="120">
                                    <p style="font-size:12px; margin-top:5px">كود: {client['qr_code']}</p>
                                </div>
                                <button onclick="location.href='?client_id={client['id']}'" style="width:100%; padding:5px; background:#28a745; color:white; border:none; border-radius:5px; cursor:pointer">
                                    عرض التفاصيل
                                </button>
                            </div>
                            """, unsafe_allow_html=True)
            
            # جدول تفصيلي
            st.subheader("📋 جدول تفصيلي للعملاء")
            rows = ""
            for c in filtered_customers:
                last_service = "لا يوجد" if not c.get('history') else c['history'][-1]['التاريخ']
                total_services = len(c.get('history', []))
                total_paid = sum(h['التكلفة'] for h in c.get('history', []))
                
                rows += f"""
                <tr>
                    <td>{c['name']}</td>
                    <td>{c['phone']}</td>
                    <td>{c['gov']}</td>
                    <td>{c['type']}</td>
                    <td>{c['qr_code']}</td>
                    <td>{total_services}</td>
                    <td>{last_service}</td>
                    <td class="{'balance-positive' if c.get('current_balance', 0) >= 0 else 'balance-negative'}">{c.get('current_balance', 0)}</td>
                    <td>{total_paid}</td>
                </tr>
                """
            
            st.markdown(f"""
            <table class='report-table'>
                <thead>
                    <tr>
                        <th>العميل</th>
                        <th>الهاتف</th>
                        <th>المحافظة</th>
                        <th>النوع</th>
                        <th>كود الباركود</th>
                        <th>عدد الصيانات</th>
                        <th>آخر صيانة</th>
                        <th>الرصيد</th>
                        <th>إجمالي المدفوع</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.warning("لا توجد عملاء مسجلين" if not search_term else "لا توجد نتائج للبحث")

    # --- 3. مسح باركود العميل وعرض بياناته ---
    elif choice == "📱 مسح باركود العميل":
        st.subheader("📱 مسح باركود العميل")
        
        # محاكاة مسح الباركود
        col_scan, col_info = st.columns([1, 2])
        
        with col_scan:
            st.markdown("### 🔍 محاكاة المسح")
            scan_method = st.radio("طريقة المسح:", ["إدخال يدوي", "رفع صورة باركود"])
            
            if scan_method == "إدخال يدوي":
                scanned_code = st.text_input("أدخل كود العميل (PL-رقم):")
                if scanned_code and st.button("🔍 مسح الكود"):
                    # استخراج رقم العميل من الكود
                    try:
                        client_id = int(scanned_code.split("-")[1])
                        st.session_state.qr_scanned = client_id
                        st.success(f"✅ تم مسح كود العميل: {scanned_code}")
                    except:
                        st.error("❌ كود غير صالح")
            
            else:
                uploaded_file = st.file_uploader("رفع صورة الباركود", type=['png', 'jpg', 'jpeg'])
                if uploaded_file:
                    st.image(uploaded_file, caption="صورة الباركود المرفوعة", width=200)
                    # في التطبيق الحقيقي، نستخدم مكتبة لقراءة الباركود
                    st.info("في التطبيق الحقيقي، سيتم قراءة الباركود تلقائياً")
        
        with col_info:
            # عرض بيانات العميل إذا تم المسح
            client_id_to_show = st.session_state.qr_scanned
            if client_id_to_show:
                client = next((c for c in customers if c['id'] == client_id_to_show), None)
                if client:
                    st.markdown(f"""
                    <div style="background:#e8f5e8; padding:20px; border-radius:10px; border-right:5px solid #28a745">
                        <h3>👤 بيانات العميل</h3>
                        <p><strong>الاسم:</strong> {client['name']}</p>
                        <p><strong>الهاتف:</strong> {client['phone']}</p>
                        <p><strong>العنوان:</strong> {client['gov']} - {client['center']} - {client['village']}</p>
                        <p><strong>نوع الجهاز:</strong> {client['type']}</p>
                        <p><strong>تاريخ التسجيل:</strong> {client['created_at']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # حساب المبالغ
                    total_paid = sum(h['التكلفة'] for h in client.get('history', []))
                    balance = client.get('current_balance', 0)
                    
                    col_balance, col_paid = st.columns(2)
                    with col_balance:
                        st.metric("💰 الرصيد الحالي", f"{balance} جنيه", delta=f"{'أرصدة دائنة' if balance >= 0 else 'مدين'}")
                    with col_paid:
                        st.metric("💳 إجمالي المدفوعات", f"{total_paid} جنيه")
                    
                    # سجل الصيانات والدفعات
                    st.subheader("📋 سجل الصيانات والدفعات")
                    if client.get('history'):
                        rows = ""
                        for h in client['history']:
                            rows += f"""
                            <tr>
                                <td>{h['التاريخ']}</td>
                                <td>{h['الفني']}</td>
                                <td>{h['العمل']}</td>
                                <td>{h['التكلفة']} جنيه</td>
                                <td>{'✅' if h['التكلفة'] > 0 else '📝'}</td>
                            </tr>
                            """
                        
                        st.markdown(f"""
                        <table class='report-table'>
                            <thead>
                                <tr>
                                    <th>التاريخ</th>
                                    <th>اسم الفني</th>
                                    <th>نوع العمل/الشمع</th>
                                    <th>المبلغ</th>
                                    <th>الحالة</th>
                                </tr>
                            </thead>
                            <tbody>{rows}</tbody>
                        </table>
                        """, unsafe_allow_html=True)
                        
                        # إحصاءات
                        technicians = set(h['الفني'] for h in client['history'])
                        st.info(f"👷 الفنيون الذين تعاملوا مع العميل: {', '.join(technicians)}")
                    else:
                        st.info("لا توجد صيانات مسجلة لهذا العميل")
                    
                    # إضافة صيانة جديدة مباشرة
                    with st.expander("➕ إضافة صيانة/دفعة جديدة"):
                        with st.form(f"add_service_{client['id']}"):
                            work_type = st.selectbox("نوع العمل", ["تغيير شمع", "صيانة دورية", "دفعة مالية", "أخرى"])
                            work_details = st.multiselect("تفاصيل الشمع/العمل", ["1", "2", "3", "M", "S", "كربون", "موتور", "فلتر", "كهرباء"])
                            amount = st.number_input("المبلغ", min_value=0, value=0)
                            technician = st.selectbox("اسم الفني", [u['username'] for u in users if u['role'] == 'technician'])
                            
                            if st.form_submit_button("حفظ الصيانة"):
                                new_service = {
                                    "التاريخ": str(datetime.now().date()),
                                    "الفني": technician,
                                    "العمل": f"{work_type}: {', '.join(work_details)}",
                                    "التكلفة": amount
                                }
                                client['history'].append(new_service)
                                # تحديث الرصيد
                                client['current_balance'] = client.get('current_balance', 0) - amount
                                save_data(CUSTOMERS_FILE, customers)
                                st.success("✅ تم إضافة الصيانة بنجاح")
                                st.rerun()
                else:
                    st.error("❌ العميل غير موجود")
            else:
                st.info("🔍 قم بمسح باركود العميل لعرض بياناته")

    # --- 4. بحث وتعديل (عرض رصيد الحساب وسجل الشمع) ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 كشف حساب العميل")
        search = st.text_input("ابحث بالاسم أو الهاتف")
        if search:
            results = [c for c in customers if search.lower() in c['name'].lower() or search in c['phone']]
            for c in results:
                with st.expander(f"👤 ملف: {c['name']} - {c['type']} - الرصيد: {c.get('current_balance', 0)} جنيه"):
                    col_info, col_qr = st.columns([2, 1])
                    with col_info:
                        st.write(f"**📞 الهاتف:** {c['phone']}")
                        st.write(f"**📍 العنوان:** {c['gov']} - {c['center']} - {c['village']}")
                        st.write(f"**📅 تاريخ التسجيل:** {c['created_at']}")
                        st.write(f"**🆔 كود الباركود:** {c['qr_code']}")
                    
                    with col_qr:
                        qr_data = f"POWERLIFE_CLIENT_ID:{c['id']},NAME:{c['name']},PHONE:{c['phone']}"
                        qr_img = generate_qr_code(qr_data)
                        st.image(f"data:image/png;base64,{qr_img}", width=150)
                    
                    total_paid = sum(h['التكلفة'] for h in c.get('history', []))
                    st.success(f"💰 إجمالي المدفوعات: {total_paid} جنيه")
                    
                    if c.get('history'):
                        st.subheader("📋 سجل المعاملات")
                        df_history = pd.DataFrame(c['history'])
                        st.dataframe(df_history, use_container_width=True)
                        
                        # إحصاءات
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            last_service = c['history'][-1]['التاريخ'] if c['history'] else "لا يوجد"
                            st.metric("📅 آخر معاملة", last_service)
                        with col2:
                            tech_count = len(set(h['الفني'] for h in c['history']))
                            st.metric("👷 عدد الفنيين", tech_count)
                        with col3:
                            avg_amount = total_paid / len(c['history']) if c['history'] else 0
                            st.metric("💸 متوسط المبلغ", f"{avg_amount:.2f} جنيه")
                    
                    # أزرار التحكم
                    col_del, col_edit, col_print = st.columns(3)
                    with col_del:
                        if st.button("🗑️ حذف العميل", key=f"del_{c['id']}"):
                            customers.remove(c)
                            save_data(CUSTOMERS_FILE, customers)
                            st.success("تم حذف العميل")
                            st.rerun()
                    with col_edit:
                        if st.button("✏️ تعديل البيانات", key=f"edit_{c['id']}"):
                            st.session_state.edit_client = c['id']
                    with col_print:
                        if st.button("🖨️ طباعة الكشف", key=f"print_{c['id']}"):
                            st.info("جاري إعداد طباعة الكشف...")

    # --- بقية الوظائف (كما هي مع تحسينات بسيطة) ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة/دفعة جديدة")
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']} (رصيد: {x.get('current_balance', 0)} جنيه)")
            with st.form("s_form"):
                work_type = st.selectbox("نوع العمل", ["تغيير شمع", "صيانة دورية", "دفعة مالية", "أخرى"])
                work = st.multiselect("الشمع المغير/تفاصيل العمل", ["1", "2", "3", "M", "S", "كربون", "موتور", "فلتر", "كهرباء", "تنظيف", "فحص"])
                price = st.number_input("المبلغ", min_value=0, value=0)
                notes = st.text_area("ملاحظات إضافية")
                
                if st.form_submit_button("💾 حفظ الصيانة"):
                    h = {
                        "التاريخ": str(datetime.now().date()),
                        "الفني": user_now['username'],
                        "العمل": f"{work_type}: {', '.join(work)}",
                        "ملاحظات": notes,
                        "التكلفة": price
                    }
                    for cust in customers:
                        if cust['id'] == target['id']: 
                            cust['history'].append(h)
                            # تحديث الرصيد
                            cust['current_balance'] = cust.get('current_balance', 0) - price
                    save_data(CUSTOMERS_FILE, customers)
                    st.success(f"✅ تم إضافة الصيانة للعميل {target['name']}")
                    
                    # عرض إشعار نجاح
                    st.balloons()

    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 مواقع الفنيين الحالية")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            t_rows = ""
            for u in techs:
                link = f"https://www.google.com/maps?q={u.get('lat',0)},{u.get('lon',0)}"
                t_rows += f"<tr><td>{u['username']}</td><td>{u.get('lat','-')}</td><td>{u.get('lon','-')}</td><td><a href='{link}' target='_blank'>فتح الخريطة 📍</a></td></tr>"
            st.markdown(f"<table class='report-table'><thead><tr><th>الفني</th><th>Lat</th><th>Lon</th><th>الموقع مباشر</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
            
            # إحصاءات الفنيين
            st.subheader("📊 إحصاءات أداء الفنيين")
            tech_stats = []
            for tech in techs:
                tech_name = tech['username']
                # حساب عدد العملاء الذين خدمهم الفني
                tech_customers = []
                for c in customers:
                    for h in c.get('history', []):
                        if h['الفني'] == tech_name:
                            tech_customers.append(c['name'])
                
                total_income = 0
                for c in customers:
                    for h in c.get('history', []):
                        if h['الفني'] == tech_name:
                            total_income += h['التكلفة']
                
                tech_stats.append({
                    "الفني": tech_name,
                    "عدد العملاء": len(set(tech_customers)),
                    "إجمالي الإيرادات": total_income
                })
            
            if tech_stats:
                df_stats = pd.DataFrame(tech_stats)
                st.dataframe(df_stats, use_container_width=True)
        else: 
            st.info("لا يوجد فنيين مسجلين")

    elif choice == "💰 أرباح الشركة":
        st.subheader("📊 تقرير الدخل المالي")
        all_income = []
        for c in customers:
            for h in c.get('history', []): 
                all_income.append({
                    **h,
                    "العميل": c['name'],
                    "الهاتف": c['phone']
                })
        
        if all_income:
            df = pd.DataFrame(all_income)
            
            # إجمالي الأرباح
            total_income = df['التكلفة'].sum()
            
            # إحصائيات
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 إجمالي الدخل", f"{total_income:,} جنيه")
            with col2:
                st.metric("👥 عدد العملاء", len(customers))
            with col3:
                st.metric("🔧 عدد المعاملات", len(df))
            with col4:
                avg_per_transaction = total_income / len(df) if len(df) > 0 else 0
                st.metric("💸 متوسط المعاملة", f"{avg_per_transaction:.2f} جنيه")
            
            # تفاصيل الدخل حسب التاريخ
            st.subheader("📅 الدخل حسب التاريخ")
            df['التاريخ'] = pd.to_datetime(df['التاريخ'])
            daily_income = df.groupby(df['التاريخ'].dt.date)['التكلفة'].sum().reset_index()
            daily_income = daily_income.sort_values('التاريخ', ascending=False)
            
            st.dataframe(daily_income, use_container_width=True)
            
            # مخطط بياني
            st.subheader("📈 مخطط الدخل اليومي")
            st.bar_chart(daily_income.set_index('التاريخ'))
            
            # أفضل الفنيين أداءً
            st.subheader("👑 أفضل الفنيين أداءً")
            tech_performance = df.groupby('الفني')['التكلفة'].agg(['sum', 'count']).reset_index()
            tech_performance = tech_performance.sort_values('sum', ascending=False)
            tech_performance.columns = ['الفني', 'إجمالي الدخل', 'عدد المعاملات']
            
            st.dataframe(tech_performance, use_container_width=True)
        else: 
            st.info("لا توجد بيانات مالية")

    elif choice == "👤 إضافة فني جديد":
        with st.form("add_t"):
            nu = st.text_input("اسم الفني")
            np = st.text_input("كلمة المرور")
            phone = st.text_input("رقم هاتف الفني")
            if st.form_submit_button("إضافة"):
                users.append({
                    "username": nu, 
                    "password": np, 
                    "phone": phone,
                    "role": "technician", 
                    "lat": 30.0444, 
                    "lon": 31.2357,
                    "joined_date": str(datetime.now().date())
                })
                save_data(USERS_FILE, users)
                st.success(f"✅ تم إضافة الفني {nu} بنجاح")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.session_state.qr_scanned = None
        st.rerun()
