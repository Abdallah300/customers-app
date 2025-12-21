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
    .tech-card { background: rgba(255, 255, 255, 0.05); border: 1px solid #00d4ff; padding: 15px; border-radius: 10px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

EGYPT_GOVS = ["القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "الشرقية", "المنوفية", "القليوبية", "البحيرة", "الغربية", "بور سعيد", "دمياط", "الإسماعيلية", "السويس", "كفر الشيخ", "الفيوم", "بني سويف", "المنيا", "أسيوط", "سوهاج", "قنا", "الأقصر", "أسوان"]
COMPANY_BRANCHES = ["فرع القاهرة الرئيسي", "فرع الجيزة", "فرع الإسكندرية", "فرع المنصورة", "فرع طنطا"]
TECHNICIANS = ["أحمد", "محمد", "محمود", "إبراهيم", "سعيد", "هاني", "مصطفى"]

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
            st.markdown(f"<div class='client-report'><div class='data-row'>👤 العميل: <b>{customer.get('name')}</b></div><div class='data-row'>📍 المحافظة: <b>{customer.get('gov')}</b></div><div class='data-row'>🏛️ الفرع: <b>{customer.get('branch')}</b></div></div>", unsafe_allow_html=True)
            st.subheader("🗓️ سجل الصيانات والتحصيلات")
            for h in reversed(history):
                style = "settlement-card" if h.get('tech') == "الإدارة" else "history-card"
                st.markdown(f"<div class='{style}'><b>📅 {h.get('date')}</b><br>📝 {h.get('note')}<br>👤 الفني: {h.get('tech')} | ✅ دفع: {h.get('price')}</div>", unsafe_allow_html=True)
            st.stop()
    except: pass

# ================== 4. نظام تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life 💧 نظام الإدارة والصيانة</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول الإدارة (Admin)", use_container_width=True):
        st.session_state.role = "admin_login"
        st.rerun()
    if c2.button("🛠️ دخول الفني (Technician)", use_container_width=True):
        st.session_state.role = "tech_login"
        st.rerun()
    st.stop()

# --- صفحة دخول الإدارة ---
if st.session_state.role == "admin_login":
    u = st.text_input("اسم مدير النظام")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123":
            st.session_state.role = "admin"
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# --- صفحة دخول الفني ---
if st.session_state.role == "tech_login":
    tech_user = st.selectbox("اختر اسمك (الفني)", TECHNICIANS)
    p = st.text_input("كلمة السر الخاصة بالفنيين", type="password")
    if st.button("دخول"):
        if p == "tech123": # كلمة سر موحدة للفنيين
            st.session_state.role = "tech"
            st.session_state.tech_name = tech_user
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الفني (Technician Interface) ==================
if st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ الفني: {st.session_state.tech_name}")
    t_menu = st.sidebar.radio("القائمة", ["📋 قائمة العملاء", "➕ تسجيل صيانة جديدة", "💰 حسابي اليومي", "🚪 خروج"])

    if t_menu == "📋 قائمة العملاء":
        st.subheader("قائمة العملاء (عرض فقط)")
        search_t = st.text_input("بحث بالاسم...")
        for c in st.session_state.data:
            if search_t in c['name']:
                with st.expander(f"👤 {c['name']} | 📱 {c['phone']}"):
                    st.write(f"📍 المحافظة: {c['gov']} | 🏛️ الفرع: {c['branch']}")
                    st.write(f"🔧 العنوان: {c['loc']}")
                    debt = sum(float(h.get('debt', 0)) for h in c.get('history', []))
                    st.error(f"⚠️ المديونية الحالية: {debt} ج.م")

    elif t_menu == "➕ تسجيل صيانة جديدة":
        st.subheader("تسجيل زيارة فنية")
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: f"{x['name']} ({x['phone']})")
        with st.form("tech_serv"):
            note = st.text_area("ماذا تم في الزيارة؟ (مثلاً: تغيير شمعة 1 و 2)")
            candles = st.number_input("عدد الشمع المستهلك", min_value=0, step=1)
            paid = st.number_input("المبلغ المستلم", min_value=0.0)
            debt = st.number_input("المتبقي دين (إن وجد)", min_value=0.0)
            if st.form_submit_button("حفظ وإرسال للسيستم"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": f"{note} (استهلاك شمع: {candles})",
                            "tech": st.session_state.tech_name,
                            "price": paid,
                            "debt": debt,
                            "candles": candles # حفظ استهلاك الشمع للتقرير
                        })
                save_data(st.session_state.data)
                st.success("تم تسجيل الصيانة بنجاح")

    elif t_menu == "💰 حسابي اليومي":
        today = datetime.now().strftime("%Y-%m-%d")
        st.subheader(f"إحصائيات اليوم: {today}")
        t_paid = 0
        t_candles = 0
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('date', '').startswith(today) and h.get('tech') == st.session_state.tech_name:
                    t_paid += float(h.get('price', 0))
                    t_candles += int(h.get('candles', 0))
        
        st.metric("💰 إجمالي تحصيلاتك اليوم", f"{t_paid} ج.م")
        st.metric("🕯️ إجمالي الشمع المستهلك", f"{t_candles} شمعة")

    elif t_menu == "🚪 خروج":
        del st.session_state.role; st.rerun()

# ================== 6. واجهة الإدارة (Admin Interface) ==================
elif st.session_state.role == "admin":
    st.sidebar.title("💎 لوحة الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة (إداري)", "📋 تقارير الفنيين", "📊 حسابات عامة", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم...")
        for i, c in enumerate(st.session_state.data):
            if search in c.get('name', ''):
                with st.expander(f"👤 {c['name']} | 📍 {c.get('branch')}"):
                    # (نفس كود التعديل والتحصيل والباركود السابق بدون تغيير)
                    with st.form(f"edit_{c['id']}"):
                        n_name = st.text_input("الاسم", value=c['name'])
                        n_phone = st.text_input("الموبايل", value=c['phone'])
                        pay_amount = st.number_input("تحصيل دين قديم", min_value=0.0)
                        pay_method = st.selectbox("طريقة الدفع", ["فودافون كاش", "تحويل بنكي", "كاش للمكتب", "عن طريق فني"])
                        selected_tech = st.selectbox("الفني المستلم", TECHNICIANS) if pay_method == "عن طريق فني" else "الإدارة"
                        if st.form_submit_button("حفظ"):
                            c['name'], c['phone'] = n_name, n_phone
                            if pay_amount > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": f"تنزيل مديونية ({pay_amount}) - {pay_method}", "tech": "الإدارة", "price": pay_amount, "debt": -pay_amount})
                            save_data(st.session_state.data); st.rerun()
                    if st.button("🖼️ باركود", key=f"q_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")

    elif menu == "📋 تقارير الفنيين":
        st.subheader("📊 تقارير نشاط الفنيين اليومية")
        today_date = datetime.now().strftime("%Y-%m-%d")
        report_data = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') in TECHNICIANS:
                    report_data.append({
                        "التاريخ": h.get('date'),
                        "الفني": h.get('tech'),
                        "العميل": c.get('name'),
                        "العمل المنجز": h.get('note'),
                        "المبلغ المحصل": h.get('price'),
                        "الشمع المستهلك": h.get('candles', 0)
                    })
        if report_data:
            df = pd.DataFrame(report_data)
            st.dataframe(df, use_container_width=True)
            # ملخص سريع لكل فني
            st.write("---")
            st.write("🔍 **ملخص أداء اليوم:**")
            for t in TECHNICIANS:
                t_sum = sum(float(r['المبلغ المحصل']) for r in report_data if r['الفني'] == t and r['التاريخ'].startswith(today_date))
                if t_sum > 0:
                    st.info(f"الفني **{t}** حصل اليوم مبلغ: **{t_sum} ج.م**")
        else:
            st.info("لا توجد تحركات فنية مسجلة بعد.")

    # (باقي أقسام الإدارة: إضافة عميل، حسابات عامة.. تبقى كما هي)
    elif menu == "📊 حسابات عامة":
        all_p = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        all_d = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي التحصيل العام", f"{all_p:,.0f} ج.م")
        st.metric("إجمالي الديون في السوق", f"{all_d:,.0f} ج.م")

    elif menu == "🚪 خروج":
        del st.session_state.role; st.rerun()
