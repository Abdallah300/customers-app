import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر الفاخر (معدلة للتاتش) ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* السماح بالتمرير بشكل إجباري */
    html, body, [data-testid="stAppViewContainer"] {
        overflow-y: auto !important;
        height: auto !important;
    }

    .stApp { 
        background: linear-gradient(135deg, #000000 0%, #001f3f 100%); 
        color: #ffffff; 
    }
    
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    .client-report { background: rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 25px; border: 1px solid #007bff; margin-bottom: 20px; }
    .data-row { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 12px 0; display: flex; justify-content: space-between; }
    .history-card { background: rgba(0, 123, 255, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 5px solid #00d4ff; }
    .finance-card { background: rgba(0, 255, 127, 0.1); border: 1px solid #00ff7f; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
    .debt-card { background: rgba(255, 69, 0, 0.1); border: 1px solid #ff4500; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات ==================
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

EGYPT_GOVS = ["القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "الشرقية", "المنوفية", "القليوبية", "البحيرة", "الغربية", "بور سعيد", "دمياط", "الإسماعيلية", "السويس", "كفر الشيخ", "الفيوم", "بني سويف", "المنيا", "أسيوط", "سوهاج", "قنا", "الأقصر", "أسوان", "البحر الأحمر", "الوادي الجديد", "مطروح", "شمال سيناء", "جنوب سيناء"]

# ================== 3. محرك صفحة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        if customer:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>مرحباً بك: {customer.get('name', 'عميلنا العزيز')}</h3>", unsafe_allow_html=True)
            
            history = customer.get('history', [])
            total_paid = sum(float(h.get('price', 0)) for h in history)
            total_debt = sum(float(h.get('debt', 0)) for h in history)

            col_finance1, col_finance2 = st.columns(2)
            with col_finance1:
                st.markdown(f"<div class='finance-card'>💰 إجمالي المدفوعات<br><h2>{total_paid:,.0f} ج.م</h2></div>", unsafe_allow_html=True)
            with col_finance2:
                st.markdown(f"<div class='debt-card'>⚠️ إجمالي المديونية<br><h2>{total_debt:,.0f} ج.م</h2></div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class='client-report'>
                <div class='data-row'><span>📍 المحافظة:</span> <b>{customer.get('gov', 'غير مسجل')}</b></div>
                <div class='data-row'><span>🏙️ المركز/العنوان:</span> <b>{customer.get('loc', 'غير مسجل')}</b></div>
                <div class='data-row'><span>🔧 نوع الجهاز:</span> <b>{customer.get('device_type', 'غير محدد')}</b></div>
                <div class='data-row'><span>📱 الموبايل:</span> <b>{customer.get('phone', 'غير مسجل')}</b></div>
                <div class='data-row'><span>🆔 الكود:</span> <b>PL-{customer.get('id', 0):04d}</b></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🗓️ سجل الصيانات")
            if history:
                for h in reversed(history):
                    st.markdown(f"""
                    <div class='history-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <span>📅 {h.get('date', '---')}</span>
                            <span style='color:#00ff7f;'>✅ دفع: {h.get('price', 0)} ج.م</span>
                        </div>
                        <p style='margin-top:10px;'>🛠️ {h.get('note', 'صيانة دورية')}</p>
                        <div style='display:flex; justify-content:space-between; border-top:1px solid rgba(255,255,255,0.1); padding-top:5px;'>
                            <small>👤 الفني: {h.get('tech', '---')}</small>
                            <small style='color:#ff4500;'>💸 متبقي: {h.get('debt', 0)} ج.م</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else: st.info("لا يوجد سجل صيانات حالياً.")
            st.stop()
    except: pass

# ================== 4. لوحة الإدارة ==================
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
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة", "📊 حسابات عامة", "🚪 خروج"])

    if menu == "➕ إضافة عميل":
        st.subheader("تسجيل عميل جديد")
        with st.form("add"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الموبايل")
            gov = st.selectbox("المحافظة", EGYPT_GOVS)
            loc = st.text_input("المركز / العنوان")
            device = st.selectbox("نوع الجهاز", ["جهاز جديد", "جهاز قديم", "جهاز خارجي"])
            if st.form_submit_button("حفظ"):
                new_id = max([c['id'] for c in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "gov": gov, "loc": loc, "device_type": device, "history": []})
                save_data(st.session_state.data)
                st.success("تم الحفظ")

    elif menu == "👥 إدارة العملاء":
        st.subheader("قائمة العملاء")
        search = st.text_input("بحث بالاسم...")
        for c in st.session_state.data:
            if search in c.get('name', ''):
                with st.expander(f"👤 {c.get('name')} | 📍 {c.get('gov')}"):
                    c_history = c.get('history', [])
                    c_debt = sum(float(h.get('debt', 0)) for h in c_history)
                    st.write(f"🔧 الجهاز: {c.get('device_type')} | ⚠️ مديونية: {c_debt} ج.م")
                    if st.button("🖼️ باركود", key=f"q_{c['id']}"):
                        url = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        qr = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}"
                        st.image(qr, width=150)
                    if st.button("🗑️ حذف", key=f"d_{c['id']}"):
                        st.session_state.data = [x for x in st.session_state.data if x['id'] != c['id']]
                        save_data(st.session_state.data)
                        st.rerun()

    elif menu == "🛠️ تسجيل صيانة":
        st.subheader("إضافة زيارة")
        target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: f"{x.get('name')} ({x.get('phone')})")
        with st.form("serv"):
            note = st.text_area("وصف العمل")
            tech = st.text_input("الفني")
            price = st.number_input("المدفوع حالياً", min_value=0)
            debt = st.number_input("المتبقي (دين)", min_value=0)
            if st.form_submit_button("حفظ"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({"date": str(datetime.now().date()), "note": note, "tech": tech, "price": price, "debt": debt})
                save_data(st.session_state.data)
                st.success("تم الحفظ")

    elif menu == "📊 حسابات عامة":
        all_paid = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        all_debt = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي التحصيل", f"{all_paid} ج.م")
        st.metric("إجمالي الديون", f"{all_debt} ج.م")

    elif menu == "🚪 خروج":
        st.session_state.auth = False
        st.rerun()
