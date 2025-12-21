import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import urllib.parse

# ================== 1. إعدادات المظهر الفاخر ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-card { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; border: 1px solid #007bff; margin-bottom: 15px; }
    .history-card { background: rgba(0, 123, 255, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 5px solid #00d4ff; }
    .settlement-card { background: rgba(0, 255, 127, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 5px solid #00ff7f; }
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

def calculate_balance(history):
    # المديونية = (إجمالي الديون المضافة والافتتاحية) - (إجمالي المبالغ المحصلة والمدفوعة)
    added_debts = sum(float(h.get('debt', 0)) for h in history)
    paid_amounts = sum(float(h.get('price', 0)) for h in history)
    return added_debts - paid_amounts

# ================== 3. رابط العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        if customer:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(customer.get('history', []))
            st.metric("💰 المديونية الحالية", f"{bal:,.0f} ج.م")
            st.markdown(f"<div class='client-card'>👤 <b>{customer['name']}</b><br>📍 {customer.get('gov')} - {customer.get('branch')}<br>🔧 {customer.get('device_type')}</div>", unsafe_allow_html=True)
            for h in reversed(customer.get('history', [])):
                st.markdown(f"<div class='history-card'><b>📅 {h['date']}</b><br>📝 {h['note']}<br>✅ دفع: {h['price']} | 👤 المستلم: {h['tech']}</div>", unsafe_allow_html=True)
            st.stop()
    except: pass

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life System 💧</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    if not t_list: st.error("لا يوجد فنيين مسجلين."); st.stop()
    t_user = st.selectbox("اختر اسمك", t_list)
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول الفني"):
        tech_data = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech_data['pass']: st.session_state.role = "tech"; st.session_state.tech_name = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الفني (رؤية الجميع + حسابات دقيقة) ==================
if st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ {st.session_state.tech_name}")
    t_menu = st.sidebar.radio("القائمة", ["📋 قائمة العملاء", "➕ تسجيل صيانة", "🚪 خروج"])

    if t_menu == "📋 قائمة العملاء":
        search = st.text_input("ابحث عن عميل...")
        for c in st.session_state.data:
            if search in c['name'] or search in c.get('phone', ''):
                with st.expander(f"👤 {c['name']} | 📱 {c['phone']}"):
                    bal = calculate_balance(c.get('history', []))
                    st.write(f"🏠 العنوان: {c['loc']} | 🏛️ الفرع: {c['branch']}")
                    st.error(f"💰 المديونية المطلوبة: {bal} ج.م")

    elif t_menu == "➕ تسجيل صيانة":
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: f"{x['name']} ({x['phone']})")
        with st.form("t_form"):
            note = st.text_area("وصف الزيارة")
            shama3 = st.number_input("عدد الشمع المستهلك", min_value=0)
            paid = st.number_input("المبلغ المستلم كاش (ينقص المديونية)", min_value=0.0)
            added = st.number_input("تكلفة الصيانة أو الجهاز (يزيد المديونية)", min_value=0.0)
            if st.form_submit_button("حفظ الزيارة"):
                prev_bal = calculate_balance(target.get('history', []))
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": f"{note} (شمع: {shama3})", "tech": st.session_state.tech_name,
                            "price": paid, "debt": added, "candles": shama3,
                            "prev_bal": prev_bal, "new_bal": prev_bal + added - paid
                        })
                save_json("customers.json", st.session_state.data); st.success("تم الحفظ وتحديث المديونية")

# ================== 6. واجهة الإدارة الشاملة (كل الوظائف السابقة) ==================
elif st.session_state.role == "admin":
    st.sidebar.title("💎 لوحة التحكم")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل جديد", "📋 تقارير الفنيين", "👷 حسابات الفنيين", "📊 حسابات عامة", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم أو الكود...")
        for i, c in enumerate(st.session_state.data):
            if search in c['name'] or search in str(c['id']):
                with st.expander(f"👤 {c['name']} (PL-{c['id']:04d})"):
                    bal = calculate_balance(c.get('history', []))
                    st.warning(f"المديونية الحالية: {bal} ج.م")
                    with st.form(f"edit_{c['id']}"):
                        col1, col2 = st.columns(2)
                        n_name = col1.text_input("تعديل الاسم", value=c['name'])
                        n_phone = col2.text_input("تعديل الرقم", value=c['phone'])
                        n_gov = col1.selectbox("المحافظة", EGYPT_GOVS, index=EGYPT_GOVS.index(c['gov']) if c['gov'] in EGYPT_GOVS else 0)
                        n_branch = col2.selectbox("الفرع", COMPANY_BRANCHES, index=COMPANY_BRANCHES.index(c['branch']) if c['branch'] in COMPANY_BRANCHES else 0)
                        n_loc = st.text_input("العنوان / المركز", value=c.get('loc'))
                        n_dev = st.selectbox("نوع الجهاز", ["جهاز جديد من الشركة", "جهاز خارجي", "جهاز قديم"], index=0)
                        
                        st.write("--- 💰 تسوية مديونية ---")
                        adm_paid = st.number_input("تحصيل مبلغ (يطرح من الدين)", min_value=0.0)
                        adm_debt = st.number_input("إضافة دين جديد (يجمع على الدين)", min_value=0.0)
                        
                        if st.form_submit_button("حفظ التعديلات والماليات"):
                            c.update({"name": n_name, "phone": n_phone, "gov": n_gov, "branch": n_branch, "loc": n_loc, "device_type": n_dev})
                            if adm_paid > 0 or adm_debt > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تسوية إدارية", "tech": "الإدارة", "price": adm_paid, "debt": adm_debt})
                            save_json("customers.json", st.session_state.data); st.success("تم التحديث"); st.rerun()
                    
                    c1, c2 = st.columns(2)
                    if c1.button("🖼️ توليد الباركود", key=f"qr_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    if c2.button("🗑️ حذف العميل نهائياً", key=f"del_{c['id']}"):
                        st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل جديد":
        st.subheader("📝 نموذج إضافة عميل كامل")
        with st.form("new_client"):
            col1, col2 = st.columns(2)
            name = col1.text_input("اسم العميل بالكامل")
            phone = col2.text_input("رقم الموبايل")
            gov = col1.selectbox("المحافظة", EGYPT_GOVS)
            branch = col2.selectbox("الفرع التابع له", COMPANY_BRANCHES)
            loc = st.text_input("العنوان / المركز / المدينة")
            dev_type = st.selectbox("حالة الجهاز", ["جهاز جديد من الشركة", "جهاز خارجي (صيانة فقط)", "جهاز قديم"])
            init_debt = st.number_input("مديونية افتتاحية على العميل (إن وجد)", min_value=0.0)
            
            if st.form_submit_button("إضافة العميل"):
                if name and phone:
                    new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                    new_c = {"id": new_id, "name": name, "phone": phone, "gov": gov, "branch": branch, "loc": loc, "device_type": dev_type, "history": []}
                    if init_debt > 0:
                        new_c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "price": 0, "debt": init_debt})
                    st.session_state.data.append(new_c); save_json("customers.json", st.session_state.data); st.success(f"تم تسجيل العميل بنجاح بكود: PL-{new_id:04d}")
                else: st.error("يرجى ملء الاسم والتليفون على الأقل.")

    elif menu == "📋 تقارير الفنيين":
        st.subheader("📊 تقرير حركة الفنيين المالي")
        reports = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') != "الإدارة":
                    reports.append({
                        "التاريخ": h['date'], "الفني": h['tech'], "العميل": c['name'], "الفرع": c.get('branch'),
                        "الوصف": h['note'], "المحصل الكاش": h['price'], "دين مضاف": h['debt'],
                        "الحساب قبل": h.get('prev_bal', 0), "الحساب بعد": h.get('new_bal', 0)
                    })
        if reports: st.dataframe(pd.DataFrame(reports), use_container_width=True)
        else: st.info("لا توجد حركات مسجلة للفنيين.")

    elif menu == "👷 حسابات الفنيين":
        st.subheader("إدارة حسابات دخول الفنيين")
        with st.form("add_tech"):
            t_name = st.text_input("اسم الفني الجديد")
            t_pass = st.text_input("كلمة السر الخاصة به")
            if st.form_submit_button("إنشاء حساب للفني"):
                st.session_state.techs.append({"name": t_name, "pass": t_pass})
                save_json("techs.json", st.session_state.techs); st.success("تم الإنشاء")
        
        for idx, t in enumerate(st.session_state.techs):
            col_a, col_b = st.columns([4,1])
            col_a.info(f"👷 {t['name']} | كلمة السر: {t['pass']}")
            if col_b.button("حذف الحساب", key=f"t_del_{idx}"):
                st.session_state.techs.pop(idx); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "📊 حسابات عامة":
        total_p = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        total_d = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        st.metric("💰 إجمالي الكاش المحصل", f"{total_p:,.0f} ج.م")
        st.metric("📉 صافي ديون السوق", f"{total_d - total_p:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()
