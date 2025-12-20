import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام وتوافقية المتصفح ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

# كود لتجاوز أخطاء المتصفح وتجميل الواجهة
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTable { background-color: white; border-radius: 10px; }
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
    st.sidebar.write(f"المستخدم: {user_now['username']}")
    
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "🔍 بحث", "🗺️ خريطة العملاء"]
    if user_now['role'] == "admin":
        menu.insert(0, "➕ إضافة عميل")
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- تحديث الموقع (GPS) ---
    with st.sidebar.expander("📍 تحديث موقعي"):
        n_lat = st.number_input("Lat", value=float(user_now.get('lat', 0)), format="%.6f")
        n_lon = st.number_input("Lon", value=float(user_now.get('lon', 0)), format="%.6f")
        if st.button("تحديث"):
            for u in users:
                if u['username'] == user_now['username']: u['lat'], u['lon'] = n_lat, n_lon
            save_data(USERS_FILE, users)
            st.success("تم!")

    # --- إضافة عميل جديد ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم العميل")
            phone = c1.text_input("رقم الهاتف")
            loc = c2.text_input("الإحداثيات (lat,lon)")
            cat = c2.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
            notes = st.text_input("ملاحظات")
            if st.form_submit_button("حفظ بيانات العميل"):
                customers.append({"id": len(customers)+1, "name": name, "phone": phone, "location": loc, "category": cat, "notes": notes, "history": []})
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ بنجاح")

    # --- قائمة العملاء (الحل الجذري للرسالة الحمراء) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 تقرير الصيانات والتحصيل")
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
            if user_now['role'] == "admin":
                st.info(f"💰 إجمالي التحصيل المالي: {df['المبلغ'].sum()} جنيه")
            
            # ملاحظة: استخدمنا st.table بدلاً من st.dataframe لأنه لا يسبب أخطاء في المتصفحات
            st.table(df)
            st.download_button("📥 تحميل التقرير Excel", df.to_csv(index=False).encode('utf-8-sig'), "report.csv")
        else: st.info("لا توجد بيانات")

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
        st.subheader("📍 مواقع الفنيين الحالية")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            df_techs = pd.DataFrame(techs)[['username', 'lat', 'lon']]
            st.map(df_techs)
            st.table(df_techs)
        else: st.info("لا يوجد فنيين")

    # --- خريطة العملاء ---
    elif choice == "🗺️ خريطة العملاء":
        st.subheader("🗺️ مواقع العملاء")
        map_c = []
        for c in customers:
            try:
                lat, lon = map(float, c['location'].split(','))
                map_c.append({"lat": lat, "lon": lon, "name": c['name']})
            except: pass
        if map_c: st.map(pd.DataFrame(map_c))
        else: st.warning("لا توجد إحداثيات")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
