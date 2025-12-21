import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر (الأزرق الاحترافي) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* كارت بيانات العميل الرئيسي */
    .client-header { 
        background: rgba(0, 123, 255, 0.1); border-radius: 15px; 
        padding: 20px; border: 1px solid #007bff; margin-bottom: 20px; 
    }
    
    /* كروت العمليات باللون الأزرق */
    .op-card { 
        background: #002b5c; /* أزرق غامق */
        color: #ffffff; border-radius: 12px; 
        padding: 15px; margin-bottom: 15px; 
        border-right: 8px solid #00d4ff; /* خط جانبي لبني */
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .op-date { font-size: 12px; color: #00d4ff; }
    .op-note { font-size: 18px; font-weight: bold; margin: 10px 0; }
    .price-tag { font-size: 16px; font-weight: bold; padding: 5px 10px; border-radius: 5px; }
    
    header {visibility: hidden;}
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

# ================== 3. واجهة الباركود (تقرير العميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            
            st.markdown(f"""
            <div class='client-header'>
                <h3 style='text-align:center; color:#00d4ff; margin-bottom:15px;'>تقرير الحساب المالي</h3>
                <div style='display:flex; justify-content:space-between; flex-wrap:wrap;'>
                    <span>👤 <b>الاسم:</b> {c['name']}</span>
                    <span>📍 <b>المحافظة:</b> {c.get('gov', '---')}</span>
                    <span>🏛️ <b>الفرع:</b> {c.get('branch', '---')}</span>
                </div>
                <hr style='opacity:0.2;'>
                <div style='text-align:center;'>
                    <p style='margin:0;'>المديونية الحالية</p>
                    <p style='font-size:32px; color:#00d4ff; font-weight:bold;'>{bal:,.0f} ج.م</p>
                </div>
            </div>
            <h3 style='margin-bottom:15px;'>📋 سجل الحركات المالية</h3>
            """, unsafe_allow_html=True)
            
            if c.get('history'):
                for h in reversed(c['history']):
                    # حماية التاريخ
                    dt = h.get('date', datetime.now().strftime("%Y-%m-%d %H:%M"))
                    h_add = float(h.get('debt', 0))
                    h_rem = float(h.get('price', 0))
                    
                    st.markdown(f"""
                    <div class="op-card">
                        <div style="display:flex; justify-content:space-between;">
                            <span class="op-date">📅 {dt}</span>
                            <span style="font-size:12px; color:#aaa;">👤 المسئول: {h.get('tech', 'الإدارة')}</span>
                        </div>
                        <div class="op-note">📝 {h.get('note', 'تسويه حساب')}</div>
                        <div style="display:flex; gap:20px;">
                            {f'<span style="color:#ff4b4b;">➕ مضاف: {h_add:,.0f} ج.م</span>' if h_add > 0 else ''}
                            {f'<span style="color:#00ffcc;">➖ مخصوم: {h_rem:,.0f} ج.م</span>' if h_rem > 0 else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد عمليات مسجلة للعميل.")
            st.stop()
    except:
        st.stop()

# ================== 4. لوحة التحكم (الدخول) ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>لوحة التحكم 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- إدارة الدخول ---
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر الفني", t_list) if t_list else st.error("لا يوجد فنيين")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech"; st.session_state.tech_name = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الإدارة الكاملة ==================
if st.session_state.role == "admin":
    st.sidebar.title("💎 الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "📊 الحسابات", "🛠️ إدارة الفنيين", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم...")
        for i, c in enumerate(st.session_state.data):
            if search in c['name']:
                with st.expander(f"👤 {c['name']}"):
                    st.info(f"المديونية الحالية: {calculate_balance(c.get('history', []))} ج.م")
                    with st.form(f"edit_{c['id']}"):
                        c['gov'] = st.text_input("المحافظة", value=c.get('gov', ''))
                        c['branch'] = st.text_input("الفرع", value=c.get('branch', ''))
                        a_add = st.number_input("إضافة مديونية", min_value=0.0)
                        a_rem = st.number_input("إزالة مديونية", min_value=0.0)
                        note = st.text_input("البيان", value="تسويه إدارية")
                        if st.form_submit_button("حفظ البيانات"):
                            if a_add > 0 or a_rem > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": "الإدارة", "debt": a_add, "price": a_rem})
                            save_json("customers.json", st.session_state.data); st.success("تم الحفظ"); st.rerun()
                    if st.button("🖼️ إنشاء باركود العميل", key=f"q_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")

    elif menu == "➕ إضافة عميل":
        with st.form("add_new"):
            n = st.text_input("اسم العميل")
            g = st.text_input("المحافظة")
            b = st.text_input("الفرع")
            d = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("إضافة العميل لقاعدة البيانات"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "gov": g, "branch": b, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "debt": d, "price": 0}] if d > 0 else []})
                save_json("customers.json", st.session_state.data); st.success("تمت الإضافة بنجاح")

    elif menu == "📊 الحسابات":
        st.metric("إجمالي مديونيات السوق", f"{sum(calculate_balance(c.get('history', [])) for c in st.session_state.data):,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني الكاملة ==================
elif st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ {st.session_state.tech_name}")
    target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
    with st.form("tech_f"):
        v1 = st.number_input("إضافة مديونية (تكلفة صيانة)", min_value=0.0)
        v2 = st.number_input("إزالة مديونية (مبلغ مستلم)", min_value=0.0)
        note = st.text_area("وصف الزيارة")
        if st.form_submit_button("حفظ الزيارة"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.tech_name, "debt": v1, "price": v2})
            save_json("customers.json", st.session_state.data); st.success("تم الحفظ بنجاح")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
