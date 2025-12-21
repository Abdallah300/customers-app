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

    /* صندوق الرصيد الملون */
    .balance-card { background: rgba(0, 255, 204, 0.1); border: 1px solid #00ffcc; border-radius: 10px; padding: 10px; text-align: center; margin: 5px 0; }
    .balance-text { color: #00ffcc; font-size: 20px; font-weight: bold; }

    .stTextInput input, .stNumberInput input, .stSelectbox div { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important;
    }
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

# ================== 3. رابط الباركود (صفحة العميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown(f"<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center;'>{c['name']}</h2>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='balance-card'><span class='balance-text'>المتبقي: {bal:,.0f} ج.م</span></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.write(f"📅 {h['date']} | 📝 {h['note']}")
                if float(h.get('price', 0)) > 0: st.success(f"💰 تم دفع: {h['price']}")
                if float(h.get('debt', 0)) > 0: st.error(f"🛠️ تكلفة: {h['debt']}")
                st.write("---")
            st.stop()
    except: st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life System</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_names) if t_names else st.error("لا يوجد فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        t_data = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == t_data['pass']: st.session_state.role = "tech_panel"; st.session_state.current_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة المدير (كاملة) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## لوحة المدير 💧")
    menu = st.sidebar.radio("التحكم", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📊 المالية":
        t_out = sum(calculate_balance(c['history']) for c in st.session_state.data)
        t_in = sum(sum(float(h.get('price', 0)) for h in c['history']) for c in st.session_state.data)
        t_serv = sum(sum(float(h.get('debt', 0)) for h in c['history']) for c in st.session_state.data)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-container'><div class='metric-title'>مديونية بره</div><div class='metric-value'>{t_out:,.0f}</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'><div class='metric-title'>إجمالي المحصل</div><div class='metric-value'>{t_in:,.0f}</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-container'><div class='metric-title'>صافي الأرباح</div><div class='metric-value'>{(t_in - (t_serv * 0.4)):,.0f}</div></div>", unsafe_allow_html=True)

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بالاسم أو الكود...")
        if search:
            results = [c for c in st.session_state.data if search.lower() in c['name'].lower() or search == str(c['id'])]
            for c in results:
                with st.expander(f"👤 {c['name']} (كود: {c['id']})"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"<div class='balance-card'><span class='balance-text'>الرصيد: {calculate_balance(c['history']):,.0f} ج.م</span></div>", unsafe_allow_html=True)
                        new_n = st.text_input("تعديل الاسم", value=c['name'], key=f"un{c['id']}")
                        new_p = st.text_input("تعديل الفون", value=c.get('phone',''), key=f"up{c['id']}")
                        if st.button("💾 حفظ", key=f"save{c['id']}"):
                            c['name'], c['phone'] = new_n, new_p
                            save_json("customers.json", st.session_state.data); st.rerun()
                        if st.button("🗑️ حذف العميل", key=f"del{c['id']}"):
                            st.session_state.data.remove(c); save_json("customers.json", st.session_state.data); st.rerun()
                    with col2:
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        st.image(qr_url, caption="باركود العميل")

    elif menu == "➕ إضافة عميل":
        with st.form("new_cust"):
            n, ph, gps, d = st.text_input("الاسم"), st.text_input("التليفون"), st.text_input("GPS"), st.number_input("دين سابق")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": ph, "gps": gps, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحي", "debt": d, "price": 0, "tech": "المدير"}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم الإضافة بكود: {new_id}")

    elif menu == "🛠️ تقارير الفنيين":
        all_visits = []
        for c in st.session_state.data:
            for h in c['history']:
                if h.get('tech') and h.get('tech') != "المدير":
                    all_visits.append({"الفني": h['tech'], "العميل": c['name'], "المحصل": h.get('price', 0), "التاريخ": h['date']})
        if all_visits:
            df = pd.DataFrame(all_visits)
            st.table(df)
            st.write("### إجمالي كل فني")
            st.table(df.groupby('الفني')['المحصل'].sum())
        with st.expander("إضافة فني جديد"):
            tn, tp = st.text_input("الاسم"), st.text_input("السر")
            if st.button("حفظ"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (مع الباركود والرصيد) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: **{st.session_state.current_tech}**")
    t_menu = st.sidebar.radio("القائمة", ["📋 تنفيذ مهمة", "💰 محفظتي", "🚪 خروج"])

    if t_menu == "📋 تنفيذ مهمة":
        st.subheader("🔍 اختر العميل")
        cust_list = {f"{c['id']} - {c['name']}": c for c in st.session_state.data}
        sq = st.selectbox("ابحث أو اختر العميل:", [""] + list(cust_list.keys()))
        
        if sq:
            selected = cust_list[sq]
            # عرض الرصيد والباركود للفني
            st.markdown(f"<div class='balance-card'><span class='balance-text'>رصيد العميل الحالي: {calculate_balance(selected['history']):,.0f} ج.م</span></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([2, 1])
            with c1:
                if selected.get('gps'): st.link_button("📍 موقع العميل (GPS)", selected['gps'])
                with st.form("tech_op"):
                    v_d, v_p = st.number_input("التكلفة (+)"), st.number_input("المحصل (-)")
                    v_s = st.multiselect("الشمع:", ["شمعة 1", "2", "3", "4", "5", "6", "7", "ممبرين"])
                    v_n = st.text_area("البيان")
                    if st.form_submit_button("إرسال التقرير"):
                        selected['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": v_n, "tech": st.session_state.current_tech, "debt": v_d, "price": v_p, "filter_used": ", ".join(v_s)})
                        save_json("customers.json", st.session_state.data); st.success("تم الحفظ بنجاح!")
            with c2:
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={selected['id']}"
                st.image(qr_url, caption="باركود العميل")

    elif t_menu == "💰 محفظتي":
        my_cash = sum(float(h.get('price', 0)) for c in st.session_state.data for h in c['history'] if h.get('tech') == st.session_state.current_tech)
        st.metric("💰 المحصل معك", f"{my_cash:,.0f} ج.م")

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
