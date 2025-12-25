import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (الواجهة الاحترافية - الصورة 2) ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* تنسيق الخلفية العامة */
    [data-testid="stAppViewContainer"] { background: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0e1117 !important; border-left: 1px solid #00d4ff; }
    
    /* الخطوط والاتجاهات */
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق العناصر الجانبية (Sidebar) */
    .stRadio [role="radiogroup"] { gap: 10px; }
    div[data-testid="stSidebarNav"] { display: none; } /* إخفاء نافذة التصفح الافتراضية */

    /* صناديق المعلومات (Metrics) */
    .metric-container { 
        background: rgba(0, 212, 255, 0.1); 
        border: 1px solid #00d4ff; 
        border-radius: 12px; 
        padding: 15px; 
        text-align: center; 
        margin-bottom: 10px; 
    }
    .metric-value { color: #00ffcc; font-size: 24px; font-weight: bold; }

    /* تحسين شكل الإدخال */
    .stTextInput input, .stNumberInput input, .stSelectbox div { 
        background-color: #1a212d !important; 
        color: #ffffff !important; 
        border: 1px solid #3d4450 !important;
    }
    
    /* الهيدر المخفي والفوتر */
    header { visibility: visible !important; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_and_refresh(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.session_state.data = load_json("customers.json", [])

if 'data' not in st.session_state:
    st.session_state.data = load_json("customers.json", [])
    st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    try: return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
    except: return 0.0

# ================== 3. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life System 💧</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير"): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (نظام الدخول مختصر للسرعة - يمكنك إضافة التحقق من كلمة السر هنا)
if st.session_state.role in ["admin_login", "tech_login"]:
    if st.button("تخطي للدخول التجريبي (أو أدخل بياناتك)"):
        st.session_state.role = "admin" if "admin" in st.session_state.role else "tech_panel"
        st.rerun()
    st.stop()

# ================== 4. واجهة التحكم الرئيسية (Sidebar) ==================
if st.session_state.role == "admin":
    # القائمة الجانبية كما في الصورة 2
    with st.sidebar:
        st.markdown("<h2 style='color:#00d4ff;'>Power Life</h2>", unsafe_allow_html=True)
        st.write("---")
        menu = st.radio("التحكم الرئيسي:", 
                        ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ إدارة الفنيين", "📊 التقارير المالية", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بالكود، الاسم أو التليفون...")
        q = search.strip().lower()
        filtered = [c for c in st.session_state.data if q in c['name'].lower() or q == str(c['id'])]
        
        for c in filtered:
            bal = calculate_balance(c['history'])
            with st.expander(f"👤 {c['name']} (كود: {c['id']})"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f"<div class='metric-container'>الرصيد الحالي:<br><span class='metric-value'>{bal:,.0f} ج.م</span></div>", unsafe_allow_html=True)
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={c['id']}")
                with col2:
                    st.write("تحديث البيانات الشخصية و GPS")
                    st.text_input("الاسم", value=c['name'], key=f"n{c['id']}")
                    st.text_input("التليفون", value=c.get('phone',''), key=f"p{c['id']}")
                    st.button("حفظ التعديلات", key=f"btn{c['id']}")

    elif menu == "➕ إضافة عميل":
        with st.container():
            st.subheader("تسجيل عميل جديد")
            n = st.text_input("اسم العميل")
            p = st.text_input("رقم التليفون")
            d = st.number_input("الرصيد الافتتاحي (مديونية)")
            if st.button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0}]})
                save_and_refresh("customers.json", st.session_state.data)
                st.success("تم الحفظ!")

    elif menu == "📊 التقارير المالية":
        t_out = sum(calculate_balance(c['history']) for c in st.session_state.data)
        st.markdown(f"<div class='metric-container'><h3>إجمالي مديونيات العملاء</h3><h1 class='metric-value'>{t_out:,.0f} ج.م</h1></div>", unsafe_allow_html=True)

    if menu == "🚪 خروج":
        del st.session_state.role; st.rerun()

# ================== 5. واجهة الفني ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.title(f"الفني: {st.session_state.get('current_tech', 'عام')}")
    if st.sidebar.button("تسجيل الخروج"): del st.session_state.role; st.rerun()
    st.write("واجهة الفني لتسجيل العمليات...")
