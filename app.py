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
    .client-card { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; border: 1px solid #007bff; margin-bottom: 15px; }
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

EGYPT_GOVS = ["القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "الشرقية", "المنوفية", "القليوبية", "البحيرة", "الغربية", "بور سعيد", "دمياط", "الإسماعيلية", "السويس", "كفر الشيخ", "الفيوم", "بني سويف", "المنيا", "أسيوط", "سوهاج", "قنا", "الأقصر", "أسوان"]
COMPANY_BRANCHES = ["فرع القاهرة الرئيسي", "فرع الجيزة", "فرع الإسكندرية", "فرع المنصورة", "فرع طنطا"]

# دالة الحساب الدقيق: (إجمالي الديون المضافة والافتتاحية) - (إجمالي المبالغ المسددة)
def calculate_balance(history):
    total_added = sum(float(h.get('debt', 0)) for h in history)
    total_paid = sum(float(h.get('price', 0)) for h in history)
    return total_added - total_paid

# ================== 3. صفحة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        if customer:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(customer.get('history', []))
            st.metric("💰 المديونية المتبقية", f"{bal:,.0f} ج.م")
            st.stop()
    except: pass

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life System 💧</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (منطق تسجيل الدخول كما هو)
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    if not t_list: st.error("لا يوجد فنيين."); st.stop()
    t_user = st.selectbox("اسم الفني", t_list)
    p = st.text_input("السر", type="password")
    if st.button("دخول الفني"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech"; st.session_state.tech_name = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الفني (تصحيح الحسابات) ==================
if st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ {st.session_state.tech_name}")
    t_menu = st.sidebar.radio("القائمة", ["📋 قائمة العملاء", "➕ تسجيل صيانة", "🚪 خروج"])

    if t_menu == "📋 قائمة العملاء":
        search = st.text_input("بحث بالاسم...")
        for c in st.session_state.data:
            if search in c['name']:
                with st.expander(f"👤 {c['name']}"):
                    bal = calculate_balance(c.get('history', []))
                    st.error(f"💰 المديونية الحالية: {bal} ج.م")

    elif t_menu == "➕ تسجيل صيانة":
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
        with st.form("tech_f"):
            paid = st.number_input("المبلغ اللي العميل دفعه (يقلل المديونية)", min_value=0.0, value=0.0)
            added = st.number_input("تكلفة الزيارة أو الجهاز (يزود المديونية)", min_value=0.0, value=0.0)
            note = st.text_area("وصف الزيارة")
            if st.form_submit_button("حفظ الزيارة"):
                prev_bal = calculate_balance(target.get('history', []))
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": note, "tech": st.session_state.tech_name,
                            "price": paid, "debt": added,
                            "prev_bal": prev_bal, "new_bal": prev_bal + added - paid
                        })
                save_json("customers.json", st.session_state.data); st.success("تم التحديث")

# ================== 6. واجهة الإدارة (إصلاح التسويه + إضافة العميل) ==================
elif st.session_state.role == "admin":
    st.sidebar.title("💎 الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "📋 تقارير الفنيين", "👷 حسابات الفنيين", "📊 حسابات عامة", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث...")
        for i, c in enumerate(st.session_state.data):
            if search in c['name']:
                with st.expander(f"👤 {c['name']} (PL-{c['id']:04d})"):
                    bal = calculate_balance(c.get('history', []))
                    st.warning(f"المديونية الحالية: {bal} ج.م")
                    with st.form(f"ed_{c['id']}"):
                        col1, col2 = st.columns(2)
                        n_name = col1.text_input("تعديل الاسم", value=c['name'])
                        n_phone = col2.text_input("تعديل الرقم", value=c.get('phone'))
                        n_gov = col1.selectbox("المحافظة", EGYPT_GOVS, index=EGYPT_GOVS.index(c['gov']) if c['gov'] in EGYPT_GOVS else 0)
                        n_loc = st.text_input("العنوان", value=c.get('loc'))
                        
                        st.write("--- 💸 التسويه المالية (طرح أو إضافة) ---")
                        adm_paid = st.number_input("تحصيل مبلغ (يطرح من الدين)", min_value=0.0, value=0.0)
                        adm_debt = st.number_input("إضافة دين جديد (يزود الدين)", min_value=0.0, value=0.0)
                        
                        if st.form_submit_button("تحديث وحفظ التسويه"):
                            # تحديث البيانات الأساسية
                            c.update({"name": n_name, "phone": n_phone, "gov": n_gov, "loc": n_loc})
                            # إضافة حركة التسويه في الهيستوري
                            if adm_paid > 0 or adm_debt > 0:
                                c['history'].append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "note": "تسويه إدارية", "tech": "الإدارة",
                                    "price": adm_paid, "debt": adm_debt
                                })
                            save_json("customers.json", st.session_state.data); st.success("تم الحفظ"); st.rerun()
                    
                    if st.button("🗑️ حذف العميل", key=f"del_{c['id']}"):
                        st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل":
        st.subheader("إضافة عميل جديد للنظام")
        with st.form("add_client"):
            col1, col2 = st.columns(2)
            name = col1.text_input("اسم العميل")
            phone = col2.text_input("الموبايل")
            gov = col1.selectbox("المحافظة", EGYPT_GOVS)
            branch = col2.selectbox("الفرع", COMPANY_BRANCHES)
            loc = st.text_input("العنوان بالتفصيل / المركز")
            dev = st.selectbox("نوع الجهاز", ["جديد", "خارجي", "قديم"])
            init_debt = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("إضافة العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                new_c = {"id": new_id, "name": name, "phone": phone, "gov": gov, "branch": branch, "loc": loc, "device_type": dev, "history": []}
                if init_debt > 0:
                    # الرصيد الافتتاحي يوضع في خانة debt لزيادة الحساب
                    new_c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "price": 0, "debt": init_debt})
                st.session_state.data.append(new_c); save_json("customers.json", st.session_state.data); st.success("تمت الإضافة")

    elif menu == "📋 تقارير الفنيين":
        all_h = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') != "الإدارة":
                    all_h.append({"الفني": h['tech'], "العميل": c['name'], "دفع": h['price'], "عليه": h['debt'], "التاريخ": h['date']})
        if all_h: st.table(pd.DataFrame(all_h))

    elif menu == "📊 حسابات عامة":
        total_market = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("صافي مديونيات السوق (لك عند الناس)", f"{total_market:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()        
