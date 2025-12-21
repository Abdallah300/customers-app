import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات المظهر ==================
st.set_page_config(
    page_title="Power Life System",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"  # ← ده المهم
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

.stApp {
    background: #000b1a;
    color: #ffffff;
}

* {
    font-family: 'Cairo', sans-serif;
    text-align: right;
    direction: rtl;
}

.client-header { 
    background: #001f3f;
    border-radius: 15px;
    padding: 20px;
    border: 2px solid #007bff;
    margin-bottom: 25px;
}

/* نخفي الشريط من غير ما نكسر زر القايمة */
header { height: 0px; }
footer { visibility: hidden; }

</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_json("customers.json", [])

if "techs" not in st.session_state:
    st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return (
        sum(float(h.get("debt", 0)) for h in history)
        - sum(float(h.get("price", 0)) for h in history)
    )

# ================== 3. واجهة الباركود ==================
params = st.query_params

if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((x for x in st.session_state.data if x["id"] == cust_id), None)

        if c:
            st.markdown("<h1 style='text-align:center;color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)

            current_bal = calculate_balance(c.get("history", []))

            st.markdown(f"""
            <div class="client-header">
                <div>👤 <b>العميل:</b> {c["name"]}</div>
                <div style="color:#00d4ff;">📍 {c.get("gov","---")} | 🏛️ {c.get("branch","---")}</div>
                <hr>
                <div style="text-align:center;">
                    <p>إجمالي المديونية الحالية</p>
                    <p style="font-size:35px;color:#00ffcc;font-weight:bold;">
                        {current_bal:,.0f} ج.م
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("📋 سجل الحركات")

            running = 0
            for h in c.get("history", []):
                running += float(h.get("debt", 0)) - float(h.get("price", 0))
                h["after"] = running

            for h in reversed(c.get("history", [])):
                st.markdown("---")
                st.markdown(f"**📝 {h.get('note','عملية')}**")
                st.markdown(f"📅 {h.get('date')} | 👤 {h.get('tech')}")
                st.info(f"💰 الرصيد بعد العملية: {h['after']:,.0f} ج.م")

        st.stop()
    except:
        st.stop()

# ================== 4. شاشة الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>Power Life Control 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 لوحة الإدارة", use_container_width=True):
        st.session_state.role = "admin_login"
        st.rerun()
    if c2.button("🛠️ لوحة الفني", use_container_width=True):
        st.session_state.role = "tech_login"
        st.rerun()
    st.stop()

# ================== 5. تسجيل دخول الإدارة ==================
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123":
            st.session_state.role = "admin"
            st.rerun()
    if st.button("رجوع"):
        del st.session_state.role
        st.rerun()
    st.stop()

# ================== 6. لوحة الإدارة ==================
if st.session_state.role == "admin":
    st.sidebar.title("💎 لوحة الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "📊 الحسابات", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم")
        for c in st.session_state.data:
            if search in c["name"]:
                with st.expander(c["name"]):
                    if st.button("🖼️ باركود", key=c["id"]):
                        qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        st.image(qr)

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("اسم العميل")
            g = st.text_input("المحافظة")
            b = st.text_input("الفرع")
            d = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("إضافة"):
                new_id = max([x["id"] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": new_id,
                    "name": n,
                    "gov": g,
                    "branch": b,
                    "history": [{
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "note": "رصيد افتتاحي",
                        "tech": "الإدارة",
                        "debt": d,
                        "price": 0
                    }] if d > 0 else []
                })
                save_json("customers.json", st.session_state.data)
                st.success("تم الإضافة")

    elif menu == "📊 الحسابات":
        total = sum(calculate_balance(c.get("history", [])) for c in st.session_state.data)
        st.metric("إجمالي المديونيات", f"{total:,.0f} ج.م")

    elif menu == "🚪 خروج":
        del st.session_state.role
        st.rerun()
