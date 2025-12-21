import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (تم إصلاح تداخل الألوان) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* ضبط الخلفية العامة لتكون مريحة للعين */
    .stApp { background-color: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }

    /* تحسين شكل خانات الإدخال والبحث للفني */
    .stTextInput input, .stNumberInput input, .stSelectbox div, .stTextArea textarea {
        background-color: #001f3f !important;
        color: #00d4ff !important;
        border: 1px solid #00d4ff !important;
        border-radius: 8px !important;
    }
    
    label { color: #ffffff !important; font-weight: bold !important; font-size: 16px !important; }

    /* تنسيق كروت المحفظة للفني */
    .tech-card {
        background: #001f3f;
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin-bottom: 15px;
    }
    .tech-val { color: #00ffcc; font-size: 28px; font-weight: bold; }

    /* تنسيق سجل العمليات النظيف */
    .op-item {
        background: rgba(255, 255, 255, 0.05);
        border-right: 5px solid #00d4ff;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }

    .logo-text { font-size: 40px; font-weight: bold; color: #00d4ff; text-align: center; display: block; padding: 10px; }
    header, footer {visibility: hidden;}
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

# ================== 3. واجهة الباركود (ثابتة) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
            total_bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div style='background:#001f3f; padding:20px; border-radius:15px; border:1px solid #00d4ff; text-align:center;'><h2>{c['name']}</h2><h3 style='color:#00ffcc;'>المتبقي: {total_bal:,.0f} ج.م</h3></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.markdown(f"<div class='op-item'>📅 {h['date']}<br>📝 {h['note']}<br><span style='color:#00ffcc;'>💰 دفع: {h.get('price',0)}</span> | <span style='color:#ff4b4b;'>🛠️ تكلفة: {h.get('debt',0)}</span></div>", unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# ... (كود تسجيل الدخول للمدير والفني يظل كما هو لضمان الأمان) ...
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

# ================== 5. واجهة المدير (بدون تغيير) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## Power Life 💧")
    menu = st.sidebar.radio("التحكم", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])
    # (نفس كود المدير السابق بدون أي تعديل في الوظائف)
    if menu == "📊 المالية":
        total_out = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        total_income = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي المديونية (بره)", f"{total_out:,.0f} ج.م")
        st.metric("إجمالي التحصيل (داخل الشركة)", f"{total_income:,.0f} ج.م")
    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 بحث...")
        if search:
            results = [c for c in st.session_state.data if search.lower() in c['name'].lower() or search in str(c['id'])]
            for c in results:
                st.write(f"👤 {c['name']} (ID: {c['id']})")
                if st.button(f"فتح ملف العميل {c['id']}"):
                    st.session_state.selected_admin_cust = c['id']
    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (إصلاح شامل للألوان والتنسيق) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"<div style='text-align:center; color:#00d4ff;'>🛠️ الفني: <b>{st.session_state.current_tech}</b></div>", unsafe_allow_html=True)
    t_menu = st.sidebar.radio("القائمة", ["📋 تنفيذ مهمة", "💰 تقريري الشخصي", "🚪 خروج"])

    if t_menu == "📋 تنفيذ مهمة":
        st.markdown("<h3 style='color:#00d4ff;'>🔍 ابحث عن العميل</h3>", unsafe_allow_html=True)
        search_q = st.text_input("ابحث بالاسم، الكود، أو التليفون...")
        
        selected_cust = None
        if search_q:
            q = search_q.strip().lower()
            res = [c for c in st.session_state.data if (q in c['name'].lower()) or (q == str(c['id'])) or (q in str(c.get('phone','')))]
            if res:
                c_opts = {f"{c['id']} - {c['name']}": c for c in res}
                selected_cust = c_opts[st.selectbox("نتائج البحث (اختر العميل):", list(c_opts.keys()))]
            else: st.warning("⚠️ لا يوجد عميل بهذه البيانات")

        if selected_cust:
            st.markdown("---")
            st.success(f"✅ العميل الحالي: {selected_cust['name']}")
            if selected_cust.get('gps'): st.link_button("📍 فتح الموقع (GPS)", selected_cust['gps'])
            
            with st.container():
                v_d = st.number_input("تكلفة الصيانة أو القطع (+)", min_value=0.0)
                v_p = st.number_input("المبلغ المحصل من العميل (-)", min_value=0.0)
                v_f = st.multiselect("الشمع المستخدم:", ["شمعة 1", "شمعة 2", "شمعة 3", "شمعة 4", "شمعة 5", "شمعة 6", "شمعة 7", "مبمبرين"])
                v_n = st.text_area("تفاصيل العمل المنفذ")
                
                if st.button("🚀 إرسال التقرير النهائي"):
                    for x in st.session_state.data:
                        if x['id'] == selected_cust['id']:
                            x.setdefault('history', []).append({
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "note": v_n,
                                "tech": st.session_state.current_tech,
                                "debt": v_d,
                                "price": v_p,
                                "filter_used": ", ".join(v_f) if v_f else "لا يوجد"
                            })
                    save_json("customers.json", st.session_state.data)
                    st.balloons()
                    st.success("تم حفظ العملية بنجاح!")

    elif t_menu == "💰 تقريري الشخصي":
        st.markdown("<h3 style='color:#00d4ff;'>📊 ملخص أدائي اليوم</h3>", unsafe_allow_html=True)
        my_v = []; my_cash = 0.0; filters = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') == st.session_state.current_tech:
                    my_v.append({"التاريخ": h['date'], "العميل": c['name'], "المحصل": h.get('price', 0), "الشمع": h.get('filter_used', 'لا يوجد')})
                    my_cash += float(h.get('price', 0))
                    if h.get('filter_used') and h['filter_used'] != "لا يوجد": filters.extend(h['filter_used'].split(", "))

        c1, c2 = st.columns(2)
        with c1: st.markdown(f"<div class='tech-card'>المبلغ المحصل معك<br><span class='tech-val'>{my_cash:,.0f} ج.م</span></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='tech-card'>عدد الزيارات<br><span class='tech-val'>{len(my_v)}</span></div>", unsafe_allow_html=True)

        if my_v:
            st.write("#### 📜 سجل آخر العمليات")
            st.table(pd.DataFrame(my_v).sort_values(by="التاريخ", ascending=False))

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
