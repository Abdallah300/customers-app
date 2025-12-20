import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================
st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; }
    .report-table th { background-color: #28a745; color: white; }
    .warning-row { background-color: #ffcccc !important; color: black !important; }
    .qr-box { border: 2px dashed #28a745; padding: 15px; text-align: center; background: #f0fff0; border-radius: 10px; }
    .client-card { border: 1px solid #28a745; padding: 10px; margin: 5px; border-radius: 5px; }
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

# ================== 2. نظام الدخول ==================
if "logged_in" not in st.session_state: st.session_state.logged_in = False

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
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- 1. إضافة عميل (بالمميزات الجديدة والباركود) ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد - بيانات تفصيلية")
        with st.form("new_c_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم الهاتف")
                gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
                center = st.text_input("المركز")
            with col2:
                village = st.text_input("البلد/القرية")
                ctype = st.selectbox("نوع الجهاز/العميل", ["جهاز جديد", "جهاز قديم", "عميل شركة"])
                loc = st.text_input("الإحداثيات (30.1, 31.2)")
            
            if st.form_submit_button("حفظ العميل وإصدار الباركود"):
                new_id = len(customers) + 1
                c_data = {
                    "id": new_id, "name": name, "phone": phone, "gov": gov,
                    "center": center, "village": village, "type": ctype,
                    "location": loc, "history": [], "created_at": str(datetime.now().date()),
                    "qr_code": f"PL-{new_id}"
                }
                customers.append(c_data)
                save_data(CUSTOMERS_FILE, customers)
                st.success(f"✅ تم الحفظ بنجاح للعميل رقم: {new_id}")
                
                # عرض باركود رقمي بسيط (QR Code Link)
                st.markdown(f"""
                <div class='qr-box'>
                    <h4>🤳 باركود العميل: {name}</h4>
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=POWERLIFE_{new_id}_{name}">
                    <p>كود العميل الرقمي: PL-{new_id}</p>
                    <p>📞 الهاتف: {phone}</p>
                    <p>📍 العنوان: {gov} - {center}</p>
                </div>
                """, unsafe_allow_html=True)

    # --- 2. قائمة العملاء (تقرير شامل) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 جميع العملاء المسجلين")
        
        if customers:
            # قسم الباركود السريع
            st.markdown("---")
            st.subheader("🔍 مسح باركود عميل")
            qr_search = st.text_input("أدخل كود العميل (PL-رقم) للمسح السريع:")
            
            if qr_search:
                try:
                    search_id = int(qr_search.replace("PL-", "").strip())
                    client = next((c for c in customers if c['id'] == search_id), None)
                    if client:
                        st.success(f"✅ تم العثور على العميل: {client['name']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div style='background:#e8f5e8; padding:15px; border-radius:10px;'>
                                <h4>👤 بيانات العميل</h4>
                                <p><strong>الاسم:</strong> {client['name']}</p>
                                <p><strong>الهاتف:</strong> {client['phone']}</p>
                                <p><strong>العنوان:</strong> {client['gov']} - {client['center']} - {client['village']}</p>
                                <p><strong>نوع الجهاز:</strong> {client['type']}</p>
                                <p><strong>تاريخ التسجيل:</strong> {client['created_at']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            # حساب إجمالي المدفوعات والرصيد
                            total_paid = sum(h['التكلفة'] for h in client.get('history', []))
                            st.markdown(f"""
                            <div style='background:#e3f2fd; padding:15px; border-radius:10px;'>
                                <h4>💰 الحساب المالي</h4>
                                <p><strong>إجمالي المدفوعات:</strong> {total_paid} جنيه</p>
                                <p><strong>عدد الصيانات:</strong> {len(client.get('history', []))}</p>
                                <p><strong>كود الباركود:</strong> {client['qr_code']}</p>
                                <p><strong>آخر صيانة:</strong> {client['history'][-1]['التاريخ'] if client.get('history') else 'لا يوجد'}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # عرض سجل الصيانات
                        if client.get('history'):
                            st.subheader("📋 سجل الصيانات والدفعات")
                            rows = ""
                            for h in client['history']:
                                rows += f"""
                                <tr>
                                    <td>{h['التاريخ']}</td>
                                    <td>{h['الفني']}</td>
                                    <td>{h['العمل']}</td>
                                    <td>{h['التكلفة']} جنيه</td>
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
                                    </tr>
                                </thead>
                                <tbody>{rows}</tbody>
                            </table>
                            """, unsafe_allow_html=True)
                            
                            # عرض إحصائية بالفنيين
                            technicians = list(set(h['الفني'] for h in client['history']))
                            if technicians:
                                st.info(f"👷 الفنيون الذين تعاملوا مع العميل: {', '.join(technicians)}")
                        else:
                            st.info("لا توجد صيانات مسجلة لهذا العميل")
                    else:
                        st.error("❌ لم يتم العثور على عميل بهذا الكود")
                except:
                    st.error("❌ كود غير صالح. الرجاء إدخال كود مثل: PL-1")
            
            st.markdown("---")
            
            # عرض جميع العملاء
            st.subheader("📊 جميع العملاء")
            search_term = st.text_input("بحث في قائمة العملاء:")
            
            filtered_customers = customers
            if search_term:
                filtered_customers = [c for c in customers if search_term.lower() in c['name'].lower() or search_term in c['phone'] or search_term in c['qr_code']]
            
            if filtered_customers:
                # إنشاء جدول بجميع البيانات
                rows = ""
                for c in filtered_customers:
                    total_paid = sum(h['التكلفة'] for h in c.get('history', []))
                    last_service = c['history'][-1]['التاريخ'] if c.get('history') else 'لا يوجد'
                    service_count = len(c.get('history', []))
                    
                    rows += f"""
                    <tr>
                        <td>{c['name']}</td>
                        <td>{c['phone']}</td>
                        <td>{c['gov']}</td>
                        <td>{c['qr_code']}</td>
                        <td>{service_count}</td>
                        <td>{total_paid} جنيه</td>
                        <td>{last_service}</td>
                        <td>
                            <a href="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=POWERLIFE_{c['id']}_{c['name']}" target="_blank">
                                عرض الباركود
                            </a>
                        </td>
                    </tr>
                    """
                
                st.markdown(f"""
                <table class='report-table'>
                    <thead>
                        <tr>
                            <th>اسم العميل</th>
                            <th>رقم الهاتف</th>
                            <th>المحافظة</th>
                            <th>كود الباركود</th>
                            <th>عدد الصيانات</th>
                            <th>إجمالي المدفوع</th>
                            <th>آخر صيانة</th>
                            <th>الباركود</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
                """, unsafe_allow_html=True)
                
                # عرض إحصائيات
                st.info(f"📈 إحصائيات: تم عرض {len(filtered_customers)} عميل من أصل {len(customers)}")
            else:
                st.warning("لا توجد عملاء مسجلين" if not search_term else "لا توجد نتائج للبحث")
        else:
            st.info("لا توجد بيانات عملاء")

    # --- 3. بحث وتعديل (عرض رصيد الحساب وسجل الشمع) ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 كشف حساب العميل")
        search = st.text_input("ابحث بالاسم أو الهاتف")
        if search:
            results = [c for c in customers if search in c['name'] or search in c['phone']]
            for c in results:
                with st.expander(f"👤 ملف: {c['name']} - {c['type']}"):
                    st.write(f"**العنوان:** {c['gov']} - {c['center']} - {c['village']}")
                    total_paid = sum(h['التكلفة'] for h in c.get('history', []))
                    st.success(f"💰 إجمالي رصيد المدفوعات: {total_paid} جنيه")
                    st.info(f"🔖 كود الباركود: {c['qr_code']}")
                    
                    # عرض باركود العميل
                    st.markdown(f"""
                    <div style='text-align:center; margin:10px; padding:10px; border:1px solid #ddd; border-radius:5px;'>
                        <p><strong>باركود العميل:</strong></p>
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=POWERLIFE_{c['id']}_{c['name']}">
                        <p style='font-size:12px;'>{c['qr_code']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if c.get('history'):
                        # إحصائيات الفنيين
                        technicians = {}
                        for h in c['history']:
                            tech = h['الفني']
                            if tech not in technicians:
                                technicians[tech] = 0
                            technicians[tech] += h['التكلفة']
                        
                        if technicians:
                            st.write("**👷 إحصائيات الفنيين:**")
                            for tech, amount in technicians.items():
                                st.write(f"- {tech}: {amount} جنيه")
                        
                        h_rows = "".join([f"<tr><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']} جنيه</td></tr>" for h in c['history']])
                        st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>الفني</th><th>العمل (الشمع)</th><th>المبلغ</th></tr></thead><tbody>{h_rows}</tbody></table>", unsafe_allow_html=True)
                    
                    if st.button("حذف العميل", key=f"del_{c['id']}"):
                        customers.remove(c)
                        save_data(CUSTOMERS_FILE, customers)
                        st.rerun()

    # --- 4. تتبع الفنيين (بدون خريطة لمنع الخطأ الأحمر) ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 مواقع الفنيين الحالية")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            t_rows = ""
            for u in techs:
                link = f"https://www.google.com/maps?q={u.get('lat',0)},{u.get('lon',0)}"
                t_rows += f"<tr><td>{u['username']}</td><td>{u.get('lat','-')}</td><td>{u.get('lon','-')}</td><td><a href='{link}' target='_blank'>فتح الخريطة 📍</a></td></tr>"
            st.markdown(f"<table class='report-table'><thead><tr><th>الفني</th><th>Lat</th><th>Lon</th><th>الموقع مباشر</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا يوجد فنيين مسجلين")

    # --- 5. أرباح الشركة (جداول HTML) ---
    elif choice == "💰 أرباح الشركة":
        st.subheader("📊 تقرير الدخل المالي")
        all_income = []
        for c in customers:
            for h in c.get('history', []): all_income.append(h)
        
        if all_income:
            df = pd.DataFrame(all_income)
            st.info(f"إجمالي خزينة الشركة: {df['التكلفة'].sum()} جنيه")
            
            # تفاصيل حسب الفني
            st.subheader("💰 الدخل حسب الفني")
            tech_income = df.groupby("الفني")["التكلفة"].sum().reset_index()
            tech_rows = "".join([f"<tr><td>{r['الفني']}</td><td>{r['التكلفة']} جنيه</td></tr>" for _, r in tech_income.iterrows()])
            st.markdown(f"<table class='report-table'><thead><tr><th>الفني</th><th>إجمالي الدخل</th></tr></thead><tbody>{tech_rows}</tbody></table>", unsafe_allow_html=True)
            
            # تفاصيل حسب التاريخ
            st.subheader("📅 الدخل حسب التاريخ")
            summary = df.groupby("التاريخ")["التكلفة"].sum().reset_index()
            s_rows = "".join([f"<tr><td>{r['التاريخ']}</td><td>{r['التكلفة']} جنيه</td></tr>" for _, r in summary.iterrows()])
            st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>إجمالي الدخل</th></tr></thead><tbody>{s_rows}</tbody></table>", unsafe_allow_html=True)
            
            # إحصائيات إضافية
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 متوسط الدخل اليومي", f"{df['التكلفة'].sum() / len(summary):.2f} جنيه" if len(summary) > 0 else "0 جنيه")
            with col2:
                st.metric("👷 عدد الفنيين العاملين", len(tech_income))
            with col3:
                st.metric("🔧 إجمالي عدد المعاملات", len(df))
        else: 
            st.info("لا توجد بيانات مالية")

    # --- بقية الوظائف ---
    elif choice == "🛠️ إضافة صيانة":
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            with st.form("s_form"):
                work = st.multiselect("الشمع المغير", ["1", "2", "3", "M", "S", "كربون", "موتور", "فلتر", "كهرباء"])
                price = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("حفظ"):
                    h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": price}
                    for cust in customers:
                        if cust['id'] == target['id']: 
                            cust['history'].append(h)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success(f"✅ تم إضافة صيانة للعميل {target['name']}")
                    
                    # عرض ملخص
                    st.info(f"""
                    **ملخص الصيانة:**
                    - العميل: {target['name']}
                    - التاريخ: {datetime.now().date()}
                    - الفني: {user_now['username']}
                    - العمل: {', '.join(work)}
                    - المبلغ: {price} جنيه
                    """)

    elif choice == "👤 إضافة فني جديد":
        with st.form("add_t"):
            nu = st.text_input("اسم الفني")
            np = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة"):
                users.append({"username": nu, "password": np, "role": "technician", "lat": 0, "lon": 0})
                save_data(USERS_FILE, users)
                st.success(f"✅ تم إضافة الفني {nu} بنجاح")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
