import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. ستايل "باور لايف" الأسود والأزرق ==================
st.set_page_config(page_title="Power Life Dark Pro", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* إجبار الخلفية على اللون الأسود العميق */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
        direction: rtl;
    }
    
    * { font-family: 'Cairo', sans-serif; color: #ffffff !important; }

    /* الكروت بلون أسود فاتح قليلاً مع حدود زرقاء */
    .main-card {
        background: #111111 !important;
        border: 2px solid #007bff; /* أزرق */
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 123, 255, 0.2);
    }

    .history-card {
        background: #1a1a1a !important;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
        border-right: 5px solid #007bff; /* أيقونة الخط الأزرق */
    }

    /* الأزرار باللون الأزرق */
    div.stButton > button {
        background: #007bff !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        font-weight: bold;
        width: 100%;
    }

    /* المدخلات بلون داكن */
    input, textarea, select {
        background-color: #222 !important;
        color: white !important;
        border: 1px solid #007bff !important;
    }

    /* أيقونات وعناوين زرقاء */
    .blue-icon { color: #007bff !important; font-size: 1.2em; margin-left: 10px; }
    h1, h2, h3 { color: #007bff !important; }
    
    /* تنبيهات المبالغ */
    .debt-text { color: #ff4b4b !important; font-weight: bold; font-size: 1.5em; }
    .paid-text { color: #00ffcc !important; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات والعمليات ==================
def load_db(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f: return json.load(f)
    return default

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_db("customers.json", [])

def get_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (Black Mode) ==================
params = st.query_params
if "id" in params:
    c_id = int(params["id"])
    c = next((x for x in st.session_state.data if x['id'] == c_id), None)
    if c:
        st.markdown(f"<h1 style='text-align:center;'>POWER LIFE 💧</h1>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='main-card'>
            <h2 style='margin:0;'>🔹 {c['name']}</h2>
            <p>الجهاز: {c.get('device_type', 'صيانة دورية')}</p>
            <hr style='border-color: #333;'>
            <p style='margin:0;'>المبلغ المتبقي المطلوب سداده:</p>
            <div class='debt-text'>{get_balance(c['history']):,.1f} ج.م</div>
        </div>
        """, unsafe_allow_html=True)
        
        for h in reversed(c['history']):
            rem = float(h.get('debt', 0)) - float(h.get('price', 0))
            st.markdown(f"""
            <div class='history-card'>
                <div style='color:#007bff;'>🔵 <b>{h['note']}</b></div>
                <div style='font-size:0.8em; color:#888;'>📅 {h['date']} | الفني: {h.get('tech','الإدارة')}</div>
                {f"<div style='color:#ff4b4b;'>متبقي: {rem} ج.م</div>" if rem > 0 else "<div style='color:#00ffcc;'>تم السداد ✅</div>"}
            </div>
            """, unsafe_allow_html=True)
        st.stop()

# ================== 4. نظام الإدارة والفنيين المطور ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>Power Life Management System</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("🔵 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    with c2: 
        if st.button("🔵 دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- لوحة الإدارة ---
if st.session_state.role == "admin":
    menu = st.sidebar.selectbox("القائمة", ["العملاء والتحكم بالأقساط", "إضافة عميل/جهاز جديد", "خروج"])
    
    if menu == "العملاء والتحكم بالأقساط":
        search = st.text_input("🔍 بحث عن عميل")
        for c in st.session_state.data:
            if not search or search in c['name']:
                with st.expander(f"👤 {c['name']} | المتبقي: {get_balance(c['history'])}"):
                    st.write(f"📞 هاتف: {c.get('phone')}")
                    qr_link = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://power-life.streamlit.app/?id={c['id']}"
                    st.image(qr_link, caption="QR Code الخاص بالعميل")
                    
                    with st.form(f"admin_ctrl_{c['id']}"):
                        st.subheader("تعديل الأقساط والمديونية")
                        d_up = st.number_input("إضافة مبلغ على العميل (دين/قسط)", 0.0)
                        d_down = st.number_input("خصم مبلغ (تحصيل)", 0.0)
                        note = st.text_input("بيان العملية")
                        if st.form_submit_button("حفظ التعديلات"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": note, "debt": d_up, "price": d_down, "tech": "الإدارة"})
                            save_db("customers.json", st.session_state.data); st.rerun()

    elif menu == "إضافة عميل/جهاز جديد":
        with st.form("new_entry"):
            name = st.text_input("اسم العميل الجديد")
            phone = st.text_input("رقم الموبايل")
            device = st.selectbox("نوع الجهاز", ["جهاز 7 مراحل جديد", "جهاز 5 مراحل جديد", "عميل صيانة خارجي"])
            full_price = st.number_input("إجمالي ثمن الجهاز/التعاقد", 0.0)
            down_payment = st.number_input("المقدم المدفوع", 0.0)
            if st.form_submit_button("تسجيل العميل في النظام"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": new_id, "name": name, "phone": phone, "device_type": device,
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": f"تعاقد جديد: {device}", "debt": full_price, "price": down_payment, "tech": "الإدارة"}]
                })
                save_db("customers.json", st.session_state.data); st.success("تم تسجيل العميل بنجاح!")
    
    elif menu == "خروج": del st.session_state.role; st.rerun()

# --- لوحة الفني ---
if st.session_state.role == "tech_p":
    st.header(f"🛠️ لوحة الفني: {st.session_state.c_tech}")
    c_list = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("اختر العميل", list(c_list.keys()), format_func=lambda x: c_list[x])
    target = next(c for c in st.session_state.data if c['id'] == sid)
    
    with st.form("tech_visit"):
        cost = st.number_input("تكلفة الزيارة/الصيانة", 0.0)
        paid = st.number_input("المبلغ المستلم من العميل", 0.0)
        note = st.text_area("تقرير الصيانة (ماذا تم؟)")
        if st.form_submit_button("إرسال التقرير"):
            target['history'].append({"date": datetime.now().strftime("%y-%m-%d"), "note": note, "debt": cost, "price": paid, "tech": st.session_state.c_tech})
            save_db("customers.json", st.session_state.data); st.success("تم حفظ التقرير")
    if st.button("تسجيل خروج"): del st.session_state.role; st.rerun()

# لوجيك الدخول
if st.session_state.role == "admin_login":
    if st.text_input("كود المدير", type="password") == "123": st.session_state.role = "admin"; st.rerun()
elif st.session_state.role == "tech_login":
    t_name = st.selectbox("اسم الفني", ["أحمد", "محمد", "محمود"])
    if st.text_input("كود الفني", type="password") == "123": 
        st.session_state.role = "tech_p"; st.session_state.c_tech = t_name; st.rerun()
