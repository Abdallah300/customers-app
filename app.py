import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import urllib.parse

# ================== 1. إعدادات المظهر والتحكم في الشاشة ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-report { background: rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 25px; border: 1px solid #007bff; margin-bottom: 20px; }
    .data-row { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 12px 0; display: flex; justify-content: space-between; }
    .history-card { background: rgba(0, 123, 255, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 5px solid #00d4ff; }
    .finance-card { background: rgba(0, 255, 127, 0.1); border: 1px solid #00ff7f; padding: 15px; border-radius: 15px; text-align: center; }
    .debt-card { background: rgba(255, 69, 0, 0.1); border: 1px solid #ff4500; padding: 15px; border-radius: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

EGYPT_GOVS = ["القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "الشرقية", "المنوفية", "القليوبية", "البحيرة", "الغربية", "بور سعيد", "دمياط", "الإسماعيلية", "السويس", "كفر الشيخ", "الفيوم", "بني سويف", "المنيا", "أسيوط", "سوهاج", "قنا", "الأقصر", "أسوان"]

# ================== 3. صفحة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        if customer:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            history = customer.get('history', [])
            total_paid = sum(float(h.get('price', 0)) for h in history)
            total_debt = sum(float(h.get('debt', 0)) for h in history)
            col1, col2 = st.columns(2)
            col1.markdown(f"<div class='finance-card'>💰 المدفوع<br><h2>{total_paid:,.0f}</h2></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='debt-card'>⚠️ المديونية<br><h2>{total_debt:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='client-report'><div class='data-row'>👤 الاسم: <b>{customer.get('name')}</b></div><div class='data-row'>📍 المحافظة: <b>{customer.get('gov')}</b></div><div class='data-row'>🔧 الجهاز: <b>{customer.get('device_type')}</b></div></div>", unsafe_allow_html=True)
            st.stop()
    except: pass

# ================== 4. لوحة الإدارة ==================
if not st.session_state.get('auth', False):
    st.markdown("<h2 style='text-align:center;'>دخول الإدارة</h2>", unsafe_allow_html=True)
    u = st.text_input("المستخدم")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123":
            st.session_state.auth = True
            st.rerun()
else:
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة", "📊 حسابات عامة", "🚪 خروج"])

    if menu == "➕ إضافة عميل":
        with st.form("add"):
            name = st.text_input("الاسم")
            phone = st.text_input("الموبايل")
            gov = st.selectbox("المحافظة", EGYPT_GOVS)
            loc = st.text_input("العنوان")
            device = st.selectbox("نوع الجهاز", ["جهاز جديد", "جهاز قديم", "جهاز خارجي"])
            if st.form_submit_button("حفظ"):
                new_id = max([c['id'] for c in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "gov": gov, "loc": loc, "device_type": device, "history": []})
                save_data(st.session_state.data)
                st.success("تم الحفظ")

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم...")
        for i, c in enumerate(st.session_state.data):
            if search in c.get('name', ''):
                with st.expander(f"👤 {c['name']} (PL-{c['id']:04d})"):
                    # عرض البيانات وتعديلها
                    with st.form(f"edit_{c['id']}"):
                        new_name = st.text_input("تعديل الاسم", value=c.get('name'))
                        new_phone = st.text_input("تعديل الموبايل", value=c.get('phone'))
                        new_gov = st.selectbox("تعديل المحافظة", EGYPT_GOVS, index=EGYPT_GOVS.index(c.get('gov')) if c.get('gov') in EGYPT_GOVS else 0)
                        new_loc = st.text_input("تعديل العنوان", value=c.get('loc'))
                        new_device = st.selectbox("تعديل نوع الجهاز", ["جهاز جديد", "جهاز قديم", "جهاز خارجي"], index=["جهاز جديد", "جهاز قديم", "جهاز خارجي"].index(c.get('device_type')) if c.get('device_type') in ["جهاز جديد", "جهاز قديم", "جهاز خارجي"] else 0)
                        
                        clear_debt = st.checkbox("تصفير المديونية (حذف الديون المسجلة)")
                        
                        if st.form_submit_button("حفظ التعديلات"):
                            c['name'] = new_name
                            c['phone'] = new_phone
                            c['gov'] = new_gov
                            c['loc'] = new_loc
                            c['device_type'] = new_device
                            if clear_debt:
                                for h in c.get('history', []): h['debt'] = 0
                            save_data(st.session_state.data)
                            st.success("تم التعديل بنجاح")
                            st.rerun()
                    
                    # أزرار الباركود والواتساب والحذف
                    c1, c2, c3 = st.columns(3)
                    if c1.button("🖼️ باركود", key=f"q_{c['id']}"):
                        url = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={url}")
                    
                    msg = urllib.parse.quote(f"رابط بياناتك: https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    c2.markdown(f'<a href="https://wa.me/2{c["phone"]}?text={msg}" target="_blank"><button style="background:#25D366; color:white; border:none; padding:8px; border-radius:5px; width:100%;">🟢 واتساب</button></a>', unsafe_allow_html=True)
                    
                    if c3.button("🗑️ حذف نهائي", key=f"del_{c['id']}"):
                        st.session_state.data.pop(i)
                        save_data(st.session_state.data)
                        st.rerun()

    elif menu == "🛠️ تسجيل صيانة":
        target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: f"{x['name']} ({x['phone']})")
        with st.form("serv"):
            note = st.text_area("وصف العمل")
            tech = st.text_input("الفني")
            price = st.number_input("المدفوع", min_value=0.0)
            debt = st.number_input("المتبقي (دين)", min_value=0.0)
            if st.form_submit_button("حفظ"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({"date": str(datetime.now().date()), "note": note, "tech": tech, "price": price, "debt": debt})
                save_data(st.session_state.data)
                st.success("تم الحفظ")

    elif menu == "📊 حسابات عامة":
        all_p = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        all_d = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي التحصيل", f"{all_p:,.0f} ج.م")
        st.metric("إجمالي الديون", f"{all_d:,.0f} ج.م")

    elif menu == "🚪 خروج":
        st.session_state.auth = False
        st.rerun()
