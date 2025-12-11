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

# إنشاء المدير إذا لم يكن موجوداً
admin_exists = any(u.get("username") == "Abdallah" for u in users)
if not admin_exists:
    users = []
    users.append({
        "username": "Abdallah", 
        "password": "772001",
        "role": "admin",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

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
    <div style='max-width: 400px; margin: 100px auto; padding: 40px; border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.1); background-color: white; text-align: center;'>
        <h1 style='color: #2c3e50; margin-bottom: 30px;'>🏢 Power Life</h1>
        <h3>🔑 تسجيل الدخول</h3>
    </div>
    """, unsafe_allow_html=True)
    
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

# ------------------ إذا تم تسجيل الدخول ------------------
else:
    user = st.session_state.current_user
    role = user.get("role", "technician")
    username = user.get("username", "")
    
    # الشريط الجانبي
    with st.sidebar:
        st.title("لوحة التحكم")
        st.markdown(f"**المستخدم:** {username}")
        st.markdown(f"**الصلاحية:** {'👑 مدير' if role == 'admin' else '👷 فني'}")
        st.divider()
        
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
    
    # ------------------ محتوى الصفحات ------------------
    
    # الصفحة الرئيسية
    if choice == "🏠 الصفحة الرئيسية":
        st.title(f"مرحباً بك {username} 👋")
        st.markdown("---")
        
        # بطاقات الإحصائيات
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("إجمالي العملاء", len(customers))
        
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
            st.metric("بحاجة لزيارة", due_count)
        
        # عدد الفنيين
        tech_count = len([u for u in users if u.get("role") == "technician"])
        
        with col3:
            st.metric("عدد الفنيين", tech_count)
        
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
                choice = "➕ إضافة عميل"
                st.experimental_rerun()
        
        # العملاء المطلوب زيارتهم
        if due_count > 0:
            st.markdown("---")
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
                name = st.text_input("اسم العميل *", placeholder="أدخل الاسم الكامل")
                phone = st.text_input("رقم الهاتف *", placeholder="مثال: 01012345678")
                category = st.selectbox("التصنيف *", ["منزل", "شركة", "مدرسة", "مستشفى", "فندق", "مطعم", "أخرى"])
            
            with col2:
                location = st.text_input("إحداثيات الموقع (اختياري)", placeholder="مثال: 30.0444,31.2357")
                last_visit = st.date_input("تاريخ آخر زيارة *", datetime.today())
                status = st.selectbox("حالة العميل", ["نشط", "معلق", "غير نشط"])
            
            notes = st.text_area("ملاحظات إضافية", placeholder="اكتب ملاحظات عن العميل...", height=100)
            
            st.markdown("---")
            st.caption("* الحقول المطلوبة")
            
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
                        "added_by": user["username"],
                        "added_date": str(datetime.today().date()),
                        "status": status,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    customers.append(new_customer)
                    save_customers()
                    st.success(f"✅ تم إضافة العميل **{name}** بنجاح")
                    st.balloons()
                else:
                    st.warning("⚠️ يرجى ملء الحقول المطلوبة (*)")
    
    # عرض العملاء
    elif choice == "📋 عرض العملاء":
        st.title("📋 قائمة العملاء")
        st.markdown("---")
        
        if not customers:
            st.info("لا يوجد عملاء مسجلين بعد.")
            return
        
        # أداة البحث السريع
        search_term = st.text_input("🔍 بحث سريع", placeholder="ابحث بالاسم أو الهاتف...")
        
        # فلترة البيانات
        filtered_customers = customers
        
        if search_term:
            filtered_customers = [
                c for c in filtered_customers 
                if search_term.lower() in c.get("name", "").lower() 
                or search_term in c.get("phone", "")
            ]
        
        if not filtered_customers:
            st.warning("لا توجد نتائج مطابقة للبحث.")
            return
        
        # تحويل إلى DataFrame
        df = pd.DataFrame(filtered_customers)
        
        # تحديد الأعمدة للعرض
        display_columns = ["id", "name", "phone", "category", "last_visit", "status"]
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
            return
        
        # نموذج البحث
        with st.form("advanced_search_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name_search = st.text_input("بحث بالاسم", placeholder="أدخل جزء من الاسم...")
                phone_search = st.text_input("بحث بالهاتف", placeholder="أدخل رقم الهاتف...")
            
            with col2:
                status_search = st.selectbox("بحث بالحالة", ["الكل", "نشط", "معلق", "غير نشط"])
                days_options = st.slider("عدد الأيام منذ آخر زيارة", 0, 180, 30)
            
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
            
            if status_search != "الكل":
                results = [c for c in results if c.get("status", "نشط") == status_search]
            
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
                display_cols = ["id", "name", "phone", "category", "last_visit", "status"]
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
            return
        
        # خيار الفلترة
        days_threshold = st.slider("حدد عدد الأيام منذ آخر زيارة", 
                                  min_value=7, max_value=180, value=30, step=1)
        
        # حساب العملاء المطلوب زيارتهم
        today = datetime.today()
        due_customers = []
        
        for c in customers:
            try:
                last_visit = datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")
                days_since = (today - last_visit).days
                
                if days_since >= days_threshold:
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
            display_cols = ["name", "phone", "category", "last_visit", "days_late", "notes"]
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
                    
                    save_customers()
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
                new_username = st.text_input("اسم المستخدم *", placeholder="أدخل اسم المستخدم")
                new_password = st.text_input("كلمة المرور *", type="password", placeholder="أدخل كلمة مرور قوية")
                confirm_password = st.text_input("تأكيد كلمة المرور *", type="password", placeholder="أعد إدخال كلمة المرور")
                new_fullname = st.text_input("الاسم الكامل (اختياري)", placeholder="الاسم الثلاثي")
                
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
                                    "role": "technician",
                                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "created_by": user["username"],
                                    "status": "active"
                                }
                                
                                users.append(new_technician)
                                save_users()
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
                    tech_data.append({
                        "اسم المستخدم": tech.get("username"),
                        "الاسم الكامل": tech.get("full_name", ""),
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
        
        # تجهيز البيانات للخريطة
        map_data = []
        map_info = []
        
        for customer in customers:
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
                        "name": customer.get("name", "بدون اسم")
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
            st.warning("⚠️ لا توجد إحداثيات صالحة للعرض")
    
    # تسجيل الخروج
    elif choice == "🚪 تسجيل الخروج":
        logout()
