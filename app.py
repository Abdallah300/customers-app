import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd

# ================== 1. إعدادات النظام وتنسيق الجدول ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

# تنسيق CSS لضمان ظهور الجداول بوضوح على الكمبيوتر وحل مشكلة الخلفية
st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white; color: black; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; }
    .report-table th { background-color: #007bff; color: white; }
    .warning-row { background-color: #ffcccc !important; } /* لون أحمر للتنبيه */
    </style>
    """, unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
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

# ================== 3. تسجيل الدخول ==================
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
        else: st.error("بيانات خاطئة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "➕ إضافة عميل", "🔍 بحث وتعديل", "📊 إحصائيات الدخل", "🗺️ خريطة العملاء"]
    if user_now['role'] == "admin":
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- ميزة 1: إضافة عميل جديد ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        with st.form("add_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("اسم العميل")
            phone = c1.text_input("رقم الهاتف")
            loc = c2.text_input("الإحداثيات (lat,lon)")
            cat = c2.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
            if st.form_submit_button("حفظ"):
                customers.append({"id": len(customers)+1, "name": name, "phone": phone, "location": loc, "category": cat, "history": [], "created_at": str(datetime.now().date())})
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ")

    # --- ميزة 2: قائمة العملاء مع تنبيهات الصيانة (تلوين) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 سجل الصيانات وتنبيهات المواعيد")
        if customers:
            rows_html = ""
            all_records = []
            today = datetime.now().date()
            
            for c in customers:
                last_date_str = c['history'][-1]['التاريخ'] if c.get('history') else c.get('created_at', str(today))
                last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
                
                # إذا مر أكثر من 90 يوم (3 شهور) نلون السطر بالأحمر
                is_due = (today - last_date).days > 90
                row_class = "warning-row" if is_due else ""
                
                if c.get('history'):
                    for h in c['history']:
                        rows_html += f"<tr class='{row_class}'><td>{c['name']}</td><td>{c['phone']}</td><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>"
                        all_records.append(h['التكلفة'])
                else:
                    rows_html += f"<tr class='{row_class}'><td>{c['name']}</td><td>{c['phone']}</td><td>لا يوجد</td><td>-</td><td>-</td><td>0</td></tr>"

            table_html = f"""
            <table class='report-table'>
                <thead><tr><th>العميل</th><th>الهاتف</th><th>التاريخ</th><th>الفني</th><th>الشمع</th><th>المبلغ</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            """
            st.markdown(table_html, unsafe_allow_html=True)
            if is_due: st.warning("⚠️ الصفوف الحمراء تعني عملاء لم يتم عمل صيانة لهم منذ أكثر من 3 أشهر.")
        else: st.info("لا توجد بيانات")

    # --- ميزة 3: إضافة صيانة + توليد فاتورة ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة جديدة")
        target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']}")
        with st.form("serv"):
            work = st.multiselect("الشمع المغير", ["1", "2", "3", "M", "S", "موتور"])
            cost = st.number_input("المبلغ", min_value=0)
            if st.form_submit_button("حفظ"):
                new_h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": cost}
                for cust in customers:
                    if cust['id'] == target['id']:
                        if 'history' not in cust: cust['history'] = []
                        cust['history'].append(new_h)
                save_data(CUSTOMERS_FILE, customers)
                st.success("تم الحفظ!")
                # فاتورة جاهزة للنسخ
                st.code(f"فاتورة صيانة Power Life\nالعميل: {target['name']}\nالتاريخ: {new_h['التاريخ']}\nالأعمال: {new_h['العمل']}\nالمبلغ: {cost} ج.م\nالفني: {user_now['username']}", language="text")

    # --- ميزة 4: إحصائيات الدخل (رسوم بيانية) ---
    elif choice == "📊 إحصائيات الدخل":
        st.subheader("📈 تحليل أرباح الشركة")
        income_data = []
        for c in customers:
            for h in c.get('history', []):
                income_data.append({"date": h['التاريخ'], "amount": h['التكلفة']})
        
        if income_data:
            df_inc = pd.DataFrame(income_data)
            df_inc['date'] = pd.to_datetime(df_inc['date'])
            daily_income = df_inc.groupby('date')['amount'].sum()
            st.line_chart(daily_income)
            st.metric("إجمالي الدخل الكلي", f"{df_inc['amount'].sum()} جنيه")
        else: st.info("لا توجد بيانات مالية بعد")

    # --- ميزة 5: بحث وتعديل وحذف ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 البحث عن عميل أو تعديل بياناته")
        term = st.text_input("اسم العميل أو هاتفه")
        if term:
            found = [c for c in customers if term in c['name'] or term in c['phone']]
            if found:
                sel = st.selectbox("نتائج البحث (اختر للتعديل)", found, format_func=lambda x: x['name'])
                new_n = st.text_input("تعديل الاسم", value=sel['name'])
                new_p = st.text_input("تعديل الهاتف", value=sel['phone'])
                if st.button("تحديث البيانات"):
                    sel['name'], sel['phone'] = new_n, new_p
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم التحديث")
                if st.button("❌ حذف هذا العميل نهائياً"):
                    customers.remove(sel)
                    save_data(CUSTOMERS_FILE, customers)
                    st.rerun()

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
