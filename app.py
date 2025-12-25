import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق (الأزرق الملكي) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* ستايل كارت العميل العلوي */
    .client-header { background: #001f3f; border-radius: 15px; padding: 20px; border: 2px solid #007bff; margin-bottom: 25px; text-align: center; }
    
    /* ستايل المربعات المنفصلة لكل تاريخ */
    .history-card {
        background: rgba(0, 31, 63, 0.7);
        border: 1px solid #00d4ff;
        border-right: 5px solid #00d4ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .date-badge { background: #007bff; color: white; padding: 2px 10px; border-radius: 5px; font-size: 14px; }
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

# ================== 3. واجهة الباركود (صفحة العميل - المربعات المنفصلة) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            
            st.markdown(f"""
            <div class='client-header'>
                <h2>{c['name']}</h2>
                <p style='font-size:18px; color:#00d4ff;'>📍 {c.get('gov','')} | 📞 {c.get('phone','')}</p>
                <div style='font-size:30px; color:#00ffcc; font-weight:bold;'>المديونية المتبقية: {bal:,.0f} ج.م</div>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("📋 سجل الحركات المالية (كل عملية في مربع)")
            
            if c.get('history'):
                running_balance = 0
                history_with_balance = []
                for h in c['history']:
                    running_balance += (float(h.get('debt', 0)) - float(h.get('price', 0)))
                    h_copy = h.copy()
                    h_copy['after_bal'] = running_balance
                    history_with_balance.append(h_copy)
                
                for h in reversed(history_with_balance):
                    st.markdown(f"""
                    <div class="history-card">
                        <span class="date-badge">📅 {h['date']}</span>
                        <div style="margin-top:10px;">
                            <b>📝 البيان:</b> {h['note']}<br>
                            <b>🛠️ مضاف (صيانة):</b> <span style="color:#ff4b4b;">{float(h.get('debt',0)):,.0f} ج.م</span> | 
                            <b>🟢 محصل:</b> <span style="color:#00ffcc;">{float(h.get('price',0)):,.0f} ج.م</span>
                            <hr style="border:0.1px solid #333; margin:10px 0;">
                            <div style="text-align:left; font-weight:bold; color:#00d4ff;">
                                المتبقي بعد هذه العملية: {h['after_bal']:,.0f} ج.م
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life Control 🔒</h2>", unsafe_allow_html=True)
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

# ================== 5. واجهة الإدارة (البحث والتعديل والباركود) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث باسم العميل أو رقم التليفون...")
        if search:
            found = False
            for i, c in enumerate(st.session_state.data):
                if search.lower() in c['name'].lower() or search in str(c.get('phone', '')):
                    found = True
                    st.markdown(f"### 👤 العميل: {c['name']} (كود: {c['id']})")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                        st.write(f"💰 الرصيد: **{calculate_balance(c.get('history', [])):,.0f} ج.م**")
                        if st.button("🗑️ حذف نهائي", key=f"del_{c['id']}", type="primary"):
                            st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()
                    with col2:
                        with st.expander("📝 تعديل البيانات", expanded=True):
                            c['name'] = st.text_input("تغيير الاسم", value=c['name'], key=f"n_{c['id']}")
                            c['phone'] = st.text_input("تعديل التليفون", value=c.get('phone',''), key=f"p_{c['id']}")
                            c['gov'] = st.text_input("المحافظة", value=c.get('gov',''), key=f"g_{c['id']}")
                            if st.button("حفظ", key=f"sv_{c['id']}"):
                                save_json("customers.json", st.session_state.data); st.success("تم")
                        with st.expander("💸 مديونية وملاحظات"):
                            a_debt = st.number_input("زيادة (+)", 0.0, key=f"ad_{c['id']}")
                            a_price = st.number_input("تحصيل (-)", 0.0, key=f"ap_{c['id']}")
                            a_note = st.text_area("الملاحظات", key=f"an_{c['id']}")
                            if st.button("تسجيل", key=f"tr_{c['id']}"):
                                c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": a_note, "tech": "الإدارة", "debt": a_debt, "price": a_price})
                                save_json("customers.json", st.session_state.data); st.rerun()
            if not found: st.warning("لا يوجد نتائج.")
    
    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("الاسم"); p = st.text_input("التليفون"); g = st.text_input("المحافظة"); d = st.number_input("افتتاحي", 0.0)
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gov": g, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "debt": d, "price": 0}]})
                save_json("customers.json", st.session_state.data); st.success("تم")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()
