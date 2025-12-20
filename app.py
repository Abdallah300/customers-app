import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات الصفحة والتوافقية ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

# كود CSS لضمان ظهور الجداول بوضوح على الكمبيوتر وحل مشكلة الخلفية والخط
st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; }
    .report-table th { background-color: #007bff; color: white; font-weight: bold; }
    .warning-row { background-color: #ffcccc !important; color: black !important; } /* لون أحمر للتنبيه */
    .stTable { background-color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# ================== 2. إدارة ملفات البيانات ==================
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

# تأمين حساب المدير (Abdallah)
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== 3. نظام تسجيل الدخول ==================
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life - دخول النظام")
    u_in = st.text_input("اسم المستخدم")
    p_in = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else: st.error("⚠️ بيانات الدخول غير صحيحة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    st.sidebar.write(f"مرحباً: **{user_now['username']}**")
    
    # القائمة البرمجية
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "➕ إضافة عميل", "🔍 بحث وتعديل", "📊 أرباح الشركة", "🗺️ خريطة العملاء"]
    if user_now['role'] == "admin":
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    menu.append("🚪 تسجيل الخروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- تحديث الموقع للجهاز الحالي ---
    with st.sidebar.expander("📍 تحديث موقعي الحالي"):
        lat_v = st.number_input("Lat", value=float(user_now.get('lat', 0)), format="%.6f")
        lon_v = st.number_input("Lon", value=float(user_now.get('lon', 0)), format="%.6f")
        if st.button("تحديث إحداثياتي"):
            for u in users:
                if u['username'] == user_now['username']: u['lat'], u['lon'] = lat_v, lon_v
            save_data(USERS_FILE, users)
            st.success("تم التحديث")

    # ================== 4. تنفيذ العمليات ==================

    # --- إضافة عميل جديد ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل بيانات عميل جديد")
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم العميل")
            phone = c1.text_input("رقم الهاتف")
            loc = c2.text_input("الإحداثيات (lat,lon)")
            cat = c2.selectbox("الفئة", ["منزل", "شركة", "مدرسة", "جامع"])
            if st.form_submit_button("حفظ العميل"):
                if name and phone:
                    customers.append({
                        "id": len(customers)+1, "name": name, "phone": phone, 
                        "location": loc, "category": cat, "history": [],
                        "created_at": str(datetime.now().date())
                    })
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("✅ تم حفظ العميل بنجاح")
                else: st.error("يرجى إدخال الاسم والهاتف")

    # --- قائمة العملاء (نسخة الاستقرار HTML) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 سجل الصيانات وتنبيهات المواعيد")
        if customers:
            rows_html = ""
            today = datetime.now().date()
            report_data = []

            for c in customers:
                # حساب تاريخ التنبيه (أكثر من 90 يوم)
                last_v = c['history'][-1]['التاريخ'] if c.get('history') else c.get('created_at', str(today))
                is_late = (today - datetime.strptime(last_v, '%Y-%m-%d').date()).days > 90
                row_style = "warning-row" if is_late else ""

                if c.get('history'):
                    for h in c['history']:
                        rows_html += f"<tr class='{row_style}'><td>{c['name']}</td><td>{c['phone']}</td><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>"
                        report_data.append(h)
                else:
                    rows_html += f"<tr class='{row_style}'><td>{c['name']}</td><td>{c['phone']}</td><td>لا يوجد</td><td>-</td><td>-</td><td>0</td></tr>"

            full_table = f"<table class='report-table'><thead><tr><th>العميل</th><th>الهاتف</th><th>تاريخ الصيانة</th><th>الفني</th><th>العمل</th><th>المبلغ</th></tr></thead><tbody>{rows_html}</tbody></table>"
            st.markdown(full_table, unsafe_allow_html=True)
            
            if report_data:
                df_exp = pd.DataFrame(report_data)
                st.download_button("📥 تحميل التقرير Excel", df_exp.to_csv(index=False).encode('utf-8-sig'), "power_life.csv")
        else: st.info("لا توجد بيانات مسجلة")

    # --- إضافة صيانة وفاتورة واتساب ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة جديدة")
        if not customers: st.warning("لا يوجد عملاء")
        else:
            sel_c = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            with st.form("serv_form"):
                work = st.multiselect("الشمع/القطع المبدلة", ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "موتور", "خزان", "كربون"])
                price = st.number_input("المبلغ المدفوع", min_value=0)
                if st.form_submit_button("حفظ وإصدار فاتورة"):
                    visit = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": price}
                    for cust in customers:
                        if cust['id'] == sel_c['id']:
                            if 'history' not in cust: cust['history'] = []
                            cust['history'].append(visit)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("✅ تم الحفظ")
                    # فاتورة للنسخ للواتساب
                    st.code(f"فاتورة Power Life 💧\nالعميل: {sel_c['name']}\nتاريخ الصيانة: {visit['التاريخ']}\nالأعمال: {visit['العمل']}\nالمبلغ: {price} ج.م\nالفني: {user_now['username']}", language="text")

    # --- أرباح الشركة (جداول بسيطة) ---
    elif choice == "📊 أرباح الشركة":
        st.subheader("📊 إحصائيات الدخل")
        all_inc = []
        for c in customers:
            for h in c.get('history', []): all_inc.append({"التاريخ": h['التاريخ'], "المبلغ": h['التكلفة']})
        if all_inc:
            df_i = pd.DataFrame(all_inc)
            st.metric("إجمالي التحصيل المالي", f"{df_i['المبلغ'].sum()} جنيه")
            st.write("### الدخل حسب التاريخ")
            st.table(df_i.groupby("التاريخ").sum())
        else: st.info("لا توجد أرباح مسجلة بعد")

    # --- بحث وتعديل وحذف ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 البحث عن عميل وإدارة بياناته")
        s_term = st.text_input("ادخل اسم العميل أو رقمه")
        if s_term:
            res = [c for c in customers if s_term in c['name'] or s_term in c['phone']]
            if res:
                item = st.selectbox("اختر عميل للتعديل", res, format_func=lambda x: x['name'])
                new_name = st.text_input("تعديل الاسم", value=item['name'])
                new_phone = st.text_input("تعديل الهاتف", value=item['phone'])
                if st.button("حفظ التعديلات"):
                    item['name'], item['phone'] = new_name, new_phone
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم التعديل")
                if st.button("❌ حذف العميل نهائياً"):
                    customers.remove(item)
                    save_data(CUSTOMERS_FILE, customers)
                    st.rerun()

    # --- تتبع الفنيين (للمدير فقط) ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 آخر مواقع الفنيين")
        tech_users = [u for u in users if u['role'] == 'technician']
        if tech_users:
            df_t = pd.DataFrame(tech_users)[['username', 'lat', 'lon']]
            st.table(df_t)
            st.map(df_t)
        else: st.info("لا يوجد فنيين مسجلين")

    # --- خريطة العملاء ---
    elif choice == "🗺️ خريطة العملاء":
        st.subheader("🗺️ مواقع جميع العملاء")
        m_data = []
        for c in customers:
            try:
                lt, ln = map(float, c['location'].split(','))
                m_data.append({"lat": lt, "lon": ln, "name": c['name']})
            except: pass
        if m_data: st.map(pd.DataFrame(m_data))
        else: st.warning("لا توجد إحداثيات")

    elif choice == "🚪 تسجيل الخروج":
        st.session_state.logged_in = False
        st.rerun()
