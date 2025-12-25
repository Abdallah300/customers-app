import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات الصفحة والتنسيق ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# الرابط الفعلي لموقعك لضمان عمل الباركود
BASE_URL = "https://xpt.streamlit.app"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { min-width: 300px !important; background-color: #0e1626 !important; border-left: 3px solid #00d4ff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* وضوح البحث */
    .stTextInput input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        font-size: 18px !important;
        border: 2px solid #00d4ff !important;
    }

    /* كروت العرض */
    .cust-card { background: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; border-radius: 15px; padding: 25px; margin-bottom: 10px; text-align: center; }
    .history-card { background: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 15px; margin-top: 5px; border-right: 5px solid #00ffcc; }
    [data-testid="sidebar-close"] { display: none; }
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

def get_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. نظام استقبال الباركود (صفحة العميل) ==================
params = st.query_params
if "id" in params:
    customer = next((c for c in st.session_state.data if str(c['id']) == str(params["id"])), None)
    if customer:
        st.markdown("<h1 style='text-align:center; color:#00d4ff;'>ملف صيانة العميل 💧</h1>", unsafe_allow_html=True)
        bal = get_balance(customer['history'])
        st.markdown(f"""<div class='cust-card'>
            <h2>العميل: {customer['name']}</h2>
            <h1 style='color:#ff4b4b;'>المبلغ المتبقي: {bal:,.0f} ج.م</h1>
            <p style='font-size:18px;'>رقم الهاتف: {customer.get('phone', '---')}</p>
        </div>""", unsafe_allow_html=True)
        
        st.subheader("🗓️ سجل الصيانات السابقة")
        for h in reversed(customer['history']):
            st.markdown(f"""<div class='history-card'>
                <p style='margin:0; color:#00d4ff;'>📅 <b>التاريخ:</b> {h.get('date')}</p>
                <p style='margin:0;'>🛠️ <b>العمل المنجز:</b> {h.get('note')}</p>
                <p style='margin:0; font-weight:bold;'>👤 <b>الفني:</b> {h.get('tech', 'الإدارة')}</p>
            </div>""", unsafe_allow_html=True)
        st.stop() # توقف هنا لعدم عرض لوحة الإدارة للعميل

# ================== 4. لوحة الإدارة والبحث ==================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00d4ff;'>باور لايف ⚙️</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("القائمة الرئيسية:", ["🔍 البحث عن عميل", "➕ إضافة عميل جديد", "📊 التقارير المالية", "📂 النسخ الاحتياطي"])

if menu == "🔍 البحث عن عميل":
    st.title("البحث السريع")
    search = st.text_input("ابحث بالاسم، الموبايل، أو الكود...").strip().lower()
    
    if search:
        res = [c for c in st.session_state.data if search in c['name'].lower() or search in str(c.get('phone','')) or search == str(c['id'])]
        if res:
            st.success(f"تم العثور على {len(res)} نتيجة")
            for c in res:
                bal = get_balance(c['history'])
                with st.expander(f"👤 {c['name']} - كود: {c['id']} - الرصيد: {bal:,.0f}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        with st.form(f"visit_{c['id']}"):
                            st.write("📝 تسجيل زيارة صيانة")
                            d = st.number_input("تكلفة الصيانة (+)", min_value=0.0)
                            p = st.number_input("تحصيل مبلغ (-)", min_value=0.0)
                            t = st.text_input("اسم الفني")
                            n = st.text_area("ملاحظات الصيانة")
                            if st.form_submit_button("حفظ الزيارة"):
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": n, "debt": d, "price": p, "tech": t})
                                save_data(st.session_state.data); st.success("تم الحفظ"); st.rerun()
                    with col2:
                        qr_url = f"{BASE_URL}/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_url}")
                        st.caption("مسح الباركود لفتح صفحة العميل")
                        if st.button("🗑️ حذف العميل", key=f"del_{c['id']}"):
                            st.session_state.data.remove(c); save_data(st.session_state.data); st.rerun()
        else: st.warning("لا توجد نتائج مطابقة")
    else: st.info("💡 اكتب بيانات العميل في خانة البحث للبدء...")

elif menu == "➕ إضافة عميل جديد":
    with st.form("new_cust"):
        st.subheader("تسجيل بيانات عميل")
        n = st.text_input("الاسم بالكامل")
        ph = st.text_input("رقم الموبايل")
        db = st.number_input("مديونية افتتاحية", min_value=0.0)
        if st.form_submit_button("إضافة"):
            new_id = max([x['id'] for x in st.session_state.data], default=100) + 1
            st.session_state.data.append({"id": new_id, "name": n, "phone": ph, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "debt": db, "price": 0}]})
            save_data(st.session_state.data); st.success(f"تمت الإضافة بنجاح كود: {new_id}")

elif menu == "📂 النسخ الاحتياطي":
    st.subheader("تحميل نسخة من الداتا")
    st.download_button("📥 تحميل ملف JSON", json.dumps(st.session_state.data, ensure_ascii=False), "power_life_data.json"()
