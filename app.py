import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. التنسيق والهوية (الاسم والأيقونة) ==================
st.set_page_config(
    page_title="Power Life", 
    page_icon="💧", 
    layout="wide"
)

# دالة لتحويل الصورة المحلية إلى كود نصي (Base64) لضمان ظهورها دائماً
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# حاول تحميل الصورة من الملف الذي رفعته أنت (1000357687.jpg)
img_base64 = get_base64_image("1000357687.jpg")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-x: hidden !important; direction: rtl; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .client-card { 
        background: #001f3f; border: 2px solid #007bff; 
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
        width: 100% !important; display: block;
    }
    div.stButton > button { width: 100% !important; border-radius: 8px; height: 45px; background-color: #007bff; color: white; }
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

def refresh_all_data():
    st.session_state.data = load_json("customers.json", [])
    st.session_state.techs = load_json("techs.json", [])
    st.cache_data.clear()

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة الباركود للعميل ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            if img_base64: st.image(f"data:image/png;base64,{img_base64}", width=150)
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-card'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:25px; color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.markdown(f'<div class="history-card"><b>📅 {h["date"]}</b><br>📝 {h["note"]}<br>💰 العملية: {float(h.get("debt",0)) - float(h.get("price",0))} ج.م</div>', unsafe_allow_html=True)
            st.stop()
    except:
        st.stop()

# ================== 4. نظام الدخول ==================
if img_base64:
    st.image(f"data:image/png;base64,{img_base64}", use_container_width=True)
else:
    st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)

if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>نظام إدارة باور لايف 🔒</h2>", unsafe_allow_html=True)
    if st.button("🔑 دخول المدير"): st.session_state.role = "admin_login"; st.rerun()
    if st.button("🛠️ دخول الفني"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (منطق تسجيل الدخول)
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_list) if t_list else st.write("لا يوجد فنيين")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 البحث والإدارة", "➕ إضافة عميل", "🛠️ الفنيين", "📊 التقارير", "🚪 خروج"])

    if menu == "👥 البحث والإدارة":
        client_base_url = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"
        search = st.text_input("🔍 ابحث...")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                with st.container():
                    st.markdown(f'<div class="client-card">', unsafe_allow_html=True)
                    st.subheader(f"👤 {c['name']}")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        qr_data = f"{client_base_url}/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={qr_data}")
                        if c.get('gps'): st.link_button("📍 الموقع", c['gps'])
                        st.write(f"💰 الرصيد: {calculate_balance(c.get('history', []))} ج.م")
                    with col2:
                        with st.expander("📝 تعديل / 💸 عمليات"):
                            c['name'] = st.text_input("الاسم", value=c['name'], key=f"n{c['id']}")
                            if st.button("حفظ الاسم", key=f"s{c['id']}"): save_json("customers.json", st.session_state.data)
                            d1 = st.number_input("إضافة (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("تحصيل (-)", 0.0, key=f"r{c['id']}")
                            if st.button("تسجيل", key=f"t{c['id']}"):
                                c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل إداري", "debt": d1, "price": d2})
                                save_json("customers.json", st.session_state.data); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ إضافة عميل":
        with st.form("add"):
            n = st.text_input("الاسم"); ph = st.text_input("التليفون"); g = st.text_input("GPS")
            if st.form_submit_button("حفظ"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": ph, "gps": g, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تم!")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني ==================
elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ الفني: {st.session_state.c_tech}")
    customer_names = {c['id']: c['name'] for c in st.session_state.data}
    selected_id = st.selectbox("🎯 اختر العميل", options=list(customer_names.keys()), format_func=lambda x: customer_names[x])
    target = next((x for x in st.session_state.data if x['id'] == selected_id), None)
    if target:
        if target.get('gps'): st.link_button("📍 موقع العميل", target['gps'], use_container_width=True)
        with st.form("visit"):
            v_add = st.number_input("التكلفة", 0.0); v_rem = st.number_input("المحصل", 0.0); note = st.text_area("ملاحظات")
            if st.form_submit_button("✅ إرسال"):
                target.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.c_tech, "debt": v_add, "price": v_rem})
                save_json("customers.json", st.session_state.data); st.success("تم!")
    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
