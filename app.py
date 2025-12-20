import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

# تنسيق CSS لضمان عدم ظهور أخطاء المتصفح ووضوح الجداول
st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 12px; text-align: right; }
    .report-table th { background-color: #007bff; color: white; }
    .qr-style { 
        background-color: #f8f9fa; border: 2px dashed #28a745; padding: 20px; 
        text-align: center; border-radius: 15px; color: #28a745; font-size: 24px; font-weight: bold;
    }
    .income-box { background-color: #e9f7ef; padding: 15px; border-radius: 10px; border: 1px solid #28a745; color: #155724; font-size: 20px; margin-bottom: 15px; }
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

if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== 2. نظام تسجيل الدخول ==================
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
        else: st.error("⚠️ بيانات الدخول خاطئة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    
    menu = ["📋 قائمة العملاء", "➕ إضافة عميل", "🛠️ إضافة صيانة", "🔍 بحث وتعديل", "💰 أرباح الشركة"]
    if user_now['role'] == "admin":
        menu.append("👷 تتبع الفنيين")
        menu.append("👤 إضافة فني جديد")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة الرئيسية", menu)

    # --- 1. إضافة عميل (حل مشكلة الباركود) ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        with st.form("add_client"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم الهاتف")
                gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
            with c2:
                center = st.text_input("المركز")
                village = st.text_input("القرية / البلد")
                ctype = st.selectbox("نوع الجهاز", ["جهاز جديد", "جهاز قديم", "شركة"])
            
            if st.form_submit_button("حفظ البيانات وإصدار الكود"):
                new_id = len(customers) + 1
                c_data = {
                    "id": new_id, "name": name, "phone": phone, "gov": gov,
                    "center": center, "village": village, "type": ctype,
                    "history": [], "date": str(datetime.now().date())
                }
                customers.append(c_data)
                save_data(CUSTOMERS_FILE, customers)
                st.success("✅ تم حفظ العميل!")
                
                # عرض الكود الرقمي البديل للباركود لضمان ظهوره
                st.markdown(f"""
                <div class="qr-style">
                    <p>كود التعريف الرقمي للعميل (الباركود)</p>
                    <h1>PL-{new_id:04d}</h1>
                    <p>العميل: {name}</p>
                </div>
                """, unsafe_allow_html=True)

    # --- 2. أرباح الشركة (حل مشكلة عدم الظهور) ---
    elif choice == "💰 أرباح الشركة":
        st.subheader("💰 سجل الأرباح والتحصيل")
        total_income = 0
        income_rows = ""
        # تجميع البيانات يدوياً لضمان عدم ظهور الرسالة الحمراء
        daily_stats = {}
        for c in customers:
            for h in c.get('history', []):
                price = int(h['التكلفة'])
                total_income += price
                date = h['التاريخ']
                daily_stats[date] = daily_stats.get(date, 0) + price
        
        if daily_stats:
            st.markdown(f"<div class='income-box'>إجمالي تحصيل الخزنة: {total_income} جنيه</div>", unsafe_allow_html=True)
            for d, p in daily_stats.items():
                income_rows += f"<tr><td>{d}</td><td>{p} جنيه</td></tr>"
            
            st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>دخل اليوم</th></tr></thead><tbody>{income_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا توجد أرباح مسجلة")

    # --- 3. تتبع الفنيين (روابط مباشرة) ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 تتبع مواقع الفنيين")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            t_rows = ""
            for u in techs:
                lat, lon = u.get('lat', 0), u.get('lon', 0)
                map_link = f"https://www.google.com/maps?q={lat},{lon}"
                t_rows += f"<tr><td>{u['username']}</td><td>{lat}</td><td>{lon}</td><td><a href='{map_link}' target='_blank'>📍 فتح الموقع</a></td></tr>"
            st.markdown(f"<table class='report-table'><thead><tr><th>الفني</th><th>Lat</th><th>Lon</th><th>الموقع</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا يوجد فنيين")

    # --- 4. بحث وتعديل ورصيد الحساب ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 كشف حساب عميل")
        s = st.text_input("ابحث بالاسم أو الهاتف")
        if s:
            results = [c for c in customers if s in c['name'] or s in c['phone']]
            for c in results:
                with st.expander(f"👤 ملف: {c['name']} - {c['phone']}"):
                    st.write(f"**العنوان:** {c['gov']} - {c['village']}")
                    total_c = sum(int(h['التكلفة']) for h in c.get('history', []))
                    st.write(f"**إجمالي المدفوعات:** {total_c} جنيه")
                    
                    if c.get('history'):
                        h_rows = "".join([f"<tr><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>" for h in c['history']])
                        st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>الفني</th><th>الشمع</th><th>المبلغ</th></tr></thead><tbody>{h_rows}</tbody></table>", unsafe_allow_html=True)
                    
                    if st.button("حذف العميل", key=f"d_{c['id']}"):
                        customers.remove(c)
                        save_data(CUSTOMERS_FILE, customers)
                        st.rerun()

    # --- بقية الأقسام ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 سجل الصيانات العام")
        rows = ""
        for c in customers:
            for h in c.get('history', []):
                rows += f"<tr><td>{c['name']}</td><td>{c['phone']}</td><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>"
        if rows:
            st.markdown(f"<table class='report-table'><thead><tr><th>العميل</th><th>الهاتف</th><th>التاريخ</th><th>الفني</th><th>العمل</th><th>المبلغ</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)

    elif choice == "🛠️ إضافة صيانة":
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']}")
            with st.form("s_f"):
                work = st.multiselect("الشمع المبدل", ["1", "2", "3", "M", "S", "كربون"])
                price = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("حفظ الصيانة"):
                    h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": price}
                    for cust in customers:
                        if cust['id'] == target['id']: cust['history'].append(h)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم الحفظ")

    elif choice == "👤 إضافة فني جديد":
        with st.form("t_f"):
            u = st.text_input("اسم الفني")
            p = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة"):
                users.append({"username": u, "password": p, "role": "technician", "lat": 0, "lon": 0})
                save_data(USERS_FILE, users)
                st.success("تم!")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
