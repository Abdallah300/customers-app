import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd
import time
import shutil

# ------------------ الملفات ------------------
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"
BACKUP_DIR = "backup"

# إنشاء مجلد النسخ الاحتياطي إذا لم يكن موجوداً
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# ------------------ الدوال المساعدة ------------------
def backup_files():
    """إنشاء نسخة احتياطية"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users_data = f.read()
            with open(f"{BACKUP_DIR}/users_{timestamp}.json", "w", encoding="utf-8") as f:
                f.write(users_data)
        
        if os.path.exists(CUSTOMERS_FILE):
            with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
                customers_data = f.read()
            with open(f"{BACKUP_DIR}/customers_{timestamp}.json", "w", encoding="utf-8") as f:
                f.write(customers_data)
        
        return True
    except:
        return False

# تحميل البيانات
def load_data():
    """تحميل البيانات من الملفات"""
    users = []
    customers = []
    
    # تحميل المستخدمين
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except:
            users = []
    else:
        users = []
    
    # تحميل العملاء
    if os.path.exists(CUSTOMERS_FILE):
        try:
            with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
                customers = json.load(f)
        except:
            customers = []
    else:
        customers = []
    
    return users, customers

# تحميل البيانات
users, customers = load_data()

# إنشاء المدير إذا لم يكن موجوداً
admin_exists = any(u.get("username") == "Abdallah" for u in users)
if not admin_exists:
    users.append({
        "username": "Abdallah",
        "password": "772001",  # كلمة مرور غير مشفرة
        "role": "admin",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "full_name": "مدير النظام",
        "phone": "",
        "email": "",
        "status": "active"
    })
    
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass

def save_users():
    """حفظ بيانات المستخدمين"""
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

def save_customers():
    """حفظ بيانات العملاء"""
    try:
        with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
            json.dump(customers, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False

# ------------------ إعداد الجلسة ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

st.set_page_config(
    page_title="Power Life - إدارة العملاء",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ تنسيق CSS ------------------
st.markdown("""
    <style>
    /* تنسيق عام */
    .main {
        padding: 0rem 1rem;
    }
    
    /* تنسيق الأزرار */
    .stButton > button {
        border-radius: 8px;
        font-weight: bold;
    }
    
    /* تنسيق العناوين */
    h1, h2, h3 {
        color: #2c3e50;
    }
    
    /* إخفاء بعض عناصر Streamlit الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* تنسيق الصفحة الرئيسية */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    
    .stats-card h3 {
        color: white;
        margin: 0;
        font-size: 14px;
        opacity: 0.9;
    }
    
    .stats-card .value {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    
    /* تنسيق صفحة تسجيل الدخول */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        background-color: white;
        text-align: center;
    }
    
    .login-title {
        color: #2c3e50;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# ------------------ تسجيل الخروج ------------------
def logout():
    """تسجيل خروج المستخدم"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.experimental_rerun()

# ------------------ تسجيل الدخول ------------------
if not st.session_state.logged_in:
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="login-title">🏢 Power Life</h1>', unsafe_allow_html=True)
    st.markdown('<h3>🔑 تسجيل الدخول</h3>', unsafe_allow_html=True)
    
    # إظهار رسالة إذا تم إنشاء حساب جديد
    if not admin_exists:
        st.info("✅ تم إنشاء حساب المدير الجديد")
    
    username = st.text_input("اسم المستخدم", value="Abdallah")
    password = st.text_input("كلمة المرور", type="password", value="772001")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        login_btn = st.button("تسجيل الدخول", type="primary", use_container_width=True)
    with col2:
        reset_btn = st.button("إعادة تعيين", type="secondary", use_container_width=True)
    
    if reset_btn:
        if os.path.exists(USERS_FILE):
            os.remove(USERS_FILE)
        st.success("✅ تم إعادة تعيين النظام. أعد تحميل الصفحة.")
        time.sleep(2)
        st.experimental_rerun()
    
    if login_btn:
        if username and password:
            user_found = False
            for user in users:
                if user["username"] == username and user["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    user_found = True
                    break
            
            if user_found:
                st.success("✅ تم تسجيل الدخول بنجاح")
                st.balloons()
                time.sleep(1)
                st.experimental_rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                st.info("**بيانات الدخول الافتراضية:**")
                st.info("- المدير: Abdallah / 772001")
        else:
            st.warning("⚠️ يرجى ملء جميع الحقول")
    
    st.markdown("""
    <div style="margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 10px; border-right: 5px solid #3498db;">
    <h4 style="margin-top: 0; color: #2c3e50;">💡 معلومات النظام</h4>
    <p style="margin-bottom: 5px;"><strong>الحساب الافتراضي:</strong></p>
    <p style="margin: 5px 0;">👑 المدير: Abdallah / 772001</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ إذا تم تسجيل الدخول ------------------
else:
    user = st.session_state.current_user
    role = user.get("role", "technician")
    username = user.get("username", "")
    full_name = user.get("full_name", username)
    
    # الشريط الجانبي
    with st.sidebar:
        # معلومات المستخدم
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px; color: white;">
            <h3 style="color: white; margin: 0 0 10px 0;">👤 {full_name}</h3>
            <p style="margin: 5px 0; opacity: 0.9;">
                <strong>الصلاحية:</strong> {'👑 مدير' if role == 'admin' else '👷 فني'}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # القائمة الرئيسية
        st.markdown("<h3 style='color: white;'>📋 القائمة الرئيسية</h3>", unsafe_allow_html=True)
        
        # القائمة حسب الصلاحيات
        if role == "admin":
            menu_options = [
                "🏠 الصفحة الرئيسية",
                "➕ إضافة عميل",
                "📋 عرض العملاء",
                "🔎 بحث متقدم",
                "⏰ تذكير الزيارة",
                "👷 إدارة الفنيين",
                "🗺️ خريطة العملاء",
                "📊 التقارير",
                "🚪 تسجيل الخروج"
            ]
        else:
            menu_options = [
                "🏠 الصفحة الرئيسية",
                "📋 عرض العملاء",
                "🔎 بحث متقدم",
                "⏰ تذكير الزيارة",
                "🗺️ خريطة العملاء",
                "🚪 تسجيل الخروج"
            ]
        
        # عرض القائمة
        choice = st.radio("اختر صفحة", menu_options)
        
        # زر النسخ الاحتياطي للمدير
        if role == "admin":
            st.divider()
            if st.button("📦 إنشاء نسخة احتياطية", use_container_width=True):
                if backup_files():
                    st.success("✅ تم إنشاء النسخة الاحتياطية")
                else:
                    st.error("❌ فشل في إنشاء النسخة")
    
    # ------------------ محتوى الصفحات ------------------
    
    # الصفحة الرئيسية
    if choice == "🏠 الصفحة الرئيسية":
        st.title(f"مرحباً بك {username} 👋")
        st.markdown("---")
        
        # بطاقات الإحصائيات
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <h3>إجمالي العملاء</h3>
                <div class="value">{len(customers)}</div>
                <p>عميل مسجل</p>
            </div>
            """, unsafe_allow_html=True)
        
        # حساب العملاء المطلوب زيارتهم
        today = datetime.today()
        due_count = 0
        for c in customers:
            try:
                last = datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")
                if (today - last).days >= 30:
                    due_count += 1
            except:
                pass
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <h3>بحاجة لزيارة</h3>
                <div class="value">{due_count}</div>
                <p>عميل متأخر</p>
            </div>
            """, unsafe_allow_html=True)
        
        # عدد الفنيين
        tech_count = len([u for u in users if u.get("role") == "technician"])
        
        with col3:
            st.markdown(f"""
            <div class="stats-card">
                <h3>عدد الفنيين</h3>
                <div class="value">{tech_count}</div>
                <p>فني نشط</p>
            </div>
            """, unsafe_allow_html=True)
        
        # العملاء الجدد هذا الشهر
        current_month = datetime.now().month
        current_year = datetime.now().year
        new_this_month = 0
        for c in customers:
            try:
                added_date = datetime.strptime(c.get("added_date", "2000-01-01"), "%Y-%m-%d")
                if added_date.month == current_month and added_date.year == current_year:
                    new_this_month += 1
            except:
                pass
        
        with col4:
            st.markdown(f"""
            <div class="stats-card">
                <h3>جدد هذا الشهر</h3>
                <div class="value">{new_this_month}</div>
                <p>عميل جديد</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # قسمين بجوار بعض
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🆕 أحدث العملاء")
            if customers:
                recent_customers = customers[-5:] if len(customers) > 5 else customers
                recent_df = pd.DataFrame(recent_customers)
                
                if not recent_df.empty:
                    display_cols = ["name", "phone", "category", "last_visit"]
                    display_cols = [col for col in display_cols if col in recent_df.columns]
                    st.dataframe(recent_df[display_cols], use_container_width=True, height=250)
            else:
                st.info("لا يوجد عملاء بعد.")
        
        with col2:
            st.subheader("📋 إحصائيات سريعة")
            
            # إحصائيات حسب التصنيف
            category_stats = {}
            for c in customers:
                cat = c.get("category", "غير محدد")
                category_stats[cat] = category_stats.get(cat, 0) + 1
            
            if category_stats:
                stats_df = pd.DataFrame(list(category_stats.items()), columns=["التصنيف", "العدد"])
                st.dataframe(stats_df, use_container_width=True, height=250)
            
            # زر إضافة سريعة
            if st.button("➕ إضافة عميل جديد", use_container_width=True, key="quick_add"):
                choice = "➕ إضافة عميل"
                st.experimental_rerun()
        
        st.markdown("---")
        
        # العملاء المطلوب زيارتهم
        if due_count > 0:
            st.subheader("🔔 عملاء بحاجة لزيارة عاجلة")
            due_customers = []
            for c in customers:
                try:
                    last = datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")
                    if (today - last).days >= 30:
                        due_customers.append(c)
                except:
                    pass
            
            if due_customers:
                due_df = pd.DataFrame(due_customers)
                display_cols = ["name", "phone", "last_visit", "notes"]
                display_cols = [col for col in display_cols if col in due_df.columns]
                st.dataframe(due_df[display_cols], use_container_width=True)
    
    # إضافة عميل
    elif choice == "➕ إضافة عميل":
        st.title("➕ إضافة عميل جديد")
        st.markdown("---")
        
        with st.form("add_customer_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("المعلومات الأساسية")
                name = st.text_input("اسم العميل *", placeholder="أدخل الاسم الكامل")
                phone = st.text_input("رقم الهاتف *", placeholder="مثال: 01012345678")
                category = st.selectbox("التصنيف *", ["منزل", "شركة", "مدرسة", "مستشفى", "فندق", "مطعم", "أخرى"])
                
                # قائمة الفنيين
                technicians = [u for u in users if u.get("role") == "technician"]
                tech_names = ["غير معين"] + [u["username"] for u in technicians]
                assigned_to = st.selectbox("الفني المسؤول", tech_names)
            
            with col2:
                st.subheader("المعلومات الإضافية")
                location = st.text_input("إحداثيات الموقع (اختياري)", placeholder="مثال: 30.0444,31.2357")
                if location:
                    st.caption("💡 انسخ الإحداثيات من Google Maps")
                
                last_visit = st.date_input("تاريخ آخر زيارة *", datetime.today())
                next_visit = st.date_input("موعد الزيارة القادمة (اختياري)", 
                                          datetime.today() + timedelta(days=30))
                
                status = st.selectbox("حالة العميل", ["نشط", "معلق", "غير نشط"])
            
            st.subheader("ملاحظات إضافية")
            notes = st.text_area("اكتب ملاحظات عن العميل (اختياري)", 
                               placeholder="مثل: يحتاج صيانة دورية، يفضل الزيارة صباحاً، إلخ...",
                               height=100)
            
            st.markdown("---")
            st.caption("* الحقول المطلوبة")
            
            col1, col2 = st.columns([1, 3])
            with col1:
                submit_btn = st.form_submit_button("💾 حفظ العميل", type="primary", use_container_width=True)
            
            if submit_btn:
                if name and phone:
                    new_customer = {
                        "id": len(customers) + 1,
                        "name": name,
                        "phone": phone,
                        "location": location,
                        "notes": notes,
                        "category": category,
                        "last_visit": str(last_visit),
                        "next_visit": str(next_visit) if next_visit else "",
                        "assigned_to": assigned_to if assigned_to != "غير معين" else "",
                        "added_by": user["username"],
                        "added_date": str(datetime.today().date()),
                        "status": status,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    customers.append(new_customer)
                    if save_customers():
                        st.success(f"✅ تم إضافة العميل **{name}** بنجاح")
                        st.balloons()
                    else:
                        st.error("❌ حدث خطأ أثناء حفظ العميل")
                else:
                    st.warning("⚠️ يرجى ملء الحقول المطلوبة (*)")
    
    # عرض العملاء
    elif choice == "📋 عرض العملاء":
        st.title("📋 قائمة العملاء")
        st.markdown("---")
        
        if not customers:
            st.info("لا يوجد عملاء مسجلين بعد.")
        
        # أداة البحث السريع
        search_col1, search_col2, search_col3 = st.columns([2, 1, 1])
        
        with search_col1:
            search_term = st.text_input("🔍 بحث سريع", placeholder="ابحث بالاسم أو الهاتف...")
        
        with search_col2:
            categories = list(set(c.get("category", "") for c in customers if c.get("category")))
            filter_category = st.selectbox("التصنيف", ["الكل"] + sorted(categories))
        
        with search_col3:
            filter_status = st.selectbox("الحالة", ["الكل", "نشط", "معلق", "غير نشط"])
        
        # فلترة البيانات
        filtered_customers = customers
        
        if search_term:
            filtered_customers = [
                c for c in filtered_customers 
                if search_term.lower() in c.get("name", "").lower() 
                or search_term in c.get("phone", "")
            ]
        
        if filter_category != "الكل":
            filtered_customers = [c for c in filtered_customers if c.get("category") == filter_category]
        
        if filter_status != "الكل":
            filtered_customers = [c for c in filtered_customers if c.get("status", "نشط") == filter_status]
        
        if not filtered_customers:
            st.warning("لا توجد نتائج مطابقة للبحث.")
        
        # تحويل إلى DataFrame
        df = pd.DataFrame(filtered_customers)
        
        # تحديد الأعمدة للعرض
        display_columns = ["id", "name", "phone", "category", "last_visit", "status", "assigned_to"]
        available_columns = [col for col in display_columns if col in df.columns]
        
        # عرض البيانات
        st.dataframe(df[available_columns], use_container_width=True, height=400)
        
        st.markdown("---")
        
        # خيارات التصدير
        if st.button("📥 تصدير إلى Excel", use_container_width=True):
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ تحميل الملف",
                data=csv,
                file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # بحث متقدم
    elif choice == "🔎 بحث متقدم":
        st.title("🔎 البحث المتقدم عن العملاء")
        st.markdown("---")
        
        if not customers:
            st.info("لا يوجد عملاء للبحث.")
        
        # نموذج البحث
        with st.form("advanced_search_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name_search = st.text_input("بحث بالاسم", placeholder="أدخل جزء من الاسم...")
                phone_search = st.text_input("بحث بالهاتف", placeholder="أدخل رقم الهاتف...")
                categories = list(set(c.get("category", "") for c in customers if c.get("category")))
                category_search = st.selectbox("بحث بالتصنيف", ["الكل"] + sorted(categories))
            
            with col2:
                status_search = st.selectbox("بحث بالحالة", ["الكل", "نشط", "معلق", "غير نشط"])
                
                # بحث بتاريخ الزيارة
                days_options = st.slider("عدد الأيام منذ آخر زيارة", 0, 180, 30)
                
                # بحث بالفني المسؤول
                technicians = [u for u in users if u.get("role") == "technician"]
                tech_names = ["الكل"] + [u["username"] for u in technicians]
                assigned_search = st.selectbox("بحث بالفني المسؤول", tech_names)
            
            # زر البحث
            search_btn = st.form_submit_button("🔍 بدء البحث", type="primary", use_container_width=True)
        
        # تطبيق البحث عند الضغط على الزر
        if search_btn:
            results = customers
            
            # تطبيق الفلاتر
            if name_search:
                results = [c for c in results if name_search.lower() in c.get("name", "").lower()]
            
            if phone_search:
                results = [c for c in results if phone_search in c.get("phone", "")]
            
            if category_search != "الكل":
                results = [c for c in results if c.get("category") == category_search]
            
            if status_search != "الكل":
                results = [c for c in results if c.get("status", "نشط") == status_search]
            
            if assigned_search != "الكل":
                results = [c for c in results if c.get("assigned_to") == assigned_search]
            
            if days_options > 0:
                filtered_results = []
                today = datetime.today()
                for c in results:
                    try:
                        last_visit = datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")
                        if (today - last_visit).days >= days_options:
                            filtered_results.append(c)
                    except:
                        pass
                results = filtered_results
            
            # عرض النتائج
            if results:
                st.success(f"🎯 تم العثور على **{len(results)}** عميل")
                
                # تحويل النتائج إلى DataFrame
                results_df = pd.DataFrame(results)
                
                # عرض النتائج
                display_cols = ["id", "name", "phone", "category", "last_visit", "status", "assigned_to"]
                display_cols = [col for col in display_cols if col in results_df.columns]
                
                st.dataframe(results_df[display_cols], use_container_width=True, height=400)
            else:
                st.warning("❌ لا توجد نتائج مطابقة لمعايير البحث")
    
    # تذكير الزيارات
    elif choice == "⏰ تذكير الزيارة":
        st.title("⏰ تذكير الزيارات")
        st.markdown("---")
        
        if not customers:
            st.info("لا يوجد عملاء لعرض التذكيرات.")
        
        # خيارات الفلترة
        col1, col2 = st.columns(2)
        
        with col1:
            days_threshold = st.slider("حدد عدد الأيام منذ آخر زيارة", 
                                      min_value=7, max_value=180, value=30, step=1)
        
        with col2:
            # فلترة إضافية بالفني
            technicians = [u for u in users if u.get("role") == "technician"]
            tech_names = ["الكل"] + [u["username"] for u in technicians]
            filter_tech = st.selectbox("فلترة بالفني المسؤول", tech_names)
        
        # حساب العملاء المطلوب زيارتهم
        today = datetime.today()
        due_customers = []
        
        for c in customers:
            try:
                last_visit = datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")
                days_since = (today - last_visit).days
                
                if days_since >= days_threshold:
                    # تطبيق فلترة الفني إذا تم تحديدها
                    if filter_tech == "الكل" or c.get("assigned_to") == filter_tech:
                        # إضافة عدد الأيام المتأخرة
                        c_copy = c.copy()
                        c_copy["days_late"] = days_since
                        due_customers.append(c_copy)
            except:
                pass
        
        # عرض النتائج
        if due_customers:
            st.warning(f"⚠️ يوجد **{len(due_customers)}** عميل بحاجة للزيارة (منذ {days_threshold} يوم أو أكثر)")
            
            # تحويل إلى DataFrame
            due_df = pd.DataFrame(due_customers)
            
            # عرض البيانات
            display_cols = ["name", "phone", "category", "last_visit", "days_late", "assigned_to", "notes"]
            display_cols = [col for col in display_cols if col in due_df.columns]
            
            st.dataframe(due_df[display_cols], use_container_width=True, height=400)
            
            st.markdown("---")
            
            # خيارات الإجراءات
            if user.get("role") == "admin":
                if st.button("📅 تحديث كل التواريخ", use_container_width=True, type="primary"):
                    for c in due_customers:
                        original_customer = next((cust for cust in customers if cust["id"] == c["id"]), None)
                        if original_customer:
                            original_customer["last_visit"] = str(today.date())
                            original_customer["next_visit"] = str(today.date() + timedelta(days=30))
                    
                    if save_customers():
                        st.success("✅ تم تحديث جميع التواريخ بنجاح")
                        st.balloons()
                        time.sleep(2)
                        st.experimental_rerun()
        else:
            st.success(f"🎉 ممتاز! لا يوجد عملاء متأخرين عن الزيارة (أكثر من {days_threshold} يوم)")
    
    # إدارة الفنيين
    elif choice == "👷 إدارة الفنيين" and role == "admin":
        st.title("👷 إدارة الفنيين")
        st.markdown("---")
        
        # تبويبات
        tab1, tab2 = st.tabs(["➕ إضافة فني", "📋 قائمة الفنيين"])
        
        with tab1:
            st.subheader("إضافة فني جديد")
            
            with st.form("add_technician_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_username = st.text_input("اسم المستخدم *", placeholder="أدخل اسم المستخدم")
                    new_fullname = st.text_input("الاسم الكامل", placeholder="الاسم الثلاثي")
                    new_phone = st.text_input("رقم الهاتف", placeholder="رقم للتواصل")
                
                with col2:
                    new_password = st.text_input("كلمة المرور *", type="password", 
                                               placeholder="أدخل كلمة مرور قوية")
                    confirm_password = st.text_input("تأكيد كلمة المرور *", type="password", 
                                                   placeholder="أعد إدخال كلمة المرور")
                    new_email = st.text_input("البريد الإلكتروني (اختياري)", placeholder="example@company.com")
                
                st.caption("* الحقول المطلوبة")
                
                submit_btn = st.form_submit_button("➕ إضافة الفني", type="primary", use_container_width=True)
                
                if submit_btn:
                    if new_username and new_password:
                        if new_password == confirm_password:
                            # التحقق من عدم تكرار اسم المستخدم
                            if any(u["username"] == new_username for u in users):
                                st.error("❌ اسم المستخدم موجود مسبقاً")
                            else:
                                new_technician = {
                                    "username": new_username,
                                    "password": new_password,
                                    "full_name": new_fullname,
                                    "phone": new_phone,
                                    "email": new_email,
                                    "role": "technician",
                                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "created_by": user["username"],
                                    "status": "active"
                                }
                                
                                users.append(new_technician)
                                if save_users():
                                    st.success(f"✅ تم إضافة الفني **{new_username}** بنجاح")
                                    st.balloons()
                        else:
                            st.error("❌ كلمات المرور غير متطابقة")
                    else:
                        st.warning("⚠️ يرجى ملء الحقول المطلوبة (*)")
        
        with tab2:
            st.subheader("قائمة الفنيين")
            
            # فلترة الفنيين
            technicians = [u for u in users if u.get("role") == "technician"]
            
            if not technicians:
                st.info("لا يوجد فنيين مسجلين بعد.")
            else:
                # تحضير البيانات للعرض
                tech_data = []
                for tech in technicians:
                    # حساب عدد العملاء المسؤول عنهم
                    assigned_count = len([c for c in customers if c.get("assigned_to") == tech["username"]])
                    
                    tech_data.append({
                        "اسم المستخدم": tech.get("username"),
                        "الاسم الكامل": tech.get("full_name", ""),
                        "الهاتف": tech.get("phone", ""),
                        "البريد الإلكتروني": tech.get("email", ""),
                        "عدد العملاء": assigned_count,
                        "الحالة": tech.get("status", "active"),
                        "تاريخ الإضافة": tech.get("created_at", "").split(" ")[0] if tech.get("created_at") else ""
                    })
                
                # عرض البيانات
                tech_df = pd.DataFrame(tech_data)
                st.dataframe(tech_df, use_container_width=True, height=300)
    
    # خريطة العملاء
    elif choice == "🗺️ خريطة العملاء":
        st.title("🗺️ خريطة مواقع العملاء")
        st.markdown("---")
        
        if not customers:
            st.info("لا يوجد عملاء لعرضهم على الخريطة.")
            return
        
        # فلترة الخريطة
        col1, col2 = st.columns(2)
        
        with col1:
            categories = list(set(c.get("category", "") for c in customers if c.get("category")))
            map_category = st.selectbox("التصنيف", ["الكل"] + sorted(categories))
        
        with col2:
            map_status = st.selectbox("الحالة", ["الكل", "نشط", "معلق", "غير نشط"])
        
        # تجهيز البيانات للخريطة
        map_data = []
        map_info = []
        
        for customer in customers:
            # تطبيق الفلاتر
            if map_category != "الكل" and customer.get("category") != map_category:
                continue
            
            if map_status != "الكل" and customer.get("status", "نشط") != map_status:
                continue
            
            # التحقق من وجود إحداثيات
            location = customer.get("location", "")
            if location:
                try:
                    # تحليل الإحداثيات
                    lat, lon = map(float, location.split(","))
                    
                    # إضافة بيانات الخريطة
                    map_point = {
                        "lat": lat,
                        "lon": lon,
                        "name": customer.get("name", "بدون اسم"),
                        "category": customer.get("category", "غير محدد")
                    }
                    
                    map_data.append(map_point)
                    map_info.append(customer)
                except:
                    continue
        
        # عرض الخريطة
        if map_data:
            st.success(f"📍 تم العثور على **{len(map_data)}** موقع صالح للعرض")
            
            # تحويل إلى DataFrame للخريطة
            map_df = pd.DataFrame(map_data)
            
            # عرض الخريطة
            st.map(map_df)
            
            st.markdown("---")
            
            # عرض تفاصيل المواقع
            with st.expander("📋 عرض تفاصيل المواقع على الخريطة"):
                if map_info:
                    info_df = pd.DataFrame(map_info)
                    display_cols = ["name", "phone", "category", "location", "last_visit"]
                    display_cols = [col for col in display_cols if col in info_df.columns]
                    
                    st.dataframe(info_df[display_cols], use_container_width=True, height=300)
            
            # تعليمات لإضافة إحداثيات
            st.info("""
            **💡 كيفية إضافة إحداثيات:**
            1. افتح Google Maps
            2. ابحث عن موقع العميل
            3. انقر بزر الماوس الأيمن على الموقع
            4. انسخ الإحداثيات (الرقم الأول)
            5. الصقها في حقل الإحداثيات عند إضافة العميل
            """)
        else:
            st.warning("⚠️ لا توجد إحداثيات صالحة للعرض مع الفلاتر المحددة")
    
    # التقارير
    elif choice == "📊 التقارير" and role == "admin":
        st.title("📊 تقارير وإحصائيات النظام")
        st.markdown("---")
        
        if not customers:
            st.info("لا توجد بيانات كافية لإنشاء التقارير.")
            return
        
        # تبويبات التقارير
        tab1, tab2 = st.tabs(["📈 إحصائيات عامة", "📅 تقارير زمنية"])
        
        with tab1:
            st.subheader("إحصائيات عامة")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # إحصائيات العملاء
                st.markdown("#### 📋 إحصائيات العملاء")
                
                total_customers = len(customers)
                
                # حسب الحالة
                status_stats = {}
                for c in customers:
                    status = c.get("status", "نشط")
                    status_stats[status] = status_stats.get(status, 0) + 1
                
                for status, count in status_stats.items():
                    st.metric(f"عملاء {status}", count)
                
                # حسب عدد الزيارات المتأخرة
                today = datetime.today()
                due_count = 0
                for c in customers:
                    try:
                        last_visit = datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")
                        if (today - last_visit).days >= 30:
                            due_count += 1
                    except:
                        pass
                
                st.metric("زيارات متأخرة", due_count)
            
            with col2:
                # إحصائيات الفنيين
                st.markdown("#### 👷 إحصائيات الفنيين")
                
                technicians = [u for u in users if u.get("role") == "technician"]
                st.metric("عدد الفنيين", len(technicians))
            
            st.markdown("---")
            
            # رسم بياني للتوزيع
            st.subheader("📊 رسم بياني للتوزيع")
            
            # توزيع حسب التصنيف
            category_dist = {}
            for c in customers:
                category = c.get("category", "غير محدد")
                category_dist[category] = category_dist.get(category, 0) + 1
            
            if category_dist:
                cat_df = pd.DataFrame(list(category_dist.items()), columns=["التصنيف", "العدد"])
                st.bar_chart(cat_df.set_index("التصنيف"))
        
        with tab2:
            st.subheader("تقارير زمنية")
            
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input("من تاريخ", datetime.today() - timedelta(days=30))
            
            with col2:
                end_date = st.date_input("إلى تاريخ", datetime.today())
            
            if st.button("إنشاء التقرير", type="primary"):
                # فلترة العملاء في الفترة
                period_customers = []
                for c in customers:
                    try:
                        added_date = datetime.strptime(c.get("added_date", "2000-01-01"), "%Y-%m-%d").date()
                        if start_date <= added_date <= end_date:
                            period_customers.append(c)
                    except:
                        pass
                
                if period_customers:
                    st.success(f"📊 تم العثور على **{len(period_customers)}** عميل في الفترة المحددة")
                    
                    # تحليل البيانات
                    period_df = pd.DataFrame(period_customers)
                    
                    # عرض النتائج
                    st.dataframe(period_df, use_container_width=True, height=400)
                    
                    # خيارات التصدير
                    csv = period_df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(
                        label="📥 تحميل التقرير",
                        data=csv,
                        file_name=f"report_{start_date}_{end_date}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.warning("لا توجد بيانات في الفترة المحددة")
    
    # تسجيل الخروج
    elif choice == "🚪 تسجيل الخروج":
        logout()
