import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات المظهر (نظيف ومبسط) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #011627 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق كارت البيانات الأساسية */
    .client-header { 
        background: rgba(255, 255, 255, 0.05); border-radius: 12px; 
        padding: 15px; border: 1px solid #00d4ff; margin-bottom: 20px; 
    }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. صفحة العميل (الباركود) - بدون أخطاء HTML ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h2 style='text-align:center;'>Power Life 💧</h2>", unsafe_allow_html=True)
            
            # رأس التقرير (بيانات العميل)
            with st.container():
                st.markdown(f"""
                <div class='client-header'>
                    <p style='margin:0;'>👤 <b>الاسم:</b> {c['name']}</p>
                    <p style='margin:5px 0;'>📍 <b>المحافظة:</b> {c.get('gov', '---')} | 🏛️ <b>الفرع:</b> {c.get('branch', '---')}</p>
                    <hr style='opacity:0.2;'>
                    <p style='text-align:center; margin:0;'>إجمالي المديونية الحالية</p>
                    <p style='text-align:center; font-size:28px; color:#00d4ff; font-weight:bold;'>{calculate_balance(c.get('history', [])):,.0f} ج.م</p>
                </div>
                """, unsafe_allow_html=True)

            st.subheader("📋 سجل العمليات")
            
            # عرض العمليات بنظام الكروت النظيفة (Streamlit Native)
            if c.get('history'):
                for h in reversed(c['history']):
                    # نستخدم st.container مع خلفية بيضاء لعمل "كارت" بدون أكواد HTML معقدة
                    with st.expander(f"📅 {h.get('date', '---')} | 📝 {h.get('note', 'تسوية')}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            if float(h.get('debt', 0)) > 0:
                                st.error(f"➕ مضاف: {h.get('debt', 0)} ج.م")
                            if float(h.get('price', 0)) > 0:
                                st.success(f"➖ مخصوم: {h.get('price', 0)} ج.م")
                        with col2:
                            st.info(f"👤 المسؤول: {h.get('tech', 'الإدارة')}")
            else:
                st.info("لا توجد عمليات مسجلة.")
            st.stop()
    except:
        st.stop()

# ================== 4. لوحة التحكم (الدخول) ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>لوحة التحكم 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (منطق الدخول للإدارة والفني)
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("الفني", t_list) if t_list else st.error("لا يوجد فنيين")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech"; st.session_state.tech_name = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الإدارة والعمليات ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "➕ إضافة عميل", "🚪 خروج"])

    if menu == "👥 العملاء":
        search = st.text_input("بحث...")
        for i, c in enumerate(st.session_state.data):
            if search in c['name']:
                with st.expander(f"👤 {c['name']}"):
                    with st.form(f"f_{c['id']}"):
                        c['gov'] = st.text_input("المحافظة", value=c.get('gov', ''))
                        c['branch'] = st.text_input("الفرع", value=c.get('branch', ''))
                        a_add = st.number_input("إضافة مديونية", min_value=0.0)
                        a_rem = st.number_input("إزالة مديونية", min_value=0.0)
                        if st.form_submit_button("حفظ"):
                            if a_add > 0 or a_rem > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تسويه إدارية", "tech": "الإدارة", "debt": a_add, "price": a_rem})
                            save_json("customers.json", st.session_state.data); st.rerun()
                    if st.button("🖼️ باركود", key=f"q_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")

    elif menu == "➕ إضافة عميل":
        with st.form("add"):
            name = st.text_input("الاسم")
            gov = st.text_input("المحافظة")
            branch = st.text_input("الفرع")
            debt = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("حفظ"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "gov": gov, "branch": branch, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "debt": debt, "price": 0}] if debt > 0 else []})
                save_json("customers.json", st.session_state.data); st.success("تم")
    
    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

elif st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ {st.session_state.tech_name}")
    target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: x['name'])
    with st.form("tf"):
        v1 = st.number_input("إضافة مديونية", min_value=0.0)
        v2 = st.number_input("إزالة مديونية", min_value=0.0)
        note = st.text_area("وصف العمل")
        if st.form_submit_button("حفظ"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.tech_name, "debt": v1, "price": v2})
            save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()                            
