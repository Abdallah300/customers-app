import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (الأزرق الملكي) ==================
st.set_page_config(page_title="Power Life Ultra", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-header { background: #001f3f; border-radius: 15px; padding: 20px; border: 2px solid #007bff; margin-bottom: 25px; }
    .metric-card { background: linear-gradient(135deg, #001f3f 0%, #007bff 100%); padding: 15px; border-radius: 12px; border: 1px solid #00d4ff; text-align: center; }
    header {visibility: hidden;}
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

# ================== 3. صفحة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            current_bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><b>👤 العميل:</b> {c['name']}<br><b>📞 تليفون:</b> {c.get('phone','---')}<br><b>📍 المحافظة:</b> {c.get('gov','---')}<hr><div style='text-align:center;'><p>المديونية الحالية</p><p style='font-size:30px; color:#00ffcc;'>{current_bal:,.0f} ج.م</p></div></div>", unsafe_allow_html=True)
            
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
                            st.markdown(f"**📝 {h.get('note', 'زيارة')}**")
                            if h.get('filters'): st.write(f"🛠️ شمع: {h.get('filters')}")
                            if float(h.get('debt', 0)) > 0: st.markdown(f"🔴 مضاف: {h.get('debt')} ج.م")
                            if float(h.get('price', 0)) > 0: st.markdown(f"🟢 محصل: {h.get('price')} ج.م")
                        with col2:
                            st.markdown(f"📅 {h.get('date', '---')}")
                        st.info(f"💰 المتبقي بعد العملية: {h['after_bal']:,.0f} ج.م")
            st.stop()
    except: st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>نظام إدارة الشركة 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_list) if t_list else st.error("لا يوجد فنيين")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech"; st.session_state.tech_name = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. شاشة المدير ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["📊 الإحصائيات", "👥 إدارة وتعديل العملاء", "➕ إضافة عميل", "🛠️ إدارة الفنيين والتحصيل", "🚪 خروج"])

    if menu == "📊 الإحصائيات":
        total_market = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        total_coll = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><p>أموال بالخارج</p><h3>{total_market:,.0f}</h3></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><p>إجمالي المحصل</p><h3>{total_coll:,.0f}</h3></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><p>الأرباح (30%)</p><h3>{total_coll * 0.3:,.0f}</h3></div>", unsafe_allow_html=True)

    elif menu == "👥 إدارة وتعديل العملاء":
        search = st.text_input("ابحث عن عميل...")
        for i, c in enumerate(st.session_state.data):
            if search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                with st.expander(f"👤 {c['name']} (📞 {c.get('phone','---')})"):
                    # عرض الباركود والرابط
                    st.write("**🔗 رابط العميل والباركود:**")
                    client_url = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={client_url}")
                    st.code(client_url)
                    
                    with st.form(f"edit_{c['id']}"):
                        new_name = st.text_input("الاسم", value=c['name'])
                        new_phone = st.text_input("التليفون", value=c.get('phone',''))
                        new_gov = st.text_input("المحافظة", value=c.get('gov',''))
                        new_branch = st.text_input("الفرع", value=c.get('branch',''))
                        if st.form_submit_button("حفظ التعديلات"):
                            c.update({"name": new_name, "phone": new_phone, "gov": new_gov, "branch": new_branch})
                            save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
                    if st.button("🗑️ حذف العميل نهائياً", key=f"del_{c['id']}"):
                        st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("اسم العميل الثلاثي"); p = st.text_input("رقم التليفون")
            g = st.text_input("المحافظة"); b = st.text_input("الفرع")
            dtype = st.selectbox("نوع الجهاز", ["جديد", "قديم"])
            filters = ""
            if dtype == "قديم":
                filters = st.multiselect("الشمع الذي تم تغييره", ["1", "2", "3", "4", "5", "6", "7"])
            d = st.number_input("المديونية الافتتاحية", min_value=0.0)
            if st.form_submit_button("تسجيل العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gov": g, "branch": b, "device": dtype, "history": [{"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "افتتاح حساب", "tech": "المدير", "debt": d, "price": 0, "filters": str(filters)}]})
                save_json("customers.json", st.session_state.data); st.success("تمت الإضافة")

    elif menu == "🛠️ إدارة الفنيين والتحصيل":
        with st.form("add_t"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("كلمة السر")
            if st.form_submit_button("إضافة فني"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()
        
        st.write("### تقارير الفنيين (تحصيل حي)")
        for t in st.session_state.techs:
            t_ops = [h for c in st.session_state.data for h in c.get('history', []) if h.get('tech') == t['name']]
            total_t = sum(float(o.get('price', 0)) for o in t_ops)
            with st.expander(f"🛠️ {t['name']} | إجمالي المحصل: {total_t:,.0f} ج.م"):
                st.write(f"**عدد الزيارات:** {len(t_ops)}")
                st.write("**تفاصيل الزيارات (بالدقيقة):**")
                for o in t_ops: st.write(f"- {o['date']} | مبلغ: {o['price']} ج.م | شمع: {o.get('filters','---')}")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني ==================
elif st.session_state.role == "tech":
    st.sidebar.title(f"الفني: {st.session_state.tech_name}")
    target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
    with st.form("tech_f"):
        v1 = st.number_input("تكلفة الصيانة (+)", min_value=0.0)
        v2 = st.number_input("مبلغ محصل (-)", min_value=0.0)
        f_change = st.multiselect("الشمع الذي تم تغييره", ["1", "2", "3", "4", "5", "6", "7"])
        note = st.text_area("ملاحظات")
        if st.form_submit_button("حفظ"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.tech_name, "debt": v1, "price": v2, "filters": str(f_change)})
            save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
