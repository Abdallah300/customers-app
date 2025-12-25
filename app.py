import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات السيستم والواجهة ==================
st.set_page_config(page_title="Power Life System", layout="wide", initial_sidebar_state="expanded")

# الرابط الصحيح لموقعك لضمان عمل الباركود
BASE_URL = "https://xpt.streamlit.app"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { min-width: 300px !important; background-color: #0e1626 !important; border-left: 3px solid #00d4ff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق البحث */
    .stTextInput input { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; font-size: 20px !important; border: 2px solid #00d4ff !important; }

    /* صفحة العميل (Client Portal) - تصميم خارجي أبيض ونظيف */
    .client-portal { background: white; color: black; border-radius: 20px; padding: 35px; text-align: center; border-top: 12px solid #00d4ff; box-shadow: 0 10px 40px rgba(0,0,0,0.5); margin: 20px; }
    .history-card { background: #f8f9fa; border-right: 6px solid #00d4ff; padding: 15px; margin-top: 10px; border-radius: 8px; text-align: right; color: #333; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات (حفظ وتلقائي) ==================
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

def get_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. محرك "صفحة العميل الخارجية" ==================
q_params = st.query_params
if "id" in q_params:
    customer = next((c for c in st.session_state.data if str(c['id']) == str(q_params["id"])), None)
    if customer:
        # إخفاء السايد بار تماماً للعميل
        st.markdown("<style> [data-testid='stSidebar'] { display:none; } [data-testid='stHeader'] { display:none; } </style>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="client-portal">
            <h1 style="color:#007bff;">💧 باور لايف لخدمات الفلاتر</h1>
            <h2 style="margin:10px 0;">مرحباً بك: {customer['name']}</h2>
            <div style="background:#fff4f4; padding:20px; border-radius:15px; border:1px solid #ffc1c1;">
                <h3 style="color:#dc3545; margin:0;">إجمالي المبلغ المتبقي</h3>
                <h1 style="font-size:50px; margin:10px 0;">{get_balance(customer['history']):,.0f} <span style="font-size:20px;">ج.م</span></h1>
            </div>
            <p style="font-size:18px; color:#666; margin-top:15px;">كود العميل: <b>{customer['id']}</b> | الهاتف: <b>{customer.get('phone', '---')}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🗓️ سجل الزيارات ومواعيد تغيير الشمع")
        for h in reversed(customer['history']):
            st.markdown(f"""
            <div class="history-card">
                <p style="margin:0; font-weight:bold; color:#007bff;">📅 التاريخ: {h.get('date')}</p>
                <p style="margin:5px 0; font-size:18px;">📋 <b>البيان:</b> {h.get('note', '---')}</p>
                <p style="margin:0; font-size:14px; color:#666;">👤 الفني المسؤول: {h.get('tech', 'إدارة الشركة')}</p>
            </div>
            """, unsafe_allow_html=True)
        st.stop() # يمنع ظهور لوحة المدير للعميل

# ================== 4. لوحة المدير (تظهر فقط عند عدم وجود ID) ==================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00d4ff;'>POWER LIFE ⚙️</h2>", unsafe_allow_html=True)
    menu = st.radio("القائمة:", ["🔍 بحث عن عميل", "➕ إضافة عميل", "📊 التقارير المالية", "📂 النسخ الاحتياطي"])

if menu == "🔍 بحث عن عميل":
    st.title("البحث عن ملف")
    query = st.text_input("ابحث بالاسم أو التليفون أو الكود...").strip().lower()
    if query:
        res = [c for c in st.session_state.data if query in c['name'].lower() or query in str(c.get('phone','')) or query == str(c['id'])]
        for c in res:
            bal = get_balance(c['history'])
            with st.expander(f"👤 {c['name']} - كود: {c['id']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**الرصيد الحالي:** {bal:,.0f} ج.م")
                    with st.form(f"visit_{c['id']}"):
                        d = st.number_input("تكلفة (+)"); p = st.number_input("محصل (-)")
                        t = st.text_input("اسم الفني"); n = st.text_area("تفاصيل العمل ومواعيد الشمع")
                        if st.form_submit_button("حفظ ✅"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": n, "debt": d, "price": p, "tech": t})
                            save_data(st.session_state.data); st.rerun()
                with col2:
                    qr_data = f"{BASE_URL}?id={c['id']}"
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}")
                    st.caption("الباركود الخاص بالعميل")
                    if st.button("🗑️ حذف العميل", key=f"del_{c['id']}"):
                        st.session_state.data.remove(c); save_data(st.session_state.data); st.rerun()
    else: st.info("ابحث للبدء...")

elif menu == "➕ إضافة عميل":
    with st.form("new"):
        n = st.text_input("الاسم"); p = st.text_input("التليفون"); d = st.number_input("مديونية سابقة")
        if st.form_submit_button("إضافة"):
            new_id = max([x['id'] for x in st.session_state.data], default=1000) + 1
            st.session_state.data.append({"id": new_id, "name": n, "phone": p, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "debt": d, "price": 0}]})
            save_data(st.session_state.data); st.success("تم الحفظ!"); st.rerun()

elif menu == "📂 النسخ الاحتياطي":
    st.download_button("📥 تحميل الداتا", json.dumps(st.session_state.data, ensure_ascii=False), "backup.json"()
