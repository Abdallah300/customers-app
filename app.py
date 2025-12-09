import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd
import time

# ------------------ الملفات ------------------
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

# -------- تحميل أو إنشاء المستخدمين ----------
if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except:
        users = []
else:
    users = []

# إذا كان ملف المستخدمين فارغاً أو بدون المدير
admin_exists = any(u.get("username") == "Abdallah" for u in users)
if not admin_exists:
    users = []  # إعادة تعيين القائمة
    users.append({
        "username": "Abdallah", 
        "password": "772001",  # بدون تشفير
        "role": "admin",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    
    st.info("✅ تم إنشاء حساب المدير: Abdallah / 772001")

# -------- تحميل العملاء ----------
if os.path.exists(CUSTOMERS_FILE):
    try:
        with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
            customers = json.load(f)
    except:
        customers = []
else:
    customers = []

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def save_customers():
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

# ------------------ إعداد الجلسة ------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

st.set_page_config(
    page_title="Power Life - إدارة العملاء",
    page_icon="🏢",
    layout="wide"
)

# ------------------ تسجيل الخروج ------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.experimental_rerun()

# ------------------ تسجيل الدخول ------------------
if not st.session_state.logged_in:
    
    st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 50px auto;
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
    
    username = st.text_input("اسم المستخدم", value="Abdallah")
    password = st.text_input("كلمة المرور", type="password", value="772001")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        login_btn = st.button("تسجيل الدخول", type="primary", use_container_width=True)
    with col2:
        if st.button("إعادة تعيين النظام", type="secondary", use_container_width=True):
            if os.path.exists(USERS_FILE):
                os.remove(USERS_FILE)
            st.success("✅ تم إعادة تعيين النظام. أعد تحميل الصفحة.")
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
                st.success(f"✅ مرحباً {username}")
                st.balloons()
                time.sleep(1)
                st.experimental_rerun()
            else:
                st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
                st.info("جرب: Abdallah / 772001")
        else:
            st.warning("⚠️ يرجى ملء جميع الحقول")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.info("""
    **إذا لم تتمكن من الدخول:**
    1. اضغط على زر "إعادة تعيين النظام"
    2. أعد تحميل الصفحة
    3. حاول الدخول مرة أخرى
    """)

# ------------------ إذا تم تسجيل الدخول ------------------
else:
    user = st.session_state.current_user
    role = user.get("role", "technician")
    username = user.get("username", "")
    
    # الشريط الجانبي
    with st.sidebar:
        st.title("لوحة التحكم")
        st.markdown(f"**المستخدم:** {username}")
        st.markdown(f"**الصلاحية:** {'مدير' if role == 'admin' else 'فني'}")
        st.divider()
        
        # القائمة حسب الصلاحيات
        if role == "admin":
            options = [
                "🏠 الصفحة الرئيسية",
                "➕ إضافة عميل",
                "📋 عرض العملاء",
                "🔎 بحث",
                "⏰ تذكير الزيارة",
                "👷 إضافة فني",
                "🗺️ خريطة العملاء",
                "🚪 تسجيل الخروج"
            ]
        else:
            options = [
                "🏠 الصفحة الرئيسية",
                "📋 عرض العملاء",
                "🔎 بحث",
                "⏰ تذكير الزيارة",
                "🗺️ خريطة العملاء",
                "🚪 تسجيل الخروج"
            ]
        
        choice = st.radio("القائمة", options)
    
    # الصفحة الرئيسية
    if choice == "🏠 الصفحة الرئيسية":
        st.title(f"مرحباً بك {username} 👋")
        
        # إحصائيات سريعة
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي العملاء", len(customers))
        with col2:
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
            st.metric("بحاجة لزيارة", due_count)
        with col3:
            tech_count = len([u for u in users if u.get("role") == "technician"])
            st.metric("عدد الفنيين", tech_count)
    
    # إضافة عميل
    elif choice == "➕ إضافة عميل":
        st.subheader("➕ إضافة عميل جديد")
        
        with st.form("add_customer_form"):
            name = st.text_input("اسم العميل *")
            phone = st.text_input("رقم التليفون *")
            location = st.text_input("إحداثيات Google Maps (اختياري)")
            notes = st.text_area("ملاحظات (اختياري)")
            category = st.selectbox("التصنيف *", ["منزل", "شركة", "مدرسة", "أخرى"])
            last_visit = st.date_input("تاريخ آخر زيارة *", datetime.today())
            
            if st.form_submit_button("إضافة العميل"):
                if name and phone:
                    new_customer = {
                        "id": len(customers) + 1,
                        "name": name,
                        "phone": phone,
                        "location": location,
                        "notes": notes,
                        "category": category,
                        "last_visit": str(last_visit),
                        "added_by": username,
                        "added_date": str(datetime.today().date())
                    }
                    
                    customers.append(new_customer)
                    save_customers()
                    st.success(f"✅ تم إضافة العميل {name} بنجاح")
                else:
                    st.warning("⚠️ يرجى ملء الحقول المطلوبة (*)")
    
    # عرض العملاء
    elif choice == "📋 عرض العملاء":
        st.subheader("📋 قائمة العملاء")
        
        if customers:
            # تحويل إلى DataFrame للعرض
            df = pd.DataFrame(customers)
            
            # تحديد الأعمدة للعرض
            display_cols = ["id", "name", "phone", "category", "last_visit"]
            display_cols = [col for col in display_cols if col in df.columns]
            
            st.dataframe(df[display_cols], use_container_width=True)
        else:
            st.info("لا يوجد عملاء بعد.")
    
    # بحث
    elif choice == "🔎 بحث":
        st.subheader("🔎 البحث عن عميل")
        
        keyword = st.text_input("اكتب اسم أو رقم هاتف للبحث")
        
        if keyword:
            results = []
            for c in customers:
                if (keyword.lower() in c.get("name", "").lower() or 
                    keyword in c.get("phone", "")):
                    results.append(c)
            
            if results:
                st.success(f"تم العثور على {len(results)} نتيجة")
                df_results = pd.DataFrame(results)
                st.dataframe(df_results, use_container_width=True)
            else:
                st.warning("لا توجد نتائج مطابقة للبحث.")
    
    # تذكير الزيارة
    elif choice == "⏰ تذكير الزيارة":
        st.subheader("⏰ العملاء المطلوب زيارتهم")
        
        today = datetime.today()
        due_customers = []
        
        for c in customers:
            try:
                last = datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")
                if (today - last).days >= 30:
                    due_customers.append(c)
            except:
                pass
        
        if due_customers:
            st.warning(f"⚠️ يوجد {len(due_customers)} عميل بحاجة للزيارة")
            
            df_due = pd.DataFrame(due_customers)
            st.dataframe(df_due[["name", "phone", "category", "last_visit", "notes"]], 
                        use_container_width=True)
        else:
            st.success("🎉 جميع العملاء محدثون. لا توجد زيارات متأخرة!")
    
    # إضافة فني (للمدير فقط)
    elif choice == "👷 إضافة فني" and role == "admin":
        st.subheader("👷 إضافة فني جديد")
        
        with st.form("add_technician"):
            new_username = st.text_input("اسم المستخدم *")
            new_password = st.text_input("كلمة المرور *", type="password")
            
            if st.form_submit_button("إضافة الفني"):
                if new_username and new_password:
                    # التحقق من عدم التكرار
                    if any(u["username"] == new_username for u in users):
                        st.error("❌ اسم المستخدم موجود مسبقاً")
                    else:
                        users.append({
                            "username": new_username,
                            "password": new_password,
                            "role": "technician",
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "created_by": username
                        })
                        save_users()
                        st.success(f"✅ تم إضافة الفني {new_username} بنجاح")
                else:
                    st.warning("⚠️ يرجى ملء جميع الحقول")
    
    # خريطة العملاء
    elif choice == "🗺️ خريطة العملاء":
        st.subheader("🗺️ خريطة مواقع العملاء")
        
        map_points = []
        
        for c in customers:
            try:
                if c.get("location"):
                    lat, lon = map(float, c["location"].split(","))
                    map_points.append({"lat": lat, "lon": lon})
            except:
                pass
        
        if map_points:
            df_map = pd.DataFrame(map_points)
            st.map(df_map)
            st.success(f"📍 تم عرض {len(map_points)} موقع على الخريطة")
        else:
            st.info("لا توجد إحداثيات صالحة للعرض.")
    
    # تسجيل الخروج
    elif choice == "🚪 تسجيل الخروج":
        logout()
