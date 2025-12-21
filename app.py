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
            total_paid = sum(float(h.get('price', 0)) for h in history)
            total_debt = sum(float(h.get('debt', 0)) for h in history)
            col1, col2 = st.columns(2)
            col1.metric("💰 إجمالي المدفوع", f"{total_paid:,.0f} ج.م")
            col2.metric("⚠️ المديونية الحالية", f"{total_debt:,.0f} ج.م")
            st.markdown(f"<div class='client-report'><div class='data-row'>👤 العميل: <b>{customer.get('name')}</b></div><div class='data-row'>📍 المحافظة: <b>{customer.get('gov')}</b></div><div class='data-row'>🏛️ الفرع: <b>{customer.get('branch')}</b></div><div class='data-row'>🔧 نوع الجهاز: <b>{customer.get('device_type')}</b></div></div>", unsafe_allow_html=True)
            st.subheader("🗓️ سجل الصيانات والتحصيلات")
            for h in reversed(history):
                style = "settlement-card" if h.get('tech') == "الإدارة" else "history-card"
                st.markdown(f"<div class='{style}'><b>📅 {h.get('date')}</b><br>📝 {h.get('note')}<br>👤 المستلم/الفني: {h.get('tech')} | ✅ دفع: {h.get('price')}</div>", unsafe_allow_html=True)
            st.stop()
    except: pass

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>نظام Power Life 💧</h2>", unsafe_allow_html=True)
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
    if not t_list: st.error("لا يوجد فنيين مسجلين. يرجى مراجعة الإدارة."); st.stop()
    t_user = st.selectbox("اسم الفني", t_list)
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
        search_t = st.text_input("بحث بالاسم...")
        for c in st.session_state.data:
            if search_t in c['name']:
                with st.expander(f"👤 {c['name']} | 📱 {c['phone']}"):
                    st.write(f"📍 {c['gov']} - {c['branch']} | 🏠 {c['loc']}")
                    debt = sum(float(h.get('debt', 0)) for h in c.get('history', []))
                    st.error(f"المديونية الحالية: {debt} ج.م")

    elif t_menu == "➕ تسجيل صيانة":
        target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: f"{x['name']} ({x['phone']})")
        with st.form("t_form"):
            note = st.text_area("وصف العمل")
            shama3 = st.number_input("شمع مستهلك", min_value=0)
            paid = st.number_input("المدفوع الآن", min_value=0.0)
            debt_new = st.number_input("الدين المتبقي من الزيارة", min_value=0.0)
            if st.form_submit_button("حفظ"):
                old_debt = sum(float(h.get('debt', 0)) for h in target.get('history', []))
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                            "note": f"{note} (شمع: {shama3})", 
                            "tech": st.session_state.tech_name, 
                            "price": paid, 
                            "debt": debt_new, 
                            "candles": shama3,
                            "prev_debt": old_debt,
                            "total_after": old_debt + debt_new
                        })
                save_json("customers.json", st.session_state.data); st.success("تم الحفظ")

    elif t_menu == "💰 حسابي اليومي":
        today = datetime.now().strftime("%Y-%m-%d")
        t_paid = sum(sum(float(h.get('price', 0)) for h in c.get('history', []) if h.get('date','').startswith(today) and h.get('tech')==st.session_state.tech_name) for c in st.session_state.data)
        st.metric("تحصيلك اليوم", f"{t_paid} ج.م")

    elif t_menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الإدارة (كاملة) ==================
elif st.session_state.role == "admin":
    st.sidebar.title("💎 لوحة الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة (إداري)", "📋 تقارير الفنيين", "👷 إدارة حسابات الفنيين", "📊 حسابات عامة", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم...")
        for i, c in enumerate(st.session_state.data):
            if search in c.get('name', ''):
                with st.expander(f"👤 {c['name']} (PL-{c['id']:04d})"):
                    current_debt = sum(float(h.get('debt', 0)) for h in c.get('history', []))
                    st.warning(f"المديونية الحالية: {current_debt} ج.م")
                    with st.form(f"edit_{c['id']}"):
                        col_a, col_b = st.columns(2)
                        n_name = col_a.text_input("تعديل الاسم", value=c.get('name'))
                        n_phone = col_b.text_input("تعديل الرقم", value=c.get('phone'))
                        n_gov = col_a.selectbox("المحافظة", EGYPT_GOVS, index=EGYPT_GOVS.index(c.get('gov')) if c.get('gov') in EGYPT_GOVS else 0)
                        n_branch = col_b.selectbox("الفرع", COMPANY_BRANCHES, index=COMPANY_BRANCHES.index(c.get('branch')) if c.get('branch') in COMPANY_BRANCHES else 0)
                        n_loc = st.text_input("تعديل العنوان", value=c.get('loc'))
                        n_dev = st.selectbox("الجهاز", ["جهاز جديد", "جهاز قديم", "جهاز خارجي"], index=0)
                        
                        st.write("--- 💰 **تسوية مديونية** ---")
                        pay_amount = st.number_input("تحصيل مبلغ من الدين", min_value=0.0)
                        pay_method = st.selectbox("طريقة التحصيل", ["فودافون كاش", "تحويل بنكي", "كاش للمكتب", "عن طريق فني"])
                        selected_tech = st.selectbox("الفني المستلم", [t['name'] for t in st.session_state.techs]) if pay_method == "عن طريق فني" else "الإدارة"
                        
                        if st.form_submit_button("حفظ التعديلات والتحصيل"):
                            c.update({"name": n_name, "phone": n_phone, "gov": n_gov, "branch": n_branch, "loc": n_loc, "device_type": n_dev})
                            if pay_amount > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": f"تنزيل مديونية ({pay_amount}) - {pay_method}", "tech": "الإدارة", "price": pay_amount, "debt": -pay_amount})
                            save_json("customers.json", st.session_state.data); st.success("تم التحديث"); st.rerun()
                    
                    c1, c2, c3 = st.columns(3)
                    if c1.button("🖼️ باركود", key=f"q_{c['id']}"): st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    if c3.button("🗑️ حذف نهائي", key=f"del_{c['id']}"): st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("add_c"):
            name = st.text_input("الاسم")
            phone = st.text_input("الموبايل")
            gov = st.selectbox("المحافظة", EGYPT_GOVS)
            branch = st.selectbox("فرع الشركة", COMPANY_BRANCHES)
            loc = st.text_input("العنوان")
            device = st.selectbox("نوع الجهاز", ["جهاز جديد", "جهاز قديم", "جهاز خارجي"])
            if st.form_submit_button("إضافة"):
                new_id = max([c['id'] for c in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "gov": gov, "branch": branch, "loc": loc, "device_type": device, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تمت الإضافة")

    elif menu == "📋 تقارير الفنيين":
        st.subheader("📊 تقرير نشاط الفنيين التفصيلي")
        all_h = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') != "الإدارة":
                    current_total = sum(float(x.get('debt', 0)) for x in c.get('history', [])[:c.get('history').index(h)+1])
                    all_h.append({
                        "التاريخ": h['date'], "الفني": h['tech'], "العميل": c['name'], "الفرع": c.get('branch'),
                        "العمل": h['note'], "المحصل": h['price'], "المديونية السابقة": h.get('prev_debt', 0), "المديونية الحالية": current_total
                    })
        if all_h: st.dataframe(pd.DataFrame(all_h), use_container_width=True)
        else: st.info("لا توجد عمليات فنية.")

    elif menu == "👷 إدارة حسابات الفنيين":
        st.subheader("إضافة أو تعديل فني")
        with st.form("add_tech"):
            t_name = st.text_input("اسم الفني الجديد")
            t_pass = st.text_input("كلمة السر")
            if st.form_submit_button("إضافة فني"):
                if t_name and t_pass:
                    st.session_state.techs.append({"name": t_name, "pass": t_pass})
                    save_json("techs.json", st.session_state.techs); st.success("تمت الإضافة")

        st.write("---")
        st.subheader("الفنيين الحاليين")
        for idx, t in enumerate(st.session_state.techs):
            with st.expander(f"👷 {t['name']}"):
                new_p = st.text_input("تغيير كلمة السر", value=t['pass'], key=f"tp_{idx}")
                if st.button("حفظ التعديل", key=f"tsave_{idx}"):
                    t['pass'] = new_p; save_json("techs.json", st.session_state.techs); st.rerun()
                if st.button("❌ حذف حساب الفني", key=f"tdel_{idx}"):
                    st.session_state.techs.pop(idx); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "📊 حسابات عامة":
        all_p = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        all_d = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي التحصيل", f"{all_p:,.0f}"); st.metric("إجمالي ديون السوق", f"{all_d:,.0f}")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()
