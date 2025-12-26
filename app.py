import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. إعدادات الهوية والاسم ==================
# هذا الجزء يحدد الاسم الذي يظهر في المتصفح وعند الإضافة للشاشة
st.set_page_config(
    page_title="Power Life", 
    page_icon="💧", 
    layout="wide"
)

# دالة لتحويل ملف الصورة الذي رفعته أنت إلى كود نصي لضمان ظهوره دائماً
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# تحويل شعار "باور لايف" الذي رفعته أنت (1000357687.jpg)
logo_base64 = get_image_base64("1000357687.jpg")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-x: hidden !important; direction: rtl; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .client-card { 
        background: #001f3f; border: 2px solid #007bff; 
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
    }
    div.stButton > button { width: 100% !important; border-radius: 8px; height: 45px; background-color: #007bff; color: white; }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
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

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (باركود) ==================
params = st.query_params
if "id" in params:
    try:
        c = next((i for i in st.session_state.data if i['id'] == int(params["id"])), None)
        if c:
            if logo_base64: st.image(f"data:image/jpeg;base64,{logo_base64}", width=150)
            st.markdown(f"<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-card'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:25px; color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.markdown(f'<div style="background:rgba(0,80,155,0.2); padding:10px; margin-top:5px; border-right:4px solid #00d4ff;"><b>📅 {h["date"]}</b><br>📝 {h["note"]}</div>', unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. صفحة الدخول مع الشعار المضمون ==================
if logo_base64:
    st.image(f"data:image/jpeg;base64,{logo_base64}", use_container_width=True)
else:
    st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)

if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>نظام إدارة باور لايف 🔒</h2>", unsafe_allow_html=True)
    if st.button("🔑 دخول المدير"): st.session_state.role = "admin_login"; st.rerun()
    if st.button("🛠️ دخول الفني"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- منطق تسجيل الدخول (Admin/Tech) ---
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "📊 التقارير", "🚪 خروج"])
    
    if menu == "👥 العملاء":
        search = st.text_input("🔍 ابحث بالاسم أو التليفون...")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                with st.container():
                    st.markdown('<div class="client-card">', unsafe_allow_html=True)
                    st.subheader(f"👤 {c['name']}")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        qr_link = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={qr_link}")
                        st.write(f"💰 الرصيد: {calculate_balance(c.get('history', []))}")
                    with col2:
                        with st.expander("💸 عمليات سريعة"):
                            d1 = st.number_input("إضافة (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("تحصيل (-)", 0.0, key=f"r{c['id']}")
                            if st.button("تسجيل", key=f"t{c['id']}"):
                                c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل إداري", "debt": d1, "price": d2})
                                save_json("customers.json", st.session_state.data); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ إضافة عميل":
        with st.form("add"):
            n = st.text_input("الاسم"); ph = st.text_input("التليفون"); g = st.text_input("GPS")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": ph, "gps": g, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تم الحفظ!")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني ==================
elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ الفني: {st.session_state.c_tech}")
    customer_names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل", options=list(customer_names.keys()), format_func=lambda x: customer_names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        if target.get('gps'): st.link_button("📍 موقع العميل", target['gps'])
        with st.form("visit"):
            v_add = st.number_input("التكلفة", 0.0); v_rem = st.number_input("المحصل", 0.0); note = st.text_area("ملاحظات")
            if st.form_submit_button("✅ إرسال التقرير"):
                target.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.c_tech, "debt": v_add, "price": v_rem})
                save_json("customers.json", st.session_state.data); st.success("تم!")
    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
