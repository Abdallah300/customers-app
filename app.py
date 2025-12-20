import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

# تنسيق CSS لضمان الوضوح التام ومنع الأخطاء البصرية
st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; }
    .report-table th { background-color: #007bff; color: white; }
    .warning-row { background-color: #ffcccc !important; color: black !important; }
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

# تأمين حساب المدير الافتراضي
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== 2. تسجيل الدخول ==================
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
        else: st.error("❌ بيانات الدخول خاطئة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "➕ إضافة عميل", "🔍 بحث وتعديل", "📊 أرباح الشركة", "🗺️ خريطة العملاء"]
    if user_now['role'] == "admin":
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- إضافة فني جديد ---
    if choice == "👤 إضافة فني جديد":
        st.subheader("👤 إضافة فني جديد للنظام")
        with st.form("tech_f"):
            t_user = st.text_input("اسم المستخدم للفني")
            t_pass = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة"):
                if t_user and t_pass:
                    users.append({"username": t_user, "password": t_pass, "role": "technician", "lat": 0, "lon": 0})
                    save_data(USERS_FILE, users)
                    st.success(f"تم إضافة الفني {t_user}")
                else: st.error("أكمل البيانات")

    # --- بحث وتعديل ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 البحث عن عميل وإدارة بياناته")
        s_text = st.text_input("ابحث بالاسم أو الهاتف")
        if s_text:
            res = [c for c in customers if s_text in c['name'] or s_text in c['phone']]
            if res:
                for c in res:
                    with st.expander(f"📝 تعديل: {c['name']}"):
                        c['name'] = st.text_input("الاسم", value=c['name'], key=f"n{c['id']}")
                        c['phone'] = st.text_input("الهاتف", value=c['phone'], key=f"p{c['id']}")
                        c['location'] = st.text_input("الإحداثيات", value=c.get('location', ''), key=f"l{c['id']}")
                        if st.button("حفظ التغييرات", key=f"s{c['id']}"):
                            save_data(CUSTOMERS_FILE, customers)
                            st.success("تم التعديل")
                            st.rerun()
                        if st.button("❌ حذف نهائي", key=f"d{c['id']}"):
                            customers.remove(c)
                            save_data(CUSTOMERS_FILE, customers)
                            st.rerun()
            else: st.warning("لا توجد نتائج")

    # --- تتبع الفنيين (خريطة وجدول) ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 أماكن الفنيين الحالية")
        tech_list = [u for u in users if u['role'] == 'technician']
        if tech_list:
            df_t = pd.DataFrame(tech_list)[['username', 'lat', 'lon']]
            st.map(df_t)
            st.table(df_t)
        else: st.info("لا يوجد فنيين حالياً")

    # --- خريطة العملاء ---
    elif choice == "🗺️ خريطة العملاء":
        st.subheader("🗺️ مواقع جميع العملاء")
        m_pts = []
        for c in customers:
            try:
                lt, ln = map(float, c['location'].split(','))
                m_pts.append({"lat": lt, "lon": ln, "name": c['name']})
            except: pass
        if m_pts: st.map(pd.DataFrame(m_pts))
        else: st.info("لا توجد إحداثيات")

    # --- قائمة العملاء ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 تقرير العملاء")
        if customers:
            r_h = ""
            today = datetime.now().date()
            for c in customers:
                last_v = c['history'][-1]['التاريخ'] if c.get('history') else c.get('created_at', str(today))
                is_late = (today - datetime.strptime(last_v, '%Y-%m-%d').date()).days > 90
                style = "warning-row" if is_late else ""
                if c.get('history'):
                    for h in c['history']:
                        r_h += f"<tr class='{style}'><td>{c['name']}</td><td>{c['phone']}</td><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>"
                else:
                    r_h += f"<tr class='{style}'><td>{c['name']}</td><td>{c['phone']}</td><td>-</td><td>-</td><td>-</td><td>0</td></tr>"
            st.markdown(f"<table class='report-table'><thead><tr><th>العميل</th><th>الهاتف</th><th>التاريخ</th><th>الفني</th><th>العمل</th><th>المبلغ</th></tr></thead><tbody>{r_h}</tbody></table>", unsafe_allow_html=True)
        else: st.info("القائمة فارغة")

    # --- إضافة صيانة ---
    elif choice == "🛠️ إضافة صيانة":
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']}")
            with st.form("s_f"):
                parts = st.multiselect("القطع", ["1", "2", "3", "M", "S"])
                amt = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("حفظ الصيانة"):
                    new_h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(parts), "التكلفة": amt}
                    for cust in customers:
                        if cust['id'] == target['id']:
                            if 'history' not in cust: cust['history'] = []
                            cust['history'].append(new_h)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم!")
                    st.code(f"صيانة Power Life\nالعميل: {target['name']}\nالتاريخ: {new_h['التاريخ']}\nالمبلغ: {amt}")
        else: st.warning("أضف عملاء أولاً")

    # --- إضافة عميل ---
    elif choice == "➕ إضافة عميل":
        with st.form("c_f"):
            n = st.text_input("اسم العميل")
            p = st.text_input("رقم الهاتف")
            l = st.text_input("الإحداثيات (مثال: 30.1,31.2)")
            if st.form_submit_button("حفظ"):
                customers.append({"id": len(customers)+1, "name": n, "phone": p, "location": l, "history": [], "created_at": str(datetime.now().date())})
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم!")

    # --- أرباح الشركة ---
    elif choice == "📊 أرباح الشركة":
        st.subheader("📊 تقرير الأرباح")
        all_rev = []
        for c in customers:
            for h in c.get('history', []): all_rev.append(h)
        if all_rev:
            df_r = pd.DataFrame(all_rev)
            st.metric("الإجمالي", f"{df_r['التكلفة'].sum()} جنيه")
            st.table(df_r.groupby("التاريخ")["التكلفة"].sum())
        else: st.info("لا بيانات مالية")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
