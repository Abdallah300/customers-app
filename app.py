import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات الصفحة ==================
st.set_page_config(
    page_title="Power Life System",
    page_icon="💧",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
.stApp { background:#000b1a; color:white; }
* { font-family:'Cairo', sans-serif; direction:rtl; text-align:right; }
.client-header {
    background:#001f3f;
    border-radius:15px;
    padding:20px;
    border:2px solid #007bff;
    margin-bottom:20px;
}
header {visibility:hidden;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. زر القايمة (الحل النهائي) ==================
if "show_menu" not in st.session_state:
    st.session_state.show_menu = True

if st.button("☰ القائمة", use_container_width=True):
    st.session_state.show_menu = not st.session_state.show_menu

# ================== 3. إدارة البيانات ==================
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return default
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_json("customers.json", [])

if "techs" not in st.session_state:
    st.session_state.techs = load_json("techs.json", [])

def calc_balance(h):
    return sum(float(x.get("debt",0)) for x in h) - sum(float(x.get("price",0)) for x in h)

# ================== 4. شاشة الباركود ==================
params = st.query_params
if "id" in params:
    cid = int(params["id"])
    c = next((x for x in st.session_state.data if x["id"] == cid), None)
    if c:
        bal = calc_balance(c.get("history", []))
        st.markdown(f"""
        <div class='client-header'>
        👤 <b>{c['name']}</b><br>
        📍 {c.get('gov','---')} | 🏛️ {c.get('branch','---')}
        <h2 style='text-align:center;color:#00ffcc'>{bal:,.0f} ج.م</h2>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# ================== 5. تسجيل الدخول ==================
if "role" not in st.session_state:
    c1, c2 = st.columns(2)
    if c1.button("🔑 الإدارة"):
        st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفني"):
        st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول") and u=="admin" and p=="admin123":
        st.session_state.role="admin"; st.rerun()
    st.stop()

# ================== 6. لوحة الإدارة ==================
if st.session_state.role == "admin":

    if st.session_state.show_menu:
        st.sidebar.title("💎 لوحة الإدارة")
        menu = st.sidebar.radio("القائمة", ["👥 العملاء","➕ إضافة","📊 حسابات","🚪 خروج"])
    else:
        menu = None

    if menu == "👥 العملاء":
        for c in st.session_state.data:
            with st.expander(c["name"]):
                st.write("الرصيد:", calc_balance(c.get("history",[])))

    if menu == "➕ إضافة":
        with st.form("add"):
            n = st.text_input("اسم العميل")
            if st.form_submit_button("حفظ"):
                new_id = max([x["id"] for x in st.session_state.data], default=0)+1
                st.session_state.data.append({"id":new_id,"name":n,"history":[]})
                save_json("customers.json", st.session_state.data)
                st.success("تم")

    if menu == "📊 حسابات":
        total = sum(calc_balance(c.get("history",[])) for c in st.session_state.data)
        st.metric("إجمالي المديونيات", f"{total:,.0f} ج.م")

    if menu == "🚪 خروج":
        del st.session_state.role
        st.rerun()
