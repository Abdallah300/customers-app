import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر ==================
st.set_page_config(page_title="Power Life Pro System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-header { background: #001f3f; border-radius: 15px; padding: 20px; border: 2px solid #007bff; margin-bottom: 25px; }
    .metric-card { background: linear-gradient(135deg, #001f3f 0%, #007bff 100%); padding: 15px; border-radius: 12px; border: 1px solid #00d4ff; text-align: center; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
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

# ================== 3. واجهة الباركود للعميل ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            current_bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><div style='font-size:18px;'>👤 <b>العميل:</b> {c['name']}</div><div style='font-size:15px; color:#00d4ff;'>📍 {c.get('gov', '---')} | 🏛️ {c.get('branch', '---')} | 📞 {c.get('phone', '---')}</div><hr style='opacity: 0.3;'><div style='text-align:center;'><p style='margin:0;'>إجمالي المديونية</p><p style='font-size:35px; color:#00ffcc; font-weight:bold; margin:0;'>{current_bal:,.0f} ج.م</p></div></div>", unsafe_allow_html=True)
            if c.get('history'):
                running_balance = 0
                history_with_balance = []
                for h in c['history']:
                    running_balance += (float(h.get('debt', 0)) - float(h.get('price', 0)))
                    h_copy = h.copy(); h_copy['after_bal'] = running_balance; history_with_balance.append(h_copy)
                for h in reversed(history_with_balance):
                    with st.container():
                        st.markdown("---")
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**📝 {h.get('note', 'عملية')}**")
                            if h.get('filters'): st.write(f"🛠️ شمع: {h.get('filters')}")
                            if float(h.get('debt', 0)) > 0: st.markdown(f"🔴 مضاف: `{h.get('debt')} ج.م`")
                            if float(h.get('price', 0)) > 0: st.markdown(f"🟢 محصل: `{h.get('price')} ج.م`")
                        with col2:
                            st.markdown(f"📅 `{h.get('date', '---')}`")
                        st.info(f"💰 المديونية بعد العملية: {h['after_bal']:,.0f} ج.م")
            st.stop()
    except: st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>نظام الإدارة 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (منطق الدخول - اختصاراً يظل كما هو)
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة المدير (الشركة) ==================
if st.session_state.role == "admin":
    admin_menu = st.sidebar.radio("القائمة", ["📊 الإحصائيات", "👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ إدارة الفنيين", "🚪 خروج"])

    if admin_menu == "📊 الإحصائيات":
        total_market = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        total_collected = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><p>أموال بالخارج</p><h3>{total_market:,.0f}</h3></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><p>إجمالي المحصل</p><h3>{total_collected:,.0f}</h3></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><p>صافي الأرباح التقديري</p><h3>{total_collected * 0.3:,.0f}</h3></div>", unsafe_allow_html=True)

    elif admin_menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم أو التليفون...")
        for i, c in enumerate(st.session_state.data):
            if search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                with st.expander(f"👤 {c['name']} (📞 {c.get('phone','---')})"):
                    col1, col2 = st.columns(2)
                    if col1.button("🗑️ حذف العميل نهائياً", key=f"del_{c['id']}"):
                        st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()
                    if col2.button("🖼️ الباركود", key=f"qr_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    
                    with st.form(f"edit_{c['id']}"):
                        c['name'] = st.text_input("تعديل الاسم", value=c['name'])
                        c['phone'] = st.text_input("تعديل التليفون", value=c.get('phone',''))
                        if st.form_submit_button("حفظ التعديلات"):
                            save_json("customers.json", st.session_state.data); st.success("تم التحديث")

    elif admin_menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("اسم العميل"); p = st.text_input("رقم التليفون")
            g = st.text_input("المحافظة"); b = st.text_input("الفرع")
            dtype = st.selectbox("نوع الجهاز", ["جديد", "قديم"])
            filters = ""
            if dtype == "قديم": filters = st.multiselect("الشمع الذي تم تغييره", ["شمعة 1", "شمعة 2", "شمعة 3", "شمعة 4", "ممبرين"])
            d = st.number_input("المديونية الافتتاحية", min_value=0.0)
            if st.form_submit_button("إضافة العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gov": g, "branch": b, "device": dtype, "history": [{"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "افتتاح حساب", "tech": "المدير", "debt": d, "price": 0, "filters": str(filters)}]})
                save_json("customers.json", st.session_state.data); st.success("تمت الإضافة")

    elif admin_menu == "🛠️ إدارة الفنيين":
        with st.form("add_t"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("كلمة سر")
            if st.form_submit_button("تسجيل"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()
        
        st.write("### تقارير الفنيين (التحصيل والزيارات)")
        for t in st.session_state.techs:
            t_name = t['name']
            t_ops = [h for c in st.session_state.data for h in c.get('history', []) if h.get('tech') == t_name]
            total_t = sum(float(o.get('price', 0)) for o in t_ops)
            with st.expander(f"🛠️ {t_name} | إجمالي التحصيل: {total_t:,.0f} ج.م"):
                st.write(f"**عدد الزيارات:** {len(t_ops)}")
                st.write("**سجل العمليات (الوقت / العميل / المبلغ / الشمع):**")
                for o in t_ops: st.write(f"- {o['date']} | مبلغ: {o['price']} | شمع: {o.get('filters','---')}")

    elif admin_menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني ==================
elif st.session_state.role == "tech":
    st.sidebar.title(f"الفني: {st.session_state.tech_name}")
    target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: x['name'])
    with st.form("visit"):
        v1 = st.number_input("تكلفة الصيانة (+)", min_value=0.0)
        v2 = st.number_input("مبلغ محصل (-)", min_value=0.0)
        f_change = st.multiselect("الشمع الذي تم تغييره", ["1", "2", "3", "4", "5", "6", "7"])
        note = st.text_area("وصف العمل")
        if st.form_submit_button("حفظ"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.tech_name, "debt": v1, "price": v2, "filters": str(f_change)})
            save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
