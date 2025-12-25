import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات التصميم ==================
st.set_page_config(page_title="Power Life System", layout="wide")

# الرابط الحالي لموقعك (تأكد إنه xpt.streamlit.app)
BASE_URL = "https://xpt.streamlit.app"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تصميم صفحة العميل (نفس الشكل المطلوب) */
    .cust-header { background: #001f3f; border: 2px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 25px; }
    .bal-box { border: 2px solid #00ffcc; border-radius: 10px; padding: 10px; display: inline-block; margin-top: 10px; }
    .log-card { background: #071221; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-right: 5px solid #00d4ff; }
    .status-paid { color: #00ffcc; font-weight: bold; }
    .status-debt { color: #ff4b4b; font-weight: bold; }
    
    /* وضوح البحث للمدير */
    .stTextInput input { background-color: white !important; color: black !important; font-weight: bold !important; font-size: 18px !important; }
</style>
""", unsafe_allow_html=True)

# ================== 2. التعامل مع الداتا ==================
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

def get_bal(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. بوابة العميل (هنا السر) ==================
# البحث عن الـ ID في الرابط بشكل مباشر
query_params = st.query_params
customer_id = query_params.get("id")

if customer_id:
    # إخفاء السايد بار تماماً للعميل لمنع دخوله على السيستم
    st.markdown("<style>[data-testid='stSidebar'] {display:none !important;}</style>", unsafe_allow_html=True)
    
    cust = next((c for c in st.session_state.data if str(c['id']) == str(customer_id)), None)
    if cust:
        st.markdown(f"""
        <div class="cust-header">
            <h2 style="color:#00d4ff;">ملف صيانة العميل: {cust['name']}</h2>
            <div class="bal-box">
                <h3 style="margin:0;">إجمالي المتبقي:</h3>
                <h1 style="color:#00ffcc; margin:5px 0;">{get_bal(cust['history']):,.0f} ج.م</h1>
            </div>
        </div>
        <h3 style="text-align:right;">📋 سجل العمليات والصيانة</h3>
        """, unsafe_allow_html=True)
        
        for h in reversed(cust['history']):
            st.markdown(f"""
            <div class="log-card">
                <p style="margin:0;">📅 <b>التاريخ:</b> {h.get('date')}</p>
                <p style="margin:5px 0; font-size:18px;">🛠️ <b>العمل:</b> {h.get('note', '---')}</p>
                <div style="display:flex; justify-content:space-between;">
                    <span class="status-paid">💰 دفع: {h.get('price', 0)} ج.م</span>
                    <span class="status-debt">🔴 مديونية: {h.get('debt', 0)} ج.م</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.stop() # ينهي الكود هنا للعميل فلا يرى الإدارة

# ================== 4. لوحة الإدارة (تظهر لك فقط) ==================
with st.sidebar:
    st.title("لوحة الإدارة ⚙️")
    menu = st.radio("القائمة:", ["🔍 بحث", "➕ إضافة", "📂 داتا"])

if menu == "🔍 بحث":
    search = st.text_input("ابحث بالاسم أو الكود...").strip().lower()
    if search:
        hits = [c for c in st.session_state.data if search in c['name'].lower() or search == str(c['id'])]
        for c in hits:
            with st.expander(f"👤 {c['name']} (كود: {c['id']})"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    with st.form(f"f_{c['id']}"):
                        d = st.number_input("تكلفة (+)"); p = st.number_input("تحصيل (-)")
                        n = st.text_area("البيان"); t = st.text_input("الفني")
                        if st.form_submit_button("حفظ الزيارة"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": n, "debt": d, "price": p, "tech": t})
                            save_db(st.session_state.data); st.rerun()
                with col2:
                    # تأكد إن هذا الرابط هو اللي في الباركود
                    qr_link = f"{BASE_URL}/?id={c['id']}"
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}")
                    st.caption("باركود العميل")
                    if st.button("🗑️ حذف", key=f"del_{c['id']}"):
                        st.session_state.data.remove(c); save_db(st.session_state.data); st.rerun()
