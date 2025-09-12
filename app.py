import streamlit as st
import json, os, re
from datetime import datetime, timedelta
import pandas as pd
import pydeck as pdk

FILE_NAME = "customers.json"
USERS_FILE = "users.json"

# تحميل العملاء
def load_customers():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

# حفظ العملاء
def save_customers(customers):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

# تحميل المستخدمين
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except:
            pass
    # إنشاء المستخدم الافتراضي إذا الملف فاضي أو فيه مشكلة
    return [{"username":"Abdallah","password":"772001","role":"admin"}]

# حفظ المستخدمين
def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# استخراج إحداثيات من رابط Google Maps
def get_lat_lon(url):
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    return None, None

customers = load_customers()
users = load_users()

st.set_page_config(page_title="Power Life CRM", layout="wide")
st.title("🏢 Power Life ترحب بكم")

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# واجهة تسجيل الدخول
if not st.session_state.logged_in:
    st.subheader("🔑 تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("تسجيل الدخول"):
        user = next((u for u in users if u.get("username")==username and u.get("password")==password), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.success(f"✅ مرحبا {username}")
            st.experimental_rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيح")

# بعد تسجيل الدخول
else:
    user = st.session_state.current_user
    role = user.get("role","technician")
    st.sidebar.title("لوحة التحكم")

    # القائمة الجانبية حسب الدور
    if role=="admin":
        menu_items = ["إضافة عميل","عرض العملاء","بحث","تذكير الزيارة","إضافة فني","عرض العملاء على الخريطة"]
    else:
        menu_items = ["عرض العملاء","بحث","تذكير الزيارة","عرض العملاء على الخريطة"]

    menu = st.sidebar.radio("لوحة التحكم", menu_items)

    if st.sidebar.button("تسجيل الخروج"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.experimental_rerun()

    # إضافة عميل
    if menu=="إضافة عميل":
        st.subheader("➕ إضافة عميل")
        with st.form("add_form"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم التليفون")
            location = st.text_input("رابط Google Maps للعنوان")
            notes = st.text_area("ملاحظات")
            category = st.selectbox("التصنيف", ["منزل","شركة","مدرسة"])
            last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())
            if st.form_submit_button("إضافة"):
                lat, lon = get_lat_lon(location)
                customers.append({
                    "id": len(customers)+1,
                    "name": name,
                    "phone": phone,
                    "location": location,
                    "lat": lat,
                    "lon": lon,
                    "notes": notes,
                    "category": category,
                    "last_visit": str(last_visit),
                    "technician": user["username"]
                })
                save_customers(customers)
                st.success(f"✅ تم إضافة {name} بنجاح.")

    # عرض العملاء
    elif menu=="عرض العملاء":
        st.subheader("📋 قائمة العملاء")
        if role=="admin":
            df = pd.DataFrame(customers)
        else:
            df = pd.DataFrame([c for c in customers if c.get("technician")==user["username"]])
        st.dataframe(df)

    # البحث
    elif menu=="بحث":
        st.subheader("🔎 البحث عن عميل")
        keyword = st.text_input("اكتب اسم أو رقم")
        if keyword:
            if role=="admin":
                results = [c for c in customers if keyword in c.get("name","") or keyword in c.get("phone","")]
            else:
                results = [c for c in customers if (keyword in c.get("name","") or keyword in c.get("phone","")) and c.get("technician")==user["username"]]
            if results:
                st.write(pd.DataFrame(results))
            else:
                st.warning("لا يوجد نتائج")

    # تذكير الزيارة
    elif menu=="تذكير الزيارة":
        st.subheader("⏰ العملاء المطلوب زيارتهم (أكثر من 30 يوم)")
        today = datetime.today()
        if role=="admin":
            reminders = [c for c in customers if datetime.strptime(c.get("last_visit",""), "%Y-%m-%d") <= today - timedelta(days=30)]
        else:
            reminders = [c for c in customers if c.get("technician")==user["username"] and datetime.strptime(c.get("last_visit",""), "%Y-%m-%d") <= today - timedelta(days=30)]
        if reminders:
            st.write(pd.DataFrame(reminders))
        else:
            st.success("لا يوجد عملاء تحتاج زيارة")

    # إضافة فني
    elif menu=="إضافة فني" and role=="admin":
        st.subheader("👷 إضافة فني جديد")
        with st.form("add_tech_form"):
            new_user = st.text_input("اسم المستخدم الجديد")
            new_pass = st.text_input("كلمة المرور", type="password")
            if st.form_submit_button("إضافة فني"):
                if new_user and new_pass:
                    users.append({"username":new_user,"password":new_pass,"role":"technician"})
                    save_users(users)
                    st.success(f"✅ تم إضافة الفني {new_user} بنجاح")
                else:
                    st.error("❌ املأ الاسم وكلمة المرور")

    # عرض العملاء على الخريطة
    elif menu=="عرض العملاء على الخريطة":
        st.subheader("🗺️ العملاء على الخريطة")
        if role=="admin":
            map_data = [c for c in customers if c.get("lat") and c.get("lon")]
        else:
            map_data = [c for c in customers if c.get("lat") and c.get("lon") and c.get("technician")==user["username"]]
        if map_data:
            df_map = pd.DataFrame(map_data)
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/streets-v11',
                initial_view_state=pdk.ViewState(
                    latitude=df_map['lat'].mean(),
                    longitude=df_map['lon'].mean(),
                    zoom=10,
                    pitch=0
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=df_map,
                        get_position='[lon, lat]',
                        get_color='[200, 30, 0, 160]',
                        get_radius=200,
                        pickable=True
                    )
                ],
                tooltip={"text":"اسم العميل: {name}\nفني: {technician}"}
            ))
        else:
            st.info("لا يوجد عملاء لعرضهم على الخريطة")
