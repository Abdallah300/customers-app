import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import urllib.parse

# ================== 1. إعدادات المظهر والتحكم ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-report { background: rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 25px; border: 1px solid #007bff; margin-bottom: 20px; }
    .data-row { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 12px 0; display: flex; justify-content: space-between; }
    .history-card { background: rgba(0, 123, 255, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 5px solid #00d4ff; text-align: right; }
    .finance-card { background: rgba(0, 255, 127, 0.1); border: 1px solid #00ff7f; padding: 15px; border-radius: 15px; text-align: center; }
    .debt-card { background: rgba(255, 69, 0, 0.1); border: 1px solid #ff4500; padding: 15px; border-radius: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات ==================
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

# ================== 3. صفحة العميل (الباركود) - عرض كامل للسجل ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        if customer:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>مرحباً بك: {customer.get('name')}</h3>", unsafe_allow_html=True)
            
            history = customer.get('history', [])
            total_paid = sum(float(h.get('price', 0)) for h in history)
            total_debt = sum(float(h.get('debt', 0)) for h in history)

            col1, col2 = st.columns(2)
            col1.markdown(f"<div class='finance-card'>💰 إجمالي المدفوع<br><h2>{total_paid:,.0f}</h2></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='debt-card'>⚠️ المديونية الحالية<br><h2>{total_debt:,.0f}</h2></div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class='client-report'>
                <div class='data-row'><span>📍 المحافظة:</span> <b>{customer.get('gov')}</b></div>
                <div class='data-row'><span>🏙️ العنوان:</span> <b>{customer.get('loc')}</b></div>
                <div class='data-row'><span>🔧 نوع الجهاز:</span> <b>{customer.get('device_type')}</b></div>
                <div class='data-row'><span>🆔 كود العميل:</span> <b>PL-{customer.get('id', 0):04d}</b></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🗓️ سجل الصيانات وتغيير الشمع")
            if not history:
                st.info("لا يوجد سجل صيانات مسجل بعد.")
            else:
                for h in reversed(history):
                    st.markdown(f"""<div class='history-card'>
                        <b>📅 التاريخ: {h.get('date')}</b><br>
                        🛠️ <b>العمل المنجز:</b> {h.get('note')}<br>
                        👤 <b>الفني:</b> {h.get('tech')}<br>
                        <span style='color:#00ff7f;'>✅ دفع: {h.get('price')}</span> | <span style='color:#ff4500;'>💸 دين: {h.get('debt')}</span>
                    </div>""", unsafe_allow_html=True)
            st.stop()
    except: pass

# ================== 4. لوحة الإدارة ==================
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>لوحة تحكم Power Life</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.button("دخول الإدارة", use_container_width=True):
            if u == "admin" and p == "admin123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("بيانات خاطئة")
else:
    st.sidebar.title("💧 Power Life")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة", "📊 حسابات عامة", "🚪 خروج"])

    if menu == "➕ إضافة عميل":
        st.subheader("تسجيل عميل جديد")
        with st.form("add"):
            name = st.text_input("الاسم")
            phone = st.text_input("رقم الموبايل")
            gov = st.selectbox("المحافظة", EGYPT_GOVS)
            loc = st.text_input("العنوان بالتفصيل")
            device = st.selectbox("نوع الجهاز", ["جهاز جديد", "جهاز قديم", "جهاز خارجي"])
            if st.form_submit_button("حفظ"):
                new_id = max([c['id'] for c in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "gov": gov, "loc": loc, "device_type": device, "history": []})
                save_data(st.session_state.data)
                st.success("تم تسجيل العميل بنجاح")

    elif menu == "👥 إدارة العملاء":
        st.subheader("إدارة بيانات العملاء والديون")
        search = st.text_input("بحث باسم العميل...")
        for i, c in enumerate(st.session_state.data):
            if search in c.get('name', ''):
                with st.expander(f"👤 {c['name']} | 🆔 PL-{c['id']:04d}"):
                    # ميزة تصفير المديونية
                    current_debt = sum(float(h.get('debt', 0)) for h in c.get('history', []))
                    if current_debt > 0:
                        st.warning(f"المديونية الحالية: {current_debt} ج.م")
                        if st.button(f"🔴 تصفير مديونية {c['name']} فوراً", key=f"clr_{c['id']}"):
                            for h in c['history']: h['debt'] = 0
                            save_data(st.session_state.data)
                            st.success("تم تصفير المديونية")
                            st.rerun()

                    # استمارة تعديل البيانات
                    with st.form(f"edit_{c['id']}"):
                        st.write("📝 تعديل البيانات الأساسية")
                        new_name = st.text_input("الاسم", value=c.get('name'))
                        new_phone = st.text_input("الموبايل", value=c.get('phone'))
                        new_gov = st.selectbox("المحافظة", EGYPT_GOVS, index=EGYPT_GOVS.index(c.get('gov')) if c.get('gov') in EGYPT_GOVS else 0)
                        new_loc = st.text_input("العنوان / الفرع", value=c.get('loc'))
                        new_dev = st.selectbox("الجهاز", ["جهاز جديد", "جهاز قديم", "جهاز خارجي"], index=0)
                        
                        if st.form_submit_button("حفظ التعديلات"):
                            c['name'] = new_name
                            c['phone'] = new_phone
                            c['gov'] = new_gov
                            c['loc'] = new_loc
                            c['device_type'] = new_dev
                            save_data(st.session_state.data)
                            st.success("تم التحديث")
                            st.rerun()

                    # أزرار إضافية
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("🖼️ الباركود", key=f"q_{c['id']}"):
                            url = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={url}")
                    with c2:
                        msg = urllib.parse.quote(f"رابط بيانات صيانة جهازك في Power Life: https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                        st.markdown(f'<a href="https://wa.me/2{c["phone"]}?text={msg}" target="_blank"><button style="background:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%;">🟢 واتساب</button></a>', unsafe_allow_html=True)
                    with c3:
                        if st.button("🗑️ حذف نهائي", key=f"del_{c['id']}"):
                            st.session_state.data.pop(i)
                            save_data(st.session_state.data)
                            st.rerun()

    elif menu == "🛠️ تسجيل صيانة":
        st.subheader("تسجيل زيارة فنية جديدة")
        if not st.session_state.data:
            st.info("قم بإضافة عملاء أولاً")
        else:
            target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: f"{x['name']} ({x['phone']})")
            with st.form("serv_form"):
                note = st.text_area("ماذا تم في الزيارة؟ (تغيير شمع، صيانة..)")
                tech = st.text_input("اسم الفني القائم بالعمل")
                price = st.number_input("المبلغ المدفوع", min_value=0.0)
                debt = st.number_input("المبلغ المتبقي (دين)", min_value=0.0)
                if st.form_submit_button("تسجيل الصيانة"):
                    for x in st.session_state.data:
                        if x['id'] == target['id']:
                            x['history'].append({"date": str(datetime.now().date()), "note": note, "tech": tech, "price": price, "debt": debt})
                    save_data(st.session_state.data)
                    st.success("تم تسجيل الصيانة في سجل العميل")

    elif menu == "📊 حسابات عامة":
        all_p = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        all_d = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي التحصيل العام", f"{all_p:,.0f} ج.م")
        st.metric("إجمالي المديونيات المتأخرة", f"{all_d:,.0f} ج.م")

    elif menu == "🚪 خروج":
        st.session_state.auth = False
        st.rerun()
