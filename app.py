import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات الصفحة والتصميم ==================
st.set_page_config(page_title="Power Life System", layout="wide", initial_sidebar_state="expanded")

# الرابط الحالي (تأكد من تعديله للرابط الشغال xpt.streamlit.app)
BASE_URL = "https://xpt.streamlit.app"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { min-width: 300px !important; background-color: #0e1626 !important; border-left: 3px solid #00d4ff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق البحث */
    .stTextInput input { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; font-size: 20px !important; border: 2px solid #00d4ff !important; }

    /* صفحة العميل الخارجية - منفصلة تماماً */
    .customer-page { background: white; color: black; border-radius: 20px; padding: 40px; text-align: center; border-top: 15px solid #00d4ff; box-shadow: 0 10px 50px rgba(0,0,0,0.8); margin: 10px; }
    .status-box { background: #fff0f0; border: 2px solid #ffcccc; border-radius: 15px; padding: 20px; margin: 20px 0; }
    .log-item { background: #f4f9ff; border-right: 8px solid #007bff; padding: 15px; margin-bottom: 15px; border-radius: 10px; text-align: right; color: #333; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_db():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_db(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state:
    st.session_state.data = load_db()

def calc_bal(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. بوابة العميل (تفتح بالباركود فقط) ==================
params = st.query_params
if "id" in params:
    # إخفاء السايد بار والمنيو تماماً للعميل
    st.markdown("<style>[data-testid='stSidebar'], [data-testid='stHeader'] {display:none !important;}</style>", unsafe_allow_html=True)
    
    target = next((c for c in st.session_state.data if str(c['id']) == str(params["id"])), None)
    if target:
        st.markdown(f"""
        <div class="customer-page">
            <h1 style="color:#007bff;">باور لايف لخدمات الفلاتر 💧</h1>
            <h2 style="margin:5px 0;">كشف حساب وصيانة العميل</h2>
            <hr>
            <h3>مرحباً بك: {target['name']}</h3>
            <div class="status-box">
                <p style="margin:0; font-size:20px; color:#555;">المبلغ المتبقي طرفكم</p>
                <h1 style="font-size:60px; color:#d9534f; margin:10px 0;">{calc_bal(target['history']):,.0f} <span style="font-size:25px;">ج.م</span></h1>
            </div>
            <p style="font-size:18px;">كود المشترك: <b>{target['id']}</b> | الهاتف: <b>{target.get('phone', '---')}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🗓️ سجل تغيير الشمع والصيانات")
        for h in reversed(target['history']):
            st.markdown(f"""
            <div class="log-item">
                <p style="margin:0; font-weight:bold; color:#007bff;">📅 التاريخ: {h.get('date')}</p>
                <p style="margin:8px 0; font-size:18px;">📋 <b>العمل:</b> {h.get('note', 'صيانة دورية')}</p>
                <p style="margin:0; font-size:14px; color:#666;">👤 الفني المسؤول: {h.get('tech', 'إدارة الشركة')}</p>
            </div>
            """, unsafe_allow_html=True)
        st.stop()

# ================== 4. لوحة المدير الكاملة ==================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00d4ff;'>POWER LIFE ADMIN</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("الوظائف:", ["🔍 البحث والتحصيل", "➕ إضافة عميل", "📊 التقارير المالية", "📂 النسخ الاحتياطي"])

if menu == "🔍 البحث والتحصيل":
    st.title("البحث السريع")
    # البحث مخفي (لا يظهر إلا بالكتابة)
    query = st.text_input("ابحث (اسم / تليفون / كود)...").strip().lower()
    if query:
        hits = [c for c in st.session_state.data if query in c['name'].lower() or query in str(c.get('phone','')) or query == str(c['id'])]
        for c in hits:
            bal = calc_bal(c['history'])
            with st.expander(f"👤 {c['name']} | كود: {c['id']} | رصيد: {bal:,.0f}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    with st.form(f"up_{c['id']}"):
                        d = st.number_input("تكلفة (+)"); p = st.number_input("محصل (-)")
                        t = st.text_input("اسم الفني"); n = st.text_area("تفاصيل العمل")
                        if st.form_submit_button("حفظ البيانات ✅"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": n, "debt": d, "price": p, "tech": t})
                            save_db(st.session_state.data); st.rerun()
                with c2:
                    qr_link = f"{BASE_URL}?id={c['id']}"
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}")
                    st.caption("باركود صفحة العميل")
                    if st.button("🗑️ حذف العميل", key=f"del_{c['id']}"):
                        st.session_state.data.remove(c); save_db(st.session_state.data); st.rerun()
    else: st.info("بانتظار البحث...")

elif menu == "➕ إضافة عميل":
    with st.form("new_c"):
        n = st.text_input("الاسم"); p = st.text_input("الموبايل"); d = st.number_input("رصيد سابق")
        if st.form_submit_button("إضافة"):
            new_id = max([x['id'] for x in st.session_state.data], default=1000) + 1
            st.session_state.data.append({"id": new_id, "name": n, "phone": p, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحي", "debt": d, "price": 0}]})
            save_db(st.session_state.data); st.success("تم الحفظ!"); st.rerun()

elif menu == "📂 النسخ الاحتياطي":
    st.download_button("📥 تحميل الداتا", json.dumps(st.session_state.data, ensure_ascii=False), "backup.json")
