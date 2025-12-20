import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================
st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; }
    .report-table th { background-color: #28a745; color: white; }
    .warning-row { background-color: #ffcccc !important; color: black !important; }
    .qr-box { border: 2px dashed #28a745; padding: 15px; text-align: center; background: #f0fff0; border-radius: 10px; }
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
    st.title("💧 Power Life Ultra - دخول")
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
    
    menu = ["📋 قائمة العملاء", "➕ إضافة عميل", "🛠️ إضافة صيانة", "🔍 بحث وتعديل", "💰 أرباح الشركة"]
    if user_now['role'] == "admin":
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- 1. إضافة عميل (بالمميزات الجديدة والباركود) ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد - بيانات تفصيلية")
        with st.form("new_c_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم الهاتف")
                gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
                center = st.text_input("المركز")
            with col2:
                village = st.text_input("البلد/القرية")
                ctype = st.selectbox("نوع الجهاز/العميل", ["جهاز جديد", "جهاز قديم", "عميل شركة"])
                loc = st.text_input("الإحداثيات (30.1, 31.2)")
            
            if st.form_submit_button("حفظ العميل وإصدار الباركود"):
                new_id = len(customers) + 1
                c_data = {
                    "id": new_id, "name": name, "phone": phone, "gov": gov,
                    "center": center, "village": village, "type": ctype,
                    "location": loc, "history": [], "created_at": str(datetime.now().date())
                }
                customers.append(c_data)
                save_data(CUSTOMERS_FILE, customers)
                st.success(f"✅ تم الحفظ بنجاح للعميل رقم: {new_id}")
                
                # عرض باركود رقمي بسيط (QR Code Link)
                st.markdown(f"""
                <div class='qr-box'>
                    <h4>🤳 باركود العميل: {name}</h4>
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=CLIENT_ID_{new_id}">
                    <p>كود العميل الرقمي: PL-{new_id}</p>
                </div>
                """, unsafe_allow_html=True)

    # --- 2. قائمة العملاء (تقرير شامل) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 تقرير سجل الصيانات")
        if customers:
            rows = ""
            for c in customers:
                if c.get('history'):
                    for h in c['history']:
                        rows += f"<tr><td>{c['name']}</td><td>{c['gov']}</td><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>"
                else:
                    rows += f"<tr><td>{c['name']}</td><td>{c['gov']}</td><td>لا يوجد</td><td>-</td><td>-</td><td>0</td></tr>"
            
            st.markdown(f"<table class='report-table'><thead><tr><th>العميل</th><th>المحافظة</th><th>التاريخ</th><th>الفني</th><th>الشمع</th><th>المبلغ</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا توجد بيانات")

    # --- 3. بحث وتعديل (عرض رصيد الحساب وسجل الشمع) ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 كشف حساب العميل")
        search = st.text_input("ابحث بالاسم أو الهاتف")
        if search:
            results = [c for c in customers if search in c['name'] or search in c['phone']]
            for c in results:
                with st.expander(f"👤 ملف: {c['name']} - {c['type']}"):
                    st.write(f"**العنوان:** {c['gov']} - {c['center']} - {c['village']}")
                    total_paid = sum(h['التكلفة'] for h in c.get('history', []))
                    st.success(f"💰 إجمالي رصيد المدفوعات: {total_paid} جنيه")
                    
                    if c.get('history'):
                        h_rows = "".join([f"<tr><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>" for h in c['history']])
                        st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>الفني</th><th>العمل (الشمع)</th><th>المبلغ</th></tr></thead><tbody>{h_rows}</tbody></table>", unsafe_allow_html=True)
                    
                    if st.button("حذف العميل", key=f"del_{c['id']}"):
                        customers.remove(c)
                        save_data(CUSTOMERS_FILE, customers)
                        st.rerun()

    # --- 4. تتبع الفنيين (بدون خريطة لمنع الخطأ الأحمر) ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 مواقع الفنيين الحالية")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            t_rows = ""
            for u in techs:
                link = f"https://www.google.com/maps?q={u.get('lat',0)},{u.get('lon',0)}"
                t_rows += f"<tr><td>{u['username']}</td><td>{u.get('lat','-')}</td><td>{u.get('lon','-')}</td><td><a href='{link}' target='_blank'>فتح الخريطة 📍</a></td></tr>"
            st.markdown(f"<table class='report-table'><thead><tr><th>الفني</th><th>Lat</th><th>Lon</th><th>الموقع مباشر</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا يوجد فنيين مسجلين")

    # --- 5. أرباح الشركة (جداول HTML) ---
    elif choice == "💰 أرباح الشركة":
        st.subheader("📊 تقرير الدخل المالي")
        all_income = []
        for c in customers:
            for h in c.get('history', []): all_income.append(h)
        
        if all_income:
            df = pd.DataFrame(all_income)
            st.info(f"إجمالي خزينة الشركة: {df['التكلفة'].sum()} جنيه")
            summary = df.groupby("التاريخ")["التكلفة"].sum().reset_index()
            s_rows = "".join([f"<tr><td>{r['التاريخ']}</td><td>{r['التكلفة']}</td></tr>" for _, r in summary.iterrows()])
            st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>إجمالي الدخل</th></tr></thead><tbody>{s_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا توجد بيانات مالية")

    # --- بقية الوظائف ---
    elif choice == "🛠️ إضافة صيانة":
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']}")
            with st.form("s_form"):
                work = st.multiselect("الشمع المغير", ["1", "2", "3", "M", "S", "كربون", "موتور"])
                price = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("حفظ"):
                    h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": price}
                    for cust in customers:
                        if cust['id'] == target['id']: cust['history'].append(h)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم!")

    elif choice == "👤 إضافة فني جديد":
        with st.form("add_t"):
            nu = st.text_input("اسم الفني")
            np = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة"):
                users.append({"username": nu, "password": np, "role": "technician", "lat": 0, "lon": 0})
                save_data(USERS_FILE, users)
                st.success("تم")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
