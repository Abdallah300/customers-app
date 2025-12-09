import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd
import hashlib
import shutil
import time

# ------------------ الملفات والمجلدات ------------------
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"
ACTIVITY_LOG = "activity_log.json"
BACKUP_DIR = "backup"

# إنشاء مجلد النسخ الاحتياطي إذا لم يكن موجوداً
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# ------------------ الدوال المساعدة ------------------
def hash_password(password):
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

def backup_files():
    """إنشاء نسخة احتياطية"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if os.path.exists(USERS_FILE):
            shutil.copy2(USERS_FILE, f"{BACKUP_DIR}/users_{timestamp}.json")
        
        if os.path.exists(CUSTOMERS_FILE):
            shutil.copy2(CUSTOMERS_FILE, f"{BACKUP_DIR}/customers_{timestamp}.json")
        
        return True
    except:
        return False

def log_activity(username, action, details=""):
    """تسجيل نشاط المستخدم"""
    try:
        if os.path.exists(ACTIVITY_LOG):
            with open(ACTIVITY_LOG, "r", encoding="utf-8") as f:
                logs = json.load(f)
        else:
            logs = []
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": username,
            "action": action,
            "details": details
        }
        
        logs.append(log_entry)
        
        # حفظ فقط آخر 1000 سجل
        if len(logs) > 1000:
            logs = logs[-1000:]
        
        with open(ACTIVITY_LOG, "w", encoding="utf-8") as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    except:
        pass

# تحميل البيانات مع معالجة الأخطاء
def load_data():
    """تحميل البيانات من الملفات"""
    users = []
    customers = []
    
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
    except Exception as e:
        st.error(f"❌ خطأ في تحميل ملف المستخدمين: {str(e)}")
        users = []
    
    try:
        if os.path.exists(CUSTOMERS_FILE):
            with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
                customers = json.load(f)
    except Exception as e:
        st.error(f"❌ خطأ في تحميل ملف العملاء: {str(e)}")
        customers = []
    
    return users, customers

# تحميل البيانات
users, customers = load_data()

# إنشاء المدير لو مش موجود
admin_exists = any(u.get("username") == "Abdallah" for u in users)
if not admin_exists:
    hashed_password = hash_password("772001")
    users.append({
        "username": "Abdallah", 
        "password": hashed_password,  # تخزين كلمة المرور مشفرة
        "role": "admin",
        "created_at": datetime.now().isoformat()
    })
    
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        log_activity("system", "إنشاء حساب المدير")
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
        # إنشاء نسخة احتياطية قبل الحفظ
        backup_files()
        
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

if "last_activity" not in st.session_state:
    st.session_state.last_activity = time.time()

# إعدادات الجلسة
SESSION_TIMEOUT = 1800  # 30 دقيقة بالثواني

# التحقق من انتهاء الجلسة
if st.session_state.logged_in:
    if time.time() - st.session_state.last_activity > SESSION_TIMEOUT:
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.warning("⏰ انتهت الجلسة بسبب عدم النشاط. يرجى تسجيل الدخول مرة أخرى.")
        st.experimental_rerun()
    else:
        st.session_state.last_activity = time.time()

st.set_page_config(
    page_title="Power Life - إدارة العملاء",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ تسجيل الخروج ------------------
def logout():
    """تسجيل خروج المستخدم"""
    if st.session_state.current_user:
        log_activity(st.session_state.current_user["username"], "تسجيل الخروج")
    
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.last_activity = 0
    st.experimental_rerun()

# ------------------ تسجيل الدخول ------------------
if not st.session_state.logged_in:
    
    # تنسيق واجهة تسجيل الدخول
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            background-color: white;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.title("🏢 Power Life")
    st.markdown("### 🔑 تسجيل الدخول")
    
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        login_btn = st.button("تسجيل الدخول", type="primary", use_container_width=True)
    with col2:
        if st.button("مساعدة", use_container_width=True):
            st.info("""
            **بيانات الدخول الافتراضية:**
            - المدير: Abdallah / 772001
            """)
    
    if login_btn:
        if username and password:
            try:
                # البحث عن المستخدم
                user = None
                for u in users:
                    if u.get("username") == username:
                        user = u
                        break
                
                if user:
                    # المقارنة بعد تشفير كلمة المرور المدخلة
                    hashed_input_password = hash_password(password)
                    
                    if user.get("password") == hashed_input_password:
                        st.session_state.logged_in = True
                        st.session_state.current_user = user
                        st.session_state.last_activity = time.time()
                        
                        log_activity(username, "تسجيل الدخول")
                        
                        st.success(f"✅ مرحباً {username}")
                        st.balloons()
                        time.sleep(1)
                        st.experimental_rerun()
                    else:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                else:
                    st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                    
            except Exception as e:
                st.error(f"❌ خطأ في النظام: {str(e)}")
                st.error("تفاصيل الخطأ للمطور:")
                st.error(str(e))
        else:
            st.warning("⚠️ يرجى ملء جميع الحقول")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------ لوحة التحكم ------------------
else:
    user = st.session_state.current_user
    role = user.get("role", "technician")
    username = user.get("username", "")
    
    # تحديث وقت النشاط
    st.session_state.last_activity = time.time()
    
    # الشريط الجانبي
    with st.sidebar:
        st.title("لوحة التحكم")
        st.markdown(f"**المستخدم:** {username}")
        st.markdown(f"**الصلاحية:** {'مدير' if role == 'admin' else 'فني'}")
        st.divider()
        
        # القائمة حسب صلاحيات المستخدم
        if role == "admin":
            menu_options = [
                "🏠 الصفحة الرئيسية",
                "➕ إضافة عميل",
                "📋 عرض العملاء",
                "✏️ إدارة العملاء",
                "🔎 بحث متقدم",
                "⏰ تذكير الزيارة",
                "👷 إدارة الفنيين",
                "🗺️ خريطة العملاء",
                "📊 التقارير والإحصائيات",
                "⚙️ الإعدادات",
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
        
        choice = st.radio("القائمة", menu_options)
        
        # زر النسخ الاحتياطي (للمدير فقط)
        if role == "admin":
            st.divider()
            if st.button("📦 إنشاء نسخة احتياطية", use_container_width=True):
                if backup_files():
                    log_activity(username, "إنشاء نسخة احتياطية")
                    st.success("✅ تم إنشاء النسخة الاحتياطية")
                else:
                    st.error("❌ فشل في إنشاء النسخة الاحتياطية")
    
    # المحتوى الرئيسي
    # ----------- الصفحة الرئيسية -----------
    if choice == "🏠 الصفحة الرئيسية":
        st.title(f"مرحباً بك {username} 👋")
        
        # بطاقات إحصائية
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("إجمالي العملاء", len(customers))
        
        # حساب العملاء المطلوب زيارتهم
        today = datetime.today()
        due_customers = []
        for c in customers:
            try:
                last = datetime.strptime(c.get("last_visit", ""), "%Y-%m-%d")
                if today - last >= timedelta(days=30):
                    due_customers.append(c)
            except:
                pass
        
        with col2:
            st.metric("بحاجة لزيارة", len(due_customers))
        
        # عد الفنيين
        technicians = [u for u in users if u.get("role") == "technician"]
        with col3:
            st.metric("عدد الفنيين", len(technicians))
        
        # العملاء المضافين هذا الشهر
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
            st.metric("جدد هذا الشهر", new_this_month)
        
        st.divider()
        
        # آخر 5 عملاء
        st.subheader("🆕 أحدث العملاء")
        if customers:
            recent_customers = customers[-5:] if len(customers) > 5 else customers
            recent_df = pd.DataFrame(recent_customers)
            
            # عرض الأعمدة المهمة فقط
            if not recent_df.empty:
                display_cols = ["id", "name", "phone", "category", "last_visit"]
                display_cols = [col for col in display_cols if col in recent_df.columns]
                st.dataframe(recent_df[display_cols], use_container_width=True)
        else:
            st.info("لا يوجد عملاء بعد.")
        
        # العملاء المطلوب زيارتهم قريباً
        if due_customers:
            st.divider()
            st.subheader("🔔 عملاء بحاجة لزيارة فورية")
            due_df = pd.DataFrame(due_customers[:10])  # عرض أول 10 فقط
            st.dataframe(due_df[["name", "phone", "last_visit", "notes"]], use_container_width=True)
    
    # ----------- إضافة عميل -----------
    elif choice == "➕ إضافة عميل":
        st.subheader("➕ إضافة عميل جديد")
        
        with st.form("add_customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("اسم العميل *", placeholder="أدخل الاسم الكامل")
                phone = st.text_input("رقم التليفون *", placeholder="مثال: 01012345678")
                category = st.selectbox("التصنيف *", ["منزل", "شركة", "مدرسة", "مستشفى", "أخرى"])
                assigned_to = st.selectbox("الفني المسؤول", ["غير معين"] + [u["username"] for u in users if u["role"] == "technician"])
            
            with col2:
                location = st.text_input("إحداثيات Google Maps", placeholder="مثال: 30.0444,31.2357")
                if location:
                    st.caption("💡 يمكنك نسخ الإحداثيات من Google Maps بالنقر على الموقع")
                
                last_visit = st.date_input("تاريخ آخر زيارة *", datetime.today())
                next_visit = st.date_input("موعد الزيارة القادمة", datetime.today() + timedelta(days=30))
                
            notes = st.text_area("ملاحظات إضافية", height=100)
            
            st.caption("* الحقول المطلوبة")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                submit_btn = st.form_submit_button("💾 حفظ", type="primary", use_container_width=True)
            with col2:
                reset_btn = st.form_submit_button("🗑️ مسح", type="secondary", use_container_width=True)
            
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
                        "added_by": username,
                        "added_date": str(datetime.today().date()),
                        "status": "نشط"
                    }
                    
                    customers.append(new_customer)
                    if save_customers():
                        log_activity(username, "إضافة عميل", f"{name} - {phone}")
                        st.success(f"✅ تم إضافة العميل {name} بنجاح")
                        st.balloons()
                    else:
                        st.error("❌ فشل في حفظ العميل")
                else:
                    st.warning("⚠️ يرجى ملء الحقول المطلوبة")
    
    # ----------- عرض العملاء -----------
    elif choice == "📋 عرض العملاء":
        st.subheader("📋 قائمة العملاء")
        
        # فلتر سريع
        col1, col2 = st.columns(2)
        with col1:
            filter_category = st.selectbox("فلتر حسب التصنيف", ["الكل"] + list(set(c["category"] for c in customers if "category" in c)))
        with col2:
            filter_status = st.selectbox("فلتر حسب الحالة", ["الكل", "نشط", "غير نشط"])
        
        # تطبيق الفلتر
        filtered_customers = customers
        
        if filter_category != "الكل":
            filtered_customers = [c for c in filtered_customers if c.get("category") == filter_category]
        
        if filter_status != "الكل":
            filtered_customers = [c for c in filtered_customers if c.get("status", "نشط") == filter_status]
        
        if filtered_customers:
            df = pd.DataFrame(filtered_customers)
            
            # تحديد الأعمدة للعرض
            display_columns = ["id", "name", "phone", "category", "last_visit", "assigned_to", "status"]
            display_columns = [col for col in display_columns if col in df.columns]
            
            st.dataframe(df[display_columns], use_container_width=True)
            
            # خيارات التصدير
            st.download_button(
                label="📥 تحميل كملف Excel",
                data=df.to_csv(index=False).encode('utf-8-sig'),
                file_name=f"customers_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("لا يوجد عملاء مطابقين للبحث.")
    
    # ----------- إدارة العملاء (للمدير فقط) -----------
    elif choice == "✏️ إدارة العملاء" and role == "admin":
        st.subheader("✏️ إدارة العملاء")
        
        if customers:
            for customer in customers:
                with st.expander(f"{customer['id']} - {customer['name']} ({customer['phone']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("الاسم", value=customer.get("name", ""), key=f"name_{customer['id']}")
                        new_phone = st.text_input("الهاتف", value=customer.get("phone", ""), key=f"phone_{customer['id']}")
                        new_category = st.selectbox(
                            "التصنيف",
                            ["منزل", "شركة", "مدرسة", "مستشفى", "أخرى"],
                            index=["منزل", "شركة", "مدرسة", "مستشفى", "أخرى"].index(customer.get("category", "منزل")) if customer.get("category") in ["منزل", "شركة", "مدرسة", "مستشفى", "أخرى"] else 0,
                            key=f"cat_{customer['id']}"
                        )
                    
                    with col2:
                        new_location = st.text_input("الإحداثيات", value=customer.get("location", ""), key=f"loc_{customer['id']}")
                        new_status = st.selectbox(
                            "الحالة",
                            ["نشط", "غير نشط"],
                            index=0 if customer.get("status", "نشط") == "نشط" else 1,
                            key=f"status_{customer['id']}"
                        )
                        new_assigned = st.selectbox(
                            "الفني المسؤول",
                            ["غير معين"] + [u["username"] for u in users if u["role"] == "technician"],
                            index=0 if customer.get("assigned_to", "") == "" else ([u["username"] for u in users if u["role"] == "technician"].index(customer.get("assigned_to", "")) + 1) if customer.get("assigned_to") in [u["username"] for u in users if u["role"] == "technician"] else 0,
                            key=f"assign_{customer['id']}"
                        )
                    
                    new_notes = st.text_area("ملاحظات", value=customer.get("notes", ""), key=f"notes_{customer['id']}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("💾 حفظ التعديلات", key=f"save_{customer['id']}", type="primary", use_container_width=True):
                            customer.update({
                                "name": new_name,
                                "phone": new_phone,
                                "category": new_category,
                                "location": new_location,
                                "status": new_status,
                                "assigned_to": new_assigned if new_assigned != "غير معين" else "",
                                "notes": new_notes
                            })
                            if save_customers():
                                log_activity(username, "تعديل عميل", f"{customer['id']} - {customer['name']}")
                                st.success("✅ تم حفظ التعديلات")
                                st.experimental_rerun()
                    
                    with col2:
                        if st.button("📅 تحديث الزيارة", key=f"visit_{customer['id']}", type="secondary", use_container_width=True):
                            customer["last_visit"] = str(date
