import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر المتقدمة ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    .header-card { 
        background: rgba(255, 255, 255, 0.08); border-radius: 12px; 
        padding: 15px; border: 1px solid #007bff; margin-bottom: 20px; 
    }
    .operation-card { 
        background: #ffffff; color: #000000; border-radius: 10px; 
        padding: 15px; margin-bottom: 15px; border-right: 6px solid #007bff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .balance-val { font-size: 24px; color: #00d4ff; font-weight: bold; text-align: center; }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات (تحميل وحفظ) ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تهيئة البيانات في الـ Session State
if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    total_added = sum(float(h.get('debt', 0)) for h in history)
    total_removed = sum(float(h.get('price', 0)) for h in history)
    return total_added - total_removed

# ================== 3. معالجة رابط الباركود للعميل ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h2 style='text-align:center;'>Power Life 💧</h2>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            
            # بيانات العميل العلوية
            st.markdown(f"""
            <div class='header-card'>
                <div style='font-size:16px;'>👤 <b>الاسم:</b> {c['name']}</div>
                <div style='font-size:14px; margin-top:5px;'>📍 <b>المحافظة:</b> {c.get('gov', 'غير محدد')} | 🏛️ <b>الفرع:</b> {c.get('branch', 'غير محدد')}</div>
                <hr style='opacity:0.2;'>
                <div style='text-align:center; font-size:14px;'>إجمالي المديونية الحالية</div>
                <div class='balance-val'>{bal:,.0f} ج.م</div>
            </div>
            <h3 style='border-right: 4px solid #007bff; padding-right:10px;'>📋 سجل العمليات</h3>
            """, unsafe_allow_html=True)
            
            # عرض العمليات (حل مشكلة التاريخ هنا)
            if c.get('history'):
                for h in reversed(c['history']):
                    # فحص التاريخ لمنع الخطأ
                    op_date = h.get('date', 'غير مسجل')
                    h_add = float(h.get('debt', 0))
                    h_rem = float(h.get('price', 0))
                    
                    st.markdown(f"""
                    <div class="operation-card">
                        <div style="display:flex; justify-content:space-between; font-size:12px; color:#666;">
                            <span>📅 {op_date}</span>
                            <span>👤 {h.get('tech', 'الإدارة')}</span>
                        </div>
                        <div style="margin: 8px 0; font-size: 16px; font-weight: bold;">📝 {h.get('note', 'تسوية مادية')}</div>
                        <div style="display: flex; gap: 15px;">
                            {f'<span style="color:red; font-weight:bold;">➕ مضاف: {h_add:,.0f}</span>' if h_add > 0 else ''}
                            {f'<span style="color:green; font-weight:bold;">➖ مخصوم: {h_rem:,.0f}</span>' if h_rem > 0 else ''}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا توجد عمليات مسجلة.")
            st.stop()
    except Exception as e:
        st.error(f"خطأ في البيانات: {e}")
        st.stop()

# ================== 4. لوحة التحكم (الإدارة والفنيين) ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>لوحة التحكم 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- واجهة تسجيل دخول الإدارة ---
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول النظام"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
        else: st.error("بيانات غير صحيحة")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# --- واجهة تسجيل دخول الفني ---
if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_list) if t_list else st.error("لا يوجد فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول الفني"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech"; st.session_state.tech_name = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. شاشة الإدارة الرئيسية ==================
if st.session_state.role == "admin":
    st.sidebar.title("💎 لوحة الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "📊 حسابات الشركة", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم...")
        for i, c in enumerate(st.session_state.data):
            if search in c['name']:
                with st.expander(f"👤 {c['name']}"):
                    st.write(f"المديونية الحالية: {calculate_balance(c.get('history', []))} ج.م")
                    with st.form(f"admin_edit_{c['id']}"):
                        c['gov'] = st.text_input("المحافظة", value=c.get('gov', ''))
                        c['branch'] = st.text_input("الفرع", value=c.get('branch', ''))
                        a_add = st.number_input("إضافة مديونية", min_value=0.0)
                        a_rem = st.number_input("إزالة مديونية", min_value=0.0)
                        if st.form_submit_button("حفظ وتحديث"):
                            if a_add > 0 or a_rem > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تسويه إدارية", "tech": "الإدارة", "debt": a_add, "price": a_rem})
                            save_json("customers.json", st.session_state.data); st.success("تم الحفظ"); st.rerun()
                    if st.button("🖼️ إظهار الباركود", key=f"qr_btn_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")

    elif menu == "➕ إضافة عميل":
        with st.form("new_cust"):
            name = st.text_input("اسم العميل")
            gov = st.text_input("المحافظة")
            branch = st.text_input("الفرع")
            debt = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("تسجيل العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": new_id, "name": name, "gov": gov, "branch": branch,
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "debt": debt, "price": 0}] if debt > 0 else []
                })
                save_json("customers.json", st.session_state.data); st.success("تم تسجيل العميل!")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. شاشة الفني الرئيسية ==================
elif st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ {st.session_state.tech_name}")
    t_menu = st.sidebar.radio("القائمة", ["📋 قائمة العملاء", "➕ تسجيل صيانة", "🚪 خروج"])
    
    if t_menu == "➕ تسجيل صيانة":
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
        with st.form("tech_entry"):
            v1 = st.number_input("إضافة مديونية (تكلفة صيانة)", min_value=0.0)
            v2 = st.number_input("إزالة مديونية (مبلغ مستلم)", min_value=0.0)
            note = st.text_area("ملاحظات الزيارة")
            if st.form_submit_button("حفظ العملية"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.tech_name, "debt": v1, "price": v2})
                save_json("customers.json", st.session_state.data); st.success("تم تسجيل البيانات بنجاح")
    
    elif t_menu == "🚪 خروج": del st.session_state.role; st.rerun()
