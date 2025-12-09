import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd
import time

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
        st.error(f"❌ خطأ في حفظ حساب المدير: {str(e)}")

def save_users():
    """حفظ بيانات المستخدمين"""
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"❌ خطأ في حفظ المستخدمين: {str(e)}")
        return False

def save_customers():
    """حفظ بيانات العملاء"""
    try:
        with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
            json.dump(customers, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"❌ خطأ في حفظ العملاء: {str(e)}")
        return False

# ------------------ إعداد الجلسة ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "page" not in st.session_state:
    st.session_state.page = "login"

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
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    
    /* تنسيق النماذج */
    .stForm {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    
    /* تنسيق العناوين */
    h1, h2, h3 {
        color: #2c3e50;
    }
    
    /* تنسيق الجداول */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* تنسيق البطاقات */
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* تنسيق رسائل التنبيه */
    .stAlert {
        border-radius: 10px;
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
    
    /* تنسيق القائمة الجانبية */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #3498db 100%);
    }
    
    /* تنسيق أزرار القائمة */
    div[data-testid="stRadio"] > label {
        background-color: transparent !important;
        color: white !important;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    
    div[data-testid="stRadio"] > label:hover {
        background-color: rgba(255,255,255,0.1) !important;
    }
    
    div[data-testid="stRadio"] > label[data-testid="stRadio"] {
        background-color: rgba(255,255,255,0.2) !important;
    }
    
    </style>
""", unsafe_allow_html=True)

# ------------------ تسجيل الخروج ------------------
def logout():
    """تسجيل خروج المستخدم"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = "login"
    st.experimental_rerun()

# ------------------ الصفحات ------------------
def login_page():
    """صفحة تسجيل الدخول"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    st.markdown('<h1 class="login-title">🏢 Power Life</h1>', unsafe_allow_html=True)
    st.markdown('<h3>🔑 تسجيل الدخول</h3>', unsafe_allow_html=True)
    
    # إظهار رسالة إذا تم إعادة تعيين النظام
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
                st.success(f"✅ تم تسجيل الدخول بنجاح")
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
    <p style="margin-bottom: 0; font-size: 12px; color: #666;">تم إنشاء هذا الحساب تلقائياً لأول استخدام</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def dashboard_page():
    """لوحة التحكم الرئيسية"""
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
            <p style="margin: 5px 0; opacity: 0.9;">
                <strong>اسم المستخدم:</strong> {username}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # القائمة الرئيسية
        st.markdown("<h3 style='color: white;'>📋 القائمة الرئيسية</h3>", unsafe_allow_html=True)
        
        menu_options = []
        if role == "admin":
            menu_options = [
                {"icon": "🏠", "label": "الصفحة الرئيسية", "id": "home"},
                {"icon": "➕", "label": "إضافة عميل", "id": "add_customer"},
                {"icon": "📋", "label": "عرض العملاء", "id": "view_customers"},
                {"icon": "✏️", "label": "تعديل العملاء", "id": "edit_customers"},
                {"icon": "🔎", "label": "بحث متقدم", "id": "search"},
                {"icon": "⏰", "label": "تذكير الزيارة", "id": "reminders"},
                {"icon": "👷", "label": "إدارة الفنيين", "id": "manage_tech"},
                {"icon": "🗺️", "label": "خريطة العملاء", "id": "map"},
                {"icon": "📊", "label": "التقارير", "id": "reports"},
                {"icon": "⚙️", "label": "الإعدادات", "id": "settings"},
                {"icon": "🚪", "label": "تسجيل الخروج", "id": "logout"}
            ]
        else:
            menu_options = [
                {"icon": "🏠", "label": "الصفحة الرئيسية", "id": "home"},
                {"icon": "📋", "label": "عرض العملاء", "id": "view_customers"},
                {"icon": "🔎", "label": "بحث متقدم", "id": "search"},
                {"icon": "⏰", "label": "تذكير الزيارة", "id": "reminders"},
                {"icon": "🗺️", "label": "خريطة العملاء", "id": "map"},
                {"icon": "🚪", "label": "تسجيل الخروج", "id": "logout"}
            ]
        
        # عرض القائمة
        selected_option = "home"
        for option in menu_options:
            if st.button(f"{option['icon']} {option['label']}", key=option['id'], use_container_width=True):
                selected_option = option['id']
        
        # زر النسخ الاحتياطي للمدير
        if role == "admin":
            st.divider()
            if st.button("📦 إنشاء نسخة احتياطية", use_container_width=True):
                if backup_files():
                    st.success("✅ تم إنشاء النسخة الاحتياطية")
                else:
                    st.error("❌ فشل في إنشاء النسخة")
    
    # المحتوى الرئيسي
    if selected_option == "home":
        home_page(user)
    elif selected_option == "add_customer":
        add_customer_page(user)
    elif selected_option == "view_customers":
        view_customers_page(user)
    elif selected_option == "edit_customers" and role == "admin":
        edit_customers_page(user)
    elif selected_option == "search":
        search_page(user)
    elif selected_option == "reminders":
        reminders_page(user)
    elif selected_option == "manage_tech" and role == "admin":
        manage_technicians_page(user)
    elif selected_option == "map":
        map_page(user)
    elif selected_option == "reports" and role == "admin":
        reports_page(user)
    elif selected_option == "settings" and role == "admin":
        settings_page(user)
    elif selected_option == "logout":
        logout()

def home_page(user):
    """الصفحة الرئيسية"""
    role = user.get("role", "technician")
    username = user.get("username", "")
    
    st.title(f"مرحباً بك {username} 👋")
    st.markdown("---")
    
    # بطاقات الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <h3>إجمالي العملاء</h3>
            <div class="value">{}</div>
            <p>عميل مسجل</p>
        </div>
        """.format(len(customers)), unsafe_allow_html=True)
    
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
        st.markdown("""
        <div class="stats-card">
            <h3>بحاجة لزيارة</h3>
            <div class="value">{}</div>
            <p>عميل متأخر</p>
        </div>
        """.format(due_count), unsafe_allow_html=True)
    
    # عدد الفنيين
    tech_count = len([u for u in users if u.get("role") == "technician"])
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <h3>عدد الفنيين</h3>
            <div class="value">{}</div>
            <p>فني نشط</p>
        </div>
        """.format(tech_count), unsafe_allow_html=True)
    
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
        st.markdown("""
        <div class="stats-card">
            <h3>جدد هذا الشهر</h3>
            <div class="value">{}</div>
            <p>عميل جديد</p>
        </div>
        """.format(new_this_month), unsafe_allow_html=True)
    
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
        if st.button("➕ إضافة عميل جديد", use_container_width=True):
            st.session_state.page = "add_customer"
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

def add_customer_page(user):
    """صفحة إضافة عميل"""
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
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit_btn = st.form_submit_button("💾 حفظ العميل", type="primary", use_container_width=True)
        with col2:
            clear_btn = st.form_submit_button("🗑️ مسح النموذج", type="secondary", use_container_width=True)
        
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
     
