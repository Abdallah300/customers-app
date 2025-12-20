import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================
st.set_page_config(page_title="Power Life CRM", page_icon="💧", layout="wide")

st.markdown("""
    <style>
    .report-table { width: 100%; border-collapse: collapse; background-color: white !important; color: black !important; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: right; vertical-align: middle; }
    .report-table th { background-color: #007bff; color: white; }
    .qr-img { width: 60px; height: 60px; border: 1px solid #eee; }
    .map-btn { background-color: #28a745; color: white; padding: 5px 10px; text-decoration: none; border-radius: 5px; font-size: 12px; }
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

    # --- 1. قائمة العملاء (مع الباركود والموقع) ---
    if choice == "📋 قائمة العملاء":
        st.subheader("📋 سجل العملاء والباركود")
        if customers:
            rows = ""
            for c in customers:
                # توليد رابط الباركود
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=PL-ID-{c['id']}"
                # تجهيز رابط الخريطة
                loc = c.get('location', '0,0')
                map_url = f"https://www.google.com/maps?q={loc}"
                
                rows += f"""
                <tr>
                    <td><img src="{qr_url}" class="qr-img"><br><small>PL-{c['id']}</small></td>
                    <td><b>{c['name']}</b><br>{c['phone']}</td>
                    <td>{c.get('gov', '')} - {c.get('village', '')}</td>
                    <td>{c.get('type', '')}</td>
                    <td><a href="{map_url}" target="_blank" class="map-btn">📍 عرض الموقع</a></td>
                </tr>
                """
            
            st.markdown(f"""
            <table class='report-table'>
                <thead>
                    <tr>
                        <th>الباركود</th>
                        <th>العميل والهاتف</th>
                        <th>العنوان</th>
                        <th>النوع</th>
                        <th>الخريطة</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else: st.info("لا توجد بيانات عملاء")

    # --- 2. إضافة عميل ---
    elif choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        with st.form("new_client"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم الهاتف")
                gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
            with col2:
                center = st.text_input("المركز")
                village = st.text_input("القرية / البلد")
                ctype = st.selectbox("نوع الجهاز", ["جهاز جديد", "جهاز قديم", "شركة"])
            
            loc_input = st.text_input("الإحداثيات (مثال: 30.123, 31.456)")
            
            if st.form_submit_button("حفظ العميل"):
                new_id = len(customers) + 1
                customers.append({
                    "id": new_id, "name": name, "phone": phone, "gov": gov,
                    "center": center, "village": village, "type": ctype,
                    "location": loc_input if loc_input else "0,0", "history": []
                })
                save_data(CUSTOMERS_FILE, customers)
                st.success("✅ تم الحفظ بنجاح")
                st.rerun()

    # --- 3. أرباح الشركة ---
    elif choice == "💰 أرباح الشركة":
        st.subheader("💰 الأرباح والتحصيل")
        total = 0
        summary_rows = ""
        daily = {}
        for c in customers:
            for h in c.get('history', []):
                val = int(h['التكلفة'])
                total += val
                daily[h['التاريخ']] = daily.get(h['التاريخ'], 0) + val
        
        st.metric("إجمالي تحصيل الخزنة", f"{total} جنيه")
        for d, v in daily.items():
            summary_rows += f"<tr><td>{d}</td><td>{v} جنيه</td></tr>"
        
        st.markdown(f"<table class='report-table'><thead><tr><th>التاريخ</th><th>الدخل اليومي</th></tr></thead><tbody>{summary_rows}</tbody></table>", unsafe_allow_html=True)

    # --- 4. تتبع الفنيين ---
    elif choice == "👷 تتبع الفنيين":
        st.subheader("📍 تتبع الفنيين")
        techs = [u for u in users if u['role'] == 'technician']
        if techs:
            t_rows = ""
            for u in techs:
                t_loc = f"{u.get('lat',0)},{u.get('lon',0)}"
                t_map = f"https://www.google.com/maps?q={t_loc}"
                t_rows += f"<tr><td>{u['username']}</td><td>{t_loc}</td><td><a href='{t_map}' target='_blank' class='map-btn'>📍 عرض الموقع</a></td></tr>"
            st.markdown(f"<table class='report-table'><thead><tr><th>الفني</th><th>الإحداثيات</th><th>الخريطة</th></tr></thead><tbody>{t_rows}</tbody></table>", unsafe_allow_html=True)
        else: st.info("لا يوجد فنيين")

    # --- بقية الوظائف ---
    elif choice == "🛠️ إضافة صيانة":
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: x['name'])
            with st.form("serv_f"):
                work = st.multiselect("الشمع المغير", ["1", "2", "3", "M", "S", "كربون"])
                price = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("حفظ"):
                    h = {"التاريخ": str(datetime.now().date()), "الفني": user_now['username'], "العمل": ", ".join(work), "التكلفة": price}
                    for cust in customers:
                        if cust['id'] == target['id']: cust['history'].append(h)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم!")

    elif choice == "🔍 بحث وتعديل":
        s = st.text_input("ابحث بالاسم أو الهاتف")
        if s:
            res = [c for c in customers if s in c['name'] or s in c['phone']]
            for c in res:
                with st.expander(f"ملف العميل: {c['name']}"):
                    st.write(f"رصيده الإجمالي: {sum(int(h['التكلفة']) for h in c.get('history', []))} جنيه")
                    if st.button("حذف", key=f"del_{c['id']}"):
                        customers.remove(c)
                        save_data(CUSTOMERS_FILE, customers)
                        st.rerun()

    elif choice == "👤 إضافة فني جديد":
        with st.form("add_t"):
            u = st.text_input("اسم الفني")
            p = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة"):
                users.append({"username": u, "password": p, "role": "technician"})
                save_data(USERS_FILE, users)
                st.success("تم")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
