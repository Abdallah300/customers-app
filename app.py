import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium import plugins

# --------------------------
# ملفات التخزين
# --------------------------
CUSTOMERS_FILE = "customers.json"
USERS_FILE = "users.json"

# --------------------------
# تحميل العملاء
# --------------------------
def load_customers():
    if os.path.exists(CUSTOMERS_FILE):
        try:
            with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_customers(customers):
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

customers = load_customers()

# --------------------------
# تحميل المستخدمين
# --------------------------
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# مستخدم افتراضي
users = load_users()
if not users:
    users = {"Abdallah": "772001"}  # المدير
    save_users(users)

# --------------------------
# session_state
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user" not in st.session_state:
    st.session_state.user = None
if "show_login" not in st.session_state:
    st.session_state.show_login = False

# --------------------------
# إعداد الصفحة
# --------------------------
st.set_page_config(page_title="Baro Life", layout="wide")
st.title("💧 Baro Life ترحب بكم")

# --------------------------
# قبل تسجيل الدخول
# --------------------------
if not st.session_state.logged_in:
    st.sidebar.subheader("تسجيل الدخول")
    username = st.sidebar.text_input("اسم المستخدم")
    password = st.sidebar.text_input("كلمة المرور", type="password")
    
    if st.sidebar.button("تسجيل الدخول"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.user_role = "admin" if username == "Abdallah" else "technician"
            st.sidebar.success(f"✅ تم تسجيل الدخول: {username}")
            st.experimental_rerun()
        else:
            st.sidebar.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

# --------------------------
# بعد تسجيل الدخول
# --------------------------
if st.session_state.logged_in:
    # زر تسجيل الخروج
    st.sidebar.subheader(f"مرحبًا، {st.session_state.user}")
    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_role = None
        st.session_state.show_login = False
        st.sidebar.success("تم تسجيل الخروج")
        st.experimental_rerun()

    # قائمة لوحة التحكم
    st.sidebar.subheader("لوحة التحكم")

    # خيارات المدير
    if st.session_state.user_role == "admin":
        menu = st.sidebar.radio("الخيارات", [
            "إضافة العميل",
            "عرض العملاء",
            "بحث",
            "تذكير الزيارة",
            "إضافة فني",
            "الخريطة التفاعلية"
        ])
    # خيارات الفني
    else:
        menu = st.sidebar.radio("الخيارات", [
            "عرض العملاء",
            "بحث",
            "تذكير الزيارة",
            "الخريطة التفاعلية"
        ])

    # --------------------------
    # إضافة العميل
    # --------------------------
    if menu == "إضافة العميل":
        st.subheader("➕ إضافة عميل")
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم التليفون")
                lat = st.number_input("Latitude", value=24.7136, format="%.6f")
                lon = st.number_input("Longitude", value=46.6753, format="%.6f")
                
            with col2:
                notes = st.text_area("ملاحظات")
                category = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
                last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())
                
            if st.form_submit_button("إضافة العميل"):
                customers.append({
                    "id": len(customers) + 1,
                    "name": name,
                    "phone": phone,
                    "lat": lat,
                    "lon": lon,
                    "notes": notes,
                    "category": category,
                    "last_visit": str(last_visit)
                })
                save_customers(customers)
                st.success(f"✅ تم إضافة {name} بنجاح.")

    # --------------------------
    # عرض العملاء
    # --------------------------
    elif menu == "عرض العملاء":
        st.subheader("📋 قائمة العملاء")
        
        if customers:
            # بحث سريع
            search_term = st.text_input("🔍 بحث سريع")
            
            # تصفية العملاء حسب البحث
            filtered_customers = customers
            if search_term:
                filtered_customers = [c for c in customers if search_term.lower() in c['name'].lower() or search_term in c.get('phone', '')]
            
            if filtered_customers:
                for c in filtered_customers:
                    with st.expander(f"{c['name']} - {c.get('phone', '')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**الهاتف:** {c.get('phone', 'غير متوفر')}")
                            st.write(f"**التصنيف:** {c.get('category', 'غير محدد')}")
                            st.write(f"**آخر زيارة:** {c.get('last_visit', 'غير معروف')}")
                            
                        with col2:
                            st.write(f"**الملاحظات:** {c.get('notes', 'لا توجد ملاحظات')}")
                            if c.get('lat') and c.get('lon'):
                                st.write(f"**الإحداثيات:** {c.get('lat')}, {c.get('lon')}")
                                
                        # أزرار الاتصال
                        if c.get('phone'):
                            phone_number = c["phone"]
                            st.markdown(f"""
                            <div style="display: flex; gap: 10px;">
                                <a href="https://wa.me/{phone_number}" target="_blank" style="text-decoration: none;">
                                    <button style="background-color: #25D366; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">واتساب</button>
                                </a>
                                <a href="tel:{phone_number}" style="text-decoration: none;">
                                    <button style="background-color: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">اتصال</button>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("لا توجد نتائج للبحث")
        else:
            st.info("لا يوجد عملاء بعد.")

    # --------------------------
    # البحث عن عميل
    # --------------------------
    elif menu == "بحث":
        st.subheader("🔎 البحث المتقدم عن عميل")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name_search = st.text_input("بحث بالاسم")
            phone_search = st.text_input("بحث بالهاتف")
            
        with col2:
            category_search = st.selectbox("بحث بالتصنيف", ["الكل", "منزل", "شركة", "مدرسة"])
            visit_days = st.slider("عدد الأيام منذ آخر زيارة", 0, 365, 30)
        
        if st.button("بحث"):
            results = customers
            
            if name_search:
                results = [c for c in results if name_search.lower() in c.get("name", "").lower()]
                
            if phone_search:
                results = [c for c in results if phone_search in c.get("phone", "")]
                
            if category_search != "الكل":
                results = [c for c in results if c.get("category") == category_search]
                
            # تصفية حسب آخر زيارة
            today = datetime.today()
            filtered_results = []
            for c in results:
                try:
                    last_visit = datetime.strptime(c.get("last_visit", ""), "%Y-%m-%d")
                    days_diff = (today - last_visit).days
                    if days_diff >= visit_days:
                        filtered_results.append(c)
                except:
                    pass
                    
            results = filtered_results
            
            if results:
                st.success(f"تم العثور على {len(results)} نتيجة")
                
                for c in results:
                    with st.expander(f"{c['name']} - {c.get('phone', '')}"):
                        st.write(f"**الهاتف:** {c.get('phone', 'غير متوفر')}")
                        st.write(f"**التصنيف:** {c.get('category', 'غير محدد')}")
                        st.write(f"**آخر زيارة:** {c.get('last_visit', 'غير معروف')}")
                        st.write(f"**الملاحظات:** {c.get('notes', 'لا توجد ملاحظات')}")
            else:
                st.warning("لا توجد نتائج للبحث")

    # --------------------------
    # تذكير بالزيارات
    # --------------------------
    elif menu == "تذكير الزيارة":
        st.subheader("⏰ العملاء المطلوب زيارتهم")
        
        days_threshold = st.slider("عدد الأيام منذ آخر زيارة", 30, 365, 30)
        
        today = datetime.today()
        reminders = []
        for c in customers:
            try:
                last_visit = datetime.strptime(c.get("last_visit", ""), "%Y-%m-%d")
                days_diff = (today - last_visit).days
                if days_diff >= days_threshold:
                    c['days_since_visit'] = days_diff
                    reminders.append(c)
            except:
                pass
                
        if reminders:
            st.info(f"يوجد {len(reminders)} عميل يحتاجون زيارة")
            
            # ترتيب العملاء حسب الأقدم
            reminders.sort(key=lambda x: x['days_since_visit'], reverse=True)
            
            for c in reminders:
                with st.expander(f"{c['name']} - {c.get('phone', '')} ({c['days_since_visit']} يوم منذ آخر زيارة)"):
                    st.write(f"**الهاتف:** {c.get('phone', 'غير متوفر')}")
                    st.write(f"**التصنيف:** {c.get('category', 'غير محدد')}")
                    st.write(f"**آخر زيارة:** {c.get('last_visit', 'غير معروف')}")
                    st.write(f"**الملاحظات:** {c.get('notes', 'لا توجد ملاحظات')}")
                    
                    if c.get('phone'):
                        phone_number = c["phone"]
                        st.markdown(f"""
                        <div style="display: flex; gap: 10px;">
                            <a href="https://wa.me/{phone_number}" target="_blank" style="text-decoration: none;">
                                <button style="background-color: #25D366; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">واتساب</button>
                            </a>
                            <a href="tel:{phone_number}" style="text-decoration: none;">
                                <button style="background-color: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">اتصال</button>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.success("لا يوجد عملاء تحتاج زيارة.")

    # --------------------------
    # إضافة فني جديد (للمدير فقط)
    # --------------------------
    elif menu == "إضافة فني" and st.session_state.user_role == "admin":
        st.subheader("➕ إضافة فني جديد")
        
        with st.form("add_tech_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_user = st.text_input("اسم المستخدم الجديد")
                new_pass = st.text_input("كلمة السر الجديدة", type="password")
                
            with col2:
                tech_name = st.text_input("اسم الفني الكامل")
                tech_phone = st.text_input("هاتف الفني")
                
            if st.form_submit_button("حفظ الفني"):
                if new_user and new_pass:
                    if new_user in users:
                        st.error("اسم المستخدم موجود بالفعل!")
                    else:
                        users[new_user] = new_pass
                        save_users(users)
                        st.success(f"✅ تم إضافة الفني {new_user} بنجاح!")

    # --------------------------
    # الخريطة التفاعلية
    # --------------------------
    elif menu == "الخريطة التفاعلية":
        st.subheader("🗺️ الخريطة التفاعلية للعملاء والفنيين")
        
        # بيانات افتراضية للفنيين (يمكن استبدالها ببيانات حقيقية)
        technicians = [
            {"name": "فني 1", "lat": 24.7136, "lon": 46.6753, "phone": "0551234567"},
            {"name": "فني 2", "lat": 24.7236, "lon": 46.6853, "phone": "0557654321"},
            {"name": "فني 3", "lat": 24.7336, "lon": 46.6953, "phone": "0551112233"},
        ]
        
        # إنشاء خريطة مركزة على الرياض
        m = folium.Map(location=[24.7136, 46.6753], zoom_start=10)
        
        # إضافة集群 للخريطة
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        # إضافة العملاء إلى الخريطة
        for customer in customers:
            if customer.get('lat') and customer.get('lon'):
                try:
                    lat = float(customer['lat'])
                    lon = float(customer['lon'])
                    
                    # إنشاء Popup مع معلومات العميل
                    popup_content = f"""
                    <div style="min-width: 200px;">
                        <h4>{customer['name']}</h4>
                        <p><strong>هاتف:</strong> {customer.get('phone', 'غير متوفر')}</p>
                        <p><strong>تصنيف:</strong> {customer.get('category', 'غير محدد')}</p>
                        <p><strong>آخر زيارة:</strong> {customer.get('last_visit', 'غير معروف')}</p>
                    </div>
                    """
                    
                    # إضافة علامة العميل إلى الخريطة
                    folium.Marker(
                        [lat, lon],
                        popup=folium.Popup(popup_content, max_width=300),
                        tooltip=customer['name'],
                        icon=folium.Icon(color='blue', icon='user', prefix='fa')
                    ).add_to(marker_cluster)
                except:
                    pass
        
        # إضافة الفنيين إلى الخريطة
        for tech in technicians:
            try:
                # إنشاء Popup مع معلومات الفني
                popup_content = f"""
                <div style="min-width: 200px;">
                    <h4>{tech['name']}</h4>
                    <p><strong>هاتف:</strong> {tech.get('phone', 'غير متوفر')}</p>
                    <p><strong>وظيفة:</strong> فني</p>
                </div>
                """
                
                # إضافة علامة الفني إلى الخريطة
                folium.Marker(
                    [tech['lat'], tech['lon']],
                    popup=folium.Popup(popup_content, max_width=300),
                    tooltip=tech['name'] + " (فني)",
                    icon=folium.Icon(color='green', icon='wrench', prefix='fa')
                ).add_to(marker_cluster)
            except:
                pass
        
        # عرض الخريطة في Streamlit
        folium_static(m, width=1000, height=600)
        
        # إحصائيات
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("عدد العملاء", len(customers))
        with col2:
            st.metric("عدد الفنيين", len(technicians))
        with col3:
            st.metric("العملاء على الخريطة", sum(1 for c in customers if c.get('lat') and c.get('lon')))
        
        # تفاصيل العملاء والفنيين
        with st.expander("عرض تفاصيل العملاء والفنيين"):
            st.subheader("العملاء")
            for customer in customers:
                if customer.get('lat') and customer.get('lon'):
                    st.write(f"{customer['name']} - {customer.get('phone', '')} - {customer.get('category', '')}")
            
            st.subheader("الفنيين")
            for tech in technicians:
                st.write(f"{tech['name']} - {tech.get('phone', '')}")

# --------------------------
# قبل تسجيل الدخول - المحتوى الأساسي
# --------------------------
if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align: center; padding: 50px 0;">
        <h2>مرحبًا بكم في نظام إدارة عملاء Baro Life</h2>
        <p>يجب تسجيل الدخول للوصول إلى النظام</p>
        <p>استخدم القائمة الجانبية لتسجيل الدخول</p>
    </div>
    """, unsafe_allow_html=True)
