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
    users = {"Abdallah": "772001"}
    save_users(users)

# --------------------------
# حالة تسجيل الدخول
# --------------------------
# عند كل تحديث للصفحة يتم اعادة تعيين login state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_login" not in st.session_state:
    st.session_state.show_login = False

# --------------------------
# إعداد الصفحة
# --------------------------
st.set_page_config(page_title="Baro Life", layout="wide")
st.title("💧 Welcome to Baro Life")

# --------------------------
# زر لإظهار حقول تسجيل الدخول
# --------------------------
if not st.session_state.logged_in:
    if st.button("Login"):
        st.session_state.show_login = True

# --------------------------
# صفحة تسجيل الدخول تظهر بعد الضغط على Login
# --------------------------
if st.session_state.show_login and not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Submit Login")

    if login_btn:
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Welcome, {username}")
        else:
            st.error("Invalid credentials")

# --------------------------
# بعد تسجيل الدخول
# --------------------------
if st.session_state.logged_in:

    # --------------------------
    # زر تسجيل الخروج
    # --------------------------
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.show_login = False
        st.experimental_rerun()

    # --------------------------
    # القائمة الرئيسية
    # --------------------------
    menu = st.radio("Menu", ["Add Customer", "View Customers", "Search", "Visit Reminder"])

    # --------------------------
    # إضافة عميل
    # --------------------------
    if menu == "Add Customer":
        st.subheader("➕ Add Customer")
        with st.form("add_form"):
            name = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
            location = st.text_input("Address or Google Maps Link")
            notes = st.text_area("Notes")
            category = st.selectbox("Category", ["Home", "Company", "School"])
            last_visit = st.date_input("Last Visit Date", datetime.today())
            if st.form_submit_button("Add"):
                customers.append({
                    "id": len(customers) + 1,
                    "name": name,
                    "phone": phone,
                    "location": location,
                    "notes": notes,
                    "category": category,
                    "last_visit": str(last_visit)
                })
                save_customers(customers)
                st.success(f"✅ {name} added successfully.")

    # --------------------------
    # عرض العملاء
    # --------------------------
    elif menu == "View Customers":
        st.subheader("📋 Customers List")
        if customers:
            for c in customers:
                st.write(f"**{c['name']}** - {c['phone']}")
                if c.get("location"):
                    st.markdown(f"[🌍 Open Location]({c['location']})", unsafe_allow_html=True)
                if c.get("phone"):
                    phone_number = c["phone"]
                    st.markdown(f"[💬 WhatsApp](https://wa.me/{phone_number}) | [📞 Call](tel:{phone_number})", unsafe_allow_html=True)
                st.write("---")
        else:
            st.info("No customers yet.")

    # --------------------------
    # البحث عن عميل
    # --------------------------
    elif menu == "Search":
        st.subheader("🔎 Search Customer")
        keyword = st.text_input("Enter name or phone")
        if keyword:
            results = [c for c in customers if keyword in c.get("name","") or keyword in c.get("phone","")]
            if results:
                for c in results:
                    st.write(f"**{c['name']}** - {c['phone']}")
                    if c.get("location"):
                        st.markdown(f"[🌍 Open Location]({c['location']})", unsafe_allow_html=True)
                    if c.get("phone"):
                        phone_number = c["phone"]
                        st.markdown(f"[💬 WhatsApp](https://wa.me/{phone_number}) | [📞 Call](tel:{phone_number})", unsafe_allow_html=True)
                    st.write("---")
            else:
                st.warning("No results found.")

    # --------------------------
    # تذكير بالزيارات
    # --------------------------
    elif menu == "Visit Reminder":
        st.subheader("⏰ Customers to Visit (30+ days)")
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
                    st.markdown(f"[🌍 Open Location]({c['location']})", unsafe_allow_html=True)
                st.write("---")
        else:
            st.success("No customers need a visit.")
