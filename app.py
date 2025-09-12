import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd

FILE_NAME = "customers.json"

# --------------------------
# وظائف تحميل وحفظ العملاء
# --------------------------
def load_customers():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_customers(customers):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

customers = load_customers()

# --------------------------
# قائمة الفنيين
# --------------------------
users = {
    "technician1": "1234",
    "technician2": "abcd",
}

# --------------------------
# حالة تسجيل الدخول
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --------------------------
# صفحة تسجيل الدخول
# --------------------------
st.sidebar.subheader("Login")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")
login_btn = st.sidebar.button("Login")

if login_btn:
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.user = username
        st.sidebar.success(f"Welcome, {username}")
    else:
        st.sidebar.error("Invalid credentials")

# --------------------------
# المحتوى الرئيسي يظهر بعد تسجيل الدخول فقط
# --------------------------
if st.session_state.logged_in:

    st.set_page_config(page_title="Customer Management - Baro Life", layout="wide")
    st.title("💧 Customer Management - Baro Life")

    menu = st.sidebar.radio("Menu", ["Add Customer", "View Customers", "Search", "Visit Reminder"])

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
    # عرض العملاء مع زر فتح اللوكيشن
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

else:
    st.info("Please login to access the app.")
