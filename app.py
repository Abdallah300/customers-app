import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd

# ---------- ملفات البيانات ----------
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

# ---------- تحميل المستخدمين ----------
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    # إنشاء مستخدم افتراضي (مدير)
    users = [{"username":"Abdallah","password":"772001","role":"admin"}]
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ---------- تحميل العملاء ----------
if os.path.exists(CUSTOMERS_FILE):
    with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
        customers = json.load(f)
else:
    customers = []

def save_customers():
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# ---------- تهيئة الجلسة ----------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'menu' not in st.session_state:
    st.session_state.menu = None

st.set_page_config(page_title="Power Life - إدارة العملاء", layout="wide")

# ---------- تسجيل الخروج ----------
def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.menu = None
    st.experimental_rerun()

# ---------- تسجيل الدخول ----------
if not st.session_state.logged_in:
    st.title("🏢 Power Life ترحب بكم")
    st.subheader("🔑 تسجيل الدخول")
    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")
    if st.button("تسجيل الدخول"):
        user = next((u for u in users if u.get("username") == username and u.get("password") == password), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.success(f"✅ مرحبا {username}")
            st.experimental_rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيح")
else:
    user = st.session_state.current_user
    role = user.get("role","technician")

    st.sidebar.title("لوحة التحكم")

    # ---------- خيارات القائمة حسب الدور ----------
    if role == "admin":
        menu_items = ["إضافة عميل","عرض العملاء","بحث","تذكير الزيارة","إضافة فني","عرض العملاء على الخريطة","تسجيل الخروج"]
    else:
        menu_items = ["عرض العملاء","بحث","تذكير الزيارة","عرض العملاء على الخريطة","تسجيل الخروج"]

    st.session_state.menu = st.sidebar.radio("لوحة التحكم", menu_items)
    menu = st.session_state.menu

    # ---------- وظائف التطبيق ----------
    if menu == "إضافة عميل":
        st.subheader("➕ إضافة عميل")
        with st.form("add_form"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم التليفون")
            location = st.text_input("العنوان أو إحداثيات Google Maps بالشكل lat,lon")
            notes = st.text_area("ملاحظات")
            category = st.selectbox("التصنيف", ["منزل","شركة","مدرسة"])
            last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())
            if st.form_submit_button("إضافة"):
                customers.append({
                    "id": len(customers)+1,
                    "name": name,
                    "phone": phone,
                    "location": location,
                    "notes": notes,
                    "category": category,
                    "last_visit": str(last_visit)
                })
                save_customers()
                st.success(f"✅ تم إضافة {name} بنجاح.")

    elif menu == "عرض العملاء":
        st.subheader("📋 قائمة العملاء")
        if customers:
            df = pd.DataFrame(customers)
            st.dataframe(df)
        else:
            st.info("لا يوجد عملاء بعد.")

    elif menu == "بحث":
        st.subheader("🔎 البحث عن عميل")
        keyword = st.text_input("اكتب اسم أو رقم")
        if keyword:
            results = [c for c in customers if keyword in c.get("name","") or keyword in c.get("phone","")]
            if results:
                st.write(pd.DataFrame(results))
            else:
                st.warning("لا يوجد نتائج.")

    elif menu == "تذكير الزيارة":
        st.subheader("⏰ العملاء المطلوب زيارتهم (أكثر من 30 يوم)")
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
            st.write(pd.DataFrame(reminders))
        else:
            st.success("لا يوجد عملاء تحتاج زيارة.")

    elif menu == "إضافة فني" and role == "admin":
        st.subheader("➕ إضافة فني جديد")
        with st.form("add_tech"):
            new_user = st.text_input("اسم المستخدم")
            new_pass = st.text_input("كلمة المرور", type="password")
            new_role = st.selectbox("الدور", ["technician"])
            if st.form_submit_button("إضافة"):
                if new_user and new_pass:
                    users.append({"username":new_user,"password":new_pass,"role":new_role})
                    save_users()
                    st.success(f"✅ تم إضافة الفني {new_user} بنجاح.")
                else:
                    st.warning("⚠️ اكتب اسم وكلمة المرور.")

    elif menu == "عرض العملاء على الخريطة":
        st.subheader("🗺️ عرض العملاء على الخريطة")
        map_data = []
        for c in customers:
            try:
                lat, lon = map(float, c.get("location","0,0").split(","))
                map_data.append({"lat":lat,"lon":lon,"name":c.get("name","")})
            except:
                continue
        if map_data:
            df_map = pd.DataFrame(map_data)
            st.map(df_map.rename(columns={"lat":"lat","lon":"lon"}))
        else:
            st.info("لا يوجد مواقع صحيحة للعملاء.")

    elif menu == "تسجيل الخروج":
        logout()
