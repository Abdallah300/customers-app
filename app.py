import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام والتنسيق ==================
st.set_page_config(page_title="Power Life CRM", page_icon="💧", layout="wide")

# تنسيق CSS ثابت يضمن ظهور الجداول بوضوح تام (نص أسود خلفية بيضاء)
st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 12px; text-align: right; }
    .report-table th { background-color: #007bff; color: white; font-weight: bold; }
    .warning-row { background-color: #ffcccc !important; color: black !important; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
    </style>
    """, unsafe_allow_html=True)

# إدارة البيانات
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
        else: st.error("⚠️ بيانات خاطئة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "➕ إضافة عميل", "🔍 بحث وتعديل", "💰 أرباح الشركة"]
    if user_now['role'] == "admin":
        menu.append("📍 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- 1. قائمة العملاء (HTML آمن) ---
    if choice == "📋 قائمة العملاء":
        st.subheader("📋 تقرير العملاء والصيانات")
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

    # --- 2. أرباح الشركة (تم حل مشكلة عدم الظهور) ---
    elif choice == "💰 أرباح الشركة":
        st.subheader("💰 إحصائيات الدخل المالي")
        income_data = []
        total_sum = 0
        for c in customers:
            for h in c.get('history', []):
                income_data.append(h)
                total_sum += h['التكلفة']
        
        if income_data:
            st.write(f"### إجمالي الدخل: {total_sum} جنيه")
            # تحويل البيانات لجدول يدوي لمنع الخطأ
            df = pd.DataFrame(income_data)
            summary = df.groupby("التاريخ")["التكلفة"].sum().reset_index()
            sum_rows = "".join([f"<tr><td>{r['التاريخ']}</td><td>{r['التكلفة']} جنيه</td></tr>" for _, r in summary.iterrows()])
            st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>دخل اليوم</th></tr></thead><tbody>{sum_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا توجد أرباح مسجلة بعد")

    # --- 3. تتبع الفنيين (بدون خريطة لمنع الخطأ الأحمر) ---
    elif choice == "📍 تتبع الفنيين":
        st.subheader("📍 مواقع الفنيين الحالية (بيانات نصية)")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            t_rows = ""
            for u in techs:
                loc = f"https://www.google.com/maps?q={u.get('lat',0)},{u.get('lon',0)}"
                t_rows += f"<tr><td>{u['username']}</td><td>{u.get('lat','-')}</td><td>{u.get('lon','-')}</td><td><a href='{loc}' target='_blank'>فتح الموقع على جوجل</a></td></tr>"
            st.markdown(f"<table class='report-table'><thead><tr><th>الفني</th><th>Lat</th><th>Lon</th><th>رابط الموقع</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا يوجد فنيين مسجلين")

    # --- 4. بحث وتعديل (نظام مبسط) ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 إدارة بيانات العملاء")
        search = st.text_input("ابحث بالاسم أو الرقم")
        if search:
            results = [c for c in customers if search in c['name'] or search in c['phone']]
            if results:
                for c in results:
                    with st.expander(f"📝 تعديل: {c['name']}"):
                        c['name'] = st.text_input("الاسم", value=c['name'], key=f"edit_n_{c['id']}")
                        c['phone'] = st.text_input("الهاتف", value=c['phone'], key=f"edit_p_{c['id']}")
                        if st.button("حفظ التعديل", key=f"btn_s_{c['id']}"):
                            save_data(CUSTOMERS_FILE, customers)
                            st.success("تم التعديل")
                        if st.button("❌ حذف العميل", key=f"btn_d_{c['id']}"):
                            customers.remove(c)
                            save_data(CUSTOMERS_FILE, customers)
                            st.rerun()
            else: st.warning("لا توجد نتائج")

    # --- 5. إضافة فني ---
    elif choice == "👤 إضافة فني جديد":
        st.subheader("👤 إنشاء حساب فني")
        with st.form("add_tech"):
            t_u = st.text_input("اسم المستخدم")
            t_p = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة الفني"):
                users.append({"username": t_u, "password": t_p, "role": "technician", "lat": 0, "lon": 0})
                save_data(USERS_FILE, users)
                st.success("تمت الإضافة")

    # --- إضافة صيانة و عميل ---
    elif choice == "🛠️ إضافة صيانة":
        if customers:
            target = st.selectbox("العميل", customers, format_func=lambda x: x['name'])
            with st.form("s_f"):
                work = st.multiselect("القطع", ["1", "2", "3", "M", "S"])
                amt = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("حفظ"):
                    visit = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": amt}
                    for cust in customers:
                        if cust['id'] == target['id']:
                            if 'history' not in cust: cust['history'] = []
                            cust['history'].append(visit)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم الحفظ!")
        else: st.warning("أضف عميل أولاً")

    elif choice == "➕ إضافة عميل":
        with st.form("c_f"):
            n = st.text_input("الاسم")
            p = st.text_input("الهاتف")
            if st.form_submit_button("حفظ"):
                customers.append({"id": len(customers)+1, "name": n, "phone": p, "history": []})
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم!")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()   
