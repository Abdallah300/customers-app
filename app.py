import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (القديم المستقر مع تحسين الفني) ==================
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

    /* تحسين شكل المدخلات للفني لتكون واضحة في الشمس */
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

# ================== 3. واجهة الباركود للعميل ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown(f"<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center;'>{c['name']}</h2>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div style='text-align:center; background:#001f3f; padding:15px; border-radius:10px; border:1px solid #00d4ff;'><h2 style='color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</h2></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                with st.container():
                    st.write(f"📅 {h['date']} | 📝 {h['note']}")
                    if float(h.get('price', 0)) > 0: st.success(f"💰 تم دفع: {h['price']} ج.م")
                    if float(h.get('debt', 0)) > 0: st.error(f"🛠️ تكلفة: {h['debt']} ج.م")
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

# ================== 5. واجهة المدير (كاملة 100%) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## لوحة المدير 💧")
    menu = st.sidebar.radio("التحكم", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📊 المالية":
        st.markdown("<h2 style='text-align:center;'>📊 التقرير المالي العام</h2>", unsafe_allow_html=True)
        t_out = 0.0; t_in = 0.0; t_serv = 0.0
        for c in st.session_state.data:
            h = c.get('history', [])
            t_out += calculate_balance(h)
            t_in += sum(float(x.get('price', 0)) for x in h)
            t_serv += sum(float(x.get('debt', 0)) for x in h)
        
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-container'><div class='metric-title'>مديونية العملاء (بره)</div><div class='metric-value'>{t_out:,.0f} ج.م</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'><div class='metric-title'>إجمالي الكاش المحصل</div><div class='metric-value'>{t_in:,.0f} ج.م</div></div>", unsafe_allow_html=True)
        with m3:
            profit = t_in - (t_serv * 0.4)
            st.markdown(f"<div class='metric-container'><div class='metric-title'>صافي أرباح الشركة</div><div class='metric-value'>{profit:,.0f} ج.م</div></div>", unsafe_allow_html=True)

    elif menu == "🛠️ تقارير الفنيين":
        st.subheader("🛠️ سجل زيارات الفنيين")
        all_visits = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') and h.get('tech') != "المدير":
                    all_visits.append({"الفني": h['tech'], "العميل": c['name'], "التاريخ": h['date'], "البيان": h.get('note',''), "المحصل": h.get('price', 0)})
        
        if all_visits:
            df = pd.DataFrame(all_visits)
            st.dataframe(df, use_container_width=True)
            # الجزء اللي كان ناقص (حساب الإجماليات لكل فني)
            st.write("### 💰 إجمالي تحصيل كل فني")
            summary = df.groupby('الفني')['المحصل'].sum().reset_index()
            st.table(summary)
        
        with st.expander("➕ إضافة فني جديد للنظام"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("كلمة سر الفني")
            if st.button("حفظ الفني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs); st.success("تم الحفظ"); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new_cust"):
            st.subheader("➕ تسجيل عميل جديد")
            n = st.text_input("اسم العميل"); ph = st.text_input("رقم التليفون"); gps = st.text_input("رابط الموقع GPS"); d = st.number_input("مديونية سابقة (إن وجد)")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": ph, "gps": gps, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحي", "debt": d, "price": 0, "tech": "المدير"}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم الإضافة بكود: {new_id}")

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بالاسم أو الكود...")
        if search:
            results = [c for c in st.session_state.data if search.lower() in c['name'].lower() or search == str(c['id'])]
            for c in results:
                st.info(f"👤 {c['name']} | كود: {c['id']} | رصيد: {calculate_balance(c.get('history', []))}")
                with st.expander("إضافة عملية سريعة (مدير)"):
                    c1, c2 = st.columns(2)
                    d1 = c1.number_input("تكلفة (+)", key=f"d{c['id']}")
                    d2 = c2.number_input("تحصيل (-)", key=f"p{c['id']}")
                    note = st.text_input("البيان", key=f"n{c['id']}")
                    if st.button("تسجيل العملية", key=f"b{c['id']}"):
                        c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": "المدير", "debt": d1, "price": d2})
                        save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (المتطورة والواضحة) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: **{st.session_state.current_tech}**")
    t_menu = st.sidebar.radio("القائمة", ["📋 تنفيذ مهمة", "💰 محفظتي", "🚪 خروج"])

    if t_menu == "📋 تنفيذ مهمة":
        st.subheader("🔍 ابحث عن العميل")
        sq = st.text_input("أدخل الاسم أو الكود أو التليفون")
        if sq:
            res = [c for c in st.session_state.data if (sq.lower() in c['name'].lower()) or (sq == str(c['id'])) or (sq in str(c.get('phone','')))]
            if res:
                selected = res[0] # اختيار أول نتيجة تلقائياً أو عبر selectbox
                if len(res) > 1:
                    c_opts = {f"{x['id']} - {x['name']}": x for x in res}
                    selected = c_map = c_opts[st.selectbox("اختر العميل الصحيح:", list(c_opts.keys()))]
                
                st.success(f"العميل: {selected['name']}")
                if selected.get('gps'): st.link_button("📍 فتح الموقع (GPS)", selected['gps'])
                
                with st.form("tech_op"):
                    v_d = st.number_input("التكلفة (+)")
                    v_p = st.number_input("المحصل (-)")
                    v_f = st.multiselect("الشمع:", ["شمعة 1", "2", "3", "4", "5", "6", "7", "ممبرين"])
                    v_n = st.text_area("ماذا تم في الزيارة؟")
                    if st.form_submit_button("إرسال التقرير"):
                        for x in st.session_state.data:
                            if x['id'] == selected['id']:
                                x.setdefault('history', []).append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "note": v_n, "tech": st.session_state.current_tech,
                                    "debt": v_d, "price": v_p, "filter_used": ", ".join(v_f)
                                })
                        save_json("customers.json", st.session_state.data); st.success("تم الحفظ بنجاح!")

    elif t_menu == "💰 محفظتي":
        my_cash = 0.0; my_v = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') == st.session_state.current_tech:
                    my_cash += float(h.get('price', 0))
                    my_v.append({"التاريخ": h['date'], "العميل": c['name'], "المحصل": h.get('price', 0), "العمل": h.get('note','')})
        st.metric("💰 إجمالي الكاش معك", f"{my_cash:,.0f} ج.م")
        if my_v: st.table(pd.DataFrame(my_v))

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
