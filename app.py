import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات الصفحة والتنسيق (الاستايل الاحترافي) ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded" # لجعل القائمة الجانبية مفتوحة تلقائياً
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* تنسيق الخلفية العامة */
    [data-testid="stAppViewContainer"] { background: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { 
        background-color: #0e1117 !important; 
        border-left: 2px solid #00d4ff;
        min-width: 250px !important;
    }
    
    /* الخطوط والاتجاهات */
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق أزرار القائمة الجانبية (Radio Buttons) لتشبه الصورة الثانية */
    .stRadio > div { direction: rtl; gap: 10px; }
    .stRadio label { 
        background: rgba(255, 255, 255, 0.05); 
        border-radius: 8px; 
        padding: 10px !important; 
        margin-bottom: 5px;
        transition: 0.3s;
    }
    .stRadio label:hover { background: rgba(0, 212, 255, 0.2); }

    /* صناديق المعلومات (Metrics) */
    .metric-container { 
        background: rgba(0, 212, 255, 0.1); 
        border: 1px solid #00d4ff; 
        border-radius: 12px; 
        padding: 15px; 
        text-align: center; 
        margin-bottom: 20px; 
    }
    .metric-value { color: #00ffcc; font-size: 26px; font-weight: bold; }

    /* تحسين رؤية مربعات الإدخال */
    .stTextInput input, .stNumberInput input, .stSelectbox div { 
        background-color: #1a212d !important; 
        color: #ffffff !important; 
        border: 1px solid #3d4450 !important;
        border-radius: 8px !important;
    }
    
    /* إظهار زر القائمة في الموبايل */
    header { visibility: visible !important; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات ==================
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

# ================== 3. نظام تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#00d4ff; margin-top:50px;'>Power Life System 💧</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 لوحة المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    with col2:
        if st.button("🛠️ لوحة الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (منطق الدخول للمدير والفني)
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
        else: st.error("خطأ في البيانات")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 4. لوحة التحكم (بالقائمة الجانبية كما في الصورة 2) ==================
if st.session_state.role == "admin":
    with st.sidebar:
        st.markdown("<h2 style='color:#00d4ff; text-align:center;'>التحكم الرئيسي</h2>", unsafe_allow_html=True)
        st.write("---")
        # القائمة الجانبية المطلوبة
        menu = st.radio("اختر القسم:", [
            "👥 إدارة العملاء", 
            "➕ إضافة عميل", 
            "🛠️ إدارة الفنيين", 
            "📊 التقارير المالية", 
            "🚪 خروج"
        ])
        st.write("---")
        st.info("نظام باور لايف v2.0")

    # --- محتوى الأقسام ---
    if menu == "👥 إدارة العملاء":
        st.subheader("إدارة بيانات العملاء")
        search = st.text_input("🔍 ابحث بالكود أو الاسم...")
        q = search.strip().lower()
        filtered = [c for c in st.session_state.data if q in c['name'].lower() or q == str(c['id'])]
        
        for c in filtered:
            bal = calculate_balance(c['history'])
            with st.expander(f"👤 {c['name']} (كود: {c['id']})"):
                col_info, col_qr = st.columns([2, 1])
                with col_info:
                    st.markdown(f"<div class='metric-container'>الرصيد الحالي:<br><span class='metric-value'>{bal:,.0f} ج.م</span></div>", unsafe_allow_html=True)
                    # نموذج تحديث البيانات كما في الصورة 1
                    with st.form(f"update_{c['id']}"):
                        st.write("تحديث بيانات العميل:")
                        new_name = st.text_input("الاسم", value=c['name'])
                        new_phone = st.text_input("التليفون", value=c.get('phone',''))
                        if st.form_submit_button("حفظ التعديلات"):
                            c['name'] = new_name
                            c['phone'] = new_phone
                            save_and_refresh("customers.json", st.session_state.data)
                            st.success("تم التحديث")
                with col_qr:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={c['id']}", caption="QR كود العميل")
                    if st.button("🗑️ حذف العميل", key=f"del{c['id']}"):
                        st.session_state.data.remove(c); save_and_refresh("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل":
        st.subheader("تسجيل عميل جديد")
        with st.form("add_form"):
            n = st.text_input("اسم العميل")
            p = st.text_input("رقم التليفون")
            d = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": new_id, "name": n, "phone": p, 
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "debt": d, "price": 0}]
                })
                save_and_refresh("customers.json", st.session_state.data)
                st.success("تمت الإضافة بنجاح")

    elif menu == "📊 التقارير المالية":
        t_out = sum(calculate_balance(c['history']) for c in st.session_state.data)
        st.markdown(f"<div class='metric-container'><h3>إجمالي المديونيات بالخارج</h3><h1 class='metric-value'>{t_out:,.0f} ج.م</h1></div>", unsafe_allow_html=True)

    elif menu == "🚪 خروج":
        del st.session_state.role; st.rerun()

# ================== 5. واجهة الفني ==================
elif st.session_state.role == "tech_panel":
    # (كود واجهة الفني بنفس منطق القوائم الجانبية)
    pass
