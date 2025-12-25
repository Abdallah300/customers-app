import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات الواجهة والتصميم ==================
st.set_page_config(page_title="Power Life System", layout="wide", initial_sidebar_state="expanded")

# الرابط الحالي لموقعك (تأكد إنه مطابق لـ xpt.streamlit.app)
BASE_URL = "https://xpt.streamlit.app"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { min-width: 300px !important; background-color: #0e1626 !important; border-left: 3px solid #00d4ff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تصميم سجل العمليات للعميل (نفس شكل الصورة المطلوبة) */
    .client-header { background: linear-gradient(90deg, #001f3f, #000b1a); border: 2px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 30px; }
    .balance-box { border: 2px solid #00ffcc; border-radius: 10px; padding: 15px; display: inline-block; margin-top: 10px; }
    .history-item { background: #071221; border-radius: 10px; padding: 15px; margin-bottom: 15px; border-right: 5px solid #00d4ff; }
    .price-tag { color: #00ffcc; font-weight: bold; }
    .debt-tag { color: #ff4b4b; font-weight: bold; }
    
    /* وضوح البحث للمدير */
    .stTextInput input { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; font-size: 18px !important; border: 2px solid #00d4ff !important; }
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

# ================== 3. صفحة العميل (تفتح من الباركود فقط) ==================
params = st.query_params
if "id" in params:
    # إخفاء كل أدوات المدير تماماً
    st.markdown("<style>[data-testid='stSidebar'], [data-testid='stHeader'] {display:none !important;}</style>", unsafe_allow_html=True)
    
    cust = next((c for c in st.session_state.data if str(c['id']) == str(params["id"])), None)
    if cust:
        st.markdown(f"""
        <div class="client-header">
            <h2 style="color:#00d4ff; margin:0;">ملف صيانة العميل: {cust['name']}</h2>
            <div class="balance-box">
                <h3 style="margin:0;">إجمالي المتبقي:</h3>
                <h1 style="color:#00ffcc; margin:5px 0;">{calc_bal(cust['history']):,.0f} ج.م</h1>
            </div>
        </div>
        <h2 style="text-align:right;">📑 سجل العمليات</h2>
        """, unsafe_allow_html=True)
        
        for h in reversed(cust['history']):
            st.markdown(f"""
            <div class="history-item">
                <p style="margin:0; font-size:18px;">📅 <b>التاريخ:</b> {h.get('date')}</p>
                <p style="margin:5px 0;">📝 <b>البيان:</b> {h.get('note', 'صيانة دورية')}</p>
                <div style="display:flex; justify-content:space-between; margin-top:10px;">
                    <span class="price-tag">💰 تم دفع: {h.get('price', 0)} ج.م</span>
                    <span class="debt-tag">🛠️ تكلفة: {h.get('debt', 0)} ج.م</span>
                </div>
                <p style="margin-top:10px; font-size:14px; color:#888;">👤 الفني: {h.get('tech', 'إدارة الشركة')}</p>
            </div>
            """, unsafe_allow_html=True)
        st.stop() # يمنع ظهور السستم

# ================== 4. لوحة المدير (البحث والوظائف) ==================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00d4ff;'>POWER LIFE</h2>", unsafe_allow_html=True)
    menu = st.radio("القائمة:", ["🔍 بحث عن عميل", "➕ إضافة عميل", "📂 النسخ الاحتياطي"])

if menu == "🔍 بحث عن عميل":
    st.title("البحث السريع")
    query = st.text_input("ابحث هنا...").strip().lower()
    if query:
        res = [c for c in st.session_state.data if query in c['name'].lower() or query in str(c.get('phone','')) or query == str(c['id'])]
        for c in res:
            bal = calc_bal(c['history'])
            with st.expander(f"👤 {c['name']} | كود: {c['id']} | رصيد: {bal}"):
                c1, c2 = st.columns([2, 1])
                with c1:
                    with st.form(f"up_{c['id']}"):
                        d = st.number_input("تكلفة صيانة (+)"); p = st.number_input("تحصيل مبلغ (-)")
                        t = st.text_input("اسم الفني"); n = st.text_area("تفاصيل العمل ومواعيد الشمع")
                        if st.form_submit_button("حفظ"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": n, "debt": d, "price": p, "tech": t})
                            save_db(st.session_state.data); st.rerun()
                with c2:
                    qr_link = f"{BASE_URL}?id={c['id']}"
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}")
                    st.caption("باركود صفحة العميل")
                    if st.button("🗑️ حذف", key=f"del_{c['id']}"):
                        st.session_state.data.remove(c); save_db(st.session_state.data); st.rerun()
    else: st.info("اكتب للبحث...")

elif menu == "➕ إضافة عميل":
    with st.form("new"):
        n = st.text_input("الاسم"); p = st.text_input("التليفون"); d = st.number_input("مديونية سابقة")
        if st.form_submit_button("إضافة"):
            new_id = max([x['id'] for x in st.session_state.data], default=1000) + 1
            st.session_state.data.append({"id": new_id, "name": n, "phone": p, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "debt": d, "price": 0}]})
            save_db(st.session_state.data); st.rerun()

elif menu == "📂 النسخ الاحتياطي":
    st.download_button("📥 تحميل الداتا", json.dumps(st.session_state.data, ensure_ascii=False), "backup.json")
