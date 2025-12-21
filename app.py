import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر الفاخر ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    .client-report { background: rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 25px; border: 1px solid #007bff; margin-bottom: 20px; }
    .data-row { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 12px 0; display: flex; justify-content: space-between; }
    .history-card { background: rgba(0, 123, 255, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 5px solid #00d4ff; }
    header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات (مع معالجة الأخطاء) ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data if isinstance(data, list) else []
            except: return []
    return []

def save_data(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# ================== 3. محرك صفحة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        
        if customer:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>مرحباً بك: {customer.get('name', 'عميلنا العزيز')}</h3>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='client-report'>
                <div class='data-row'><span>📍 العنوان:</span> <b>{customer.get('loc', 'غير مسجل')}</b></div>
                <div class='data-row'><span>📱 الموبايل:</span> <b>{customer.get('phone', 'غير مسجل')}</b></div>
                <div class='data-row'><span>🆔 الكود:</span> <b>PL-{customer.get('id', 0):04d}</b></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🗓️ سجل الصيانات")
            history = customer.get('history', [])
            if history:
                for h in reversed(history):
                    # استخدام .get لتجنب KeyError لو فيه معلومة ناقصة في الملف
                    h_date = h.get('date', 'تاريخ غير مسجل')
                    h_note = h.get('note', h.get('work', 'صيانة دورية'))
                    h_price = h.get('price', h.get('amount', 0))
                    h_tech = h.get('tech', 'فني Power Life')
                    
                    st.markdown(f"""
                    <div class='history-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <span>📅 {h_date}</span>
                            <span style='color:#00d4ff;'>💰 {h_price} ج.م</span>
                        </div>
                        <p style='margin-top:10px;'>🛠️ {h_note}</p>
                        <small>👤 الفني: {h_tech}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا يوجد سجل صيانات حالياً.")
            
            st.success("Power Life تتمنى لكم مياه صحية ونقية 💧")
            st.stop() # إيقاف التنفيذ هنا تماماً للعميل
    except:
        pass # لو حصل أي خطأ في الـ ID ميعرضش حاجة خالص

# ================== 4. لوحة الإدارة (للمدير فقط) ==================
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>لوحة تحكم Power Life</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول الإدارة", use_container_width=True):
            if u == "admin" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("بيانات خاطئة")
else:
    st.sidebar.title("💧 Power Life Admin")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة", "🚪 خروج"])

    if menu == "➕ إضافة عميل":
        st.subheader("إضافة عميل")
        with st.form("add"):
            name = st.text_input("الاسم")
            phone = st.text_input("الموبايل")
            loc = st.text_input("العنوان")
            if st.form_submit_button("حفظ"):
                new_id = max([c['id'] for c in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "loc": loc, "history": []})
                save_data(st.session_state.data)
                st.success("تم الحفظ")

    elif menu == "👥 إدارة العملاء":
        st.subheader("قائمة العملاء")
        search = st.text_input("بحث بالاسم...")
        for c in st.session_state.data:
            if search in c.get('name', ''):
                col_a, col_b, col_c = st.columns([3, 1, 1])
                col_a.write(f"👤 {c['name']} (PL-{c['id']})")
                with col_b:
                    if st.button("🖼️ باركود", key=f"q_{c['id']}"):
                        url = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        qr = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}"
                        st.image(qr, width=150)
                with col_c:
                    if st.button("🗑️ حذف", key=f"d_{c['id']}"):
                        st.session_state.data = [x for x in st.session_state.data if x['id'] != c['id']]
                        save_data(st.session_state.data)
                        st.rerun()

    elif menu == "🛠️ تسجيل صيانة":
        st.subheader("إضافة زيارة")
        target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: x.get('name', 'بدون اسم'))
        with st.form("serv"):
            note = st.text_area("وصف العمل")
            tech = st.text_input("الفني")
            price = st.number_input("المبلغ", min_value=0)
            if st.form_submit_button("حفظ"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({"date": str(datetime.now().date()), "note": note, "tech": tech, "price": price})
                save_data(st.session_state.data)
                st.success("تم التحديث")

    elif menu == "🚪 خروج":
        st.session_state.auth = False
        st.rerun()
