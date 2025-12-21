import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (Power Life Theme) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* كروت الإحصائيات */
    .metric-box { background: rgba(0, 212, 255, 0.1); border: 2px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center; margin: 10px; }
    .metric-val { color: #00d4ff; font-size: 25px; font-weight: bold; }
    
    /* صندوق الرصيد للفني والمدير */
    .balance-card { background: rgba(0, 255, 204, 0.15); border: 1px solid #00ffcc; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 20px; }
    .balance-text { color: #00ffcc; font-size: 22px; font-weight: bold; }

    /* تحسين شكل المدخلات */
    .stTextInput input, .stNumberInput input, .stSelectbox div { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات (بدون ضياع) ==================
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def get_bal(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. رابط الباركود (صفحة العميل) ==================
params = st.query_params
if "id" in params:
    try:
        cid = int(params["id"])
        c = next((x for x in st.session_state.data if x['id'] == cid), None)
        if c:
            st.markdown(f"<h1 style='text-align:center;'>Power Life 💧</h1><h2 style='text-align:center;'>{c['name']}</h2>", unsafe_allow_html=True)
            st.markdown(f"<div class='balance-card'><span class='balance-text'>المتبقي: {get_bal(c['history']):,.0f} ج.م</span></div>", unsafe_allow_html=True)
            for h in reversed(c['history']):
                st.write(f"📅 {h['date']} | {h['note']} | 💰 {h.get('price',0)} | 🛠️ {h.get('debt',0)}")
                st.write("---")
            st.stop()
    except: st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#00d4ff;'>نظام Power Life 💧</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("الباسورد", type="password")
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
    menu = st.sidebar.radio("التحكم", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📊 المالية":
        t_out = sum(get_bal(c['history']) for c in st.session_state.data)
        t_in = sum(sum(float(h.get('price', 0)) for h in c['history']) for c in st.session_state.data)
        t_serv = sum(sum(float(h.get('debt', 0)) for h in c['history']) for c in st.session_state.data)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-box'>مديونية بره<br><span class='metric-val'>{t_out:,.0f}</span></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-box'>تحصيل الشركة<br><span class='metric-val'>{t_in:,.0f}</span></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-box'>صافي الأرباح<br><span class='metric-val'>{(t_in-(t_serv*0.4)):,.0f}</span></div>", unsafe_allow_html=True)

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 بحث عن عميل...")
        res = [c for c in st.session_state.data if search.lower() in c['name'].lower() or search == str(c['id'])]
        for c in res:
            with st.expander(f"👤 {c['name']} (كود: {c['id']})"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"<div class='balance-card'>الرصيد: {get_bal(c['history']):,.0f} ج.م</div>", unsafe_allow_html=True)
                    # تعديل وحذف (صلاحيات مدير)
                    new_n = st.text_input("تعديل الاسم", value=c['name'], key=f"n{c['id']}")
                    new_p = st.text_input("تعديل الفون", value=c.get('phone',''), key=f"p{c['id']}")
                    if st.button("💾 حفظ التعديلات", key=f"s{c['id']}"):
                        c['name'], c['phone'] = new_n, new_p
                        save_json("customers.json", st.session_state.data); st.success("تم التعديل"); st.rerun()
                    if st.button("🗑️ حذف العميل", key=f"d{c['id']}"):
                        st.session_state.data.remove(c); save_json("customers.json", st.session_state.data); st.rerun()
                with col2:
                    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                    st.image(qr, caption="باركود العميل")
                
                # إضافة عملية من المدير
                st.write("---")
                with st.form(f"form{c['id']}"):
                    d1, d2, nt = st.number_input("تكلفة (+)"), st.number_input("تحصيل (-)"), st.text_input("البيان")
                    if st.form_submit_button("تسجيل العملية"):
                        c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": nt, "tech": "المدير", "debt": d1, "price": d2})
                        save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("add"):
            n, ph, loc, d = st.text_input("الاسم"), st.text_input("الفون"), st.text_input("GPS"), st.number_input("دين سابق")
            if st.form_submit_button("إضافة العميل"):
                nid = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": nid, "name": n, "phone": ph, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0, "tech": "المدير"}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم الإضافة بكود: {nid}")

    elif menu == "🛠️ تقارير الفنيين":
        all_v = []
        for c in st.session_state.data:
            for h in c['history']:
                if h.get('tech') and h.get('tech') != "المدير":
                    all_v.append({"الفني": h['tech'], "العميل": c['name'], "التاريخ": h['date'], "المحصل": h.get('price', 0), "البيان": h['note']})
        if all_v:
            df = pd.DataFrame(all_v)
            st.table(df)
            st.write("### إجمالي تحصيل كل فني")
            st.table(df.groupby("الفني")["المحصل"].sum())
        with st.expander("إضافة فني جديد"):
            tn, tp = st.text_input("الاسم"), st.text_input("السر")
            if st.button("حفظ الفني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs); st.rerun()

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (كاملة مع الرصيد والباركود) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.title(f"🛠️ الفني: {st.session_state.current_tech}")
    t_menu = st.sidebar.radio("القائمة", ["📋 مهمة جديدة", "💰 محفظتي", "🚪 خروج"])

    if t_menu == "📋 مهمة جديدة":
        cust_opts = {f"{c['id']} - {c['name']}": c for c in st.session_state.data}
        choice = st.selectbox("اختر العميل:", [""] + list(cust_opts.keys()))

        if choice:
            selected = cust_opts[choice]
            # عرض الرصيد والباركود للفني
            st.markdown(f"<div class='balance-card'>رصيد العميل الحالي:<br><span class='balance-text'>{get_bal(selected['history']):,.0f} ج.م</span></div>", unsafe_allow_html=True)
            
            c1, c2 = st.columns([2, 1])
            with c1:
                if selected.get('phone'): st.info(f"📞 تليفون: {selected['phone']}")
                if selected.get('gps'): st.link_button("📍 موقع العميل", selected['gps'])
            with c2:
                qr = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={selected['id']}"
                st.image(qr, caption="باركود العميل")

            with st.form("tech_f"):
                v_d, v_p = st.number_input("التكلفة (+)"), st.number_input("المحصل (-)")
                v_s = st.multiselect("الشمع:", ["شمعة 1", "2", "3", "4", "5", "6", "7", "ممبرين"])
                v_n = st.text_area("البيان")
                if st.form_submit_button("إرسال التقرير"):
                    selected['history'].append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "note": f"{v_n} | شمع: {', '.join(v_s)}",
                        "tech": st.session_state.current_tech,
                        "debt": v_d, "price": v_p
                    })
                    save_json("customers.json", st.session_state.data); st.success("تم الحفظ بنجاح")

    elif t_menu == "💰 محفظتي":
        cash = sum(float(h.get('price', 0)) for c in st.session_state.data for h in c['history'] if h.get('tech') == st.session_state.current_tech)
        st.metric("إجمالي المحصل معك", f"{cash:,.0f} ج.م")

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
