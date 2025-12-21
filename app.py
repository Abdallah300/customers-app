import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق (الأزرق الملكي) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-header { background: #001f3f; border-radius: 15px; padding: 20px; border: 2px solid #007bff; margin-bottom: 25px; text-align: center; }
    .history-card { background: rgba(0, 31, 63, 0.7); border: 1px solid #00d4ff; border-right: 5px solid #00d4ff; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
    .date-badge { background: #007bff; color: white; padding: 2px 10px; border-radius: 5px; font-size: 14px; }
    header, footer {visibility: hidden;}
    .stMetric { background: #001f3f; padding: 10px; border-radius: 10px; border: 1px solid #007bff; }
    .logo-container { text-align: center; padding: 20px; margin-bottom: 10px; }
    .logo-text { font-size: 45px; font-weight: bold; color: #00d4ff; text-shadow: 2px 2px 10px #007bff; }
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

# ================== 3. واجهة الباركود (صفحة العميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<div class='logo-container'><span class='logo-text'>Power Life 💧</span></div>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><h2>{c['name']}</h2><div style='font-size:30px; color:#00ffcc;'>المديونية المتبقية: {bal:,.0f} ج.م</div></div>", unsafe_allow_html=True)
            if c.get('history'):
                running_balance = 0
                history_with_balance = []
                for h in c['history']:
                    running_balance += (float(h.get('debt', 0)) - float(h.get('price', 0)))
                    h_copy = h.copy(); h_copy['after_bal'] = running_balance; history_with_balance.append(h_copy)
                for h in reversed(history_with_balance):
                    st.markdown(f'<div class="history-card"><span class="date-badge">📅 {h["date"]}</span><div style="margin-top:10px;"><b>📝 البيان:</b> {h["note"]}<br><b>🛠️ صيانة:</b> {float(h.get("debt",0))} | <b>🟢 محصل:</b> {float(h.get("price",0))}<hr><b>المتبقي: {h["after_bal"]:,.0f} ج.م</b></div></div>', unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<div class='logo-container'><span class='logo-text'>Power Life 💧</span></div>", unsafe_allow_html=True)
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
    t_user = st.selectbox("اختر اسمك", t_names) if t_names else st.error("لا يوجد فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech_data = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech_data['pass']: st.session_state.role = "tech_panel"; st.session_state.current_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الإدارة (إدارة العملاء والبحث) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("<h2 style='text-align:center; color:#00d4ff;'>Power Life 💧</h2>", unsafe_allow_html=True)
    menu = st.sidebar.radio("التحكم الرئيسي", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ إدارة الفنيين", "📊 التقارير المالية", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بالكود (رقم فقط) أو بالاسم أو التليفون...")
        
        if search:
            search_clean = search.strip().lower()
            filtered_data = []

            for c in st.session_state.data:
                # ميزة البحث الدقيق بالـ ID: لو المستخدم كتب رقم فقط، قارن بالـ ID بالظبط
                if search_clean.isdigit():
                    if str(c['id']) == search_clean:
                        filtered_data.append(c)
                # لو كتب حروف، ابحث في الاسم والتليفون بشكل عادي
                else:
                    if (search_clean in c['name'].lower()) or (search_clean in str(c.get('phone', ''))):
                        filtered_data.append(c)

            for c in filtered_data:
                with st.container():
                    st.markdown(f"### {c['name']} (كود: {c['id']})")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        # الباركود (QR Code) شغال كما هو
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                        if c.get('gps'): st.link_button("📍 فتح اللوكيشن (GPS)", c['gps'])
                    with col2:
                        with st.expander("📝 تعديل البيانات والجي بي اس"):
                            c['name'] = st.text_input("الاسم", value=c['name'], key=f"n{c['id']}")
                            c['phone'] = st.text_input("التليفون", value=c.get('phone',''), key=f"p{c['id']}")
                            c['gps'] = st.text_input("رابط جوجل ماب (GPS)", value=c.get('gps',''), key=f"g{c['id']}")
                            if st.button("حفظ التعديلات", key=f"s{c['id']}"): save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
                        with st.expander("💸 مديونية سريعة"):
                            d1 = st.number_input("صيانة (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("تحصيل (-)", 0.0, key=f"r{c['id']}")
                            if st.button("تسجيل", key=f"t{c['id']}"):
                                c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل إداري", "tech": "المدير", "debt": d1, "price": d2})
                                save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("الاسم"); p = st.text_input("التليفون"); loc = st.text_input("رابط اللوكيشن (GPS)"); d = st.number_input("مديونية افتتاحية", 0.0)
            if st.form_submit_button("إضافة للسيستم"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "tech": "المدير", "debt": d, "price": 0}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم الإضافة بكود: {new_id}")

    elif menu == "🛠️ إدارة الفنيين":
        with st.form("add_tech"):
            tn = st.text_input("اسم الفني"); tp = st.text_input("كلمة سر الدخول")
            if st.form_submit_button("تسجيل فني"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()
        for t in st.session_state.techs: st.info(f"🛠️ {t['name']}")

    elif menu == "📊 التقارير المالية":
        total_market = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي المديونية في الخارج", f"{total_market:,.0f} ج.م")
        today = datetime.now().strftime("%Y-%m-%d")
        daily_coll = sum(sum(float(h.get('price', 0)) for h in c.get('history', []) if today in h['date']) for c in st.session_state.data)
        st.metric("تحصيل اليوم", f"{daily_coll:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (إضافة زيارة) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown("<h2 style='text-align:center; color:#00d4ff;'>Power Life 💧</h2>", unsafe_allow_html=True)
    st.sidebar.info(f"🛠️ الفني: {st.session_state.current_tech}")
    target = st.selectbox("اختر العميل للزيارة", st.session_state.data, format_func=lambda x: f"{x['id']} - {x['name']}")
    
    if target.get('gps'): st.link_button("📍 فتح الخريطة للذهاب للعميل", target['gps'], use_container_width=True)
    
    with st.form("visit_form"):
        v_add = st.number_input("تكلفة الصيانة", 0.0); v_rem = st.number_input("المحصل", 0.0); note = st.text_area("التقرير")
        if st.form_submit_button("إرسال التقرير"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.current_tech, "debt": v_add, "price": v_rem})
            save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
