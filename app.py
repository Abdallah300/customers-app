import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام ==================
st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
<style>
.report-table { width:100%; border-collapse:collapse; background:white; color:black }
.report-table th, .report-table td { border:1px solid #ddd; padding:8px; text-align:right }
.report-table th { background:#28a745; color:white }
.qr-box { border:2px dashed #28a745; padding:15px; text-align:center; background:#f0fff0; border-radius:10px }
</style>
""", unsafe_allow_html=True)

USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)

# حساب المدير
if not any(u["username"] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30, "lon": 31})
    save_data(USERS_FILE, users)

# ================== 2. تسجيل الدخول ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life Ultra - دخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u and x["password"] == p), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")
    st.stop()

user_now = st.session_state.user

menu = ["➕ إضافة عميل", "📋 قائمة العملاء", "🛠️ إضافة صيانة", "💰 أرباح الشركة", "🚪 خروج"]
choice = st.sidebar.radio("القائمة", menu)

# ================== إضافة عميل ==================
if choice == "➕ إضافة عميل":
    with st.form("add_customer"):
        name = st.text_input("اسم العميل *")
        phone = st.text_input("الهاتف *")
        gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "الإسكندرية", "أخرى"])
        submit = st.form_submit_button("حفظ")

        if submit:
            if not name or not phone:
                st.error("الاسم والهاتف مطلوبين")
            else:
                new_id = max([c["id"] for c in customers], default=0) + 1
                qr_code = f"PL-{new_id:04d}"

                customers.append({
                    "id": new_id,
                    "name": name,
                    "phone": phone,
                    "gov": gov,
                    "history": [],
                    "qr_code": qr_code
                })
                save_data(CUSTOMERS_FILE, customers)

                st.success("تم الحفظ")
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_code}"

                st.markdown(f"""
                <div class='qr-box'>
                    <h4>{name}</h4>
                    <img src="{qr_url}">
                    <p>{qr_code}</p>
                </div>
                """, unsafe_allow_html=True)

# ================== قائمة العملاء ==================
elif choice == "📋 قائمة العملاء":
    search_qr = st.text_input("بحث بالباركود (PL-0001)")
    if search_qr:
        c = next((x for x in customers if x["qr_code"] == search_qr), None)
        if c:
            st.session_state.current = c
        else:
            st.error("غير موجود")

    if "current" in st.session_state:
        c = st.session_state.current
        st.subheader(c["name"])
        st.write(c["phone"])
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={c['qr_code']}"
        st.image(qr_url)

        if c["history"]:
            df = pd.DataFrame(c["history"])
            st.dataframe(df)

    st.markdown("---")
    for c in customers:
        if st.button(f"عرض {c['name']}", key=c["id"]):
            st.session_state.current = c
            st.rerun()

# ================== إضافة صيانة ==================
elif choice == "🛠️ إضافة صيانة":
    if not customers:
        st.info("لا يوجد عملاء")
    else:
        c = st.selectbox("اختر العميل", customers, format_func=lambda x: x["name"])
        with st.form("service"):
            work = st.text_input("العمل")
            price = st.number_input("المبلغ", 0)
            save = st.form_submit_button("حفظ")
            if save:
                c["history"].append({
                    "التاريخ": str(datetime.now().date()),
                    "الفني": user_now["username"],
                    "العمل": work,
                    "التكلفة": price
                })
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم")

# ================== أرباح ==================
elif choice == "💰 أرباح الشركة":
    all_data = []
    for c in customers:
        all_data.extend(c["history"])
    if all_data:
        df = pd.DataFrame(all_data)
        st.success(f"الإجمالي: {df['التكلفة'].sum()} جنيه")
        st.dataframe(df)
    else:
        st.info("لا توجد بيانات")

# ================== خروج ==================
elif choice == "🚪 خروج":
    st.session_state.logged_in = False
    st.rerun()
