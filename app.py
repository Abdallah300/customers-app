import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر المتقدمة (للموبايل والكمبيوتر) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تصميم كارت بيانات العميل */
    .client-header { background: rgba(0, 123, 255, 0.15); border-radius: 15px; padding: 20px; border: 1px solid #007bff; margin-bottom: 20px; }
    .data-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05); }
    .label { color: #00d4ff; font-weight: bold; }
    
    /* تصميم سجل العمليات للموبايل (كروت) */
    .mobile-card { background: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 15px; margin-bottom: 15px; border-right: 5px solid #007bff; }
    .card-date { font-size: 0.85rem; color: #aaa; }
    .card-amount { font-size: 1.1rem; font-weight: bold; margin-top: 5px; }
    .plus { color: #ff4b4b; } /* إضافة مديونية */
    .minus { color: #00ffcc; } /* إزالة مديونية */
    
    /* إخفاء الهيدر الافتراضي لستريمليت */
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
    total_added = sum(float(h.get('debt', 0)) for h in history)
    total_removed = sum(float(h.get('price', 0)) for h in history)
    return total_added - total_removed

# ================== 3. واجهة الباركود (منظمة للموبايل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            
            # قسم البيانات الأساسية
            st.markdown(f"""
            <div class='client-header'>
                <div class='data-row'><span class='label'>👤 العميل:</span> <span>{c['name']}</span></div>
                <div class='data-row'><span class='label'>📱 الموبايل:</span> <span>{c.get('phone', '---')}</span></div>
                <div class='data-row'><span class='label'>🔧 الجهاز:</span> <span>{c.get('device_type', '---')}</span></div>
                <div style='text-align:center; margin-top:15px;'>
                    <span style='font-size:1.2rem;'>إجمالي المديونية الحالية</span><br>
                    <span style='font-size:2rem; color:#00d4ff; font-weight:bold;'>{bal:,.0f} ج.م</span>
                </div>
            </div>
            <h3 style='border-right: 4px solid #007bff; padding-right: 10px;'>📋 سجل العمليات المالي</h3>
            """, unsafe_allow_html=True)
            
            # عرض العمليات بشكل "كروت" للموبايل لضمان التنسيق
            if c.get('history'):
                for h in reversed(c['history']):
                    h_date = h.get('date', '---')
                    h_note = h.get('note', 'زيارة صيانة')
                    h_add = float(h.get('debt', 0))
                    h_rem = float(h.get('price', 0))
                    h_tech = h.get('tech', 'الإدارة')
                    
                    st.markdown(f"""
                    <div class='mobile-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <span class='card-date'>📅 {h_date}</span>
                            <span style='font-size:0.8rem; color:#00d4ff;'>👤 {h_tech}</span>
                        </div>
                        <div style='margin: 10px 0;'>📝 {h_note}</div>
                        <div style='display:flex; gap: 20px;'>
                            {f"<div class='card-amount plus'>➕ مضاف: {h_add:,.0f}</div>" if h_add > 0 else ""}
                            {f"<div class='card-amount minus'>➖ مخصوم: {h_rem:,.0f}</div>" if h_rem > 0 else ""}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد عمليات مسجلة حالياً.")
            
            st.stop() # منع ظهور أي شيء آخر (مثل صفحة الدخول) تحت التقرير
    except:
        st.error("عذراً، لم يتم العثور على بيانات هذا العميل.")
        st.stop()

# ================== 4. واجهة النظام (إدارة وفنيين) ==================
# تظهر فقط إذا لم يكن هناك ID في الرابط
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>لوحة التحكم 🔒</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if col1.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if col2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- بقية منطق الإدارة والفني كما هو مع تحسين أسماء الخانات ---
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اسم الفني", t_list) if t_list else st.error("لا يوجد فنيين")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech"; st.session_state.tech_name = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# --- واجهة الإدارة ---
if st.session_state.role == "admin":
    st.sidebar.title("💎 لوحة الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "📊 الحسابات", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم...")
        for i, c in enumerate(st.session_state.data):
            if search in c['name']:
                with st.expander(f"👤 {c['name']}"):
                    bal = calculate_balance(c.get('history', []))
                    st.write(f"المديونية الحالية: **{bal} ج.م**")
                    with st.form(f"ed_{c['id']}"):
                        adm_add = st.number_input("إضافة مديونية (يزيد الحساب)", min_value=0.0)
                        adm_rem = st.number_input("إزالة مديونية (ينقص الحساب)", min_value=0.0)
                        note = st.text_input("البيان", value="تسويه إدارية")
                        if st.form_submit_button("حفظ العملية"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": "الإدارة", "debt": adm_add, "price": adm_rem})
                            save_json("customers.json", st.session_state.data); st.success("تم الحفظ"); st.rerun()
                    
                    if st.button("🖼️ باركود العميل", key=f"qr_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")

    elif menu == "➕ إضافة عميل":
        with st.form("add"):
            name = st.text_input("اسم العميل")
            init_debt = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                new_c = {"id": new_id, "name": name, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "debt": init_debt, "price": 0}] if init_debt > 0 else []}
                st.session_state.data.append(new_c); save_json("customers.json", st.session_state.data); st.success("تم!")

    elif menu == "📊 الحسابات":
        st.metric("صافي مديونيات السوق", f"{sum(calculate_balance(c.get('history', [])) for c in st.session_state.data):,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# --- واجهة الفني ---
elif st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ {st.session_state.tech_name}")
    t_menu = st.sidebar.radio("القائمة", ["📋 قائمة العملاء", "➕ تسجيل صيانة", "🚪 خروج"])
    
    if t_menu == "➕ تسجيل صيانة":
        target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: x['name'])
        with st.form("tech_f"):
            v_add = st.number_input("إضافة مديونية (تكلفة صيانة)", min_value=0.0)
            v_rem = st.number_input("إزالة مديونية (تحصيل مبلغ)", min_value=0.0)
            note = st.text_area("وصف العمل")
            if st.form_submit_button("حفظ"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.tech_name, "debt": v_add, "price": v_rem})
                save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
    
    elif t_menu == "🚪 خروج": del st.session_state.role; st.rerun()
