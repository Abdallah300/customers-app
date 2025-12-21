import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام ==================
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
    .balance-box { background: rgba(0, 255, 204, 0.15); border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; text-align: center; margin: 10px 0; }
    .logo-text { font-size: 45px; font-weight: bold; color: #00d4ff; text-align: center; display: block; text-shadow: 2px 2px 10px #007bff; padding: 10px; }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div { 
        background-color: #ffffff !important; 
        color: #000000 !important; font-weight: bold !important;
    }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات (تحديث فوري) ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.session_state.data = data # تحديث الحالة فوراً في الذاكرة

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    try: return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
    except: return 0.0

# ================== 3. واجهة الباركود (صفحة العميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><h2 style='color:white;'>{c['name']}</h2><div class='balance-box'><h2 style='color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</h2></div></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                with st.container():
                    st.write(f"📅 {h.get('date','')}")
                    if float(h.get('price', 0)) > 0: st.success(f"💰 تم دفع: {h['price']:,.0f} ج.م")
                    if float(h.get('debt', 0)) > 0: st.error(f"🛠️ تكلفة: {h['debt']:,.0f} ج.م")
                    st.write(f"📝 {h.get('note','-')}")
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

# ... (أكواد تسجيل دخول المدير والفني كما هي في ملفك) ...
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

# ================== 5. واجهة المدير (إدارة العملاء والمالية) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## Power Life 💧")
    menu = st.sidebar.radio("التحكم", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📊 المالية":
        total_out = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        total_income = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        total_serv = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-container'><div class='metric-title'>مديونية بره</div><div class='metric-value'>{total_out:,.0f}</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'><div class='metric-title'>إجمالي الكاش</div><div class='metric-value'>{total_income:,.0f}</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-container'><div class='metric-title'>صافي الأرباح</div><div class='metric-value'>{(total_income - (total_serv * 0.4)):,.0f}</div></div>", unsafe_allow_html=True)

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث (اسم/كود/تليفون)...")
        if search:
            q = search.strip().lower()
            filtered = [c for c in st.session_state.data if (q in c['name'].lower()) or (q == str(c['id'])) or (q in str(c.get('phone','')))]
            for c in filtered:
                bal = calculate_balance(c.get('history', []))
                with st.expander(f"👤 {c['name']} | كود: {c['id']} | الرصيد: {bal:,.0f}"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                        if st.button("🗑️ حذف العميل", key=f"del{c['id']}"):
                            st.session_state.data.remove(c); save_json("customers.json", st.session_state.data); st.rerun()
                    with col2:
                        st.write("**تعديل البيانات:**")
                        c['name'] = st.text_input("الاسم", c['name'], key=f"n{c['id']}")
                        c['phone'] = st.text_input("التليفون", c.get('phone',''), key=f"p{c['id']}")
                        if st.button("حفظ التعديلات", key=f"s{c['id']}"): save_json("customers.json", st.session_state.data); st.success("تم الحفظ")

    elif menu == "➕ إضافة عميل":
        with st.form("new"):
            n, p, loc, d = st.text_input("الاسم"), st.text_input("الفون"), st.text_input("GPS"), st.number_input("دين سابق")
            if st.form_submit_button("إضافة"):
                nid = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": nid, "name": n, "phone": p, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0, "tech": "المدير"}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم الإضافة كود: {nid}")

    elif menu == "🛠️ تقارير الفنيين":
        all_v = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') and h.get('tech') != "المدير":
                    all_v.append({"الفني": h['tech'], "العميل": c['name'], "التاريخ": h['date'], "المحصل": h.get('price', 0), "البيان": h['note']})
        if all_v:
            df = pd.DataFrame(all_v)
            st.table(df)
            st.write("### إجمالي تحصيل كل فني")
            st.table(df.groupby('الفني')['المحصل'].sum())

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (السرعة القصوى + رصيد + باركود) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: **{st.session_state.current_tech}**")
    t_menu = st.sidebar.radio("القائمة", ["📋 تنفيذ مهمة", "💰 محفظتي", "🚪 خروج"])

    if t_menu == "📋 تنفيذ مهمة":
        # عرض كل العملاء في قائمة اختيار + بحث
        cust_dict = {f"{c['id']} - {c['name']}": c for c in st.session_state.data}
        choice = st.selectbox("🔍 ابحث واختر العميل:", [""] + list(cust_dict.keys()))

        if choice:
            selected = cust_dict[choice]
            bal = calculate_balance(selected.get('history', []))
            
            # عرض الرصيد والباركود فوراً للفني
            st.markdown(f"<div class='balance-box'><h3 style='margin:0; color:#00ffcc;'>رصيد العميل الحالي: {bal:,.0f} ج.م</h3></div>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns([2, 1])
            with col_b:
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={selected['id']}", caption="باركود العميل")
            with col_a:
                if selected.get('gps'): st.link_button("📍 فتح الموقع (GPS)", selected['gps'])
                st.write(f"📞 تليفون: {selected.get('phone','-')}")

            with st.form("tech_op", clear_on_submit=True):
                v_d = st.number_input("تكلفة الصيانة (+)", min_value=0.0)
                v_p = st.number_input("المبلغ المحصل (-)", min_value=0.0)
                v_f = st.multiselect("الشمع المستخدم:", ["1", "2", "3", "4", "5", "6", "7", "ممبرين"])
                v_n = st.text_area("تفاصيل الزيارة")
                
                if st.form_submit_button("إرسال التقرير فوراً 🚀"):
                    # إضافة العملية في التاريخ واللحظة
                    new_entry = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "note": f"{v_n} (شمع: {', '.join(v_f)})",
                        "tech": st.session_state.current_tech,
                        "debt": v_d,
                        "price": v_p
                    }
                    # التحديث في الذاكرة والحفظ في الملف
                    for c in st.session_state.data:
                        if c['id'] == selected['id']:
                            c.setdefault('history', []).append(new_entry)
                            break
                    
                    save_json("customers.json", st.session_state.data)
                    st.success("✅ تم تسجيل العملية وسمعت في السيستم!")
                    st.balloons()

    elif t_menu == "💰 محفظتي":
        cash = sum(float(h.get('price', 0)) for c in st.session_state.data for h in c.get('history', []) if h.get('tech') == st.session_state.current_tech)
        st.metric("💰 كاش معك", f"{cash:,.0f} ج.م")

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()              
