import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام والبيانات ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

def load_data(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f: return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)

# تأمين حساب المدير
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 29.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== 2. تسجيل الدخول ==================
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life - تسجيل الدخول")
    u_in = st.text_input("اسم المستخدم")
    p_in = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else: st.error("بيانات غير صحيحة")

else:
    # تحديث موقع الفني الحالي في الخلفية
    user_now = st.session_state.current_user
    
    # ================== 3. القائمة الجانبية ==================
    st.sidebar.title("💧 Power Life")
    st.sidebar.write(f"المستخدم: {user_now['username']} ({user_now['role']})")
    
    menu = ["📋 قائمة العملاء", "🔍 بحث", "🛠️ إضافة صيانة", "🗺️ خريطة العملاء"]
    if user_now['role'] == "admin":
        menu.insert(0, "➕ إضافة عميل")
        menu.append("👷 تتبع الفنيين")
        menu.append("➕ إضافة فني جديد")
    
    menu.append("🚪 تسجيل الخروج")
    choice = st.sidebar.radio("الانتقال إلى", menu)

    # تحديث إحداثيات الفني (للتتبع)
    with st.sidebar.expander("📍 تحديث موقعي الحالي"):
        curr_lat = st.number_input("Lat", value=float(user_now.get('lat', 0)))
        curr_lon = st.number_input("Lon", value=float(user_now.get('lon', 0)))
        if st.button("تحديث إحداثياتي"):
            for u in users:
                if u['username'] == user_now['username']:
                    u['lat'], u['lon'] = curr_lat, curr_lon
            save_data(USERS_FILE, users)
            st.success("تم التحديث")

    # ================== 4. الوظائف ==================

    # --- إضافة عميل جديد ---
    if choice == "➕ إضافة عميل":
        st.subheader("إضافة عميل جديد للنظام")
        with st.form("add_cust"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم الهاتف")
            with c2:
                loc = st.text_input("الإحداثيات (lat,lon)")
                cat = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
            notes = st.text_input("ملاحظات")
            if st.form_submit_button("حفظ العميل"):
                customers.append({"id": len(customers)+1, "name": name, "phone": phone, "location": loc, "category": cat, "notes": notes, "history": []})
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ!")

    # --- قائمة العملاء ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("كل العملاء المسجلين")
        if customers:
            df = pd.DataFrame(customers).drop(columns=['history'], errors='ignore')
            st.dataframe(df, use_container_width=True)
        else: st.info("القائمة فارغة")

    # --- بحث عن عميل ---
    elif choice == "🔍 بحث":
        st.subheader("البحث في البيانات")
        search_term = st.text_input("ادخل اسم العميل أو رقم الهاتف")
        if search_term:
            results = [c for c in customers if search_term in c['name'] or search_term in c['phone']]
            if results: st.table(pd.DataFrame(results).drop(columns=['history'], errors='ignore'))
            else: st.error("لا توجد نتائج")

    # --- إضافة صيانة (الميزة المطلوبة) ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("تسجيل صيانة جديدة")
        if not customers: st.warning("لا يوجد عملاء")
        else:
            # اختيار العميل من القائمة
            selected_c = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            
            st.info(f"العميل: {selected_c['name']} | آخر ملاحظة: {selected_c.get('notes', '')}")
            
            # عرض سجل الصيانات القديم لهذا العميل
            with st.expander("📜 عرض سجل الصيانات القديم"):
                if selected_c.get('history'):
                    st.table(pd.DataFrame(selected_c['history']))
                else: st.write("لا يوجد تاريخ صيانة سابق")

            # نموذج إضافة صيانة جديدة
            with st.form("add_service"):
                st.write("--- تفاصيل الصيانة الجديدة ---")
                col1, col2 = st.columns(2)
                with col1:
                    work = st.multiselect("العمل المنجز", ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "صيانة موتور"])
                with col2:
                    cost = st.number_input("التكلفة", min_value=0)
                
                if st.form_submit_button("حفظ الصيانة باسمي"):
                    new_visit = {
                        "التاريخ": str(datetime.today().strftime('%Y-%m-%d')),
                        "العمل": ", ".join(work),
                        "التكلفة": cost,
                        "الفني": user_now['username'] # الميزة المطلوبة: حفظ اسم الفني
                    }
                    if 'history' not in selected_c: selected_c['history'] = []
                    selected_c['history'].append(new_visit)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success(f"تم تسجيل الصيانة بواسطة الفني: {user_now['username']}")

    # --- خريطة العملاء ---
    elif choice == "🗺️ خريطة العملاء":
        st.subheader("مواقع العملاء")
        map_c = []
        for c in customers:
            try:
                lat, lon = map(float, c['location'].split(','))
                map_c.append({"lat": lat, "lon": lon, "name": c['name']})
            except: pass
        if map_c: st.map(pd.DataFrame(map_c))
        else: st.warning("لا توجد إحداثيات")

    # --- تتبع الفنيين (للمدير فقط) ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("آخر موقع ظهر فيه الفنيين")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            df_techs = pd.DataFrame(techs)[['username', 'lat', 'lon']]
            st.map(df_techs)
            st.table(df_techs)
        else: st.info("لا يوجد فنيين مسجلين")

    # --- إضافة فني جديد ---
    elif choice == "➕ إضافة فني جديد":
        st.subheader("إضافة حساب فني جديد")
        with st.form("new_tech"):
            t_user = st.text_input("اسم الفني")
            t_pass = st.text_input("كلمة مرور الفني")
            if st.form_submit_button("إضافة"):
                users.append({"username": t_user, "password": t_pass, "role": "technician", "lat": 0, "lon": 0})
                save_data(USERS_FILE, users)
                st.success("تمت الإضافة")

    elif choice == "🚪 تسجيل الخروج":
        st.session_state.logged_in = False
        st.rerun()
