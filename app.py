import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام الأساسية ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

# أسماء ملفات البيانات
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

# دوال إدارة البيانات
def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f: 
        json.dump(data, f, ensure_ascii=False, indent=2)

# تحميل البيانات عند بدء التشغيل
users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)

# تأمين حساب المدير الافتراضي (Abdallah)
if not any(u['username'] == "Abdallah" for u in users):
    users.append({
        "username": "Abdallah", 
        "password": "772001", 
        "role": "admin", 
        "lat": 30.0444, "lon": 31.2357 # إحداثيات افتراضية (القاهرة)
    })
    save_data(USERS_FILE, users)

# ================== 2. نظام التحقق من الهوية ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life - تسجيل الدخول")
    col_l, _ = st.columns([1, 1])
    with col_l:
        u_in = st.text_input("اسم المستخدم")
        p_in = st.text_input("كلمة المرور", type="password")
        if st.button("دخول للنظام"):
            user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
            if user:
                st.session_state.logged_in = True
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("❌ بيانات الدخول غير صحيحة")

else:
    user_now = st.session_state.current_user
    
    # ================== 3. القائمة الجانبية (Sidebar) ==================
    st.sidebar.title("💧 Power Life")
    st.sidebar.markdown(f"**المستخدم:** `{user_now['username']}`")
    st.sidebar.markdown(f"**الرتبة:** `{user_now['role']}`")
    
    # تحديد الخيارات بناءً على الصلاحيات
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "🔍 بحث", "🗺️ خريطة العملاء"]
    if user_now['role'] == "admin":
        menu.insert(0, "➕ إضافة عميل جديد")
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    
    menu.append("🚪 تسجيل الخروج")
    choice = st.sidebar.radio("انتقل إلى:", menu)

    # تحديث موقع الفني الحالي (للتتبع)
    with st.sidebar.expander("📍 تحديث موقعي (GPS)"):
        c_lat = st.number_input("خط العرض (Lat)", value=float(user_now.get('lat', 0)), format="%.6f")
        c_lon = st.number_input("خط الطول (Lon)", value=float(user_now.get('lon', 0)), format="%.6f")
        if st.button("تحديث موقعي الآن"):
            for u in users:
                if u['username'] == user_now['username']:
                    u['lat'], u['lon'] = c_lat, c_lon
            save_data(USERS_FILE, users)
            st.success("✅ تم تحديث موقعك بنجاح")

    # ================== 4. الوظائف الرئيسية ==================

    # --- أ: إضافة عميل جديد (للمدير فقط) ---
    if choice == "➕ إضافة عميل جديد":
        st.subheader("➕ تسجيل عميل جديد في النظام")
        with st.form("new_customer_form"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("اسم العميل بالكامل")
                phone = st.text_input("رقم الهاتف")
                cat = st.selectbox("نوع المنشأة", ["منزل", "شركة", "محل", "مدرسة"])
            with c2:
                loc = st.text_input("الإحداثيات (مثال: 30.1,31.2)")
                notes = st.text_input("ملاحظات عامة")
            
            if st.form_submit_button("حفظ بيانات العميل"):
                if name and phone:
                    customers.append({
                        "id": len(customers) + 1,
                        "name": name, "phone": phone, "location": loc,
                        "category": cat, "notes": notes, "history": []
                    })
                    save_data(CUSTOMERS_FILE, customers)
                    st.success(f"✅ تم حفظ العميل {name}")
                else: st.warning("⚠️ يرجى إدخال الاسم والهاتف")

    # --- ب: إضافة صيانة (الميزة المطلوبة للفنيين) ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل عملية صيانة جديدة")
        if not customers: st.info("لا يوجد عملاء مضافين")
        else:
            selected_c = st.selectbox("اختر العميل من القائمة", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            
            # عرض تاريخ العميل
            with st.expander("📜 تاريخ الصيانات السابقة لهذا العميل"):
                if selected_c.get('history'):
                    st.table(pd.DataFrame(selected_c['history']))
                else: st.write("لا يوجد سجل صيانات سابق.")

            # نموذج الصيانة
            with st.form("service_form"):
                st.write("📝 تفاصيل الزيارة الحالية")
                col1, col2 = st.columns(2)
                with col1:
                    work = st.multiselect("ما تم تغييره (الشمعات)", ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "موتور", "خزان", "كربون"])
                    other = st.text_input("إضافات أخرى")
                with col2:
                    cost = st.number_input("المبلغ المدفوع (جنيه)", min_value=0)
                
                if st.form_submit_button("إرسال التقرير باسمي"):
                    work_done = ", ".join(work) + (f" - {other}" if other else "")
                    new_entry = {
                        "التاريخ": datetime.today().strftime('%Y-%m-%d'),
                        "الفني": user_now['username'],
                        "العمل": work_done,
                        "التكلفة": cost
                    }
                    # إضافة الصيانة لسجل العميل
                    for c in customers:
                        if c['id'] == selected_c['id']:
                            if 'history' not in c: c['history'] = []
                            c['history'].append(new_entry)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success(f"✅ تم تسجيل الصيانة بنجاح بواسطة {user_now['username']}")

    # --- ج: قائمة العملاء التفصيلية (طلبك الأخير) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 تقرير الصيانات والتحصيل المالي")
        if customers:
            full_report = []
            for c in customers:
                if c.get('history'):
                    for h in c['history']:
                        full_report.append({
                            "اسم العميل": c['name'], "الهاتف": c['phone'],
                            "التاريخ": h['التاريخ'], "الفني": h['الفني'],
                            "الشمع المغير": h['العمل'], "المبلغ": h['التكلفة']
                        })
                else:
                    full_report.append({
                        "اسم العميل": c['name'], "الهاتف": c['phone'],
                        "التاريخ": "لا يوجد", "الفني": "---", "الشمع المغير": "---", "المبلغ": 0
                    })
            
            df = pd.DataFrame(full_report)
            
            # إحصائيات للمدير
            if user_now['role'] == "admin":
                st.metric("إجمالي دخل الشركة", f"{df['المبلغ'].sum()} جنيه")
            
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 تحميل التقرير (Excel)", df.to_csv(index=False).encode('utf-8-sig'), "power_life_report.csv")
        else: st.info("لا يوجد بيانات")

    # --- د: تتبع الفنيين (للمدير فقط) ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 خريطة تواجد الفنيين الآن")
        tech_list = [u for u in users if u['role'] == 'technician']
        if tech_list:
            df_techs = pd.DataFrame(tech_list)[['username', 'lat', 'lon']]
            st.map(df_techs)
            st.table(df_techs)
        else: st.info("لا يوجد فنيين مسجلين حالياً")

    # --- هـ: خريطة العملاء (للجميع) ---
    elif choice == "🗺️ خريطة العملاء":
        st.subheader("🗺️ مواقع العملاء")
        map_c = []
        for c in customers:
            try:
                lat, lon = map(float, c['location'].split(','))
                map_c.append({"lat": lat, "lon": lon, "name": c['name']})
            except: pass
        if map_c: st.map(pd.DataFrame(map_c))
        else: st.warning("لا توجد إحداثيات متاحة")

    # --- و: إضافة فني جديد (للمدير فقط) ---
    elif choice == "👤 إضافة فني جديد":
        st.subheader("👤 إنشاء حساب جديد لفني")
        with st.form("add_tech_form"):
            new_u = st.text_input("اسم المستخدم للفني")
            new_p = st.text_input("كلمة المرور")
            if st.form_submit_button("إنشاء الحساب"):
                users.append({"username": new_u, "password": new_p, "role": "technician", "lat": 0, "lon": 0})
                save_data(USERS_FILE, users)
                st.success("✅ تم إنشاء حساب الفني")

    # --- ز: بحث ---
    elif choice == "🔍 بحث":
        st.subheader("🔍 البحث عن عميل")
        term = st.text_input("ادخل الاسم أو رقم الهاتف")
        if term:
            results = [c for c in customers if term in c['name'] or term in c['phone']]
            if results: st.dataframe(pd.DataFrame(results).drop(columns=['history'], errors='ignore'))
            else: st.error("لم يتم العثور على نتائج")

    # --- ح: تسجيل الخروج ---
    elif choice == "🚪 تسجيل الخروج":
        st.session_state.logged_in = False
        st.rerun()
