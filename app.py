import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

# تنسيق CSS لضمان وضوح الجداول وحل مشكلة الخلفية السوداء/البيضاء
st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; font-size: 16px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 12px; text-align: right; }
    .report-table th { background-color: #007bff; color: white; font-weight: bold; }
    .warning-row { background-color: #ffcccc !important; color: black !important; }
    .stTable { background-color: white !important; }
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

if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== 2. تسجيل الدخول ==================
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life - دخول")
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
    st.sidebar.write(f"المستخدم: **{user_now['username']}**")
    
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "➕ إضافة عميل", "🔍 بحث وتعديل", "📊 أرباح الشركة"]
    if user_now['role'] == "admin":
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- 1. قائمة العملاء (بدون الخطأ الأحمر) ---
    if choice == "📋 قائمة العملاء":
        st.subheader("📋 سجل العملاء والصيانات")
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
            
            table_html = f"<table class='report-table'><thead><tr><th>العميل</th><th>الهاتف</th><th>التاريخ</th><th>الفني</th><th>العمل</th><th>المبلغ</th></tr></thead><tbody>{rows}</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)
        else: st.info("لا توجد بيانات")

    # --- 2. إضافة صيانة ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة جديدة")
        if customers:
            sel_c = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']}")
            with st.form("serv_form"):
                work = st.multiselect("القطع المبدلة", ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "موتور"])
                price = st.number_input("المبلغ المدفوع", min_value=0)
                if st.form_submit_button("حفظ"):
                    visit = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": price}
                    for cust in customers:
                        if cust['id'] == sel_c['id']:
                            if 'history' not in cust: cust['history'] = []
                            cust['history'].append(visit)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("✅ تم الحفظ")
        else: st.warning("يجب إضافة عملاء أولاً")

    # --- 3. أرباح الشركة (حل مشكلة الصورة 3 و 5) ---
    elif choice == "📊 أرباح الشركة":
        st.subheader("📊 إحصائيات الدخل المالي")
        income_list = []
        for c in customers:
            for h in c.get('history', []):
                income_list.append({"التاريخ": h['التاريخ'], "المبلغ": h['التكلفة']})
        
        if income_list:
            df = pd.DataFrame(income_list)
            st.info(f"💰 إجمالي الإيرادات: {df['المبلغ'].sum()} جنيه")
            # عرض جدول مجمع بالتواريخ بدلاً من الرسم البياني لتجنب الخطأ
            summary = df.groupby("التاريخ")["المبلغ"].sum().reset_index()
            sum_rows = "".join([f"<tr><td>{r['التاريخ']}</td><td>{r['المبلغ']}</td></tr>" for _, r in summary.iterrows()])
            st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>إجمالي دخل اليوم</th></tr></thead><tbody>{sum_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا توجد عمليات مالية مسجلة")

    # --- 4. تتبع الفنيين (حل مشكلة الصورة 7) ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 آخر مواقع الفنيين")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            t_rows = "".join([f"<tr><td>{u['username']}</td><td>{u.get('lat','-')}</td><td>{u.get('lon','-')}</td></tr>" for u in techs])
            st.markdown(f"<table class='report-table'><thead><tr><th>الفني</th><th>خط العرض (Lat)</th><th>خط الطول (Lon)</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا يوجد فنيين مسجلين")

    # --- بقية العناصر (إضافة عميل، بحث) ---
    elif choice == "➕ إضافة عميل":
        with st.form("add_c"):
            n = st.text_input("الاسم")
            p = st.text_input("الهاتف")
            l = st.text_input("الإحداثيات (30.1, 31.2)")
            if st.form_submit_button("حفظ"):
                customers.append({"id": len(customers)+1, "name": n, "phone": p, "location": l, "history": [], "created_at": str(datetime.now().date())})
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
