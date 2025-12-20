import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd

# ------------------ الملفات ------------------
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

# -------- تحميل المستخدمين ----------
if os.path.exists(USERS_FILE):
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except:
        users = []
else:
    users = []

# إنشاء المدير لو مش موجود
admin_exists = any(u.get("username") == "Abdallah" for u in users)
if not admin_exists:
    users.append({"username": "Abdallah", "password": "772001", "role": "admin"})
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

if "menu" not in st.session_state:
    st.session_state.menu = None


st.set_page_config(page_title="Power Life - إدارة العملاء", layout="wide")

# ------------------ تسجيل الخروج ------------------
def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.menu = None
    st.experimental_rerun()


# ------------------ تسجيل الدخول ------------------
if not st.session_state.logged_in:

    st.title("🏢 Power Life ترحب بكم")
    st.subheader("🔑 تسجيل الدخول")

    username = st.text_input("اسم المستخدم")
    password = st.text_input("كلمة المرور", type="password")

    if st.button("تسجيل الدخول"):
        try:
            user = next(
                (u for u in users if u.get("username") == username and u.get("password") == password),
                None
            )
        except:
            st.error("❌ خطأ داخلي في قراءة المستخدمين")
            user = None

        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.success(f"✅ مرحباً {username}")
            st.experimental_rerun()
        else:
            st.error("❌ البيانات غير صحيحة")

# ------------------ لوحة التحكم ------------------
else:

    user = st.session_state.current_user
    role = user.get("role", "technician")

    st.sidebar.title("لوحة التحكم")

    # القائمة حسب صلاحيات المستخدم
    if role == "admin":
        options = [
            "إضافة عميل",
            "عرض العملاء",
            "بحث",
            "تذكير الزيارة",
            "إضافة فني",
            "عرض العملاء على الخريطة",
            "تسجيل الخروج"
        ]
    else:
        options = [
            "عرض العملاء",
            "بحث",
            "تذكير الزيارة",
            "عرض العملاء على الخريطة",
            "تسجيل الخروج"
        ]

    choice = st.sidebar.radio("القائمة", options)

    # ----------- إضافة عميل -----------
    if choice == "إضافة عميل":
        st.subheader("➕ إضافة عميل")
        with st.form("add_customer"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم التليفون")
            location = st.text_input("إحداثيات Google Maps مثال: 30.0444,31.2357")
            notes = st.text_area("ملاحظات")
            category = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
            last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())

            if st.form_submit_button("إضافة"):
                customers.append({
                    "id": len(customers) + 1,
                    "name": name,
                    "phone": phone,
                    "location": location,
                    "notes": notes,
                    "category": category,
                    "last_visit": str(last_visit)
                })
                save_customers()
                st.success("✅ تم إضافة العميل بنجاح")


    # ----------- عرض العملاء -----------
    elif choice == "عرض العملاء":
        st.subheader("📋 قائمة العملاء")
        if customers:
            st.dataframe(pd.DataFrame(customers))
        else:
            st.info("لا يوجد عملاء بعد.")


    # ----------- بحث -----------
    elif choice == "بحث":
        st.subheader("🔎 البحث عن عميل")
        keyword = st.text_input("اكتب اسم أو رقم للبحث")

        if keyword:
            results = [c for c in customers if keyword in c["name"] or keyword in c["phone"]]
            if results:
                st.dataframe(pd.DataFrame(results))
            else:
                st.warning("لا يوجد نتائج")


    # ----------- تذكير -----------
    elif choice == "تذكير الزيارة":
        st.subheader("⏰ العملاء المطلوب زيارتهم")
        today = datetime.today()
        due = []

        for c in customers:
            try:
                last = datetime.strptime(c["last_visit"], "%Y-%m-%d")
                if today - last >= timedelta(days=30):
                    due.append(c)
            except:
                pass

        if due:
            st.dataframe(pd.DataFrame(due))
        else:
            st.success("لا يوجد عملاء بحاجة لزيارة الآن")


    # ----------- إضافة فني (للمدير فقط) -----------
    elif choice == "إضافة فني" and role == "admin":
        st.subheader("➕ إضافة فني جديد")
        with st.form("add_tech"):
            new_user = st.text_input("اسم المستخدم")
            new_pass = st.text_input("كلمة المرور", type="password")

            if st.form_submit_button("إضافة"):
                users.append({
                    "username": new_user,
                    "password": new_pass,
                    "role": "technician"
                })
                save_users()
                st.success("✅ تم إضافة الفني بنجاح")


    # ----------- عرض العملاء على الخريطة -----------
    elif choice == "عرض العملاء على الخريطة":
        st.subheader("🗺️ خريطة العملاء")

        map_points = []

        for c in customers:
            try:
                lat, lon = map(float, c["location"].split(","))
                map_points.append({"lat": lat, "lon": lon})
            except:
                pass

        if map_points:
            df_map = pd.DataFrame(map_points)
            st.map(df_map)
        else:
            st.info("لا توجد إحداثيات صالحة للعرض.")


    # ----------- تسجيل الخروج -----------
    elif choice == "تسجيل الخروج":
        logout()
