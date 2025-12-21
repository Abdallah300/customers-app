import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import urllib.parse

# ================== 1. إعدادات المظهر ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-report { background: rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; border: 1px solid #007bff; margin-bottom: 20px; }
    .data-row { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 12px 0; display: flex; justify-content: space-between; align-items: center; }
    .history-card { background: rgba(0, 123, 255, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 5px solid #00d4ff; text-align: right; }
    .settlement-card { background: rgba(0, 255, 127, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 5px solid #00ff7f; text-align: right; }
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

# ================== 3. صفحة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        if customer:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            history = customer.get('history', [])
            # المديونية الصافية = مجموع (الدين المضاف - المدفوع)
            total_debt = sum(float(h.get('debt', 0)) for h in history)
            total_paid = sum(float(h.get('price', 0)) for h in history)
            current_balance = total_debt - total_paid

            col1, col2 = st.columns(2)
            col1.metric("💰 إجمالي المدفوع", f"{total_paid:,.0f} ج.م")
            col2.metric("⚠️ المديونية الحالية", f"{current_balance:,.0f} ج.م")
            st.markdown(f"""<div class='client-report'>
                <div class='data-row'>👤 العميل: <b>{customer.get('name')}</b></div>
                <div class='data-row'>📍 المحافظة: <b>{customer.get('gov')}</b></div>
                <div class='data-row'>🏛️ الفرع: <b>{customer.get('branch')}</b></div>
                <div class='data-row'>🔧 الجهاز: <b>{customer.get('device_type')}</b></div>
                <div class='data-row'>🏠 العنوان: <b>{customer.get('loc')}</b></div>
            </div>""", unsafe_allow_html=True)
            for h in reversed(history):
                style = "settlement-card" if h.get('tech') == "الإدارة" else "history-card"
                st.markdown(f"<div class='{style}'><b>📅 {h.get('date')}</b><br>📝 {h.get('note')}<br>👤 المستلم: {h.get('tech')} | ✅ دفع: {h.get('price')} ج.م</div>", unsafe_allow_html=True)
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
    u = st.text_input("المستخدم")
    p = st.text_input("السر", type="password")
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

# ================== 5. واجهة الفني ==================
if st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ الفني: {st.session_state.tech_name}")
    t_menu = st.sidebar.radio("القائمة", ["📋 قائمة العملاء", "➕ تسجيل صيانة", "💰 حسابي اليومي", "🚪 خروج"])

    if t_menu == "📋 قائمة العملاء":
        search_t = st.text_input("ابحث عن عميل...")
        for c in st.session_state.data:
            if search_t in c['name'] or search_t in c.get('phone', ''):
                with st.expander(f"👤 {c['name']} | 📱 {c['phone']}"):
                    st.write(f"🏠 {c['loc']} | 🏛️ {c.get('branch')}")
                    # حساب المديونية الفعلية
                    bal = sum(float(h.get('debt', 0)) for h in c.get('history', [])) - sum(float(h.get('price', 0)) for h in c.get('history', []))
                    st.error(f"💰 مديونية العميل الحالية: {bal} ج.م")

    elif t_menu == "➕ تسجيل صيانة":
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: f"{x['name']} ({x['phone']})")
        with st.form("t_form"):
            note = st.text_area("وصف الزيارة (مثال: صيانة دورية + تحصيل قسط)")
            shama3 = st.number_input("شمع مستهلك", min_value=0)
            paid = st.number_input("المبلغ المحصل (اللي الفني استلمه فعلياً)", min_value=0.0)
            added_debt = st.number_input("دين جديد مضاف (قيمة الصيانة أو الجهاز الجديد)", min_value=0.0)
            
            if st.form_submit_button("حفظ الزيارة"):
                # حساب المديونية قبل العملية
                prev_bal = sum(float(h.get('debt', 0)) for h in target.get('history', [])) - sum(float(h.get('price', 0)) for h in target.get('history', []))
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": f"{note} (شمع: {shama3})",
                            "tech": st.session_state.tech_name,
                            "price": paid, # مبلغ خارج من جيب العميل
                            "debt": added_debt, # مبلغ مضاف لمديونية العميل
                            "candles": shama3,
                            "prev_bal": prev_bal,
                            "new_bal": prev_bal + added_debt - paid
                        })
                save_json("customers.json", st.session_state.data); st.success("تم الحفظ وتحديث الحسابات")

    elif t_menu == "💰 حسابي اليومي":
        today = datetime.now().strftime("%Y-%m-%d")
        t_paid = sum(sum(float(h.get('price', 0)) for h in c.get('history', []) if h.get('date','').startswith(today) and h.get('tech')==st.session_state.tech_name) for c in st.session_state.data)
        st.metric("تحصيلك اليوم", f"{t_paid} ج.م")
    
    elif t_menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الإدارة (كاملة المواصفات) ==================
elif st.session_state.role == "admin":
    st.sidebar.title("💎 لوحة الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "📋 تقارير الفنيين", "👷 حسابات الفنيين", "📊 حسابات عامة", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم أو الكود...")
        for i, c in enumerate(st.session_state.data):
            if search in c.get('name', '') or search in str(c.get('id')):
                with st.expander(f"👤 {c['name']} (PL-{c['id']:04d})"):
                    bal = sum(float(h.get('debt', 0)) for h in c.get('history', [])) - sum(float(h.get('price', 0)) for h in c.get('history', []))
                    st.warning(f"المديونية الصافية: {bal} ج.م")
                    
                    with st.form(f"edit_{c['id']}"):
                        col1, col2 = st.columns(2)
                        n_name = col1.text_input("الاسم", value=c['name'])
                        n_phone = col2.text_input("الموبايل", value=c.get('phone'))
                        n_gov = col1.selectbox("المحافظة", EGYPT_GOVS, index=EGYPT_GOVS.index(c['gov']) if c['gov'] in EGYPT_GOVS else 0)
                        n_branch = col2.selectbox("الفرع", COMPANY_BRANCHES, index=COMPANY_BRANCHES.index(c['branch']) if c['branch'] in COMPANY_BRANCHES else 0)
                        n_loc = st.text_input("العنوان بالتفصيل", value=c.get('loc'))
                        n_dev = st.selectbox("نوع الجهاز", ["جهاز جديد", "جهاز قديم", "جهاز خارجي"], index=0)
                        
                        st.write("--- 💸 تسوية مالية سريعة ---")
                        adm_paid = st.number_input("تحصيل مبلغ (ينقص الدين)", min_value=0.0)
                        adm_debt = st.number_input("إضافة مبلغ (يزود الدين)", min_value=0.0)
                        
                        if st.form_submit_button("حفظ كافة التعديلات"):
                            c.update({"name": n_name, "phone": n_phone, "gov": n_gov, "branch": n_branch, "loc": n_loc, "device_type": n_dev})
                            if adm_paid > 0 or adm_debt > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل حساب إداري", "tech": "الإدارة", "price": adm_paid, "debt": adm_debt})
                            save_json("customers.json", st.session_state.data); st.success("تم التحديث"); st.rerun()
                    
                    if st.button("🖼️ الباركود", key=f"q_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    if st.button("🗑️ حذف العميل", key=f"del_{c['id']}"):
                        st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل":
        st.subheader("📝 تسجيل عميل جديد في النظام")
        with st.form("new_client_form"):
            col1, col2 = st.columns(2)
            c_name = col1.text_input("اسم العميل بالكامل")
            c_phone = col2.text_input("رقم الموبايل")
            c_gov = col1.selectbox("المحافظة", EGYPT_GOVS)
            c_branch = col2.selectbox("الفرع التابع له", COMPANY_BRANCHES)
            c_loc = st.text_input("العنوان التفصيلي")
            c_dev = st.selectbox("حالة الجهاز", ["جهاز جديد من الشركة", "جهاز خارجي (صيانة فقط)", "جهاز قديم"])
            c_initial_debt = st.number_input("مديونية افتتاحية (لو عليه فلوس قديمة)", min_value=0.0)
            
            if st.form_submit_button("إضافة العميل وتوليد الكود"):
                if c_name and c_phone:
                    new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                    new_cust = {
                        "id": new_id, "name": c_name, "phone": c_phone, "gov": c_gov, 
                        "branch": c_branch, "loc": c_loc, "device_type": c_dev, 
                        "history": []
                    }
                    if c_initial_debt > 0:
                        new_cust['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": "مديونية افتتاحية", "tech": "الإدارة", "price": 0, "debt": c_initial_debt})
                    
                    st.session_state.data.append(new_cust)
                    save_json("customers.json", st.session_state.data)
                    st.success(f"تم تسجيل العميل بنجاح بكود: PL-{new_id:04d}")
                else: st.error("يرجى إدخال الاسم والرقم")

    elif menu == "📋 تقارير الفنيين":
        st.subheader("📊 تقرير حركة الفنيين المالي")
        all_h = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') != "الإدارة":
                    all_h.append({
                        "التاريخ": h.get('date'), "الفني": h.get('tech'), "العميل": c['name'],
                        "الفرع": c.get('branch'), "العمل": h.get('note'), "المحصل": h.get('price', 0),
                        "دين مضاف": h.get('debt', 0), "الحساب قبل": h.get('prev_bal', 0), "الحساب بعد": h.get('new_bal', 0)
                    })
        if all_h: st.dataframe(pd.DataFrame(all_h), use_container_width=True)
        else: st.info("لا توجد حركات فنية.")

    elif menu == "👷 حسابات الفنيين":
        with st.form("add_tech_form"):
            t_n = st.text_input("اسم الفني")
            t_p = st.text_input("السر")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": t_n, "pass": t_p})
                save_json("techs.json", st.session_state.techs); st.rerun()
        for idx, t in enumerate(st.session_state.techs):
            col1, col2 = st.columns([3,1])
            col1.write(f"👷 {t['name']} (Pass: {t['pass']})")
            if col2.button("حذف الحساب", key=f"t_del_{idx}"):
                st.session_state.techs.pop(idx); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "📊 حسابات عامة":
        all_p = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        all_d = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي التحصيلات (كاش)", f"{all_p:,.0f} ج.م")
        st.metric("صافي ديون السوق", f"{all_d - all_p:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()
