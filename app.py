import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق العام (Responsive Design) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    .client-card { 
        background: #001f3f; border: 2px solid #007bff; 
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        width: 100%; box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .history-card { 
        background: rgba(0, 80, 155, 0.2); border-radius: 10px; 
        padding: 15px; margin-bottom: 10px; border-right: 5px solid #00d4ff; 
    }
    .tech-tag { 
        background: #007bff; color: white; padding: 4px 10px; 
        border-radius: 8px; font-size: 13px; font-weight: bold;
    }
    .part-tag { background: #28a745; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left: 2px; }
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

if 'data' not in st.session_state:
    st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state:
    st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (QR) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"""
                <div class='client-card'>
                    <h2 style='text-align:center;'>{c['name']}</h2>
                    <p style='text-align:center; font-size:22px; color:#00ffcc;'>
                    المديونية المتبقية: {bal:,.0f} ج.م
                    </p>
                </div>
            """, unsafe_allow_html=True)

            st.subheader("📋 سجل الصيانة")
            for h in reversed(c.get('history', [])):
                st.markdown(f"""
                <div class="history-card">
                    <b>📅 {h['date']}</b><br>
                    🛠️ الفني: {h.get('tech','')}<br>
                    📝 {h.get('note','')}<br>
                    💰 مديونية: {h.get('debt',0)} | تحصيل: {h.get('price',0)}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except:
        st.error("خطأ في الرابط")
        st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>نظام الإدارة 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير"): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفني"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123":
            st.session_state.role = "admin"
            st.rerun()
    st.stop()

# ================== 5. لوحة المدير ==================
if st.session_state.role == "admin":

    # 🔄 زر تحديث
    if st.sidebar.button("🔄 تحديث الصفحة"):
        st.rerun()

    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        for i, c in enumerate(st.session_state.data):
            st.markdown('<div class="client-card">', unsafe_allow_html=True)
            st.subheader(c['name'])
            st.info(f"💰 المديونية الحالية: {calculate_balance(c.get('history', [])):,.0f} ج.م")

            # ✅ زيادة / إزالة مديونية
            with st.expander("💰 تعديل المديونية (زيادة / إزالة)"):
                col1, col2 = st.columns(2)
                with col1:
                    add_debt = st.number_input("➕ زيادة مديونية", 0.0, key=f"a{c['id']}")
                with col2:
                    rem_debt = st.number_input("➖ إزالة مديونية", 0.0, key=f"r{c['id']}")

                note = st.text_input("ملاحظة", value="تعديل إداري", key=f"n{c['id']}")

                if st.button("💾 حفظ التعديل", key=f"s{c['id']}"):
                    if add_debt > 0 or rem_debt > 0:
                        c.setdefault("history", []).append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "tech": "المدير",
                            "parts": [],
                            "note": note,
                            "debt": add_debt,
                            "price": rem_debt
                        })
                        save_json("customers.json", st.session_state.data)
                        st.success("✅ تم التعديل")
                        st.rerun()
                    else:
                        st.warning("⚠️ أدخل قيمة")

            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "🚪 خروج":
        del st.session_state.role
        st.rerun()
