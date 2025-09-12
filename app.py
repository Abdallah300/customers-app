import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd

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
            "إضافة فني"
        ])
    # خيارات الفني
    else:
        menu = st.sidebar.radio("لوحة التحكم", [
            "عرض العملاء",
            "بحث",
            "تذكير الزيارة"
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

        # ✅ عرض الخريطة دايمًا
        st.subheader("🗺️ مواقع العملاء على الخريطة")
        locations = []
        for c in customers:
            try:
                if c.get("lat") and c.get("lon"):
                    lat = float(c["lat"])
                    lon = float(c["lon"])
                    locations.append({"name": c["name"], "lat": lat, "lon": lon})
            except:
                pass

        import pydeck as pdk
        if locations:
            df = pd.DataFrame(locations)
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/streets-v11',
                initial_view_state=pdk.ViewState(
                    latitude=df["lat"].mean(),
                    longitude=df["lon"].mean(),
                    zoom=10,
                    pitch=0,
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=df,
                        get_position='[lon, lat]',
                        get_color='[200, 30, 0, 160]',
                        get_radius=200,
                        pickable=True
                    )
                ]
            ))
        else:
            st.map(pd.DataFrame({"lat": [30.0444], "lon": [31.2357]}))  # القاهرة كمثال

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
