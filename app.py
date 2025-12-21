import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import hashlib
import plotly.express as px
import time

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================
st.set_page_config(page_title="Power Life CRM Pro", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stApp { background-color: #f8f9fa; }
    .stat-card {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white; padding: 20px; border-radius: 15px;
        text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .qr-card-custom {
        border: 2px dashed #28a745; padding: 20px;
        background: #fff; border-radius: 15px; text-align: center;
        max-width: 300px; margin: auto;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

customers = load_data("customers.json", [])
users = load_data("users.json", [{"username": "admin", "password": "123", "role": "admin"}])

# ================== 3. صفحة العميل (عند مسح الباركود) ==================
query_params = st.query_params
if "id" in query_params:
    cust_id = int(query_params["id"])
    c = next((item for item in customers if item["id"] == cust_id), None)
    if c:
        st.title(f"💧 ملف المتابعة: {c['name']}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("رقم العميل", f"PL-{c['id']:04d}")
            st.info(f"📍 العنوان: {c['gov']} - {c['village']}")
        with col2:
            total = sum(h.get('amount', 0) for h in c.get('history', []))
            st.metric("إجمالي المدفوعات", f"{total} ج.م")
        
        st.subheader("🛠️ سجل الصيانة")
        if c.get('history'):
            st.table(pd.DataFrame(c['history'])[['date', 'work', 'amount', 'technician']])
        else:
            st.warning("لا يوجد سجلات حالية.")
        st.stop()

# ================== 4. نظام تسجيل الدخول ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life - دخول النظام")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u and x["password"] == p), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else: st.error("بيانات خطأ")
else:
    # ================== 5. القائمة الرئيسية ==================
    curr_user = st.session_state.user
    menu = ["📊 لوحة التحكم", "👥 العملاء", "➕ إضافة عميل", "🛠️ الصيانة", "📈 التقارير", "🚪 خروج"]
    choice = st.sidebar.radio("القائمة", menu)

    if choice == "📊 لوحة التحكم":
        st.title("📊 حالة الشغل اليوم")
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='stat-card'><h4>العملاء</h4><h2>{len(customers)}</h2></div>", unsafe_allow_html=True)
        # حساب الدخل
        total_inc = sum(h.get('amount', 0) for c in customers for h in c.get('history', []))
        c2.markdown(f"<div class='stat-card'><h4>الأرباح</h4><h2>{total_inc} ج.م</h2></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-card'><h4>الفنيين</h4><h2>{len(users)}</h2></div>", unsafe_allow_html=True)

    elif choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        with st.form("add_cust"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("الموبايل")
            gov = st.selectbox("المحافظة", ["المنوفية", "الغربية", "القاهرة", "الجيزة"])
            village = st.text_input("القرية")
            ctype = st.selectbox("نوع الجهاز", ["7 مراحل", "5 مراحل", "جامبو"])
            submit = st.form_submit_button("حفظ وإصدار الباركود")
            
            if submit and name and phone:
                new_id = max([c['id'] for c in customers], default=0) + 1
                # --- تعديل الرابط هنا عند الرفع ---
                # استبدل الرابط اللي تحت برابط موقعك الحقيقي
                site_url = "https://power-life.streamlit.app" 
                qr_link = f"{site_url}/?id={new_id}"
                
                customers.append({
                    "id": new_id, "name": name, "phone": phone, "gov": gov,
                    "village": village, "type": ctype, "history": [], "date": str(datetime.now().date())
                })
                save_data("customers.json", customers)
                st.success("✅ تم الحفظ")
                
                # إظهار الباركود فوراً
                qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_link}"
                st.markdown(f"""
                <div class="qr-card-custom">
                    <h3 style="color:#28a745">كارت متابعة</h3>
                    <img src="{qr_api}">
                    <p><b>{name}</b></p>
                    <p>PL-{new_id:04d}</p>
                </div>
                """, unsafe_allow_html=True)

    elif choice == "🛠️ الصيانة":
        st.subheader("🛠️ تسجيل زيارة صيانة")
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            with st.form("serv"):
                work = st.text_area("الأعمال التي تمت")
                price = st.number_input("المبلغ المدفوع", min_value=0)
                if st.form_submit_button("حفظ الزيارة"):
                    record = {
                        "date": str(datetime.now().date()),
                        "work": work,
                        "amount": price,
                        "technician": curr_user['username']
                    }
                    for c in customers:
                        if c['id'] == target['id']:
                            c['history'].append(record)
                    save_data("customers.json", customers)
                    st.success("تم تسجيل الصيانة بنجاح")
        else: st.warning("لا يوجد عملاء")

    elif choice == "👥 العملاء":
        st.subheader("👥 قائمة جميع العملاء")
        if customers:
            df = pd.DataFrame(customers)[['id', 'name', 'phone', 'gov', 'village', 'type']]
            st.dataframe(df, use_container_width=True)
        else: st.info("القائمة فارغة")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
