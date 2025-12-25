import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات الصفحة والتثبيت الإجباري للقائمة ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* تثبيت القائمة الجانبية ومنع اختفائها */
    [data-testid="stSidebar"] {
        min-width: 300px !important;
        background-color: #0e1626 !important;
        border-left: 3px solid #00d4ff;
    }
    
    /* تحسين الرؤية والألوان */
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }

    /* جعل مربع البحث أبيض صريح للوضوح التام */
    .stTextInput input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        font-size: 18px !important;
        border: 2px solid #00d4ff !important;
    }

    /* تنسيق الكروت المالية */
    .metric-container { 
        background: rgba(0, 212, 255, 0.1); 
        border: 1px solid #00d4ff; 
        border-radius: 12px; 
        padding: 15px; 
        text-align: center; 
        margin-bottom: 10px; 
    }
    .metric-value { color: #00ffcc; font-size: 24px; font-weight: bold; }
    
    /* إخفاء زر إغلاق السايد بار لضمان بقائه مفتوحاً */
    [data-testid="sidebar-close"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات (الربط بملفات JSON) ==================
def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تحميل البيانات في الذاكرة
if 'data' not in st.session_state:
    st.session_state.data = load_data("customers.json", [])
    st.session_state.techs = load_data("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life System 💧</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# منطق الدخول (تم اختصاره للتوضيح، يمكنك إضافة كلمة السر)
if st.session_state.role == "admin_login":
    if st.button("دخول كمدير (تجريبي)"): st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 4. لوحة التحكم (السايد بار ثابت ومفتوح) ==================
if st.session_state.role == "admin":
    with st.sidebar:
        st.markdown("<h2 style='color:#00d4ff; text-align:center;'>لوحة الإدارة</h2>", unsafe_allow_html=True)
        menu = st.radio("القائمة:", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        st.subheader("إدارة بيانات العملاء والبحث")
        # البحث الذكي بالاسم أو الكود أو التليفون
        search = st.text_input("🔍 ابحث هنا (اسم / كود / تليفون)...").strip().lower()
        
        filtered = [c for c in st.session_state.data if search in c['name'].lower() or search in str(c.get('phone','')) or search == str(c['id'])] if search else st.session_state.data
        
        for c in filtered:
            bal = calculate_balance(c['history'])
            with st.expander(f"👤 {c['name']} | كود: {c['id']} | رصيد: {bal:,.0f}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    with st.form(f"f_{c['id']}"):
                        d = st.number_input("تكلفة (+)"); p = st.number_input("محصل (-)"); n = st.text_input("ملاحظات")
                        if st.form_submit_button("حفظ العملية"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": n, "debt": d, "price": p})
                            save_data("customers.json", st.session_state.data); st.rerun()
                with col2:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={c['id']}")
                    if st.button("🗑️ حذف العميل", key=f"del_{c['id']}"):
                        st.session_state.data.remove(c); save_data("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new"):
            n = st.text_input("الاسم"); p = st.text_input("التليفون"); d = st.number_input("مديونية افتتاحية")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0}]})
                save_data("customers.json", st.session_state.data); st.success("تم!"); st.rerun()

    elif menu == "📊 المالية":
        total = sum(calculate_balance(c['history']) for c in st.session_state.data)
        st.markdown(f"<div class='metric-container'><h3>إجمالي المديونية بالخارج</h3><h1 class='metric-value'>{total:,.0f} ج.م</h1></div>", unsafe_allow_html=True)

    if menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 5. لوحة الفني ==================
elif st.session_state.role == "tech_panel":
    # كود الفني بنفس نظام البحث والسايد بار الثابت
    st.sidebar.write("لوحة الفني")
    if st.sidebar.button("خروج"): del st.session_state.role; st.rerun()
