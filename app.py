import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات الصفحة (فصل تام للواجهة) ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# الرابط الحالي لموقعك (تأكد أنه xpt.streamlit.app)
BASE_URL = "https://xpt.streamlit.app"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { min-width: 300px !important; background-color: #0e1626 !important; border-left: 3px solid #00d4ff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق البحث للوضوح التام */
    .stTextInput input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        font-size: 20px !important;
        border: 3px solid #00d4ff !important;
    }

    /* صفحة العميل الخارجية (تصميم منفصل) */
    .client-portal {
        background: white;
        color: black;
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        border-top: 10px solid #00d4ff;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    .history-card {
        background: #f1f8ff;
        border-right: 5px solid #00d4ff;
        padding: 15px;
        margin-top: 10px;
        border-radius: 8px;
        text-align: right;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
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

# ================== 3. صفحة العميل الخارجية (تفتح بالباركود فقط) ==================
q_params = st.query_params
if "id" in q_params:
    cid = q_params["id"]
    cust = next((c for c in st.session_state.data if str(c['id']) == str(cid)), None)
    
    if cust:
        # إخفاء السايد بار تماماً للعميل باستخدام CSS
        st.markdown("<style> [data-testid='stSidebar'] { display:none; } </style>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="client-portal">
            <h1 style="color:#007bff; margin-bottom:10px;">باور لايف لخدمات الفلاتر 💧</h1>
            <h2 style="margin:0;">ملف صيانة العميل: {cust['name']}</h2>
            <hr>
            <div style="background:#ffeded; padding:20px; border-radius:15px; margin:20px 0;">
                <h3 style="color:#d9534f; margin:0;">إجمالي المبلغ المتبقي</h3>
                <h1 style="font-size:45px; margin:10px 0;">{get_balance(cust['history']):,.0f} ج.م</h1>
            </div>
            <p style="font-size:18px; color:#555;">كود العميل: <b>{cust['id']}</b> | الهاتف: <b>{cust.get('phone', '---')}</b></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🛠️ سجل مواعيد التغيير والصيانات")
        if cust['history']:
            for h in reversed(cust['history']):
                st.markdown(f"""
                <div class="history-card">
                    <p style="margin:0; font-weight:bold; color:#007bff;">📅 التاريخ: {h.get('date')}</p>
                    <p style="margin:5px 0;">📋 البيان: {h.get('note', '---')}</p>
                    <p style="margin:0; font-size:14px; color:#666;">👤 الفني المسؤول: {h.get('tech', 'الإدارة')}</p>
                </div>
                """, unsafe_allow_html=True)
        st.stop() # إيقاف التنفيذ لضمان عدم رؤية السستم

# ================== 4. نظام الإدارة (السايد بار والبحث) ==================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00d4ff;'>لوحة التحكم ⚙️</h2>", unsafe_allow_html=True)
    menu = st.radio("القائمة:", ["🔍 بحث عن عميل", "➕ إضافة عميل", "📊 المالية", "📂 النسخ الاحتياطي"])

if menu == "🔍 بحث عن عميل":
    st.title("البحث السريع")
    search = st.text_input("ابحث هنا (اسم / تليفون / كود)...").strip().lower()
    
    if search:
        results = [c for c in st.session_state.data if search in c['name'].lower() or search in str(c.get('phone','')) or search == str(c['id'])]
        if results:
            for c in results:
                bal = get_balance(c['history'])
                with st.expander(f"👤 {c['name']} - كود: {c['id']} - رصيد: {bal:,.0f}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        with st.form(f"form_{c['id']}"):
                            st.write("تسجيل صيانة/تحصيل:")
                            debt = st.number_input("تكلفة الشمع/الصيانة (+)")
                            paid = st.number_input("المحصل من العميل (-)")
                            note = st.text_area("وصف العملية (مواعيد تغيير الشمع)")
                            tech = st.text_input("اسم الفني القائم بالعمل")
                            if st.form_submit_button("حفظ العملية"):
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "debt": debt, "price": paid, "tech": tech})
                                save_data(st.session_state.data); st.rerun()
                    with col2:
                        qr_url = f"{BASE_URL}?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_url}")
                        st.caption("الباركود الخاص بصفحة العميل الخارجية")
                        if st.button("🗑️ حذف", key=f"del_{c['id']}"):
                            st.session_state.data.remove(c); save_data(st.session_state.data); st.rerun()
    else: st.info("اكتب بيانات العميل للبحث...")

elif menu == "➕ إضافة عميل":
    with st.form("new"):
        st.subheader("إضافة عميل جديد")
        n = st.text_input("اسم العميل"); p = st.text_input("رقم الهاتف"); d = st.number_input("مديونية سابقة")
        if st.form_submit_button("حفظ العميل"):
            new_id = max([x['id'] for x in st.session_state.data], default=1000) + 1
            st.session_state.data.append({"id": new_id, "name": n, "phone": p, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "debt": d, "price": 0}]})
            save_data(st.session_state.data); st.success(f"تمت الإضافة بكود {new_id}")

elif menu == "📂 النسخ الاحتياطي":
    st.download_button("📥 تحميل كافة البيانات (JSON)", json.dumps(st.session_state.data, ensure_ascii=False), "backup.json")
