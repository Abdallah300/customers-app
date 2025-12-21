import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (Power Life Style) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    .metric-container { background: rgba(0, 212, 255, 0.1); border: 2px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center; margin: 10px; }
    .metric-title { color: #ffffff; font-size: 18px; font-weight: bold; }
    .metric-value { color: #00d4ff; font-size: 28px; font-weight: bold; }

    .balance-box { background: rgba(0, 255, 204, 0.15); border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; text-align: center; margin: 10px 0; }
    .logo-text { font-size: 45px; font-weight: bold; color: #00d4ff; text-align: center; display: block; text-shadow: 2px 2px 10px #007bff; padding: 10px; }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div { 
        background-color: #ffffff !important; 
        color: #000000 !important; font-weight: bold !important;
    }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات والتحديث اللحظي ==================
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

if 'data' not in st.session_state or st.sidebar.button("🔄 تحديث البيانات"):
    st.session_state.data = load_json("customers.json", [])
    st.session_state.techs = load_json("techs.json", [])
    if 'data' in st.session_state: st.toast("تم مزامنة البيانات ✅")

def calculate_balance(history):
    try: return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
    except: return 0.0

# ================== 3. واجهة الباركود للعملاء ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div style='text-align:center; background:rgba(0,212,255,0.1); padding:20px; border-radius:15px; border:1px solid #00d4ff;'><h2 style='color:white;'>مرحباً: {c['name']}</h2><h1 style='color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</h1></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.write(f"📅 {h.get('date','')}")
                if float(h.get('price', 0)) > 0: st.success(f"💰 تم دفع: {h['price']}")
                if float(h.get('debt', 0)) > 0: st.error(f"🛠️ تكلفة: {h['debt']}")
                st.write(f"📝 {h.get('note','-')}")
                st.markdown("---")
            st.stop()
    except: st.stop()

# ================== 4. نظام تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
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

# ================== 5. واجهة المدير (إدارة شاملة) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## لوحة المدير")
    if st.sidebar.button("🔃 تحديث السيستم الآن"): st.rerun()
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📊 المالية":
        t_out = sum(calculate_balance(c['history']) for c in st.session_state.data)
        t_in = sum(sum(float(h.get('price', 0)) for h in c['history']) for c in st.session_state.data)
        t_serv = sum(sum(float(h.get('debt', 0)) for h in c['history']) for c in st.session_state.data)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-container'><div class='metric-title'>مديونية بره</div><div class='metric-value'>{t_out:,.0f}</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'><div class='metric-title'>المحصل كاش</div><div class='metric-value'>{t_in:,.0f}</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-container'><div class='metric-title'>صافي الربح</div><div class='metric-value'>{(t_in - (t_serv * 0.4)):,.0f}</div></div>", unsafe_allow_html=True)

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث (اسم/كود/فون)...")
        if search:
            q = search.strip().lower()
            filtered = [c for c in st.session_state.data if (q in c['name'].lower()) or (q == str(c['id'])) or (q in str(c.get('phone','')))]
            for c in filtered:
                bal = calculate_balance(c['history'])
                with st.expander(f"👤 {c['name']} | كود: {c['id']} | الرصيد: {bal:,.0f}"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                        if st.button("🗑️ حذف العميل", key=f"del{c['id']}"):
                            st.session_state.data.remove(c); save_and_refresh("customers.json", st.session_state.data); st.rerun()
                    with col2:
                        with st.form(key=f"adm_form_{c['id']}", clear_on_submit=True):
                            a_d = st.number_input("تكلفة (+)", 0.0, key=f"ad{c['id']}")
                            a_p = st.number_input("تحصيل (-)", 0.0, key=f"ap{c['id']}")
                            a_f = st.multiselect("الشمع:", ["1", "2", "3", "4", "5", "6", "7", "ممبرين"], key=f"f{c['id']}")
                            a_n = st.text_input("البيان", key=f"an{c['id']}")
                            if st.form_submit_button("حفظ العملية 🚀"):
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": f"{a_n} - شمع: {', '.join(a_f)}", "tech": "المدير", "debt": a_d, "price": a_p, "filters": a_f})
                                save_and_refresh("customers.json", st.session_state.data); st.success("تم الحفظ"); st.rerun()

    elif menu == "🛠️ تقارير الفنيين":
        st.markdown("<h2 style='color:#00d4ff;'>🛠️ تقارير الأداء والاستهلاك</h2>", unsafe_allow_html=True)
        all_visits = []
        all_filters = []
        tech_debt = []
        
        for c in st.session_state.data:
            for h in c['history']:
                if h.get('tech') and h.get('tech') != "المدير":
                    # سجل الزيارات
                    all_visits.append({"الفني": h['tech'], "العميل": c['name'], "المحصل": h.get('price', 0), "التاريخ": h['date'], "البيان": h.get('note','')})
                    # حصر الشمع
                    if h.get('filters'):
                        for f in h['filters']: all_filters.append({"الفني": h['tech'], "الشمعة": f})
                    # مديونية سابها الفني (التكلفة أكبر من المحصل)
                    if float(h.get('debt', 0)) > float(h.get('price', 0)):
                        tech_debt.append({"كود العميل": c['id'], "العميل": c['name'], "الفني": h['tech'], "مديونية العملية": float(h['debt']) - float(h['price']), "التاريخ": h['date']})

        tab1, tab2, tab3 = st.tabs(["📋 سجل الزيارات", "📦 استهلاك الشمع", "⚠️ مديونيات الفنيين"])
        
        with tab1:
            if all_visits:
                df_v = pd.DataFrame(all_visits)
                st.dataframe(df_v, use_container_width=True)
                st.write("### إجمالي التحصيل:")
                st.table(df_v.groupby('الفني')['المحصل'].sum())
        
        with tab2:
            if all_filters:
                df_f = pd.DataFrame(all_filters)
                st.write("### إجمالي استهلاك الشمع لكل فني:")
                st.table(pd.crosstab(df_f['الفني'], df_f['الشمعة']))
            else: st.info("لا توجد بيانات شمع مسجلة")

        with tab3:
            if tech_debt:
                st.warning("هذا الجدول يوضح المبالغ التي لم يتم تحصيلها بالكامل أثناء زيارة الفني")
                df_d = pd.DataFrame(tech_debt)
                st.dataframe(df_d, use_container_width=True)
                st.write("### مديونية مسجلة باسم كل فني:")
                st.table(df_d.groupby('الفني')['مديونية العملية'].sum())
            else: st.success("لا توجد مديونيات متروكة من الفنيين")

        with st.expander("➕ إدارة الفنيين"):
            tn, tp = st.text_input("اسم الفني"), st.text_input("السر")
            if st.button("حفظ الفني الجديد"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_and_refresh("techs.json", st.session_state.techs); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n, p, d = st.text_input("الاسم"), st.text_input("الفون"), st.number_input("مديونية سابقة")
            if st.form_submit_button("إضافة"):
                nid = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": nid, "name": n, "phone": p, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح الحساب", "debt": d, "price": 0, "tech": "المدير"}]})
                save_and_refresh("customers.json", st.session_state.data); st.success("تم الإضافة"); st.rerun()

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (تحديث لحظي) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: **{st.session_state.current_tech}**")
    t_menu = st.sidebar.radio("القائمة", ["📋 تنفيذ مهمة", "💰 محفظتي", "🚪 خروج"])

    if t_menu == "📋 تنفيذ مهمة":
        cust_list = {f"{c['id']} - {c['name']}": c for c in st.session_state.data}
        choice = st.selectbox("🔍 ابحث واختر العميل:", [""] + list(cust_list.keys()))

        if choice:
            selected = cust_list[choice]
            st.markdown(f"<div class='balance-box'><h3>رصيد العميل الحالي: {calculate_balance(selected['history']):,.0f} ج.م</h3></div>", unsafe_allow_html=True)
            
            c_a, c_b = st.columns([2, 1])
            with c_b:
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={selected['id']}", caption="باركود العميل")
            with c_a:
                with st.form("t_form", clear_on_submit=True):
                    v_d, v_p = st.number_input("تكلفة الصيانة (+)"), st.number_input("المحصل (-)")
                    v_f = st.multiselect("الشمع المستهلك:", ["1", "2", "3", "4", "5", "6", "7", "ممبرين"])
                    v_n = st.text_area("البيان")
                    if st.form_submit_button("إرسال التقرير 🚀"):
                        selected['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": f"{v_n} - شمع: {', '.join(v_f)}", "tech": st.session_state.current_tech, "debt": v_d, "price": v_p, "filters": v_f})
                        save_and_refresh("customers.json", st.session_state.data)
                        st.success("تم الحفظ بنجاح!"); st.rerun()

    elif t_menu == "💰 محفظتي":
        cash = sum(float(h.get('price', 0)) for c in st.session_state.data for h in c['history'] if h.get('tech') == st.session_state.current_tech)
        st.metric("إجمالي المحصل معك", f"{cash:,.0f} ج.م")

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
