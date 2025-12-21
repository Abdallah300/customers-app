import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-report { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; border: 1px solid #007bff; margin-bottom: 20px; }
    .data-row { border-bottom: 1px solid rgba(255,255,255,0.05); padding: 12px 0; display: flex; justify-content: space-between; }
    th { background-color: #007bff !important; color: white !important; }
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

# ================== 3. صفحة الباركود (منع ظهور أي شيء آخر) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            
            st.markdown(f"""
            <div class='client-report'>
                <h3 style='text-align:center; color:#00d4ff;'>تقرير العميل</h3>
                <div class='data-row'>👤 الاسم: <b>{c['name']}</b></div>
                <div class='data-row'>📱 الموبايل: <b>{c.get('phone', 'غير مسجل')}</b></div>
                <div class='data-row'>🔧 الجهاز: <b>{c.get('device_type', '-')}</b></div>
                <hr>
                <div class='data-row' style='color:#00d4ff; font-size:24px;'>💰 المديونية الحالية: <b>{bal:,.0f} ج.م</b></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📋 سجل الزيارات والتحصيلات")
            if c.get('history'):
                hist_data = []
                for h in reversed(c['history']):
                    hist_data.append({
                        "التاريخ والوقت": h.get('date', datetime.now().strftime("%Y-%m-%d")),
                        "البيان/الملاحظات": h.get('note', '-'),
                        "إضافة مديونية (+)": f"{h.get('debt', 0)} ج.م",
                        "إزالة مديونية (-)": f"{h.get('price', 0)} ج.م",
                        "المسؤول/الفني": h.get('tech', 'الإدارة')
                    })
                st.table(pd.DataFrame(hist_data))
            else:
                st.info("لا توجد عمليات سابقة.")
            
            st.stop() # هذا السطر يمنع ظهور صفحة تسجيل الدخول نهائياً للعميل
    except:
        st.error("خطأ في عرض بيانات الباركود.")
        st.stop()

# ================== 4. نظام تسجيل الدخول (للإدارة والفنيين فقط) ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>لوحة التحكم - Power Life 💧</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (منطق تسجيل الدخول المعتاد)
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسم الفني", t_list) if t_list else st.error("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech"; st.session_state.tech_name = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الفني (إضافة وإزالة مديونية) ==================
if st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ {st.session_state.tech_name}")
    t_menu = st.sidebar.radio("القائمة", ["📋 قائمة العملاء", "➕ تسجيل زيارة", "🚪 خروج"])
    
    if t_menu == "➕ تسجيل زيارة":
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
        with st.form("tech_f"):
            v_add = st.number_input("إضافة مديونية (تكلفة صيانة/جهاز)", min_value=0.0)
            v_rem = st.number_input("إزالة مديونية (مبلغ محصل)", min_value=0.0)
            note = st.text_area("وصف الزيارة")
            if st.form_submit_button("حفظ"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                            "note": note, "tech": st.session_state.tech_name, 
                            "debt": v_add, "price": v_rem
                        })
                save_json("customers.json", st.session_state.data); st.success("تم الحفظ")

# ================== 6. واجهة الإدارة ==================
elif st.session_state.role == "admin":
    st.sidebar.title("💎 الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "📋 التقارير", "📊 الحسابات", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم...")
        for i, c in enumerate(st.session_state.data):
            if search in c['name']:
                with st.expander(f"👤 {c['name']}"):
                    bal = calculate_balance(c.get('history', []))
                    st.warning(f"المديونية: {bal} ج.م")
                    with st.form(f"ed_{c['id']}"):
                        n_name = st.text_input("تعديل الاسم", value=c['name'])
                        st.write("--- تسوية مالية ---")
                        adm_add = st.number_input("إضافة مديونية", min_value=0.0)
                        adm_rem = st.number_input("إزالة مديونية", min_value=0.0)
                        if st.form_submit_button("حفظ"):
                            c.update({"name": n_name})
                            if adm_add > 0 or adm_rem > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تسوية إدارية", "tech": "الإدارة", "debt": adm_add, "price": adm_rem})
                            save_json("customers.json", st.session_state.data); st.success("تم التحديث"); st.rerun()
                    
                    if st.button("🖼️ باركود العميل", key=f"q_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")

    elif menu == "➕ إضافة عميل":
        with st.form("add"):
            name = st.text_input("اسم العميل")
            init_debt = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                new_c = {"id": new_id, "name": name, "history": []}
                if init_debt > 0:
                    new_c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "debt": init_debt, "price": 0})
                st.session_state.data.append(new_c); save_json("customers.json", st.session_state.data); st.success("تمت الإضافة")

    elif menu == "📊 الحسابات":
        st.metric("صافي مديونيات السوق", f"{sum(calculate_balance(c.get('history', [])) for c in st.session_state.data):,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()
