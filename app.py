import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================
st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; }
    .report-table th { background-color: #28a745; color: white; }
    .warning-row { background-color: #ffcccc !important; color: black !important; }
    .qr-box { border: 2px dashed #28a745; padding: 15px; text-align: center; background: #f0fff0; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)

# تأمين حساب المدير
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== قراءة الباركود من الرابط (التعديل الجديد) ==================
query = st.query_params
if "qr" in query:
    qr_val = query["qr"]
    found_customer = next((c for c in customers if c.get("qr_code") == qr_val), None)
    if found_customer:
        st.session_state.qr_customer = found_customer
        st.session_state.logged_in = True
        st.session_state.current_user = {"username": "QR", "role": "viewer"}

# ================== 2. نظام الدخول ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life Ultra - دخول")
    u_in = st.text_input("اسم المستخدم")
    p_in = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")
    st.stop()

user_now = st.session_state.current_user
st.sidebar.title("💧 Power Life")

menu = ["📋 قائمة العملاء", "➕ إضافة عميل", "🛠️ إضافة صيانة", "🔍 بحث وتعديل", "💰 أرباح الشركة"]
if user_now.get("role") == "admin":
    menu.append("👷 تتبع الفنيين")
    menu.append("👤 إضافة فني جديد")
menu.append("🚪 خروج")

choice = st.sidebar.radio("القائمة الرئيسية", menu)

# ================== إضافة عميل ==================
if choice == "➕ إضافة عميل":
    st.subheader("➕ تسجيل عميل جديد")

    with st.form("new_c_form"):
        name = st.text_input("اسم العميل *")
        phone = st.text_input("رقم الهاتف *")
        gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
        submitted = st.form_submit_button("💾 حفظ العميل وإصدار الباركود")

        if submitted:
            if not name or not phone:
                st.error("يرجى ملء البيانات المطلوبة")
            else:
                new_id = max([c["id"] for c in customers], default=0) + 1
                qr_code = f"PL-{new_id:04d}"

                c_data = {
                    "id": new_id,
                    "name": name,
                    "phone": phone,
                    "gov": gov,
                    "history": [],
                    "qr_code": qr_code
                }

                customers.append(c_data)
                save_data(CUSTOMERS_FILE, customers)

                st.success("تم حفظ العميل")
                st.subheader("🤳 باركود العميل")

                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://YOUR_APP_URL/?qr={qr_code}"

                st.markdown(f"""
                <div class='qr-box'>
                    <h4>{name}</h4>
                    <img src="{qr_url}" width="180">
                    <p><strong>{qr_code}</strong></p>
                </div>
                """, unsafe_allow_html=True)

# ================== قائمة العملاء / تقرير العميل ==================
elif choice == "📋 قائمة العملاء":

    if "qr_customer" in st.session_state:
        c = st.session_state.qr_customer
        st.subheader(f"👤 ملف العميل: {c['name']}")

        total_paid = sum(h['التكلفة'] for h in c.get("history", []))
        st.write(f"📞 {c['phone']}")
        st.write(f"💰 إجمالي المدفوعات: {total_paid} جنيه")

        if c.get("history"):
            rows = ""
            for h in c["history"]:
                rows += f"<tr><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>"

            st.markdown(f"""
            <table class='report-table'>
            <thead><tr><th>التاريخ</th><th>الفني</th><th>العمل</th><th>المبلغ</th></tr></thead>
            <tbody>{rows}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.info("لا توجد صيانات مسجلة")

# ================== خروج ==================
elif choice == "🚪 خروج":
    st.session_state.logged_in = False
    st.rerun()
