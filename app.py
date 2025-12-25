import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات الصفحة والتنسيق (الرؤية الواضحة) ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* خلفية داكنة مع نصوص بيضاء واضحة جداً */
    [data-testid="stAppViewContainer"] { background: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0e1626 !important; border-left: 3px solid #00d4ff; }
    
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق البحث: خلفية بيضاء وخط أسود عريض للرؤية في الشمس */
    .stTextInput input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        border: 2px solid #00d4ff !important;
    }

    /* كروت المعلومات المالية */
    .metric-container { 
        background: rgba(0, 212, 255, 0.1); 
        border: 1px solid #00d4ff; 
        border-radius: 12px; 
        padding: 15px; 
        text-align: center; 
        margin-bottom: 10px; 
    }
    .metric-value { color: #00ffcc; font-size: 24px; font-weight: bold; }

    header { visibility: visible !important; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات (الربط بملفات JSON) ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تحميل البيانات عند بدء التطبيق
if 'data' not in st.session_state:
    st.session_state.data = load_json("customers.json", [])
    st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    try: return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
    except: return 0.0

# ================== 3. نظام تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life System 💧</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (منطق الدخول للمدير والفني)
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_names)
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech_data = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech_data['pass']: 
            st.session_state.role = "tech_panel"; st.session_state.current_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 4. لوحة تحكم المدير (كاملة) ==================
if st.session_state.role == "admin":
    with st.sidebar:
        st.markdown("<h2 style='color:#00d4ff; text-align:center;'>لوحة التحكم</h2>", unsafe_allow_html=True)
        menu = st.radio("انتقل إلى:", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "📊 المالية", "🚪 خروج"])

    # --- القسم 1: إدارة العملاء والبحث الذكي ---
    if menu == "👥 إدارة العملاء":
        st.subheader("إدارة بيانات العملاء")
        search_query = st.text_input("🔍 ابحث فوراً (بالاسم، الكود، أو التليفون)...")
        
        # محرك البحث الذكي
        s = search_query.strip().lower()
        filtered = [c for c in st.session_state.data if s in c['name'].lower() or s in str(c.get('phone','')) or s == str(c['id'])] if s else st.session_state.data
        
        for c in filtered:
            bal = calculate_balance(c['history'])
            with st.expander(f"👤 {c['name']} | كود: {c['id']} | رصيد: {bal:,.0f} ج.م"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    # تسجيل عملية مالية
                    with st.form(key=f"form_{c['id']}"):
                        st.write("📝 تسجيل صيانة / تحصيل")
                        debt = st.number_input("تكلفة (+)", 0.0, key=f"d_{c['id']}")
                        price = st.number_input("محصل (-)", 0.0, key=f"p_{c['id']}")
                        note = st.text_input("ملاحظات", key=f"n_{c['id']}")
                        if st.form_submit_button("حفظ العملية"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": note, "debt": debt, "price": price, "tech": "المدير"})
                            save_data("customers.json", st.session_state.data); st.success("تم الحفظ"); st.rerun()
                with col2:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={c['id']}")
                    st.write(f"📞 {c.get('phone', 'بدون تليفون')}")
                    if st.button("🗑️ حذف", key=f"del_{c['id']}"):
                        st.session_state.data.remove(c); save_data("customers.json", st.session_state.data); st.rerun()

    # --- القسم 2: إضافة عميل ---
    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("اسم العميل الجديد"); p = st.text_input("رقم التليفون"); d = st.number_input("مديونية افتتاحية")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "debt": d, "price": 0}]})
                save_data("customers.json", st.session_state.data); st.success("تمت الإضافة"); st.rerun()

    # --- القسم 3: إدارة الفنيين ---
    elif menu == "🛠️ الفنيين":
        st.subheader("إدارة طاقم الفنيين")
        with st.expander("➕ إضافة فني جديد"):
            tn = st.text_input("الاسم"); tp = st.text_input("كلمة السر")
            if st.button("حفظ الفني"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_data("techs.json", st.session_state.techs); st.rerun()
        st.write("قائمة الفنيين:")
        for t in st.session_state.techs: st.text(f"🛠️ {t['name']}")

    # --- القسم 4: المالية ---
    elif menu == "📊 المالية":
        t_out = sum(calculate_balance(c['history']) for c in st.session_state.data)
        st.markdown(f"<div class='metric-container'><h3>إجمالي مديونيات العملاء</h3><h1 class='metric-value'>{t_out:,.0f} ج.م</h1></div>", unsafe_allow_html=True)

    if menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 5. لوحة تحكم الفني (تسجيل مأموريات) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: **{st.session_state.current_tech}**")
    t_choice = st.sidebar.radio("القائمة", ["📋 تنفيذ مأمورية", "🚪 خروج"])
    
    if t_choice == "📋 تنفيذ مأمورية":
        st.subheader("تسجيل زيارة عميل")
        search_t = st.text_input("🔍 ابحث عن العميل (اسم/كود/تليفون)")
        st.write("---")
        # نفس محرك البحث الذكي للفني
        s_t = search_t.strip().lower()
        t_filtered = [c for c in st.session_state.data if s_t in c['name'].lower() or s_t in str(c.get('phone','')) or s_t == str(c['id'])] if s_t else []
        
        for c in t_filtered:
            with st.expander(f"👤 {c['name']} (رصيد: {calculate_balance(c['history']):,.0f})"):
                with st.form(f"tech_f_{c['id']}"):
                    d = st.number_input("تكلفة صيانة"); p = st.number_input("المحصل"); n = st.text_area("ملاحظات")
                    if st.form_submit_button("إرسال التقرير للمدير"):
                        c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": n, "debt": d, "price": p, "tech": st.session_state.current_tech})
                        save_data("customers.json", st.session_state.data); st.success("تم الإرسال"); st.rerun()
    
    if t_choice == "🚪 خروج": del st.session_state.role; st.rerun()
