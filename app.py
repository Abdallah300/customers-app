import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام وإعدادات الصفحة ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded" # تجعل القائمة تفتح تلقائياً إذا كانت الشاشة تسمح
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق الكروت */
    .metric-container { background: rgba(0, 212, 255, 0.1); border: 2px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center; margin: 10px; }
    .metric-value { color: #00d4ff; font-size: 28px; font-weight: bold; }
    .logo-text { font-size: 40px; font-weight: bold; color: #00d4ff; text-align: center; display: block; text-shadow: 2px 2px 10px #007bff; padding: 10px; }
    
    /* تحسين شكل التابات (Tabs) لتكون بديلة للقائمة الجانبية */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { 
        background-color: rgba(0, 212, 255, 0.1); 
        border-radius: 10px 10px 0px 0px; 
        padding: 10px 20px;
        color: white !important;
    }
    
    /* تأكيد ظهور زر القائمة الجانبية */
    header { visibility: visible !important; }
    footer { visibility: hidden; }
    
    .stTextInput input, .stNumberInput input { 
        background-color: #ffffff !important; color: #000 !important; 
    }
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
    st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول المدير", use_container_width=True): 
        st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفنيين", use_container_width=True): 
        st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- صفحات الدخول ---
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    if not t_names: st.error("لا يوجد فنيين مسجلين")
    else:
        t_user = st.selectbox("اختر اسمك", t_names)
        p = st.text_input("كلمة السر", type="password")
        if st.button("دخول"):
            tech = next(t for t in st.session_state.techs if t['name'] == t_user)
            if p == tech['pass']: 
                st.session_state.role = "tech_panel"; st.session_state.current_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 4. واجهة المدير (باستخدام التابات لحل مشكلة القائمة) ==================
if st.session_state.role == "admin":
    st.markdown("<h2 style='text-align:center;'>نظام الإدارة</h2>", unsafe_allow_html=True)
    
    # هذه التابات تظهر في صدر الصفحة وتغنيك عن القائمة الجانبية المخفية
    tab_cust, tab_add, tab_tech, tab_fin = st.tabs(["👥 العملاء", "➕ إضافة عميل", "🛠️ التقارير", "📊 المالية"])

    with tab_fin:
        t_out = sum(calculate_balance(c['history']) for c in st.session_state.data)
        t_in = sum(sum(float(h.get('price', 0)) for h in c['history']) for c in st.session_state.data)
        m1, m2 = st.columns(2)
        with m1: st.markdown(f"<div class='metric-container'>مديونية خارجية<br><span class='metric-value'>{t_out:,.0f}</span></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'>إجمالي المحصل<br><span class='metric-value'>{t_in:,.0f}</span></div>", unsafe_allow_html=True)

    with tab_cust:
        search = st.text_input("🔍 ابحث هنا بالاسم أو الكود...")
        filtered = [c for c in st.session_state.data if search.lower() in c['name'].lower() or search == str(c['id'])]
        for c in filtered:
            with st.expander(f"👤 {c['name']} (رصيد: {calculate_balance(c['history']):,.0f})"):
                # نموذج تحديث بيانات العميل هنا
                st.write(f"رقم الهاتف: {c.get('phone', 'غير مسجل')}")
                if st.button(f"حذف {c['id']}", key=f"del{c['id']}"):
                    st.session_state.data.remove(c); save_and_refresh("customers.json", st.session_state.data); st.rerun()

    with tab_add:
        with st.form("new_cust"):
            n = st.text_input("الاسم"); ph = st.text_input("الهاتف"); d = st.number_input("مديونية سابقة")
            if st.form_submit_button("إضافة العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": ph, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0}]})
                save_and_refresh("customers.json", st.session_state.data); st.success("تمت الإضافة"); st.rerun()

    with tab_tech:
        st.write("إدارة الفنيين")
        with st.expander("➕ إضافة فني"):
            tn = st.text_input("الاسم"); tp = st.text_input("السر")
            if st.button("حفظ"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_and_refresh("techs.json", st.session_state.techs); st.rerun()

    if st.button("🚪 تسجيل الخروج", use_container_width=True):
        del st.session_state.role; st.rerun()

# ================== 5. واجهة الفني ==================
elif st.session_state.role == "tech_panel":
    st.markdown(f"<h3 style='text-align:center;'>مرحباً فني: {st.session_state.current_tech}</h3>", unsafe_allow_html=True)
    
    t_tab1, t_tab2 = st.tabs(["📋 تسجيل مأمورية", "💰 حسابي"])
    
    with t_tab1:
        cust_names = {f"{c['id']} - {c['name']}": c for c in st.session_state.data}
        choice = st.selectbox("اختر العميل", [""] + list(cust_names.keys()))
        if choice:
            selected = cust_names[choice]
            with st.form("tech_work"):
                cost = st.number_input("تكلفة الصيانة")
                paid = st.number_input("المبلغ المحصل")
                note = st.text_area("ماذا تم في الزيارة؟")
                if st.form_submit_button("إرسال التقرير"):
                    selected['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.current_tech, "debt": cost, "price": paid})
                    save_and_refresh("customers.json", st.session_state.data); st.success("تم الحفظ"); st.rerun()

    with t_tab2:
        my_cash = sum(float(h.get('price', 0)) for c in st.session_state.data for h in c['history'] if h.get('tech') == st.session_state.current_tech)
        st.markdown(f"<div class='metric-container'>تحصيلك الكلي<br><span class='metric-value'>{my_cash:,.0f}</span></div>", unsafe_allow_html=True)

    if st.button("🚪 خروج"):
        del st.session_state.role; st.rerun()
