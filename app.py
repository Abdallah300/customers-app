import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== إعداد الصفحة ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

# ================== إدارة الملفات ==================
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
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 0, "lon": 0})
    save_data(USERS_FILE, users)

# ================== نظام التتبع (GPS) ==================
# دالة لتحديث موقع المستخدم الحالي (فني أو مدير)
def update_user_location(lat, lon):
    for u in users:
        if u['username'] == st.session_state.current_user['username']:
            u['lat'], u['lon'] = lat, lon
            break
    save_data(USERS_FILE, users)

# ================== تسجيل الدخول = :
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 تسجيل دخول Power Life")
    u_input = st.text_input("اسم المستخدم")
    p_input = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u_input and x["password"] == p_input), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else: st.error("بيانات خاطئة")
else:
    # تحديث موقع الفني/المدير عند الدخول (محاكاة)
    # ملاحظة: في المتصفح الحقيقي يتطلب صلاحيات GPS، هنا نضع حقول لإدخالها يدوياً للتبسيط
    with st.sidebar.expander("📍 تحديث موقعي الحالي"):
        my_lat = st.number_input("Lat", value=st.session_state.current_user.get('lat', 0.0), format="%.6f")
        my_lon = st.number_input("Lon", value=st.session_state.current_user.get('lon', 0.0), format="%.6f")
        if st.button("تحديث الموقع"):
            update_user_location(my_lat, my_lon)
            st.success("تم التحديث")

    # ================== القائمة الجانبية ==================
    user_role = st.session_state.current_user['role']
    st.sidebar.title(f"مرحباً {st.session_state.current_user['username']}")
    
    menu = ["إضافة صيانة", "خريطة العملاء", "البحث"]
    if user_role == "admin":
        menu.insert(0, "إدارة العملاء")
        menu.append("تتبع الفنيين 👷")
        menu.append("إضافة فني جديد")
    
    menu.append("تسجيل الخروج")
    choice = st.sidebar.radio("القائمة", menu)

    # ================== 1. إضافة صيانة (للفني والمدير) ==================
    if choice == "إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة لعميل سابق")
        if not customers: st.info("لا يوجد عملاء مضافين")
        else:
            search_c = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            
            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📋 بيانات العميل: {search_c['name']}")
                st.write(f"📞 هاتف: {search_c['phone']}")
                st.write(f"📍 موقع: {search_c['location']}")
            with col2:
                st.warning("🕰️ السجل القديم")
                if search_c.get('history'): st.write(search_c['history'][-1]) # عرض آخر صيانة
                else: st.write("لا توجد صيانات سابقة")

            with st.expander("➕ إضافة صيانة جديدة الآن"):
                work = st.multiselect("الأعمال", ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "تغيير موتور", "صيانة دورية"])
                cost = st.number_input("التكلفة", min_value=0)
                if st.button("حفظ الصيانة"):
                    new_visit = {"date": str(datetime.today().date()), "work": work, "cost": cost, "tech": st.session_state.current_user['username']}
                    if 'history' not in search_c: search_c['history'] = []
                    search_c['history'].append(new_visit)
                    search_c['last_visit'] = str(datetime.today().date())
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم تسجيل الصيانة بنجاح!")

    # ================== 2. خريطة العملاء (للجميع) ==================
    elif choice == "خريطة العملاء":
        st.subheader("🗺️ مواقع العملاء على الخريطة")
        map_data = []
        for c in customers:
            try:
                lat, lon = map(float, c['location'].split(','))
                map_data.append({"lat": lat, "lon": lon, "name": c['name']})
            except: pass
        if map_data: st.map(pd.DataFrame(map_data))
        else: st.warning("لا توجد إحداثيات للعملاء")

    # ================== 3. تتبع الفنيين (للمدير فقط) ==================
    elif choice == "تتبع الفنيين 👷":
        st.subheader("📍 مواقع الفنيين الحالية")
        tech_data = []
        for u in users:
            if u['role'] == 'technician' and u.get('lat'):
                tech_data.append({"lat": u['lat'], "lon": u['lon'], "name": u['username']})
        if tech_data:
            st.write("النقاط تظهر آخر تواجد للفنيين")
            st.map(pd.DataFrame(tech_data))
            st.table(pd.DataFrame(tech_data))
        else: st.info("لا يوجد فنيين متصلين حالياً")

    # ================== 4. إدارة العملاء (إضافة جديد) ==================
    elif choice == "إدارة العملاء":
        st.subheader("➕ إضافة عميل جديد للنظام")
        with st.form("new_cust"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("اسم العميل")
                phone = st.text_input("الهاتف")
            with c2:
                loc = st.text_input("الإحداثيات (مثال: 30.0,31.2)")
                cat = st.selectbox("الفئة", ["منزل", "شركة"])
            if st.form_submit_button("حفظ العميل"):
                customers.append({"id": len(customers)+1, "name": name, "phone": phone, "location": loc, "category": cat, "history": []})
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم الإضافة")

    elif choice == "تسجيل الخروج":
        st.session_state.logged_in = False
        st.rerun()
