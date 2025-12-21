import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق (Power Life Dashboard) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-header { background: linear-gradient(135deg, #001f3f 0%, #000b1a 100%); border-radius: 20px; padding: 25px; border: 1px solid #007bff; text-align: center; margin-bottom: 30px; }
    .balance-tag { font-size: 26px; font-weight: bold; color: #00ffcc; background: rgba(0, 255, 204, 0.1); padding: 10px 20px; border-radius: 12px; border: 1px solid #00ffcc; display: inline-block; }
    .op-card { background: rgba(255, 255, 255, 0.03); border-radius: 15px; padding: 20px; margin-bottom: 15px; border-right: 5px solid #007bff; }
    .op-note { font-size: 18px; font-weight: bold; color: #f0f0f0; margin: 10px 0; }
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

# ================== 3. واجهة الباركود (صفحة العميل بنظام المربعات) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown(f"<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><h2 style='color:white;'>مرحباً بك: {c['name']}</h2><div class='balance-tag'>إجمالي المتبقي: {bal:,.0f} ج.م</div></div>", unsafe_allow_html=True)
            
            st.markdown("### 📑 سجل العمليات")
            for h in reversed(c.get('history', [])):
                p = float(h.get('price', 0))
                d = float(h.get('debt', 0))
                color = "#00ffcc" if p > 0 else "#ff4b4b"
                icon = "💰 تحصيل" if p > 0 else "🛠️ صيانة"
                st.markdown(f"""
                <div class="op-card" style="border-right-color: {color}">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color:#8899ac;">📅 {h.get('date','')}</span>
                        <span style="color:{color}; font-weight:bold;">{icon}</span>
                    </div>
                    <div class="op-note">{h.get('note','-')}</div>
                    <div style="border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                        {f"<span style='color:#ff4b4b;'>تكلفة: {d} ج.م</span>" if d > 0 else ""}
                        {f"<span style='color:#00ffcc; margin-right:15px;'>دفع: {p} ج.م</span>" if p > 0 else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
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

# ================== 5. واجهة الإدارة الشاملة ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## Power Life 💧")
    menu = st.sidebar.radio("التحكم", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بالكود (رقم) أو الاسم أو التليفون...")
        if search:
            s_clean = search.strip().lower()
            filtered = [c for c in st.session_state.data if (s_clean.isdigit() and str(c['id']) == s_clean) or (not s_clean.isdigit() and (s_clean in c['name'].lower() or s_clean in str(c.get('phone',''))))]
            for c in filtered:
                bal = calculate_balance(c.get('history', []))
                st.markdown(f"### {c['name']} (كود: {c['id']})")
                st.markdown(f"<div class='balance-tag'>الرصيد: {bal:,.0f} ج.م</div>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    with st.expander("📍 تعديل البيانات والـ GPS"):
                        c['name'] = st.text_input("تعديل الاسم", c['name'], key=f"un{c['id']}")
                        c['phone'] = st.text_input("تعديل الفون", c.get('phone',''), key=f"up{c['id']}")
                        c['gps'] = st.text_input("تعديل GPS", c.get('gps',''), key=f"ug{c['id']}")
                        if st.button("حفظ التعديلات", key=f"us{c['id']}"): save_json("customers.json", st.session_state.data); st.success("تم")
                with col2:
                    with st.expander("💸 تسجيل عملية مالية"):
                        d1 = st.number_input("صيانة (+)", key=f"d{c['id']}"); d2 = st.number_input("تحصيل (-)", key=f"r{c['id']}")
                        note = st.text_input("ملاحظات", key=f"nt{c['id']}")
                        if st.button("تسجيل", key=f"t{c['id']}"):
                            c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": "المدير", "debt": d1, "price": d2})
                            save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "🛠️ تقارير الفنيين":
        st.subheader("🛠️ مراقبة أداء الفنيين")
        all_visits = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') and h.get('tech') != "المدير":
                    all_visits.append({"الفني": h['tech'], "العميل": c['name'], "التاريخ": h['date'], "البيان": h['note'], "المحصل": h.get('price', 0)})
        if all_visits:
            df = pd.DataFrame(all_visits)
            st.dataframe(df, use_container_width=True)
            st.table(df.groupby('الفني')['المحصل'].sum().reset_index())
        else: st.info("لا زيارات.")
        with st.expander("➕ إضافة فني جديد"):
            tn = st.text_input("الاسم"); tp = st.text_input("الباسورد")
            if st.button("حفظ الفني"): st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new"):
            n = st.text_input("الاسم"); p = st.text_input("الفون"); loc = st.text_input("GPS"); d = st.number_input("مديونية افتتاحية")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم! الكود: {new_id}")

    elif menu == "📊 المالية":
        total = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي المديونية بالخارج", f"{total:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: {st.session_state.current_tech}")
    target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: f"{x['id']} - {x['name']}")
    with st.form("v"):
        v_d = st.number_input("تكلفة صيانة", 0.0); v_p = st.number_input("محصل", 0.0); v_n = st.text_area("ماذا تم؟")
        if st.form_submit_button("إرسال تقرير"):
            for x in st.session_state.data:
                if x['id'] == target['id']: x.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": v_n, "tech": st.session_state.current_tech, "debt": v_d, "price": v_p})
            save_json("customers.json", st.session_state.data); st.success("تم")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
