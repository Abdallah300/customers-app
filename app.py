import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (أزرق Power Life الأصلي) ==================
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

    /* تنسيق خاص لخانة رصيد العميل للفني */
    .balance-box { background: rgba(0, 255, 204, 0.1); border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; text-align: center; margin: 10px 0; }
    .balance-val { color: #00ffcc; font-size: 22px; font-weight: bold; }

    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data
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

# ================== 3. واجهة الباركود للعميل (ثابتة) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center;'>{c['name']}</h2>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div style='text-align:center; background:#001f3f; padding:15px; border-radius:10px; border:1px solid #00d4ff;'><h2 style='color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</h2></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.write(f"📅 {h['date']} | 📝 {h['note']}")
                if float(h.get('price', 0)) > 0: st.success(f"💰 دفع: {h['price']}")
                if float(h.get('debt', 0)) > 0: st.error(f"🛠️ تكلفة: {h['debt']}")
                st.write("---")
            st.stop()
    except: st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#00d4ff;'>نظام Power Life</h1>", unsafe_allow_html=True)
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

# ================== 5. واجهة المدير (بدون أي تغيير) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## لوحة المدير")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📊 المالية":
        t_out = 0.0; t_in = 0.0; t_serv = 0.0
        for c in st.session_state.data:
            h = c.get('history', [])
            t_out += calculate_balance(h)
            t_in += sum(float(x.get('price', 0)) for x in h)
            t_serv += sum(float(x.get('debt', 0)) for x in h)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-container'><div class='metric-title'>مديونية بره</div><div class='metric-value'>{t_out:,.0f}</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'><div class='metric-title'>إجمالي المحصل</div><div class='metric-value'>{t_in:,.0f}</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-container'><div class='metric-title'>صافي الأرباح</div><div class='metric-value'>{(t_in - (t_serv*0.4)):,.0f}</div></div>", unsafe_allow_html=True)

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
            st.table(df.groupby('الفني')['المحصل'].sum().reset_index())
        with st.expander("إضافة فني"):
            tn, tp = st.text_input("الاسم"), st.text_input("السر")
            if st.button("حفظ"): st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new"):
            n, ph, loc, d = st.text_input("الاسم"), st.text_input("الفون"), st.text_input("GPS"), st.number_input("دين سابق")
            if st.form_submit_button("إضافة"):
                nid = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": nid, "name": n, "phone": ph, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0, "tech": "المدير"}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم الإضافة بكود: {nid}")

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 بحث...")
        if search:
            res = [c for c in st.session_state.data if search.lower() in c['name'].lower() or search == str(c['id'])]
            for c in res:
                st.info(f"👤 {c['name']} (كود: {c['id']})")
                with st.expander("عملية سريعة"):
                    d1, d2 = st.number_input("تكلفة", key=f"d{c['id']}"), st.number_input("تحصيل", key=f"p{c['id']}")
                    if st.button("حفظ", key=f"b{c['id']}"):
                        c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل مدير", "tech": "المدير", "debt": d1, "price": d2})
                        save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (التحديث المطلوب) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.title(f"🛠️ {st.session_state.current_tech}")
    t_tab = st.sidebar.radio("القائمة", ["📋 تنفيذ مهمة", "💰 محفظتي", "🚪 خروج"])

    if t_tab == "📋 تنفيذ مهمة":
        st.markdown("### 🔍 اختر العميل أو ابحث عنه")
        # إظهار جميع العملاء في قائمة منسدلة مع إمكانية البحث
        cust_list = {f"{c['id']} - {c['name']}": c for c in st.session_state.data}
        choice = st.selectbox("ابحث عن العميل أو اختر من القائمة:", [""] + list(cust_list.keys()))

        if choice:
            selected = cust_list[choice]
            bal = calculate_balance(selected.get('history', []))
            
            # عرض بيانات العميل، الرصيد، والباركود
            c1, c2 = st.columns([2, 1])
            with c1:
                st.markdown(f"<div class='balance-box'>رصيد العميل الحالي:<br><span class='balance-val'>{bal:,.0f} ج.م</span></div>", unsafe_allow_html=True)
                if selected.get('phone'): st.info(f"📞 تليفون: {selected['phone']}")
                if selected.get('gps'): st.link_button("📍 موقع العميل (GPS)", selected['gps'])
            with c2:
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={selected['id']}"
                st.image(qr_url, caption="باركود العميل")

            st.write("---")
            with st.form("operation"):
                v_d = st.number_input("تكلفة الصيانة (+)", 0.0)
                v_p = st.number_input("المبلغ المحصل (-)", 0.0)
                v_f = st.multiselect("الشمع المستخدم:", ["شمعة 1", "2", "3", "4", "5", "6", "7", "ممبرين"])
                v_n = st.text_area("تفاصيل الزيارة")
                if st.form_submit_button("إرسال التقرير"):
                    for x in st.session_state.data:
                        if x['id'] == selected['id']:
                            x.setdefault('history', []).append({
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "note": v_n, "tech": st.session_state.current_tech,
                                "debt": v_d, "price": v_p, "filter_used": ", ".join(v_f)
                            })
                    save_json("customers.json", st.session_state.data)
                    st.success("✅ تم حفظ البيانات بنجاح")

    elif t_tab == "💰 محفظتي":
        my_cash = 0.0; filters = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') == st.session_state.current_tech:
                    my_cash += float(h.get('price', 0))
                    if h.get('filter_used'): filters.extend(h['filter_used'].split(", "))
        st.metric("💰 إجمالي المحصل معك", f"{my_cash:,.0f} ج.م")
        if filters:
            st.write("#### 📦 حصر الشمع:")
            st.table(pd.Series([f for f in filters if f]).value_counts())

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
