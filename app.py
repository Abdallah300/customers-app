import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import qrcode
from io import BytesIO

# ================== 1. إعدادات النظام ==================
st.set_page_config(page_title="Power Life Ultra", page_icon="💧", layout="wide")

st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; }
    .report-table th { background-color: #28a745; color: white; }
    .stMetric { border: 1px solid #28a745; padding: 10px; border-radius: 10px; }
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

# تأمين المدير
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin", "lat": 30.0, "lon": 31.0})
    save_data(USERS_FILE, users)

# ================== 2. وظائف إضافية (الباركود) ==================
def generate_qr(data):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ================== 3. نظام الدخول ==================
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life Ultra - دخول")
    u_in = st.text_input("المستخدم")
    p_in = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else: st.error("خطأ في البيانات")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 Power Life")
    
    menu = ["📋 قائمة العملاء", "🛠️ إضافة صيانة", "➕ إضافة عميل", "🔍 بحث وتعديل", "💰 الأرباح"]
    if user_now['role'] == "admin":
        menu.append("📍 تتبع الفنيين")
        menu.append("👤 إضافة فني")
    menu.append("🚪 خروج")
    choice = st.sidebar.radio("القائمة", menu)

    # --- 1. إضافة عميل (المميزات الجديدة) ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد بالتفاصيل")
        with st.form("new_c_form"):
            col1, col2 = st.columns(2)
            with col1:
                n = st.text_input("اسم العميل")
                p = st.text_input("رقم الهاتف")
                gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
            with col2:
                center = st.text_input("المركز")
                village = st.text_input("البلد/القرية")
                ctype = st.selectbox("نوع العميل", ["جهاز جديد", "جهاز قديم", "شركة/منشأة"])
            
            lat_lon = st.text_input("الإحداثيات (اختياري: 30.1, 31.2)")
            
            if st.form_submit_button("حفظ وإصدار الباركود"):
                new_id = len(customers) + 1
                c_data = {
                    "id": new_id, "name": n, "phone": p, "gov": gov, 
                    "center": center, "village": village, "type": ctype,
                    "location": lat_lon, "history": [], "balance": 0
                }
                customers.append(c_data)
                save_data(CUSTOMERS_FILE, customers)
                st.success(f"✅ تم تسجيل {n} بنجاح")
                
                # إظهار الباركود للعميل
                st.write("### 🤳 باركود العميل الخاص")
                qr_img = generate_qr(f"العميل: {n}\nالرقم: {p}\nالحالة: {ctype}\nسجل الصيانات متاح في النظام.")
                st.image(qr_img, caption=f"QR Code - {n}")

    # --- 2. تتبع الفنيين (الخريطة المدمجة) ---
    elif choice == "📍 تتبع الفنيين":
        st.subheader("📍 خريطة تواجد الفنيين الآن")
        tech_data = [u for u in users if u['role'] == 'technician']
        if tech_data:
            df_techs = pd.DataFrame(tech_data)[['username', 'lat', 'lon']]
            # محاولة عرض الخريطة، وإذا فشلت تظهر كجدول
            try:
                st.map(df_techs)
            except:
                st.warning("تعذر تحميل الخريطة التفاعلية، إليك المواقع كبيانات:")
            
            t_rows = "".join([f"<tr><td>{u['username']}</td><td>{u['lat']}</td><td>{u['lon']}</td></tr>" for u in tech_data])
            st.markdown(f"<table class='report-table'><thead><tr><th>الفني</th><th>Lat</th><th>Lon</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا يوجد فنيين مسجلين")

    # --- 3. بحث وتعديل (صفحة العميل ورصيده) ---
    elif choice == "🔍 بحث وتعديل":
        st.subheader("🔍 البحث عن ملف عميل")
        s = st.text_input("الاسم أو الهاتف")
        if s:
            results = [c for c in customers if s in c['name'] or s in c['phone']]
            for c in results:
                with st.expander(f"👤 ملف العميل: {c['name']} ({c['type']})"):
                    st.write(f"**الموقع:** {c['gov']} - {c['center']} - {c['village']}")
                    st.write(f"**رصيد الحساب:** {sum(h['التكلفة'] for h in c['history'])} جنيه")
                    
                    # سجل الصيانة التفصيلي داخل البحث
                    if c['history']:
                        h_rows = "".join([f"<tr><td>{h['التاريخ']}</td><td>{h['الفني']}</td><td>{h['العمل']}</td><td>{h['التكلفة']}</td></tr>" for h in c['history']])
                        st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>الفني</th><th>الشمع المغير</th><th>المبلغ</th></tr></thead><tbody>{h_rows}</tbody></table>", unsafe_allow_html=True)
                    else: st.write("لا يوجد سجل صيانات.")

    # --- 4. الأرباح وقائمة العملاء (بنفس نظام الاستقرار السابق) ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 القائمة الشاملة")
        if customers:
            rows = ""
            for c in customers:
                row_total = sum(h['التكلفة'] for h in c['history'])
                rows += f"<tr><td>{c['name']}</td><td>{c['phone']}</td><td>{c['gov']}</td><td>{c['type']}</td><td>{row_total}</td></tr>"
            st.markdown(f"<table class='report-table'><thead><tr><th>الاسم</th><th>الهاتف</th><th>المحافظة</th><th>النوع</th><th>إجمالي المدفوع</th></tr></thead><tbody>{rows}</tbody></table>", unsafe_allow_html=True)

    elif choice == "💰 الأرباح":
        st.subheader("💰 تقرير الخزنة")
        total = sum(sum(h['التكلفة'] for h in c['history']) for c in customers)
        st.metric("إجمالي تحصيل الشركة", f"{total} جنيه")

    elif choice == "🛠️ إضافة صيانة":
        target = st.selectbox("اختر العميل", customers, format_func=lambda x: x['name'])
        with st.form("s_f"):
            parts = st.multiselect("الشمع", ["1", "2", "3", "M", "S", "كربون", "موتور"])
            price = st.number_input("المبلغ", min_value=0)
            if st.form_submit_button("حفظ"):
                h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(parts), "التكلفة": price}
                for cust in customers:
                    if cust['id'] == target['id']: cust['history'].append(h)
                save_data(CUSTOMERS_FILE, customers)
                st.success("✅ تم التسجيل")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
