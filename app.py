import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق المتقدم للموبايل ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-x: hidden !important; direction: rtl; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .client-card { 
        background: #001f3f; border: 2px solid #007bff; 
        border-radius: 12px; padding: 15px; margin-bottom: 15px;
        width: 100% !important; display: block;
    }
    div.stButton > button { width: 100% !important; border-radius: 8px; height: 50px; }
    .stSelectbox, .stTextInput, .stNumberInput { width: 100% !important; margin-bottom: 10px; }
    .history-card { background: rgba(0, 80, 155, 0.2); border-radius: 8px; padding: 12px; margin-top: 8px; border-right: 4px solid #00d4ff; }
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

# ================== 3. واجهة الباركود للعميل (بالرابط القديم) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-card'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:25px; color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.markdown(f'<div class="history-card"><b>📅 {h["date"]}</b><br>📝 {h["note"]}<br>💰 العملية: {float(h.get("debt",0)) - float(h.get("price",0))} ج.م</div>', unsafe_allow_html=True)
            st.stop()
    except:
        st.error("خطأ في البيانات.")
        st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:30px;'>Power Life System 🔒</h2>", unsafe_allow_html=True)
    if st.button("🔑 دخول المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    st.divider()
    if st.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
        else: st.error("خطأ في البيانات")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_list) if t_list else st.write("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    st.subheader("📊 لوحة تحكم المدير")
    if st.button("🔄 تحديث ومزامنة البيانات", use_container_width=True):
        refresh_all_data(); st.rerun()

    menu = st.sidebar.radio("القائمة", ["👥 البحث والإدارة", "➕ إضافة عميل", "🛠️ الفنيين", "🚪 خروج"])

    if menu == "👥 البحث والإدارة":
        # تم إرجاع الرابط الأصلي الخاص بك هنا
        client_base_url = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"
        search = st.text_input("🔍 ابحث بالاسم أو التليفون...")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                with st.container():
                    st.markdown(f'<div class="client-card">', unsafe_allow_html=True)
                    st.subheader(f"👤 {c['name']}")
                    st.write(f"📞 {c.get('phone','---')} | 💰 {calculate_balance(c.get('history', []))} ج.م")
                    with st.expander("⚙️ خيارات الإدارة"):
                        c['name'] = st.text_input("تعديل الاسم", value=c['name'], key=f"n{c['id']}")
                        if st.button("حفظ الاسم", key=f"sn{c['id']}"): 
                            save_json("customers.json", st.session_state.data); st.success("تم التعديل")
                        qr_data = f"{client_base_url}/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_data}", caption="باركود العميل")
                    st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("الاسم"); p = st.text_input("التليفون"); g = st.text_input("رابط GPS")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تم الإضافة")

    elif menu == "🛠️ الفنيين":
        with st.form("add_t"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("كلمة سر الفني")
            if st.form_submit_button("حفظ الفني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني ==================
elif st.session_state.role == "tech_p":
    st.markdown(f"<h3 style='text-align:center;'>مرحباً بك: {st.session_state.c_tech} 🛠️</h3>", unsafe_allow_html=True)
    if st.button("🔄 تحديث قائمة العملاء", use_container_width=True):
        refresh_all_data(); st.rerun()

    customer_names = {c['id']: c['name'] for c in st.session_state.data}
    selected_id = st.selectbox("🎯 اختر العميل لبدء العمل", options=list(customer_names.keys()), format_func=lambda x: customer_names[x])
    target = next((x for x in st.session_state.data if x['id'] == selected_id), None)
    
    if target:
        st.markdown(f"<div class='client-card'><b>العميل الحالى:</b> {target['name']}</div>", unsafe_allow_html=True)
        if target.get('gps'): st.link_button("📍 فتح الخريطة", target['gps'], use_container_width=True)
        with st.form("visit_form", clear_on_submit=True):
            v_add = st.number_input("تكلفة الصيانة", 0.0); v_rem = st.number_input("المحصل كاش", 0.0)
            note = st.text_area("ملاحظات الزيارة")
            if st.form_submit_button("✅ حفظ وإرسال"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.c_tech, "debt": v_add, "price": v_rem})
                save_json("customers.json", st.session_state.data); refresh_all_data(); st.success("تم التسجيل!")

    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
