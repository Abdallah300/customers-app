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
        
        # إنشاء فورم جديد
        with st.form("new_c_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم العميل *", placeholder="أدخل اسم العميل")
                phone = st.text_input("رقم الهاتف *", placeholder="أدخل رقم الهاتف")
                gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
                center = st.text_input("المركز", placeholder="أدخل المركز")
            with col2:
                village = st.text_input("البلد/القرية", placeholder="أدخل اسم البلد أو القرية")
                ctype = st.selectbox("نوع الجهاز/العميل", ["جهاز جديد", "جهاز قديم", "عميل شركة"])
                loc = st.text_input("الإحداثيات (30.1, 31.2)", placeholder="مثال: 30.0444, 31.2357")
            
            # زر الحفظ
            submitted = st.form_submit_button("💾 حفظ العميل وإصدار الباركود")
            
            if submitted:
                # التحقق من الحقول المطلوبة
                if not name or not phone:
                    st.error("⚠️ يرجى ملء اسم العميل ورقم الهاتف (الحقول المطلوبة)")
                else:
                    # إنشاء ID جديد
                    new_id = 1
                    if customers:
                        new_id = max(c['id'] for c in customers) + 1
                    
                    # بيانات العميل
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
                        "created_at": str(datetime.now().date()),
                        "qr_code": f"PL-{new_id:04d}"
                    }
                    
                    # حفظ العميل
                    customers.append(c_data)
                    save_data(CUSTOMERS_FILE, customers)
                    
                    # رسالة نجاح
                    st.success(f"✅ تم حفظ العميل بنجاح!")
                    st.info(f"**رقم العميل:** {new_id} | **كود الباركود:** PL-{new_id:04d}")
                    
                    # عرض الباركود
                    st.markdown("---")
                    st.subheader("🤳 باركود العميل")
                    
                    # إنشاء صورة الباركود
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=POWERLIFE_{new_id}_{name.replace(' ', '_')}"
                    
                    col_qr1, col_qr2, col_qr3 = st.columns(3)
                    
                    with col_qr2:
                        st.markdown(f"""
                        <div class='qr-box'>
                            <h4>{name}</h4>
                            <img src="{qr_url}" alt="باركود العميل" width="180">
                            <p><strong>كود العميل:</strong> PL-{new_id:04d}</p>
                            <p><strong>الهاتف:</strong> {phone}</p>
                            <p><strong>التاريخ:</strong> {datetime.now().date()}</p>
                            <p style="font-size:12px; color:#666;">يمكن مسح الباركود للوصول السريع لبيانات العميل</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # معلومات إضافية
                    st.markdown("""
                    ### 📋 تعليمات استخدام الباركود:
                    1. يمكن للعميل مسح الباركود من خلال كاميرا الهاتف
                    2. أو استخدام تطبيق ماسح الباركود
                    3. الباركود يحتوي على رقم العميل للوصول السريع
                    4. يمكن حفظ الباركود كصورة وطباعته للعميل
                    """)
                    
                    # زر لإضافة صيانة مباشرة
                    st.markdown("---")
                    if st.button(f"➕ إضافة صيانة لهذا العميل ({name})"):
                        st.session_state.current_customer_id = new_id
                        st.rerun()

    # --- 2. قائمة العملاء (تقرير شامل) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 تقرير سجل الصيانات")
        
        # قسم البحث عن عميل بالباركود
        st.markdown("---")
        st.subheader("🔍 البحث عن عميل بالباركود")
        
        col_search1, col_search2 = st.columns([2, 1])
        with col_search1:
            qr_input = st.text_input("أدخل كود العميل (مثل: PL-0001)", placeholder="PL-0001")
        
        with col_search2:
            if st.button("🔍 بحث بالباركود"):
                if qr_input:
                    # البحث عن العميل
                    found_customer = None
                    for c in customers:
                        if c.get('qr_code') == qr_input:
                            found_customer = c
                            break
                    
                    if found_customer:
                        st.session_state.qr_customer = found_customer
                        st.success(f"✅ تم العثور على العميل: {found_customer['name']}")
                    else:
                        st.error("❌ لم يتم العثور على عميل بهذا الكود")
        
        # عرض بيانات العميل إذا تم البحث عنه
        if 'qr_customer' in st.session_state and st.session_state.qr_customer:
            c = st.session_state.qr_customer
            st.markdown("---")
            st.subheader(f"👤 بيانات العميل: {c['name']}")
            
            # معلومات العميل
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"""
                **المعلومات الشخصية:**
                - **الهاتف:** {c['phone']}
                - **المحافظة:** {c['gov']}
                - **المركز:** {c['center']}
                - **القرية:** {c['village']}
                - **النوع:** {c['type']}
                """)
            
            with col_info2:
                # حساب الإحصائيات
                total_paid = sum(h['التكلفة'] for h in c.get('history', []))
                service_count = len(c.get('history', []))
                last_service = c['history'][-1]['التاريخ'] if c.get('history') else 'لا يوجد'
                
                st.markdown(f"""
                **الإحصائيات:**
                - **كود الباركود:** {c.get('qr_code', 'غير معروف')}
                - **عدد الصيانات:** {service_count}
                - **إجمالي المدفوعات:** {total_paid} جنيه
                - **آخر صيانة:** {last_service}
                """)
            
            # عرض الباركود
            if c.get('qr_code'):
                qr_code = c['qr_code']
                qr_num = qr_code.replace("PL-", "")
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=POWERLIFE_{qr_num}_{c['name'].replace(' ', '_')}"
                
                st.markdown(f"""
                <div style="text-align: center; padding: 10px; border: 1px solid #28a745; border-radius: 10px; margin: 10px 0;">
                    <h4>باركود العميل</h4>
                    <img src="{qr_url}" width="120">
                    <p style="font-size: 12px;">{qr_code}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # عرض سجل الصيانات
            if c.get('history'):
                st.subheader("📋 سجل الصيانات والدفعات")
                
                # حساب إحصائيات الفنيين
                technicians = {}
                for h in c['history']:
                    tech = h['الفني']
                    if tech not in technicians:
                        technicians[tech] = {'count': 0, 'total': 0}
                    technicians[tech]['count'] += 1
                    technicians[tech]['total'] += h['التكلفة']
                
                # عرض إحصائيات الفنيين
                if technicians:
                    st.write("**👷 إحصائيات الفنيين:**")
                    tech_cols = st.columns(len(technicians))
                    for idx, (tech, stats) in enumerate(technicians.items()):
                        with tech_cols[idx % len(tech_cols)]:
                            st.metric(f"{tech}", f"{stats['total']} جنيه", f"{stats['count']} زيارة")
                
                # عرض جدول الصيانات
                rows = ""
                for h in c['history']:
                    rows += f"<tr><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']} جنيه</td></tr>"
                
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
            else:
                st.info("لا توجد صيانات مسجلة لهذا العميل")
            
            # أزرار التحكم
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("🛠️ إضافة صيانة جديدة", key=f"add_service_{c['id']}"):
                    st.session_state.add_service_for = c['id']
                    st.rerun()
            with col_btn2:
                if st.button("📄 طباعة التقرير", key=f"print_{c['id']}"):
                    st.info("جاري إعداد التقرير للطباعة...")
            with col_btn3:
                if st.button("❌ إغلاق التقرير", key=f"close_{c['id']}"):
                    del st.session_state.qr_customer
                    st.rerun()
        
        st.markdown("---")
        
        # عرض جميع العملاء
        if customers:
            # فلترة العملاء
            search_filter = st.text_input("🔍 بحث في جميع العملاء", placeholder="بحث بالاسم أو الهاتف")
            
            if search_filter:
                filtered_customers = [c for c in customers if search_filter.lower() in c['name'].lower() or search_filter in c['phone']]
            else:
                filtered_customers = customers
            
            if filtered_customers:
                # إنشاء جدول بجميع العملاء
                rows = ""
                for c in filtered_customers:
                    # حساب الإحصائيات
                    total_paid = sum(h['التكلفة'] for h in c.get('history', []))
                    service_count = len(c.get('history', []))
                    last_service = c['history'][-1]['التاريخ'] if c.get('history') else 'لا يوجد'
                    
                    rows += f"""
                    <tr>
                        <td>{c['name']}</td>
                        <td>{c['phone']}</td>
                        <td>{c['gov']}</td>
                        <td>{c.get('qr_code', 'غير معروف')}</td>
                        <td>{service_count}</td>
                        <td>{total_paid} جنيه</td>
                        <td>{last_service}</td>
                        <td>
                            <button onclick="window.location.href='?customer={c['id']}'" style="padding: 5px 10px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer;">
                                عرض
                            </button>
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
                            <th>الإجراءات</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
                """, unsafe_allow_html=True)
                
                st.info(f"عرض {len(filtered_customers)} من أصل {len(customers)} عميل")
            else:
                st.warning("لا توجد نتائج للبحث")
        else:
            st.info("لا توجد عملاء مسجلين بعد")

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
                    
                    if c.get('history'):
                        h_rows = "".join([f"<tr><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>" for h in c['history']])
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
            summary = df.groupby("التاريخ")["التكلفة"].sum().reset_index()
            s_rows = "".join([f"<tr><td>{r['التاريخ']}</td><td>{r['التكلفة']}</td></tr>" for _, r in summary.iterrows()])
            st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>إجمالي الدخل</th></tr></thead><tbody>{s_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا توجد بيانات مالية")

    # --- بقية الوظائف ---
    elif choice == "🛠️ إضافة صيانة":
        if customers:
            # إذا كان هناك عميل محدد من قبل
            if 'add_service_for' in st.session_state:
                target_id = st.session_state.add_service_for
                target = next((c for c in customers if c['id'] == target_id), customers[0])
                del st.session_state.add_service_for
            else:
                target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            
            with st.form("s_form"):
                work = st.multiselect("الشمع المغير", ["1", "2", "3", "M", "S", "كربون", "موتور"])
                price = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("حفظ"):
                    h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": price}
                    for cust in customers:
                        if cust['id'] == target['id']: cust['history'].append(h)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم!")

    elif choice == "👤 إضافة فني جديد":
        with st.form("add_t"):
            nu = st.text_input("اسم الفني")
            np = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة"):
                users.append({"username": nu, "password": np, "role": "technician", "lat": 0, "lon": 0})
                save_data(USERS_FILE, users)
                st.success("تم")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
