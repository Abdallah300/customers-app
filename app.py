import streamlit as st
import json, os, re
from datetime import datetime, timedelta
import pandas as pd
import hashlib
import pytz
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# ------------------ إعدادات التطبيق ------------------
st.set_page_config(
    page_title="Power Life - نظام إدارة العملاء",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ الثوابت ------------------
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"
CUSTOMERS_BACKUP_FILE = "customers_backup.json"
TIMEZONE = pytz.timezone("Africa/Cairo")

# ------------------ الأنماط CSS ------------------
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1E3A8A;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #10B981;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #F59E0B;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #FEE2E2;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #EF4444;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #DBEAFE;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #3B82F6;
        margin: 1rem 0;
    }
    .card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    .dataframe {
        width: 100%;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

# ------------------ فئات العملاء ------------------
CUSTOMER_CATEGORIES = {
    "منزل": "🏠",
    "شركة": "🏢",
    "مدرسة": "🏫",
    "مستشفى": "🏥",
    "مصنع": "🏭",
    "فندق": "🏨",
    "متجر": "🛒"
}

# ------------------ دوال المساعدة ------------------
def hash_password(password: str) -> str:
    """تشفير كلمة المرور باستخدام SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_phone(phone: str) -> bool:
    """التحقق من صحة رقم الهاتف المصري"""
    pattern = r'^(01[0-2,5]{1}[0-9]{8}|02[0-9]{7})$'
    return bool(re.match(pattern, phone.strip()))

def validate_coordinates(coords: str) -> bool:
    """التحقق من صحة الإحداثيات"""
    try:
        lat, lon = map(float, coords.split(','))
        return -90 <= lat <= 90 and -180 <= lon <= 180
    except:
        return False

def format_coordinates(coords: str) -> Optional[str]:
    """تنسيق الإحداثيات بشكل صحيح"""
    if not coords or ',' not in coords:
        return None
    try:
        lat, lon = map(float, coords.split(','))
        return f"{lat:.6f},{lon:.6f}"
    except:
        return None

def create_backup():
    """إنشاء نسخة احتياطية من بيانات العملاء"""
    try:
        if os.path.exists(CUSTOMERS_FILE):
            with open(CUSTOMERS_FILE, 'r', encoding='utf-8') as f:
                data = f.read()
            with open(CUSTOMERS_BACKUP_FILE, 'w', encoding='utf-8') as f:
                f.write(data)
    except Exception as e:
        st.error(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")

# ------------------ إدارة الملفات ------------------
def load_data(filename: str, default_value: list = None) -> list:
    """تحميل البيانات من ملف JSON"""
    if default_value is None:
        default_value = []
    
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else default_value
    except Exception as e:
        st.error(f"خطأ في تحميل {filename}: {str(e)}")
    
    return default_value

def save_data(filename: str, data: list):
    """حفظ البيانات إلى ملف JSON"""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        if filename == CUSTOMERS_FILE:
            create_backup()
    except Exception as e:
        st.error(f"خطأ في حفظ {filename}: {str(e)}")

# ------------------ تحميل البيانات ------------------
users = load_data(USERS_FILE, [])
customers = load_data(CUSTOMERS_FILE, [])

# ------------------ تهيئة المستخدم الإداري ------------------
if not any(u.get("username") == "admin" for u in users):
    users.append({
        "username": "admin",
        "password": hash_password("admin123"),  # كلمة مرور مشفرة
        "role": "admin",
        "created_at": datetime.now(TIMEZONE).isoformat(),
        "full_name": "مدير النظام"
    })
    save_data(USERS_FILE, users)

# ------------------ إعداد الجلسة ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# ------------------ تسجيل الخروج ------------------
def logout():
    """تسجيل خروج المستخدم"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = "login"
    st.success("تم تسجيل الخروج بنجاح")
    st.experimental_rerun()

# ------------------ صفحة تسجيل الدخول ------------------
def login_page():
    """عرض صفحة تسجيل الدخول"""
    
    # الترويسة
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🏢 Power Life")
        st.subheader("نظام إدارة العملاء المتقدم")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # نموذج تسجيل الدخول
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔐 تسجيل الدخول")
            
            username = st.text_input(
                "اسم المستخدم",
                placeholder="أدخل اسم المستخدم"
            )
            
            password = st.text_input(
                "كلمة المرور",
                type="password",
                placeholder="أدخل كلمة المرور"
            )
            
            if st.button("تسجيل الدخول", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("يرجى ملء جميع الحقول")
                else:
                    hashed_password = hash_password(password)
                    user = next(
                        (u for u in users if u.get("username") == username and u.get("password") == hashed_password),
                        None
                    )
                    
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.current_user = user
                        st.success(f"مرحباً بك {user.get('full_name', username)}")
                        st.experimental_rerun()
                    else:
                        st.error("اسم المستخدم أو كلمة المرور غير صحيحة")
            
            # معلومات الحساب الافتراضي (للتنمية فقط)
            if st.checkbox("عرض بيانات الدخول للاختبار"):
                st.info("""
                **حساب المدير:**
                - اسم المستخدم: admin
                - كلمة المرور: admin123
                """)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ------------------ لوحة التحكم ------------------
def dashboard():
    """لوحة التحكم الرئيسية"""
    
    user = st.session_state.current_user
    role = user.get("role", "technician")
    username = user.get("username", "")
    
    # الشريط الجانبي
    with st.sidebar:
        st.markdown(f"""
        <div class="card">
            <h4>👤 {user.get('full_name', username)}</h4>
            <p><strong>الصلاحية:</strong> {role}</p>
            <p><strong>عدد العملاء:</strong> {len(customers)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # القائمة حسب الصلاحية
        if role == "admin":
            menu_options = {
                "📊 لوحة الإحصائيات": "dashboard",
                "➕ إضافة عميل جديد": "add_customer",
                "📋 قائمة العملاء": "view_customers",
                "🔍 بحث متقدم": "search",
                "⏰ تذكير الزيارات": "reminders",
                "🗺️ خريطة العملاء": "map_view",
                "👥 إدارة المستخدمين": "manage_users",
                "⚙️ الإعدادات": "settings",
                "🚪 تسجيل الخروج": "logout"
            }
        else:
            menu_options = {
                "📊 لوحة الإحصائيات": "dashboard",
                "📋 قائمة العملاء": "view_customers",
                "🔍 بحث متقدم": "search",
                "⏰ تذكير الزيارات": "reminders",
                "🗺️ خريطة العملاء": "map_view",
                "🚪 تسجيل الخروج": "logout"
            }
        
        # زر القائمة
        selected = st.selectbox(
            "القائمة الرئيسية",
            list(menu_options.keys())
        )
        
        if st.button("تحديث الصفحة"):
            st.experimental_rerun()
    
    # تحديث حالة الصفحة
    st.session_state.page = menu_options[selected]
    
    # عرض الصفحة المحددة
    page_handlers = {
        "dashboard": show_dashboard,
        "add_customer": add_customer_page,
        "view_customers": view_customers_page,
        "search": search_page,
        "reminders": reminders_page,
        "map_view": map_view_page,
        "manage_users": manage_users_page,
        "settings": settings_page,
        "logout": logout
    }
    
    if st.session_state.page in page_handlers:
        page_handlers[st.session_state.page]()

# ------------------ الصفحات الفرعية ------------------
def show_dashboard():
    """عرض لوحة الإحصائيات"""
    st.markdown("## 📊 لوحة الإحصائيات")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.metric("إجمالي العملاء", len(customers))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        overdue = len([c for c in customers if is_visit_overdue(c)])
        st.metric("العملاء المتأخرين", overdue, delta=f"-{overdue}" if overdue else None)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        companies = len([c for c in customers if c.get("category") == "شركة"])
        st.metric("الشركات", companies)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        homes = len([c for c in customers if c.get("category") == "منزل"])
        st.metric("المنازل", homes)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # آخر 5 عملاء تمت إضافتهم
    st.markdown("### 📝 آخر العملاء المضافين")
    if customers:
        recent_customers = sorted(customers, key=lambda x: x.get('id', 0), reverse=True)[:5]
        df_recent = pd.DataFrame(recent_customers)
        st.dataframe(df_recent[['id', 'name', 'phone', 'category', 'last_visit']])
    else:
        st.info("لا يوجد عملاء بعد.")

def is_visit_overdue(customer):
    """التحقق إذا كانت زيارة العميل متأخرة"""
    try:
        last_visit = datetime.fromisoformat(customer.get("last_visit", ""))
        days_diff = (datetime.now(TIMEZONE) - last_visit).days
        return days_diff > 30
    except:
        return False

def add_customer_page():
    """صفحة إضافة عميل جديد"""
    st.markdown("## ➕ إضافة عميل جديد")
    
    with st.form("add_customer_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("اسم العميل *", help="اسم العميل بالكامل")
            phone = st.text_input("رقم الهاتف *", help="رقم هاتف مصري صالح")
            category = st.selectbox(
                "التصنيف *",
                options=list(CUSTOMER_CATEGORIES.keys()),
                format_func=lambda x: f"{CUSTOMER_CATEGORIES[x]} {x}"
            )
        
        with col2:
            location = st.text_input(
                "إحداثيات الموقع",
                placeholder="مثال: 30.0444,31.2357",
                help="إحداثيات GPS من Google Maps"
            )
            last_visit = st.date_input(
                "تاريخ آخر زيارة *",
                datetime.now(TIMEZONE).date()
            )
        
        notes = st.text_area(
            "ملاحظات إضافية",
            height=100,
            placeholder="أي ملاحظات إضافية عن العميل..."
        )
        
        # التحقق من الحقول الإلزامية
        st.markdown("**الحقول المميزة بعلامة (*) إلزامية**")
        
        submitted = st.form_submit_button("إضافة العميل", type="primary")
        
        if submitted:
            if not name or not phone or not category:
                st.error("يرجى ملء جميع الحقول الإلزامية (*)")
            elif not validate_phone(phone):
                st.error("رقم الهاتف غير صالح. يرجى إدخال رقم هاتف مصري صحيح")
            elif location and not validate_coordinates(location):
                st.error("إحداثيات الموقع غير صالحة. يرجى التأكد من التنسيق")
            else:
                new_customer = {
                    "id": len(customers) + 1,
                    "name": name.strip(),
                    "phone": phone.strip(),
                    "category": category,
                    "location": format_coordinates(location) if location else "",
                    "notes": notes.strip(),
                    "last_visit": last_visit.isoformat(),
                    "created_at": datetime.now(TIMEZONE).isoformat(),
                    "created_by": st.session_state.current_user.get("username"),
                    "status": "active"
                }
                
                customers.append(new_customer)
                save_data(CUSTOMERS_FILE, customers)
                
                st.success("✅ تم إضافة العميل بنجاح")
                st.balloons()
                
                # عرض ملخص العميل المضاف
                with st.expander("عرض تفاصيل العميل المضاف"):
                    st.json(new_customer)

def view_customers_page():
    """صفحة عرض قائمة العملاء"""
    st.markdown("## 📋 قائمة العملاء")
    
    if not customers:
        st.info("لا يوجد عملاء مسجلين حتى الآن.")
        return
    
    # أشرطة التصفية
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_category = st.selectbox(
            "التصنيف",
            ["الكل"] + list(CUSTOMER_CATEGORIES.keys())
        )
    
    with col2:
        filter_status = st.selectbox(
            "الحالة",
            ["الكل", "نشط", "غير نشط"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "ترتيب حسب",
            ["تاريخ الإضافة", "اسم العميل", "تاريخ آخر زيارة"]
        )
    
    # تطبيق الفلاتر
    filtered_customers = customers.copy()
    
    if filter_category != "الكل":
        filtered_customers = [c for c in filtered_customers if c.get("category") == filter_category]
    
    if filter_status == "نشط":
        filtered_customers = [c for c in filtered_customers if c.get("status") != "inactive"]
    elif filter_status == "غير نشط":
        filtered_customers = [c for c in filtered_customers if c.get("status") == "inactive"]
    
    # التصفية حسب الترتيب
    if sort_by == "اسم العميل":
        filtered_customers.sort(key=lambda x: x.get("name", ""))
    elif sort_by == "تاريخ آخر زيارة":
        filtered_customers.sort(key=lambda x: x.get("last_visit", ""), reverse=True)
    else:
        filtered_customers.sort(key=lambda x: x.get("id", 0), reverse=True)
    
    # عرض البيانات
    if filtered_customers:
        df = pd.DataFrame(filtered_customers)
        
        # تنسيق الأعمدة
        display_cols = ["id", "name", "phone", "category", "last_visit", "status"]
        if "notes" in df.columns:
            display_cols.append("notes")
        
        st.dataframe(
            df[display_cols],
            use_container_width=True,
            height=400
        )
        
        # خيارات التصدير
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 تصدير إلى Excel"):
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="تحميل CSV",
                    data=csv,
                    file_name=f"customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    else:
        st.warning("لا توجد نتائج مطابقة للبحث")

def search_page():
    """صفحة البحث المتقدم"""
    st.markdown("## 🔍 بحث متقدم")
    
    search_tab1, search_tab2 = st.tabs(["بحث سريع", "بحث متقدم"])
    
    with search_tab1:
        quick_search = st.text_input(
            "ابحث عن عميل",
            placeholder="اكتب اسم العميل، رقم الهاتف، أو الملاحظات..."
        )
        
        if quick_search:
            results = []
            for customer in customers:
                search_fields = [str(customer.get(field, "")).lower() for field in ['name', 'phone', 'notes', 'category']]
                if any(quick_search.lower() in field for field in search_fields):
                    results.append(customer)
            
            if results:
                st.success(f"تم العثور على {len(results)} نتيجة")
                df_results = pd.DataFrame(results)
                st.dataframe(df_results[['id', 'name', 'phone', 'category', 'last_visit']])
            else:
                st.info("لا توجد نتائج مطابقة")
    
    with search_tab2:
        with st.form("advanced_search"):
            col1, col2 = st.columns(2)
            
            with col1:
                search_name = st.text_input("اسم العميل")
                search_phone = st.text_input("رقم الهاتف")
            
            with col2:
                search_category = st.multiselect(
                    "التصنيف",
                    list(CUSTOMER_CATEGORIES.keys())
                )
                search_date_from = st.date_input("تاريخ الزيارة من")
                search_date_to = st.date_input("تاريخ الزيارة إلى")
            
            if st.form_submit_button("🔍 بحث"):
                # تطبيق البحث
                pass

def reminders_page():
    """صفحة تذكير الزيارات"""
    st.markdown("## ⏰ تذكير الزيارات المتأخرة")
    
    overdue_customers = []
    warning_customers = []
    
    for customer in customers:
        try:
            last_visit = datetime.fromisoformat(customer.get("last_visit", ""))
            days_diff = (datetime.now(TIMEZONE) - last_visit).days
            
            if days_diff > 30:
                customer['days_overdue'] = days_diff - 30
                overdue_customers.append(customer)
            elif days_diff > 25:
                customer['days_until_due'] = 30 - days_diff
                warning_customers.append(customer)
        except:
            continue
    
    # العملاء المتأخرين
    if overdue_customers:
        st.markdown(f"### ⚠️ العملاء المتأخرين ({len(overdue_customers)})")
        overdue_df = pd.DataFrame(overdue_customers)
        overdue_df['التأخير (أيام)'] = overdue_df['days_overdue']
        st.dataframe(overdue_df[['name', 'phone', 'category', 'last_visit', 'التأخير (أيام)']])
    else:
        st.success("🎉 لا يوجد عملاء متأخرين عن الزيارة")
    
    # العملاء الذين يقترب موعدهم
    if warning_customers:
        st.markdown(f"### 📅 العملاء المقترب موعدهم ({len(warning_customers)})")
        warning_df = pd.DataFrame(warning_customers)
        warning_df['المتبقي (أيام)'] = warning_df['days_until_due']
        st.dataframe(warning_df[['name', 'phone', 'category', 'last_visit', 'المتبقي (أيام)']])

def map_view_page():
    """صفحة خريطة العملاء"""
    st.markdown("## 🗺️ خريطة العملاء")
    
    # استخراج الإحداثيات الصالحة
    map_data = []
    invalid_coords = []
    
    for customer in customers:
        coords = customer.get("location", "")
        if coords and validate_coordinates(coords):
            try:
                lat, lon = map(float, coords.split(','))
                map_data.append({
                    "name": customer.get("name", ""),
                    "category": customer.get("category", ""),
                    "lat": lat,
                    "lon": lon
                })
            except:
                invalid_coords.append(customer.get("name"))
        else:
            invalid_coords.append(customer.get("name"))
    
    if map_data:
        df_map = pd.DataFrame(map_data)
        
        # عرض الخريطة
        st.map(df_map, zoom=10)
        
        # عرض البيانات
        st.markdown("### تفاصيل العملاء على الخريطة")
        st.dataframe(df_map)
        
        if invalid_coords:
            st.warning(f"لا توجد إحداثيات صالحة لـ {len(invalid_coords)} عميل")
            with st.expander("عرض قائمة العملاء بدون إحداثيات"):
                st.write(", ".join(invalid_coords))
    else:
        st.error("لا توجد إحداثيات صالحة للعرض على الخريطة")
        st.info("يرجى إضافة إحداثيات صالحة للعملاء لعرضهم على الخريطة")

def manage_users_page():
    """صفحة إدارة المستخدمين (للمدير فقط)"""
    if st.session_state.current_user.get("role") != "admin":
        st.error("⛔ ليس لديك صلاحية للوصول إلى هذه الصفحة")
        return
    
    st.markdown("## 👥 إدارة المستخدمين")
    
    tab1, tab2 = st.tabs(["إضافة مستخدم", "عرض المستخدمين"])
    
    with tab1:
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("الاسم الكامل *")
                username = st.text_input("اسم المستخدم *")
            
            with col2:
                password = st.text_input("كلمة المرور *", type="password")
                confirm_password = st.text_input("تأكيد كلمة المرور *", type="password")
                role = st.selectbox("الدور *", ["technician", "admin"])
            
            if st.form_submit_button("إضافة المستخدم", type="primary"):
                if not all([full_name, username, password, confirm_password]):
                    st.error("يرجى ملء جميع الحقول الإلزامية (*)")
                elif password != confirm_password:
                    st.error("كلمات المرور غير متطابقة")
                elif any(u.get("username") == username for u in users):
                    st.error("اسم المستخدم موجود بالفعل")
                else:
                    new_user = {
                        "username": username,
                        "password": hash_password(password),
                        "role": role,
                        "full_name": full_name,
                        "created_at": datetime.now(TIMEZONE).isoformat(),
                        "created_by": st.session_state.current_user.get("username")
                    }
                    
                    users.append(new_user)
                    save_data(USERS_FILE, users)
                    st.success(f"✅ تم إضافة المستخدم {full_name} بنجاح")
    
    with tab2:
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    "الاسم": user.get("full_name", ""),
                    "اسم المستخدم": user.get("username", ""),
                    "الدور": user.get("role", ""),
                    "تاريخ الإنشاء": user.get("created_at", "")
                })
            
            df_users = pd.DataFrame(user_data)
            st.dataframe(df_users)
        else:
            st.info("لا يوجد مستخدمين مسجلين")

def settings_page():
    """صفحة الإعدادات"""
    st.markdown("## ⚙️ الإعدادات")
    
    with st.expander("إعدادات النظام"):
        st.info("إعدادات النظام العامة")
        
        backup_col, restore_col = st.columns(2)
        
        with backup_col:
            if st.button("إنشاء نسخة احتياطية"):
                create_backup()
                st.success("تم إنشاء النسخة الاحتياطية بنجاح")
        
        with restore_col:
            if os.path.exists(CUSTOMERS_BACKUP_FILE):
                if st.button("استعادة من النسخة الاحتياطية"):
                    with open(CUSTOMERS_BACKUP_FILE, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    global customers
                    customers = backup_data
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم استعادة البيانات بنجاح")
            else:
                st.warning("لا توجد نسخة احتياطية")
    
    with st.expander("معلومات النظام"):
        st.write(f"**عدد العملاء:** {len(customers)}")
        st.write(f"**عدد المستخدمين:** {len(users)}")
        st.write(f"**آخر تحديث:** {datetime.now(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button("تحديث البيانات"):
            global users, customers
            users = load_data(USERS_FILE, [])
            customers = load_data(CUSTOMERS_FILE, [])
            st.success("تم تحديث البيانات")

# ------------------ التطبيق الرئيسي ------------------
def main():
    """الدالة الرئيسية للتطبيق"""
    
    # التحقق من حالة تسجيل الدخول
    if not st.session_state.logged_in:
        login_page()
    else:
        # شريط التنقل العلوي
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"# 🏢 Power Life - نظام إدارة العملاء")
        
        with col2:
            st.markdown(f"**👤 {st.session_state.current_user.get('full_name', '')}**")
        
        with col3:
            if st.button("🚪 تسجيل الخروج"):
                logout()
        
        st.markdown("---")
        
        # عرض لوحة التحكم
        dashboard()
        
        # التذييل
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #666; padding: 1rem;'>
                <p>© 2024 Power Life - نظام إدارة العملاء المتقدم</p>
                <p>الإصدار 2.0 | تطوير باستخدام Streamlit</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# ------------------ تشغيل التطبيق ------------------
if __name__ == "__main__":
    main()
