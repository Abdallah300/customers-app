import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام وتصميم الجداول ==================
st.set_page_config(page_title="Power Life Ultra", page_icon="💧", layout="wide")

st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 12px; text-align: right; }
    .report-table th { background-color: #007bff; color: white; }
    .stMetric { border: 1px solid #eee; padding: 15px; border-radius: 10px; background-color: #f9f9f9; }
    </style>
    """, unsafe_allow_html=True)

# إدارة ملفات البيانات
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f: 
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)

# حساب المدير الافتراضي
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== 2. تسجيل الدخول ==================
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life Ultra - دخول")
    u_in = st.text_input("اسم المستخدم")
    p_in = st.text_input("كلمة المرور", type="password")
    if st.button("دخول للنظام"):
        user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else: st.error("بيانات الدخول غير صحيحة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    
    menu = ["📋 قائمة العملاء", "➕ إضافة عميل", "🛠️ إضافة صيانة", "🔍 بحث وتعديل رصيد", "💰 الأرباح والتقارير"]
    if user_now['role'] == "admin":
        menu.append("📍 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- 1. إضافة عميل بالتفاصيل ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد (بيانات تفصيلية)")
        with st.form("new_customer"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("اسم العميل بالكامل")
                phone = st.text_input("رقم الهاتف")
                gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "الدقهلية", "أخرى"])
            with c2:
                center = st.text_input("المركز / المدينة")
                village = st.text_input("البلد / القرية")
                ctype = st.selectbox("حالة الجهاز", ["جهاز جديد (تركيبنا)", "جهاز قديم (صيانة فقط)", "عميل شركة / منشأة"])
            
            if st.form_submit_button("حفظ العميل"):
                new_id = len(customers) + 1
                customers.append({
                    "id": new_id, "name": name, "phone": phone, "gov": gov,
                    "center": center, "village": village, "type": ctype, "history": []
                })
                save_data(CUSTOMERS_FILE, customers)
                st.success(f"✅ تم حفظ العميل {name} بنجاح")
                # رابط باركود بسيط (يعمل في المتصفح)
                st.info(f"رابط ملف العميل للباركود: https://powerlife-crm.com/client/{new_id}")

    # --- 2. إضافة صيانة (تسجيل الفني والشمع) ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة دورية")
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            with st.form("service"):
                shame3 = st.multiselect("أنواع الشمع المبدل", ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "بوست كربون", "كالسيت", "موتور", "خزان"])
                cost = st.number_input("المبلغ المطلوب تحصيله", min_value=0)
                if st.form_submit_button("تسجيل الصيانة"):
                    h = {
                        "التاريخ": str(datetime.now().date()),
                        "الفني": user_now['username'],
                        "العمل": ", ".join(shame3),
                        "التكلفة": cost
                    }
                    for c in customers:
                        if c['id'] == target['id']: c['history'].append(h)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("✅ تم التسجيل بنجاح")
        else: st.warning("لا يوجد عملاء")

    # --- 3. بحث وتعديل ورصيد العميل ---
    elif choice == "🔍 بحث وتعديل رصيد":
        st.subheader("🔍 كشف حساب العميل")
        s = st.text_input("ابحث باسم العميل أو رقم هاتفه")
        if s:
            results = [c for c in customers if s in c['name'] or s in c['phone']]
            for c in results:
                with st.expander(f"👤 ملف: {c['name']} | العنوان: {c['village']}"):
                    st.write(f"**نوع العميل:** {c['type']}")
                    st.write(f"**إجمالي المدفوعات (الرصيد):** {sum(h['التكلفة'] for h in c['history'])} جنيه")
                    # عرض سجل الشمع والفنيين
                    if c['history']:
                        rows = "".join([f"<tr><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>" for h in c['history']])
                        st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>الفني المسئول</th><th>الشمع المبدل</th><th>المبلغ</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
                    else: st.write("لا توجد صيانات سابقة.")

    # --- 4. تتبع الفنيين (جدول آمن) ---
    elif choice == "📍 تتبع الفنيين":
        st.subheader("📍 مواقع الفنيين الحالية")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            rows = ""
            for u in techs:
                rows += f"<tr><td>{u['username']}</td><td>{u.get('lat',0)}</td><td>{u.get('lon',0)}</td></tr>"
            st.markdown(f"<table class='report-table'><thead><tr><th>اسم الفني</th><th>خط العرض</th><th>خط الطول</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
            st.info("💡 لمشاهدة الموقع بدقة، انسخ الإحداثيات وضعها في جوجل ماب.")
        else: st.info("لا يوجد فنيين مسجلين")

    # --- 5. الأرباح وقائمة العملاء ---
    elif choice == "💰 الأرباح والتقارير":
        total = sum(sum(h['التكلفة'] for h in c['history']) for c in customers)
        st.metric("إجمالي الخزنة", f"{total} جنيه")
        
    elif choice == "👤 إضافة فني جديد":
        with st.form("add_tech"):
            tu = st.text_input("اسم المستخدم للفني")
            tp = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة"):
                users.append({"username": tu, "password": tp, "role": "technician", "lat": 0, "lon": 0})
                save_data(USERS_FILE, users)
                st.success("تم")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
