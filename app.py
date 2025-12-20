import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

# كود CSS لتحسين مظهر الجداول وتوحيد الألوان
st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white; color: black; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 12px; text-align: right; }
    .report-table th { background-color: #f2f2f2; color: #333; }
    .report-table tr:nth-child(even) { background-color: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

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

# تأمين حساب المدير
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== 2. نظام الدخول ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life - دخول")
    u_in = st.text_input("اسم المستخدم")
    p_in = st.text_input("كلمة المرور", type="password")
    if st.button("دخول للنظام"):
        user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else: st.error("بيانات خاطئة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "🔍 بحث", "🗺️ خريطة العملاء"]
    if user_now['role'] == "admin":
        menu.insert(0, "➕ إضافة عميل")
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- إضافة عميل جديد ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم العميل")
            phone = c1.text_input("رقم الهاتف")
            loc = c2.text_input("الإحداثيات (lat,lon)")
            cat = c2.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
            if st.form_submit_button("حفظ بيانات العميل"):
                customers.append({"id": len(customers)+1, "name": name, "phone": phone, "location": loc, "category": cat, "history": []})
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ بنجاح")

    # --- قائمة العملاء (تعديل العرض ليظهر على الكمبيوتر) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 تقرير الصيانات والتحصيل المالي")
        if customers:
            all_records = []
            for c in customers:
                if c.get('history'):
                    for h in c['history']:
                        all_records.append({
                            "العميل": c['name'], "الهاتف": c['phone'], 
                            "التاريخ": h['التاريخ'], "الفني": h['الفني'], 
                            "الشمع": h['العمل'], "المبلغ": h['التكلفة']
                        })
                else:
                    all_records.append({
                        "العميل": c['name'], "الهاتف": c['phone'], 
                        "التاريخ": "لا يوجد", "الفني": "-", "الشمع": "-", "المبلغ": 0
                    })
            
            df = pd.DataFrame(all_records)
            
            # عرض إجمالي الدخل
            if user_now['role'] == "admin":
                st.info(f"💰 إجمالي التحصيل المالي: {df['المبلغ'].sum()} جنيه")
            
            # الحل النهائي: عرض الجدول بصيغة HTML ثابتة لضمان الظهور على الكمبيوتر
            st.write(df.to_html(classes='report-table', index=False), unsafe_allow_html=True)
            
            st.write("") # مسافة
            st.download_button("📥 تحميل التقرير Excel", df.to_csv(index=False).encode('utf-8-sig'), "report.csv")
        else: st.info("لا توجد بيانات ليتم عرضها")

    # --- إضافة صيانة ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة جديدة")
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            with st.form("serv_form"):
                work = st.multiselect("الشمع المغير", ["1", "2", "3", "M", "S", "موتور", "خزان"])
                cost = st.number_input("المبلغ المدفوع", min_value=0)
                if st.form_submit_button("حفظ الصيانة"):
                    new_h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": cost}
                    for cust in customers:
                        if cust['id'] == target['id']:
                            if 'history' not in cust: cust['history'] = []
                            cust['history'].append(new_h)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success(f"تم التسجيل بواسطة الفني: {user_now['username']}")

    # --- تتبع الفنيين (للمدير) ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 مواقع الفنيين")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            df_techs = pd.DataFrame(techs)[['username', 'lat', 'lon']]
            st.table(df_techs) # استخدام جدول بسيط لضمان الظهور
        else: st.info("لا يوجد فنيين مسجلين")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
