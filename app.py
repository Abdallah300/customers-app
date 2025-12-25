import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق (إصلاح القوائم والشاشة) ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* جعل القوائم كبيرة وواضحة */
    .client-card { 
        background: #001f3f; border: 2px solid #007bff; 
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        width: 100%; box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .history-card { background: rgba(0, 80, 155, 0.2); border-radius: 10px; padding: 15px; margin-bottom: 10px; border-right: 5px solid #00d4ff; }
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
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة الباركود للعميل (ثابتة ومنظمة) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-card'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:25px; color:#00ffcc;'>إجمالي المتبقي: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.markdown(f'<div class="history-card"><b>📅 {h["date"]}</b><br>📝 {h["note"]}<br>💰 العملية: {float(h.get("debt",0)) - float(h.get("price",0))} ج.م</div>', unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life System 🔒</h2>", unsafe_allow_html=True)
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
    t_user = st.selectbox("اختر اسمك", t_list) if t_list else st.error("لا يوجد فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة (متابعة الفنيين + إصلاح التقارير) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 البحث والإدارة", "➕ إضافة عميل", "🛠️ مراقبة الفنيين", "📊 التقارير المالية", "🚪 خروج"])

    if menu == "👥 البحث والإدارة":
        search = st.text_input("🔍 ابحث بالاسم أو التليفون...")
        if search:
            for i, c in enumerate(st.session_state.data):
                if search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                    with st.container():
                        st.markdown(f'<div class="client-card">', unsafe_allow_html=True)
                        st.subheader(f"👤 {c['name']}")
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                            if c.get('gps'): st.link_button("📍 موقع العميل", c['gps'])
                            st.write(f"💰 الرصيد: {calculate_balance(c.get('history', []))} ج.م")
                        with col2:
                            with st.expander("📝 تعديل البيانات", expanded=True):
                                c['name'] = st.text_input("الاسم", value=c['name'], key=f"n{c['id']}")
                                c['phone'] = st.text_input("التليفون", value=c.get('phone',''), key=f"p{c['id']}")
                                c['gps'] = st.text_input("GPS", value=c.get('gps',''), key=f"g{c['id']}")
                                if st.button("حفظ", key=f"s{c['id']}"): save_json("customers.json", st.session_state.data); st.success("تم")
                            with st.expander("💸 عملية سريعة"):
                                d1 = st.number_input("إضافة (+)", 0.0, key=f"d{c['id']}"); d2 = st.number_input("تحصيل (-)", 0.0, key=f"r{c['id']}")
                                if st.button("تسجيل", key=f"t{c['id']}"):
                                    c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل إداري", "tech": "المدير", "debt": d1, "price": d2})
                                    save_json("customers.json", st.session_state.data); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "🛠️ مراقبة الفنيين":
        st.subheader("🛠️ تقارير أداء الفنيين اليومية")
        all_ops = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') != "المدير":
                    all_ops.append({"التاريخ": h['date'], "الفني": h['tech'], "العميل": c['name'], "المحصل": h.get('price', 0), "الصيانة": h.get('debt', 0), "الملاحظات/الشمع": h.get('note', '')})
        if all_ops:
            st.table(all_ops) # عرض جدول كامل لمراقبة الفنيين
        else: st.info("لا توجد زيارات مسجلة للفنيين بعد.")
        
        st.divider()
        with st.form("add_tech"):
            st.write("➕ إضافة فني جديد")
            tn = st.text_input("اسم الفني"); tp = st.text_input("السر")
            if st.form_submit_button("حفظ الفني"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "📊 التقارير المالية":
        total_m = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        today = datetime.now().strftime("%Y-%m-%d")
        t_coll = sum(sum(float(h.get('price', 0)) for h in c.get('history', []) if today in str(h['date'])) for c in st.session_state.data)
        st.metric("💰 إجمالي الديون في السوق", f"{total_m:,.0f} ج.م")
        st.metric("🟢 تحصيل اليوم", f"{t_coll:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (تتبع + تسجيل الشمع والمبالغ) ==================
elif st.session_state.role == "tech_p":
    st.sidebar.title(f"🛠️ الفني: {st.session_state.c_tech}")
    target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
    if target.get('gps'): st.link_button("📍 فتح الخريطة للوصول للعميل", target['gps'], use_container_width=True)
    
    with st.form("tech_visit"):
        v_add = st.number_input("تكلفة الشمع/الصيانة", 0.0)
        v_rem = st.number_input("المبلغ المستلم من العميل", 0.0)
        filters = st.multiselect("الشمع الذي تم تغييره", ["1", "2", "3", "4", "5", "6", "7"])
        note = st.text_area("ملاحظات إضافية")
        if st.form_submit_button("إرسال التقرير"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    full_note = f"شمع: {filters} | ملاحظة: {note}"
                    x.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": full_note, "tech": st.session_state.c_tech, "debt": v_add, "price": v_rem})
            save_json("customers.json", st.session_state.data); st.success("تم الحفظ بنجاح")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
