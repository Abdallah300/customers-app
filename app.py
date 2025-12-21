import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px

# ================== 1. إعدادات المظهر (أزرق في أسود) ==================
st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* الخلفية العامة */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #001f3f 100%);
        color: #ffffff;
    }
    
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }

    /* البطاقات */
    .stat-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #007bff;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        transition: 0.3s;
    }
    .stat-card:hover { border-color: #00d4ff; background: rgba(255, 255, 255, 0.1); }

    /* أزرار المنيو */
    .stButton>button {
        background: linear-gradient(45deg, #007bff, #00d4ff);
        color: white; border: none; border-radius: 10px; width: 100%;
    }

    /* الباركود */
    .qr-container {
        background: white; padding: 20px; border-radius: 15px;
        display: inline-block; margin-top: 10px; border: 5px solid #007bff;
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
# كلمة السر هنا: admin / admin123
users = [{"username": "admin", "password": "admin123", "role": "admin"}]

# ================== 3. صفحة العميل (الباركود) ==================
query_params = st.query_params
if "id" in query_params:
    cust_id = int(query_params["id"])
    c = next((item for item in customers if item["id"] == cust_id), None)
    if c:
        st.title(f"💧 ملف المتابعة: {c['name']}")
        st.markdown(f"### كود العميل: PL-{c['id']:04d}")
        st.info(f"📍 الموقع: {c['gov']} - {c['village']}")
        
        if c.get('history'):
            st.subheader("🛠️ سجل الصيانات السابقة")
            st.table(pd.DataFrame(c['history']))
        st.stop()

# ================== 4. تسجيل الدخول ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>Power Life Login</h1>", unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u and x["password"] == p), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else: st.error("بيانات الدخول غير صحيحة")
else:
    # ================== 5. القائمة الرئيسية ==================
    st.sidebar.title("💎 Power Life Ultra")
    menu = ["📊 الإحصائيات", "👥 العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة", "🚪 خروج"]
    choice = st.sidebar.radio("انتقل إلى", menu)

    if choice == "📊 الإحصائيات":
        st.title("📊 لوحة التحكم")
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f"<div class='stat-card'><h3>العملاء</h3><h2>{len(customers)}</h2></div>", unsafe_allow_html=True)
        with c2: 
            income = sum(h.get('amount', 0) for c in customers for h in c.get('history', []))
            st.markdown(f"<div class='stat-card'><h3>الإيرادات</h3><h2>{income} ج.م</h2></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='stat-card'><h3>التنبيهات</h3><h2>0</h2></div>", unsafe_allow_html=True)

    elif choice == "➕ إضافة عميل":
        st.subheader("📝 تسجيل عميل جديد")
        with st.form("new_customer"):
            name = st.text_input("الاسم")
            phone = st.text_input("رقم الهاتف")
            gov = st.selectbox("المحافظة", ["المنوفية", "الغربية", "القاهرة", "الجيزة"])
            village = st.text_input("القرية/المركز")
            submit = st.form_submit_button("حفظ العميل وإصدار الكود")
            
            if submit and name and phone:
                new_id = max([c['id'] for c in customers], default=0) + 1
                # الرابط التلقائي لموقعك
                site_url = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"
                qr_link = f"{site_url}/?id={new_id}"
                
                customers.append({
                    "id": new_id, "name": name, "phone": phone, "gov": gov,
                    "village": village, "history": []
                })
                save_data("customers.json", customers)
                
                st.success(f"✅ تم حفظ العميل PL-{new_id:04d}")
                # إظهار الباركود
                qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data={qr_link}"
                st.markdown(f"<div class='qr-container'><img src='{qr_api}'><br><p style='color:black;'>{name}</p></div>", unsafe_allow_html=True)

    elif choice == "🛠️ تسجيل صيانة":
        if not customers: st.warning("لا يوجد عملاء مسجلين")
        else:
            cust = st.selectbox("اختر العميل", customers, format_func=lambda x: x['name'])
            with st.form("serv_form"):
                work = st.text_area("ما تم تنفيذه")
                amount = st.number_input("المبلغ المدفوع", min_value=0)
                if st.form_submit_button("تحديث السجل"):
                    for c in customers:
                        if c['id'] == cust['id']:
                            c['history'].append({"date": str(datetime.now().date()), "work": work, "amount": amount})
                    save_data("customers.json", customers)
                    st.success("تم التحديث")

    elif choice == "👥 العملاء":
        st.subheader("👥 قاعدة البيانات")
        if customers: st.dataframe(pd.DataFrame(customers).drop(columns=['history']))

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
