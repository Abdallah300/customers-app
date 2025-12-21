import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (إرجاع النظام الأصلي) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق كروت المالية والمدير الأصلية */
    .metric-container { background: rgba(0, 212, 255, 0.1); border: 2px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center; margin: 10px; }
    .metric-title { color: #ffffff; font-size: 18px; font-weight: bold; }
    .metric-value { color: #00d4ff; font-size: 28px; font-weight: bold; }
    
    /* تنسيق واجهة الفني الجديدة (تحسين الوضوح) */
    .tech-box { background: #001f3f; border: 1px solid #00d4ff; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
    .stTextInput input, .stNumberInput input, .stSelectbox div { background-color: #ffffff !important; color: #000000 !important; }
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
    try: return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
    except: return 0.0

# ================== 3. واجهة الباركود (بدون تعديل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.title(f"مرحباً: {c['name']}")
            bal = calculate_balance(c.get('history', []))
            st.subheader(f"إجمالي المتبقي: {bal:,.0f} ج.م")
            st.write("---")
            for h in reversed(c.get('history', [])):
                st.write(f"📅 {h['date']} | 📝 {h['note']}")
                st.write(f"💰 دفع: {h.get('price',0)} | 🛠️ تكلفة: {h.get('debt',0)}")
                st.write("---")
            st.stop()
    except: st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.title("Power Life 💧")
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير"): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_names) if t_names else st.error("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech_data = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech_data['pass']: st.session_state.role = "tech_panel"; st.session_state.current_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة المدير (رجعت زي ما كانت بالظبط) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## لوحة التحكم")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📊 المالية":
        st.header("📊 التقارير المالية")
        t_out = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        t_in = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        t_serv = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-container'><div class='metric-title'>مديونية بره</div><div class='metric-value'>{t_out:,.0f}</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'><div class='metric-title'>إجمالي المحصل</div><div class='metric-value'>{t_in:,.0f}</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-container'><div class='metric-title'>صافي الأرباح</div><div class='metric-value'>{(t_in - (t_serv*0.4)):,.0f}</div></div>", unsafe_allow_html=True)

    elif menu == "🛠️ تقارير الفنيين":
        st.header("🛠️ سجل الفنيين")
        all_v = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') and h.get('tech') != "المدير":
                    all_v.append({"الفني": h['tech'], "العميل": c['name'], "التاريخ": h['date'], "المحصل": h.get('price', 0), "البيان": h['note']})
        if all_v: st.table(pd.DataFrame(all_v))
        with st.expander("إضافة فني جديد"):
            tn, tp = st.text_input("الاسم"), st.text_input("السر")
            if st.button("حفظ"): st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "➕ إضافة عميل":
        st.header("➕ إضافة عميل جديد")
        with st.form("add_form"):
            n, p, loc, d = st.text_input("الاسم"), st.text_input("التليفون"), st.text_input("GPS"), st.number_input("دين سابق")
            if st.form_submit_button("إضافة العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحي", "debt": d, "price": 0}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم الإضافة بكود: {new_id}")

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 بحث عن عميل...")
        if search:
            results = [c for c in st.session_state.data if search.lower() in c['name'].lower() or search in str(c['id'])]
            for c in results:
                st.info(f"👤 {c['name']} (كود: {c['id']})")
                with st.expander("إضافة عملية"):
                    d1, d2 = st.number_input("تكلفة", key=f"d{c['id']}"), st.number_input("تحصيل", key=f"p{c['id']}")
                    nt = st.text_input("البيان", key=f"n{c['id']}")
                    if st.button("حفظ", key=f"b{c['id']}"):
                        c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": nt, "tech": "المدير", "debt": d1, "price": d2})
                        save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (تعديل المطلوب فقط) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.title(f"🛠️ {st.session_state.current_tech}")
    t_tab = st.sidebar.radio("القائمة", ["📋 مهمة جديدة", "💰 تقريري", "🚪 خروج"])

    if t_tab == "📋 مهمة جديدة":
        st.subheader("🔍 ابحث عن العميل")
        s_q = st.text_input("ابحث بالاسم أو الكود أو التليفون")
        if s_q:
            res = [c for c in st.session_state.data if s_q.lower() in c['name'].lower() or s_q in str(c['id']) or s_q in str(c.get('phone',''))]
            if res:
                c_map = {f"{x['id']} - {x['name']}": x for x in res}
                selected = c_map[st.selectbox("اختر العميل:", list(c_map.keys()))]
                
                if selected.get('gps'): st.link_button("📍 موقع العميل", selected['gps'])
                
                with st.form("tech_f"):
                    v_d, v_p = st.number_input("التكلفة (+)"), st.number_input("المحصل (-)")
                    v_s = st.multiselect("الشمع:", ["شمعة 1", "2", "3", "4", "5", "6", "7", "ممبرين"])
                    v_n = st.text_area("ماذا تم؟")
                    if st.form_submit_button("إرسال التقرير"):
                        for x in st.session_state.data:
                            if x['id'] == selected['id']:
                                x.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": v_n, "tech": st.session_state.current_tech, "debt": v_d, "price": v_p, "filter_used": ", ".join(v_s)})
                        save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
            else: st.warning("لا يوجد نتائج")

    elif t_tab == "💰 تقريري":
        my_cash = 0.0; my_v = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') == st.session_state.current_tech:
                    my_cash += float(h.get('price', 0))
                    my_v.append({"العميل": c['name'], "المحصل": h.get('price', 0), "الشمع": h.get('filter_used', '')})
        st.metric("💰 المحصل معك", f"{my_cash:,.0f} ج.م")
        if my_v: st.table(pd.DataFrame(my_v))

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
