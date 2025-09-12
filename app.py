import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd
import pydeck as pdk

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
    if st.button("Login"):
        st.session_state.show_login = True

# --------------------------
# حقول تسجيل الدخول
# --------------------------
if not st.session_state.logged_in and st.session_state.show_login:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Submit Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.session_state.user_role = "admin" if username == "Abdallah" else "technician"
            st.success(f"✅ تم تسجيل الدخول: {username}")
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

# --------------------------
# بعد تسجيل الدخول
# --------------------------
if st.session_state.logged_in:

    # زر تسجيل الخروج
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.user_role = None
        st.session_state.show_login = False
        st.success("تم تسجيل الخروج")

    # قائمة لوحة التحكم
    st.sidebar.subheader("لوحة التحكم")

    # خيارات المدير
    if st.session_state.user_role == "admin":
        menu = st.sidebar.radio("لوحة التحكم", [
            "إضافة العميل",
            "عرض العملاء",
            "بحث",
            "تذكير الزيارة",
            "إضافة فني",
            "عرض العملاء على الخريطة",
            "عرض الفنيين على الخريطة"
        ])
    # خيارات الفني
    else:
        menu = st.sidebar.radio("لوحة التحكم", [
            "عرض العملاء",
            "بحث",
            "تذكير الزيارة",
            "عرض العملاء على الخريطة"
        ])

    # --------------------------
    # إضافة العميل
    # --------------------------
    if menu == "إضافة العميل":
        st.subheader("➕ إضافة عميل")
        with st.form("add_form"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم التليفون")
            lat = st.text_input("Latitude")
            lon = st.text_input("Longitude")
            location = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else ""
            notes = st.text_area("ملاحظات")
            category = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
            last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())
            if st.form_submit_button("إضافة"):
                customers.append({
                    "id": len(customers) + 1,
                    "name": name,
                    "phone": phone,
                    "lat": lat,
                    "lon": lon,
                    "location": location,
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
            for c in customers:
                st.write(f"**{c['name']}** - {c['phone']}")
                if c.get("location"):
                    st.markdown(f"[🌍 فتح الموقع]({c['location']})", unsafe_allow_html=True)
                if c.get("phone"):
                    phone_number = c["phone"]
                    st.markdown(f"[💬 واتساب](https://wa.me/{phone_number}) | [📞 اتصال](tel:{phone_number})", unsafe_allow_html=True)
                st.write("---")
        else:
            st.info("لا يوجد عملاء بعد.")

    # --------------------------
    # البحث عن عميل
    # --------------------------
    elif menu == "بحث":
        st.subheader("🔎 البحث عن عميل")
        keyword = st.text_input("اكتب اسم العميل أو رقم التليفون")
        if keyword:
            results = [c for c in customers if keyword in c.get("name","") or keyword in c.get("phone","")]
            if results:
                for c in results:
                    st.write(f"**{c['name']}** - {c['phone']}")
                    if c.get("location"):
                        st.markdown(f"[🌍 فتح الموقع]({c['location']})", unsafe_allow_html=True)
                    if c.get("phone"):
                        phone_number = c["phone"]
                        st.markdown(f"[💬 واتساب](https://wa.me/{phone_number}) | [📞 اتصال](tel:{phone_number})", unsafe_allow_html=True)
                    st.write("---")
            else:
                st.warning("لا يوجد نتائج.")

    # --------------------------
    # تذكير بالزيارات
    # --------------------------
    elif menu == "تذكير الزيارة":
        st.subheader("⏰ العملاء المطلوب زيارتهم (30+ يوم)")
        today = datetime.today()
        reminders = []
        for c in customers:
            try:
                last = datetime.strptime(c.get("last_visit",""), "%Y-%m-%d")
                if today - last >= timedelta(days=30):
                    reminders.append(c)
            except:
                pass
        if reminders:
            for c in reminders:
                st.write(f"**{c['name']}** - {c['phone']}")
                if c.get("location"):
                    st.markdown(f"[🌍 فتح الموقع]({c['location']})", unsafe_allow_html=True)
                st.write("---")
        else:
            st.success("لا يوجد عملاء تحتاج زيارة.")

    # --------------------------
    # إضافة فني جديد (للمدير فقط)
    # --------------------------
    elif menu == "إضافة فني" and st.session_state.user_role == "admin":
        st.subheader("➕ إضافة فني جديد")
        new_user = st.text_input("اسم المستخدم الجديد")
        new_pass = st.text_input("كلمة السر الجديدة", type="password")
        if st.button("حفظ الفني"):
            if new_user and new_pass:
                if new_user in users:
                    st.error("اسم المستخدم موجود بالفعل!")
                else:
                    users[new_user] = new_pass
                    save_users(users)
                    st.success(f"✅ تم إضافة الفني {new_user} بنجاح!")

    # --------------------------
    # عرض العملاء على الخريطة
    # --------------------------
    elif menu == "عرض العملاء على الخريطة":
        st.subheader("🗺️ جميع العملاء على الخريطة")
        
        # إنشاء بيانات للخريطة
        customer_locations = []
        for c in customers:
            try:
                if c.get("lat") and c.get("lon"):
                    lat = float(c["lat"])
                    lon = float(c["lon"])
                    customer_locations.append({
                        "name": c["name"], 
                        "lat": lat, 
                        "lon": lon,
                        "type": "customer",
                        "phone": c.get("phone", ""),
                        "category": c.get("category", "")
                    })
            except:
                pass

        if customer_locations:
            # تحويل إلى DataFrame
            df = pd.DataFrame(customer_locations)
            
            # تحديد أيقونات مختلفة لأنواع مختلفة
            ICON_URL = "https://cdn-icons-png.flaticon.com/512/484/484167.png"  # أيقونة عميل
            
            # إعداد بيانات الأيقونة
            icon_data = {
                "url": ICON_URL,
                "width": 100,
                "height": 100,
                "anchorY": 1
            }
            
            # إضافة بيانات الأيقونة لكل نقطة
            df["icon_data"] = None
            for i in df.index:
                df["icon_data"][i] = icon_data
            
            # إنشاء طبقة الأيقونات
            icon_layer = pdk.Layer(
                "IconLayer",
                data=df,
                get_icon="icon_data",
                get_size=4,
                size_scale=15,
                get_position=["lon", "lat"],
                pickable=True,
            )
            
            # إنشاء الخريطة
            view_state = pdk.ViewState(
                latitude=df["lat"].mean(),
                longitude=df["lon"].mean(),
                zoom=10,
                pitch=0,
            )
            
            # أداة التلميح
            tooltip = {
                "html": "<b>العميل:</b> {name}<br><b>الهاتف:</b> {phone}<br><b>النوع:</b> {category}",
                "style": {
                    "backgroundColor": "steelblue",
                    "color": "white"
                }
            }
            
            # عرض الخريطة
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=view_state,
                layers=[icon_layer],
                tooltip=tooltip
            ))
            
            # عرض قائمة بالعملاء
            st.subheader("قائمة العملاء المعروضين على الخريطة")
            for loc in customer_locations:
                st.write(f"**{loc['name']}** - {loc['phone']} ({loc['category']})")
        else:
            st.info("❌ لا يوجد إحداثيات صالحة للعرض على الخريطة")

    # --------------------------
    # عرض الفنيين على الخريطة (للمدير فقط)
    # --------------------------
    elif menu == "عرض الفنيين على الخريطة" and st.session_state.user_role == "admin":
        st.subheader("👨‍🔧 الفنيين على الخريطة")
        
        # بيانات افتراضية للفنيين (يمكن استبدالها ببيانات حقيقية)
        technicians = [
            {"name": "فني 1", "lat": 24.7136, "lon": 46.6753, "phone": "0551234567"},
            {"name": "فني 2", "lat": 24.7236, "lon": 46.6853, "phone": "0557654321"},
            {"name": "فني 3", "lat": 24.7336, "lon": 46.6953, "phone": "0551112233"},
        ]
        
        # تحويل إلى DataFrame
        df_tech = pd.DataFrame(technicians)
        
        # أيقونة الفني
        TECH_ICON_URL = "https://cdn-icons-png.flaticon.com/512/3442/3442718.png"
        
        # إعداد بيانات الأيقونة
        tech_icon_data = {
            "url": TECH_ICON_URL,
            "width": 100,
            "height": 100,
            "anchorY": 1
        }
        
        # إضافة بيانات الأيقونة لكل نقطة
        df_tech["icon_data"] = None
        for i in df_tech.index:
            df_tech["icon_data"][i] = tech_icon_data
        
        # إنشاء طبقة الأيقونات للفنيين
        tech_icon_layer = pdk.Layer(
            "IconLayer",
            data=df_tech,
            get_icon="icon_data",
            get_size=4,
            size_scale=15,
            get_position=["lon", "lat"],
            pickable=True,
        )
        
        # إنشاء الخريطة
        view_state = pdk.ViewState(
            latitude=df_tech["lat"].mean(),
            longitude=df_tech["lon"].mean(),
            zoom=10,
            pitch=0,
        )
        
        # أداة التلميح
        tooltip = {
            "html": "<b>الفني:</b> {name}<br><b>الهاتف:</b> {phone}",
            "style": {
                "backgroundColor": "green",
                "color": "white"
            }
        }
        
        # عرض الخريطة
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/light-v9',
            initial_view_state=view_state,
            layers=[tech_icon_layer],
            tooltip=tooltip
        ))
        
        # عرض قائمة بالفنيين
        st.subheader("قائمة الفنيين المعروضين على الخريطة")
        for tech in technicians:
            st.write(f"**{tech['name']}** - {tech['phone']}")
