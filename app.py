import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

# تنسيق CSS لضمان الوضوح التام وحل مشاكل المتصفح
st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; }
    .report-table th { background-color: #007bff; color: white; }
    .warning-row { background-color: #ffcccc !important; color: black !important; }
    .stButton>button { width: 100%; }
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

# تأمين حساب المدير
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== 2. نظام الدخول ==================
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
        else: st.error("بيانات غير صحيحة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "➕ إضافة عميل", "🔍 بحث وتعديل", "📊 أرباح الشركة", "🗺️ خريطة العملاء"]
    if user_now['role'] == "admin":
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- 1. قائمة العملاء ---
    if choice == "📋 قائمة العملاء":
        st.subheader("📋 سجل الصيانات والعملاء")
        if customers:
            rows = ""
            today = datetime.now().date()
            for c in customers:
                last_v = c['history'][-1]['التاريخ'] if c.get('history') else c.get('created_at', str(today))
                is_late = (today - datetime.strptime(last_v, '%Y-%m-%d').date()).days > 90
                row_style = "warning-row" if is_late else ""
                
                if c.get('history'):
                    for h in c['history']:
                        rows += f"<tr class='{row_style}'><td>{c['name']}</td><td>{c['phone']}</td><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>"
                else:
                    rows += f"<tr class='{row_style}'><td>{c['name']}</td><td>{c['phone']}</td><td>-</td><td>-</td><td>-</td><td>0</td></tr>"
            
            st.markdown(f"<table class='report-table'><thead><tr><th>العميل</th><th>الهاتف</th><th>التاريخ</th><th>الفني</th><th>العمل</th><th>المبلغ</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا توجد بيانات")

    # --- 2. إضافة فني جديد (تم الإصلاح) ---
    elif choice == "👤 إضافة فني جديد":
        st.subheader("👤 إنشاء حساب فني جديد")
        with st.form("add_tech_form"):
            new_u = st.text_input("اسم المستخدم للفني")
            new_p = st.text_input("كلمة المرور")
            if st.form_submit_button("إنشاء الحساب"):
                if new_u and new_p:
                    users.append({"username": new_u, "password": new_p, "role": "technician", "lat": 0, "lon": 0})
                    save_data(USERS_FILE, users)
                    st.success(f"✅ تم إضافة الفني {new_u} بنجاح")
                else: st.error("يرجى ملء كافة الخانات")

    # --- 3. بحث وتعديل (تم الإصلاح) ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 البحث عن عميل وتعديله")
        search_term = st.text_input("ابحث بالاسم أو رقم الهاتف")
        if search_term:
            found = [c for c in customers if search_term in c['name'] or search_term in c['phone']]
            if found:
                for c in found:
                    with st.expander(f"تعديل بيانات العميل: {c['name']}"):
                        u_name = st.text_input("الاسم", value=c['name'], key=f"n_{c['id']}")
                        u_phone = st.text_input("الهاتف", value=c['phone'], key=f"p_{c['id']}")
                        u_loc = st.text_input("الإحداثيات", value=c.get('location', ''), key=f"l_{c['id']}")
                        if st.button("حفظ التعديلات", key=f"b_{c['id']}"):
                            c['name'], c['phone'], c['location'] = u_name, u_phone, u_loc
                            save_data(CUSTOMERS_FILE, customers)
                            st.success("تم التعديل")
                            st.rerun()
                        if st.button("❌ حذف العميل", key=f"d_{c['id']}"):
                            customers.remove(c)
                            save_data(CUSTOMERS_FILE, customers)
                            st.rerun()
            else: st.warning("لا توجد نتائج")

    # --- 4. تتبع الفنيين والعملاء بالخرائط ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 مواقع الفنيين على الخريطة")
        t_list = [u for u in users if u['role'] == 'technician']
        if t_list:
            df_t = pd.DataFrame(t_list)[['username', 'lat', 'lon']]
            st.map(df_t) # الخرائط عادة لا تسبب الخطأ الأحمر، إذا سببت الخطأ سنحولها لجدول
            st.table(df_t)
        else: st.info("لا يوجد فنيين مسجلين")

    elif choice == "🗺️ خريطة العملاء":
        st.subheader("🗺️ مواقع العملاء")
        m_data = []
        for c in customers:
            try:
                lt, ln = map(float, c['location'].split(','))
                m_data.append({"lat": lt, "lon": ln, "name": c['name']})
            except: pass
        if m_data: st.map(pd.DataFrame(m_data))
        else: st.warning("لا توجد إحداثيات")

    # --- 5. إضافة صيانة و إضافة عميل و أرباح ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة")
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']}")
            with st.form("serv"):
                work = st.multiselect("القطع", ["1", "2", "3", "M", "S"])
                price = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("حفظ"):
                    h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": price}
                    for cust in customers:
                        if cust['id'] == target['id']:
                            if 'history' not in cust: cust['history'] = []
                            cust['history'].append(h)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم!")

    elif choice == "📊 أرباح الشركة":
        st.subheader("📊 الأرباح")
        all_h = []
        for c in customers:
            for h in c.get('history', []): all_h.append(h)
        if all_h:
            df_a = pd.DataFrame(all_h)
            st.metric("إجمالي الدخل", f"{df_a['التكلفة'].sum()} جنيه")
            st.table(df_a.groupby("التاريخ")["التكلفة"].sum())
        else: st.info("لا بيانات")

    elif choice == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("الاسم")
            p = st.text_input("الهاتف")
            l = st.text_input("الإحداثيات")
            if st.form_submit_button("حفظ"):
                customers.append({"id": len(customers)+1, "name": n, "phone": p, "location": l, "history": [], "created_at": str(datetime.now().date())})
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()           
