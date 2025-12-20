import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import base64
from io import BytesIO
import qrcode

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================

st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
<style>  
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');  
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }  
    .report-table { width: 100%; border-collapse: collapse; background-color: white; color: black; margin-bottom: 20px; }  
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: center; }  
    .report-table th { background-color: #28a745; color: white; }  
    .qr-container { border: 2px dashed #28a745; padding: 20px; text-align: center; background: #f0fff0; border-radius: 10px; margin: auto; max-width: 400px; }  
    .qr-container img { max-width: 100%; height: auto; margin: 10px 0; }  
    .download-btn { background-color: #28a745; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; margin: 10px; }  
    .download-btn:hover { background-color: #218838; }  
    .customer-info-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }  
    .stats-card { background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 15px; border-radius: 10px; margin: 10px 0; }  
    .technician-badge { background: #ffc107; color: #000; padding: 5px 10px; border-radius: 20px; display: inline-block; margin: 3px; }  
</style>  
""", unsafe_allow_html=True)

# ================== 2. إدارة ملفات البيانات ==================

USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)

# تأمين حساب المدير
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin"})
    save_data(USERS_FILE, users)

# ================== 3. وظائف مساعدة ==================

def generate_qr_code(data):
    """إنشاء رمز QR بصورة يمكن تحميلها"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # تحويل الصورة إلى بايتس
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    
    # ترميز الصورة لعرضها في HTML
    encoded = base64.b64encode(img_bytes).decode()
    
    return encoded, img_bytes

def create_qr_download_link(img_bytes, filename="powerlife_qr.png"):
    """إنشاء رابط تحميل للباركود"""
    b64 = base64.b64encode(img_bytes).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}" class="download-btn">📥 تحميل الباركود</a>'
    return href

def get_customer_url(customer_id):
    """إنشاء رابط العميل - استبدل برابطك الحقيقي عند النشر"""
    base_url = "https://powerlife.streamlit.app"  # استبدل برابطك
    return f"{base_url}/?id={customer_id}"

def calculate_monthly_stats(customer_history):
    """حساب الإحصائيات الشهرية للعميل"""
    monthly_data = {}
    for entry in customer_history:
        date = datetime.strptime(entry['التاريخ'], "%Y-%m-%d")
        month_year = f"{date.year}-{date.month:02d}"
        
        if month_year not in monthly_data:
            monthly_data[month_year] = {
                "المبلغ": 0,
                "الزيارات": 0,
                "الفنيين": set()
            }
        
        monthly_data[month_year]["المبلغ"] += entry['التكلفة']
        monthly_data[month_year]["الزيارات"] += 1
        monthly_data[month_year]["الفنيين"].add(entry['الفني'])
    
    # تحويل إلى قائمة مرتبة
    result = []
    for month in sorted(monthly_data.keys(), reverse=True):
        result.append({
            "الشهر": month,
            "المبلغ الإجمالي": monthly_data[month]["المبلغ"],
            "عدد الزيارات": monthly_data[month]["الزيارات"],
            "الفنيين": ", ".join(monthly_data[month]["الفنيين"])
        })
    
    return result

# ================== 4. صفحة العميل العامة (من خلال الباركود) ==================

query_params = st.query_params
if "id" in query_params:
    try:
        cust_id = int(query_params["id"])
        target_cust = next((c for c in customers if c['id'] == cust_id), None)
        
        if target_cust:
            # ========== تصميم صفحة العميل ==========
            st.title(f"💧 مرحباً بك: {target_cust['name']}")
            st.subheader("سجل الصيانة والمدفوعات الخاص بك")
            
            # بطاقة معلومات العميل
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div class="customer-info-card">
                    <h4>📋 معلومات العميل</h4>
                    <p><strong>رقم العميل:</strong> PL-{target_cust['id']:04d}</p>
                    <p><strong>الهاتف:</strong> {target_cust['phone']}</p>
                    <p><strong>المحافظة:</strong> {target_cust['gov']}</p>
                    <p><strong>القرية:</strong> {target_cust['village']}</p>
                    <p><strong>نوع الجهاز:</strong> {target_cust['type']}</p>
                    <p><strong>تاريخ التسجيل:</strong> {target_cust['created_at']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # الإحصائيات
            history = target_cust.get('history', [])
            total_paid = sum(h['التكلفة'] for h in history)
            total_visits = len(history)
            technicians = set(h['الفني'] for h in history)
            
            with col2:
                st.markdown(f"""
                <div class="stats-card">
                    <h4>💰 الإحصائيات العامة</h4>
                    <p><strong>إجمالي المدفوعات:</strong> {total_paid} ج.م</p>
                    <p><strong>عدد زيارات الصيانة:</strong> {total_visits}</p>
                    <p><strong>الفنيون الذين قاموا بالخدمة:</strong> {len(technicians)}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                # عرض الفنيين
                st.markdown("### 👷 الفنيون الذين قاموا بخدمتك")
                if technicians:
                    for tech in technicians:
                        st.markdown(f'<div class="technician-badge">{tech}</div>', unsafe_allow_html=True)
                else:
                    st.info("لم تتم أي صيانة حتى الآن")
            
            # ========== الإحصائيات الشهرية ==========
            st.markdown("---")
            st.subheader("📊 الإحصائيات الشهرية")
            
            monthly_stats = calculate_monthly_stats(history)
            if monthly_stats:
                df_monthly = pd.DataFrame(monthly_stats)
                st.dataframe(df_monthly, use_container_width=True)
                
                # رسم بياني للمدفوعات الشهرية
                if not df_monthly.empty:
                    df_monthly['الشهر'] = pd.to_datetime(df_monthly['الشهر'] + '-01')
                    chart_data = df_monthly.set_index('الشهر')[['المبلغ الإجمالي']]
                    st.line_chart(chart_data)
            else:
                st.info("لا توجد بيانات شهرية متاحة")
            
            # ========== سجل الصيانة الكامل ==========
            st.markdown("---")
            st.subheader("🛠️ سجل الصيانة الكامل")
            
            if history:
                # فرز السجل من الأحدث إلى الأقدم
                sorted_history = sorted(history, key=lambda x: x['التاريخ'], reverse=True)
                
                for i, h in enumerate(sorted_history, 1):
                    with st.expander(f"زيارة {i} - {h['التاريخ']} (المبلغ: {h['التكلفة']} ج.م)"):
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.write(f"**التاريخ:** {h['التاريخ']}")
                        with col_b:
                            st.write(f"**الفني:** {h['الفني']}")
                        with col_c:
                            st.write(f"**المبلغ:** {h['التكلفة']} ج.م")
                        st.write(f"**الأعمال المنجزة:** {h['العمل']}")
                
                # عرض كجدول أيضاً
                st.markdown("### 📋 عرض جدولي للسجل")
                rows = "".join([
                    f"<tr><td>{h['التاريخ']}</td><td>{h['العمل']}</td><td>{h['التكلفة']} ج.م</td><td>{h['الفني']}</td></tr>"
                    for h in sorted_history
                ])
                st.markdown(f"""
                <table class='report-table'>
                    <thead>
                        <tr><th>التاريخ</th><th>العمل المنجز</th><th>المبلغ</th><th>الفني</th></tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
                """, unsafe_allow_html=True)
            else:
                st.info("لا توجد سجلات صيانة حالية.")
            
            # ========== ملاحظات إضافية ==========
            st.markdown("---")
            st.info("""
            **ملاحظات مهمة:**
            1. يمكنك حفظ هذه الصفحة كمفضلة لمراجعة سجل الصيانة الخاص بك
            2. جميع البيانات محدثة تلقائياً عند كل صيانة جديدة
            3. للاستفسار، يرجى الاتصال بخدمة العملاء: 01234567890
            """)
            
        else:
            st.error("❌ كود العميل غير صحيح أو غير موجود")
            st.info("يرجى التأكد من صحة الباركود أو التواصل مع إدارة الشركة")
    
    except ValueError:
        st.error("❌ كود العميل غير صحيح")
    
    st.stop()

# ================== 5. نظام دخول الموظفين ==================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life Ultra - دخول")
    u_in = st.text_input("اسم المستخدم")
    p_in = st.text_input("كلمة المرور", type="password")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("دخول", type="primary", use_container_width=True):
            user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("بيانات غير صحيحة")
    
    with col2:
        st.info("""
        **بيانات الدخول الافتراضية:**
        - المدير: Abdallah / 772001
        - أضف فنيين جدد من القائمة
        """)
else:
    user_now = st.session_state.current_user
    st.sidebar.title(f"💧 {user_now['username']}")
    
    # القائمة
    menu = ["📋 قائمة العملاء", "➕ إضافة عميل", "🛠️ إضافة صيانة", "🔍 بحث وتعديل", "💰 أرباح الشركة"]
    if user_now['role'] == "admin":
        menu.extend(["👤 إدارة الفنيين", "📊 التقارير", "🚪 خروج"])
    else:
        menu.append("🚪 خروج")
    
    choice = st.sidebar.radio("القائمة الرئيسية", menu)
    
    # --- إضافة عميل جديد ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("اسم العميل *", help="الاسم الكامل للعميل")
                phone = st.text_input("رقم الهاتف *", help="رقم الهاتف الأساسي")
                gov = st.selectbox("المحافظة *", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
                
            with col2:
                village = st.text_input("القرية/المركز *")
                ctype = st.selectbox("نوع الجهاز *", ["7 مراحل", "5 مراحل", "جامبو", "فلتر عادي"])
                notes = st.text_area("ملاحظات إضافية")
            
            submitted = st.form_submit_button("💾 حفظ وإصدار الباركود", type="primary")
            
            if submitted:
                if not name or not phone or not village:
                    st.error("يرجى ملء الحقول الإلزامية (*)")
                else:
                    new_id = max([c['id'] for c in customers], default=0) + 1
                    customer_url = get_customer_url(new_id)
                    
                    new_cust = {
                        "id": new_id,
                        "name": name,
                        "phone": phone,
                        "gov": gov,
                        "village": village,
                        "type": ctype,
                        "notes": notes,
                        "history": [],
                        "created_by": user_now['username'],
                        "created_at": str(datetime.now().date())
                    }
                    
                    customers.append(new_cust)
                    save_data(CUSTOMERS_FILE, customers)
                    
                    st.success(f"✅ تم تسجيل العميل {name} بنجاح!")
                    
                    # إنشاء وعرض الباركود
                    st.markdown("---")
                    st.subheader("🎫 كارت متابعة العميل")
                    
                    # إنشاء QR Code
                    qr_encoded, qr_bytes = generate_qr_code(customer_url)
                    
                    # عرض المعلومات والباركود
                    col_a, col_b = st.columns([1, 1])
                    
                    with col_a:
                        st.markdown(f"""
                        <div class="customer-info-card">
                            <h3>معلومات العميل</h3>
                            <p><strong>الاسم:</strong> {name}</p>
                            <p><strong>رقم العميل:</strong> PL-{new_id:04d}</p>
                            <p><strong>الهاتف:</strong> {phone}</p>
                            <p><strong>العنوان:</strong> {gov} - {village}</p>
                            <p><strong>نوع الجهاز:</strong> {ctype}</p>
                            <p><strong>تاريخ التسجيل:</strong> {new_cust['created_at']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown(f"""
                        <div class="qr-container">
                            <h4>باركود المتابعة</h4>
                            <img src="data:image/png;base64,{qr_encoded}" alt="QR Code">
                            <p>🔍 مسح الباركود لمتابعة الصيانة</p>
                            <p><strong>كود العميل: PL-{new_id:04d}</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # روابط التحميل والمشاركة
                        st.markdown("### 📤 خيارات التحميل والمشاركة")
                        
                        # رابط تحميل الباركود
                        st.markdown(
                            create_qr_download_link(qr_bytes, f"powerlife_{new_id}.png"),
                            unsafe_allow_html=True
                        )
                        
                        # نسخ الرابط
                        st.code(customer_url, language="text")
                        if st.button("📋 نسخ الرابط"):
                            st.session_state.copied_url = customer_url
                            st.success("تم نسخ الرابط!")
                        
                        # تعليمات الاستخدام
                        with st.expander("📖 تعليمات استخدام الباركود"):
                            st.markdown("""
                            1. **قم بتحميل الباركود** واحفظه على جهازك
                            2. **أرسل الباركود للعميل** عبر الواتساب أو أي وسيلة
                            3. **يمكن للعميل**:
                               - مسح الباركود بالكاميرا
                               - حفظ الصورة وعرضها عند الحاجة
                               - مشاركة الرابط مباشرة
                            4. **عند مسح الباركود** سيظهر للعميل:
                               - جميع زيارات الصيانة
                               - المبالغ المدفوعة
                               - الفنيين الذين قاموا بالخدمة
                               - الإحصائيات الشهرية
                            """)
    
    # --- إضافة صيانة ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة جديدة")
        
        if customers:
            # فلترة العملاء مع إمكانية البحث
            search_term = st.text_input("🔍 بحث عن عميل (بالاسم أو الهاتف)")
            
            if search_term:
                filtered_customers = [
                    c for c in customers 
                    if search_term.lower() in c['name'].lower() 
                    or search_term in c['phone']
                ]
            else:
                filtered_customers = customers
            
            if filtered_customers:
                target = st.selectbox(
                    "اختر العميل",
                    filtered_customers,
                    format_func=lambda x: f"{x['name']} - {x['phone']} - {x['gov']}"
                )
                
                with st.form("service_form"):
                    st.markdown(f"### عميل: **{target['name']}**")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        work_options = ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "كربون", "موتور", "تغيير خزان", "تنظيف", "صيانة دورية", "أخرى"]
                        work = st.multiselect("الأعمال المنجزة", work_options)
                        custom_work = st.text_input("أعمال أخرى (اكتبها)")
                    
                    with col2:
                        price = st.number_input("المبلغ المدفوع (ج.م)", min_value=0, value=0)
                        payment_method = st.selectbox("طريقة الدفع", ["نقدي", "تحويل بنكي", "آخرى"])
                        notes = st.text_area("ملاحظات الصيانة")
                    
                    if st.form_submit_button("💾 حفظ الصيانة"):
                        if not work and not custom_work:
                            st.error("يرجى تحديد الأعمال المنجزة")
                        else:
                            # تجميع الأعمال
                            all_work = work
                            if custom_work:
                                all_work.append(custom_work)
                            
                            entry = {
                                "التاريخ": str(datetime.now().date()),
                                "الفني": user_now['username'],
                                "العمل": ", ".join(all_work),
                                "التكلفة": price,
                                "طريقة الدفع": payment_method,
                                "ملاحظات": notes
                            }
                            
                            for c in customers:
                                if c['id'] == target['id']:
                                    c.setdefault('history', []).append(entry)
                                    break
                            
                            save_data(CUSTOMERS_FILE, customers)
                            st.success("✅ تم حفظ بيانات الصيانة بنجاح!")
                            
                            # عرض الباركود مرة أخرى للعميل
                            st.info("يمكنك إرسال الباركود للعميل لمتابعة الصيانة:")
                            cust_url = get_customer_url(target['id'])
                            qr_encoded, _ = generate_qr_code(cust_url)
                            st.markdown(f"""
                            <div class="qr-container" style="max-width: 300px;">
                                <img src="data:image/png;base64,{qr_encoded}" alt="QR Code">
                                <p>كود العميل: PL-{target['id']:04d}</p>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("لا توجد نتائج للبحث")
        else:
            st.warning("لا يوجد عملاء مسجلين")
    
    # --- قائمة العملاء ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 سجل العملاء")
        
        if customers:
            # أزرار التحكم
            col1, col2, col3 = st.columns([2, 1, 1])
            with col2:
                show_qr = st.checkbox("عرض الباركود")
            with col3:
                export_data = st.button("📥 تصدير البيانات")
            
            # عرض البيانات
            for customer in customers:
                with st.expander(f"{customer['name']} - {customer['phone']} - {customer['gov']}"):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        st.write(f"**رقم العميل:** PL-{customer['id']:04d}")
                        st.write(f"**القرية:** {customer['village']}")
                        st.write(f"**نوع الجهاز:** {customer['type']}")
                        st.write(f"**تاريخ التسجيل:** {customer['created_at']}")
                        st.write(f"**عدد زيارات الصيانة:** {len(customer.get('history', []))}")
                    
                    with col_b:
                        if show_qr:
                            cust_url = get_customer_url(customer['id'])
                            qr_encoded, qr_bytes = generate_qr_code(cust_url)
                            st.markdown(f"""
                            <div style="text-align: center;">
                                <img src="data:image/png;base64,{qr_encoded}" width="150">
                                <p style="font-size: 12px;">PL-{customer['id']:04d}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.download_button(
                                label="📥",
                                data=qr_bytes,
                                file_name=f"qr_{customer['id']}.png",
                                mime="image/png",
                                key=f"qr_{customer['id']}"
                            )
            
            # تصدير البيانات
            if export_data:
                df = pd.DataFrame(customers)
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 تحميل كملف CSV",
                    data=csv,
                    file_name="powerlife_customers.csv",
                    mime="text/csv"
                )
        else:
            st.info("لا توجد بيانات.")
    
    # --- أرباح الشركة ---
    elif choice == "💰 أرباح الشركة":
        st.subheader("💰 الحسابات والإيرادات")
        
        if customers:
            all_entries = []
            total_income = 0
            technician_earnings = {}
            
            for c in customers:
                for h in c.get('history', []):
                    all_entries.append({
                        "التاريخ": h['التاريخ'],
                        "العميل": c['name'],
                        "الفني": h['الفني'],
                        "الأعمال": h['العمل'],
                        "المبلغ": h['التكلفة'],
                        "طريقة الدفع": h.get('طريقة الدفع', 'نقدي')
                    })
                    total_income += h['التكلفة']
                    
                    # إحصائيات الفنيين
                    tech = h['الفني']
                    if tech not in technician_earnings:
                        technician_earnings[tech] = 0
                    technician_earnings[tech] += h['التكلفة']
            
            # عرض الإحصائيات
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("إجمالي الدخل", f"{total_income:,} ج.م")
            with col2:
                st.metric("عدد المعاملات", len(all_entries))
            with col3:
                st.metric("عدد العملاء", len(customers))
            
            # أرباح الفنيين
            st.subheader("🎯 أرباح الفنيين")
            if technician_earnings:
                df_tech = pd.DataFrame({
                    "الفني": list(technician_earnings.keys()),
                    "الإجمالي": list(technician_earnings.values())
                })
                st.bar_chart(df_tech.set_index("الفني"))
            
            # تفاصيل المعاملات
            st.subheader("📋 تفاصيل جميع المعاملات")
            if all_entries:
                df_all = pd.DataFrame(all_entries)
                st.dataframe(df_all.sort_values("التاريخ", ascending=False), use_container_width=True)
                
                # تصدير البيانات
                csv_all = df_all.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 تحميل كافة المعاملات",
                    data=csv_all,
                    file_name="powerlife_transactions.csv",
                    mime="text/csv"
                )
    
    # --- إدارة الفنيين (للمدير فقط) ---
    elif choice == "👤 إدارة الفنيين" and user_now['role'] == "admin":
        st.subheader("👤 إدارة الفنيين والمستخدمين")
        
        tab1, tab2 = st.tabs(["إضافة فني جديد", "قائمة الفنيين"])
        
        with tab1:
            with st.form("add_tech_form"):
                u = st.text_input("اسم المستخدم *")
                p = st.text_input("كلمة المرور *", type="password")
                role = st.selectbox("الدور", ["technician", "admin"])
                
                if st.form_submit_button("إضافة مستخدم جديد"):
                    if u and p:
                        if any(x['username'] == u for x in users):
                            st.error("اسم المستخدم موجود مسبقاً!")
                        else:
                            users.append({
                                "username": u,
                                "password": p,
                                "role": role
                            })
                            save_data(USERS_FILE, users)
                            st.success(f"✅ تم إضافة {u} بنجاح!")
                    else:
                        st.error("يرجى ملء جميع الحقول")
        
        with tab2:
            if users:
                df_users = pd.DataFrame(users)
                st.dataframe(df_users, use_container_width=True)
            else:
                st.info("لا يوجد مستخدمين")
    
    # --- التقارير (للمدير فقط) ---
    elif choice == "📊 التقارير" and user_now['role'] == "admin":
        st.subheader("📊 التقارير والإحصائيات المتقدمة")
        
        if customers:
            # تحليل البيانات
            df_customers = pd.DataFrame(customers)
            
            # توزيع العملاء حسب المحافظة
            st.subheader("📍 توزيع العملاء حسب المحافظة")
            gov_dist = df_customers['gov'].value_counts()
            st.bar_chart(gov_dist)
            
            # توزيع أنواع الأجهزة
            st.subheader("🛠️ توزيع أنواع الأجهزة")
            type_dist = df_customers['type'].value_counts()
            st.bar_chart(type_dist)
            
            # العملاء الجدد حسب الشهر
            st.subheader("📈 العملاء الجدد حسب الشهر")
            try:
                df_customers['created_at'] = pd.to_datetime(df_customers['created_at'])
                monthly_new = df_customers.set_index('created_at').resample('M').size()
                st.line_chart(monthly_new)
            except:
                st.info("لا توجد بيانات زمنية كافية")
    
    # --- خروج ---
    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
