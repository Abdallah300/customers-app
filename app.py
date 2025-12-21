import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات المظهر (إلغاء كل القيود) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

# كود CSS بسيط جداً ومفتوح للسماح بالتمرير الطبيعي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* السماح بالتمرير العمودي في كل مكان */
    html, body, [data-testid="stAppViewContainer"] {
        overflow-y: auto !important;
        height: auto !important;
    }

    .stApp { 
        background: #000b1a; 
        color: #ffffff;
    }
    
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    .client-header { 
        background: #001f3f; border-radius: 15px; 
        padding: 20px; border: 2px solid #007bff; margin-bottom: 25px; 
    }
    
    header, footer {visibility: hidden;}

    /* شريط تمرير عريض لسهولة الإمساك به على التاتش */
    ::-webkit-scrollbar { width: 12px; }
    ::-webkit-scrollbar-track { background: #000b1a; }
    ::-webkit-scrollbar-thumb { background: #007bff; border-radius: 10px; border: 2px solid #ffffff; }
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

# ================== 3. واجهة الباركود (العميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            current_bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><div style='font-size:18px;'>👤 <b>العميل:</b> {c['name']}</div><div style='font-size:15px; color:#00d4ff;'>📍 {c.get('gov', '---')} | 🏛️ {c.get('branch', '---')}</div><hr><div style='text-align:center;'><p>المديونية الحالية</p><p style='font-size:35px; color:#00ffcc; font-weight:bold;'>{current_bal:,.0f} ج.م</p></div></div>", unsafe_allow_html=True)
            
            st.subheader("📋 سجل الحركات")
            if c.get('history'):
                running_balance = 0
                history_with_balance = []
                for h in c['history']:
                    running_balance += (float(h.get('debt', 0)) - float(h.get('price', 0)))
                    h_copy = h.copy()
                    h_copy['after_bal'] = running_balance
                    history_with_balance.append(h_copy)
                for h in reversed(history_with_balance):
                    st.markdown("---")
                    st.markdown(f"**📝 {h.get('note', 'عملية')}** | 📅 `{h.get('date', '---')}`")
                    st.info(f"💰 المديونية بعد العملية: {h['after_bal']:,.0f} ج.م")
            st.stop()
    except: st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>نظام إدارة القوة 🔒</h2>", unsafe_allow_html=True)
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

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "➕ إضافة", "📊 إحصائيات", "🛠️ الفنيين", "🚪 خروج"])

    if menu == "👥 العملاء":
        search = st.text_input("بحث...")
        for i, c in enumerate(st.session_state.data):
            if search in c['name']:
                with st.expander(f"👤 {c['name']}"):
                    st.write(f"المحافظة: {c.get('gov','')}")
                    if st.button("🖼️ باركود", key=f"qr_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    if st.button("🗑️ حذف", key=f"del_{c['id']}", type="primary"):
                        st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة":
        with st.form("new"):
            n = st.text_input("الاسم"); g = st.text_input("المحافظة"); b = st.text_input("الفرع"); d = st.number_input("مديونية", 0.0)
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "gov": g, "branch": b, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "tech": "الإدارة", "debt": d, "price": 0}]})
                save_json("customers.json", st.session_state.data); st.success("تم")

    elif menu == "📊 إحصائيات":
        total = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي المديونية في السوق", f"{total:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. لوحة الفني ==================
elif st.session_state.role == "tech":
    st.sidebar.title(f"الفني: {st.session_state.tech_name}")
    target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: x['name'])
    with st.form("visit"):
        v_add = st.number_input("تكلفة صيانة", 0.0); v_rem = st.number_input("تحصيل", 0.0)
        note = st.text_area("الملاحظات")
        if st.form_submit_button("حفظ"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.tech_name, "debt": v_add, "price": v_rem})
            save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
    if st.sidebar.button("خروج"): del st.session_state.role; st.rerun()
