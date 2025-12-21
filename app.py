import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (نفس تنسيقك المعتمد) ==================
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

    .client-header { background: linear-gradient(135deg, #003366 0%, #000b1a 100%); border-radius: 20px; padding: 25px; border: 1px solid #00d4ff; text-align: center; margin-bottom: 30px; }
    .after-op-bal { background: rgba(0, 212, 255, 0.1); border: 1px dashed #00d4ff; border-radius: 10px; padding: 10px; margin-top: 10px; color: #00d4ff; font-weight: bold; font-size: 16px; text-align: center; }
    .logo-text { font-size: 45px; font-weight: bold; color: #00d4ff; text-align: center; display: block; text-shadow: 2px 2px 10px #007bff; padding: 10px; }
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

# ================== 3. واجهة الباركود ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
            total_bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><h2 style='color:white;'>مرحباً بك: {c['name']}</h2><div style='font-size: 26px; font-weight: bold; color: #00ffcc; background: rgba(0, 255, 204, 0.1); padding: 10px 20px; border-radius: 12px; border: 1px solid #00ffcc; display: inline-block;'>إجمالي المتبقي: {total_bal:,.0f} ج.م</div></div>", unsafe_allow_html=True)
            rb = 0
            h_list = []
            for h in c.get('history', []):
                rb += (float(h.get('debt', 0)) - float(h.get('price', 0)))
                h_copy = h.copy(); h_copy['rb'] = rb; h_list.append(h_copy)
            for h in reversed(h_list):
                with st.container():
                    st.write(f"📅 {h.get('date','')}")
                    st.write(f"📝 {h.get('note','-')}")
                    if float(h.get('price', 0)) > 0: st.success(f"💰 تم دفع: {h['price']:,.0f} ج.م")
                    if float(h.get('debt', 0)) > 0: st.error(f"🛠️ تكلفة: {h['debt']:,.0f} ج.م")
                    st.markdown(f"<div class='after-op-bal'>المتبقي بعد العملية: {h['rb']:,.0f} ج.م</div>", unsafe_allow_html=True)
                    st.markdown("---")
            st.stop()
    except: st.stop()

# ================== 4. تسجيل الدخول ==================
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

# ================== 5. واجهة المدير (كما كانت بالضبط) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## Power Life 💧")
    menu = st.sidebar.radio("التحكم", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📊 المالية":
        st.markdown("<h2 style='text-align:center; color:#00d4ff;'>📊 التقرير المالي العام</h2>", unsafe_allow_html=True)
        total_out = 0.0; total_income = 0.0; total_services = 0.0
        for c in st.session_state.data:
            hists = c.get('history', [])
            total_out += calculate_balance(hists)
            total_income += sum(float(h.get('price', 0)) for h in hists)
            total_services += sum(float(h.get('debt', 0)) for h in hists)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-container'><div class='metric-title'>إجمالي المديونية (بره)</div><div class='metric-value'>{total_out:,.0f} ج.م</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'><div class='metric-title'>إجمالي الدخل (الكاش)</div><div class='metric-value'>{total_income:,.0f} ج.م</div></div>", unsafe_allow_html=True)
        with m3:
            profit = total_income - (total_services * 0.4)
            st.markdown(f"<div class='metric-container'><div class='metric-title'>صافي أرباح الشركة</div><div class='metric-value'>{profit:,.0f} ج.م</div></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.info(f"إجمالي قيمة الخدمات المسجلة: {total_services:,.0f} ج.م")

    elif menu == "🛠️ تقارير الفنيين":
        st.subheader("🛠️ سجل زيارات الفنيين")
        all_visits = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') and h.get('tech') != "المدير":
                    all_visits.append({"الفني": h['tech'], "العميل": c['name'], "التاريخ": h['date'], "البيان": h['note'], "المحصل": h.get('price', 0)})
        if all_visits:
            df = pd.DataFrame(all_visits)
            st.dataframe(df, use_container_width=True)
            st.write("### إجمالي تحصيل كل فني")
            st.table(df.groupby('الفني')['المحصل'].sum().reset_index())
        with st.expander("➕ إضافة فني جديد"):
            tn, tp = st.text_input("اسم الفني"), st.text_input("الباسورد")
            if st.button("حفظ الفني"): 
                st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بالكود أو الاسم أو التليفون...")
        if search:
            s_clean = search.strip().lower()
            filtered = [c for c in st.session_state.data if (s_clean.isdigit() and str(c['id']) == s_clean) or (not s_clean.isdigit() and (s_clean in c['name'].lower() or s_clean in str(c.get('phone',''))))]
            for c in filtered:
                bal = calculate_balance(c.get('history', []))
                st.info(f"👤 {c['name']} | كود: {c['id']} | الرصيد: {bal:,.0f}")
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    with st.expander("⚙️ تعديل البيانات والـ GPS"):
                        c['name'] = st.text_input("الاسم", c['name'], key=f"un{c['id']}")
                        c['phone'] = st.text_input("الفون", c.get('phone',''), key=f"up{c['id']}")
                        c['gps'] = st.text_input("GPS", c.get('gps',''), key=f"ug{c['id']}")
                        if st.button("حفظ التعديلات", key=f"us{c['id']}"): save_json("customers.json", st.session_state.data); st.success("تم")
                with col2:
                    with st.expander("💸 عملية جديدة"):
                        d1 = st.number_input("صيانة (+)", key=f"d{c['id']}"); d2 = st.number_input("تحصيل (-)", key=f"r{c['id']}")
                        note = st.text_input("البيان", key=f"nt{c['id']}")
                        if st.button("تسجيل", key=f"t{c['id']}"):
                            c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": "المدير", "debt": d1, "price": d2})
                            save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new"):
            n, p, loc, d = st.text_input("الاسم"), st.text_input("الفون"), st.text_input("GPS"), st.number_input("دين سابق")
            if st.form_submit_button("إضافة"):
                nid = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": nid, "name": n, "phone": p, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم الكود: {nid}")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (التحديث المطلوب فقط) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: **{st.session_state.current_tech}**")
    t_menu = st.sidebar.radio("القائمة", ["📋 تنفيذ مهمة", "💰 محفظتي وتقريري", "🚪 خروج"])

    if t_menu == "📋 تنفيذ مهمة":
        st.markdown(f"### 🔍 ابحث عن العميل")
        search_query = st.text_input("أدخل الاسم، الكود، أو رقم التليفون...")
        selected_cust = None
        if search_query:
            q = search_query.strip().lower()
            results = [c for c in st.session_state.data if (q in c['name'].lower()) or (q == str(c['id'])) or (q in str(c.get('phone','')))]
            if results:
                cust_options = {f"{c['id']} - {c['name']}": c for c in results}
                selected_cust = cust_options[st.selectbox("اختر العميل:", list(cust_options.keys()))]
            else: st.warning("⚠️ لا يوجد نتائج")

        if selected_cust:
            st.info(f"👤 {selected_cust['name']} | كود: {selected_cust['id']}")
            if selected_cust.get('gps'): st.link_button("📍 GPS", selected_cust['gps'])
            with st.form("tech_op"):
                v_d, v_p = st.number_input("التكلفة (+)"), st.number_input("المحصل (-)")
                v_f = st.multiselect("الشمع:", ["شمعة 1", "شمعة 2", "شمعة 3", "شمعة 4", "شمعة 5", "شمعة 6", "شمعة 7", "مبمبرين"])
                v_n = st.text_area("البيان")
                if st.form_submit_button("إرسال"):
                    for x in st.session_state.data:
                        if x['id'] == selected_cust['id']:
                            x.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": v_n, "tech": st.session_state.current_tech, "debt": v_d, "price": v_p, "filter_used": ", ".join(v_f)})
                    save_json("customers.json", st.session_state.data); st.success("تم")

    elif t_menu == "💰 محفظتي وتقريري":
        my_v = []; cash = 0.0; filters = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') == st.session_state.current_tech:
                    my_v.append({"التاريخ": h['date'], "العميل": c['name'], "المحصل": h.get('price', 0), "الشمع": h.get('filter_used', '')})
                    cash += float(h.get('price', 0))
                    if h.get('filter_used'): filters.extend(h['filter_used'].split(", "))
        st.metric("💰 المحصل معك حالياً", f"{cash:,.0f} ج.م")
        if my_v: st.table(pd.DataFrame(my_v))
        if filters: st.write("📦 حصر الشمع:"); st.table(pd.Series(filters).value_counts())

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
