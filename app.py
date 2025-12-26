import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. واجهة الألوان الفخمة (كحلي وذهبي) ==================
st.set_page_config(page_title="Power Life Dashboard", page_icon="💧", layout="wide")

# تصميم CSS احترافي ثابت
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* الخلفية العامة - لون رمادي بارد */
    [data-testid="stAppViewContainer"] {
        background-color: #f0f2f5 !important;
        direction: rtl;
    }
    
    * { font-family: 'Cairo', sans-serif; }

    /* الكارت الرئيسي - كحلي ملكي */
    .main-card {
        background: #1a2a6c !important;
        color: white !important;
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
        border-right: 8px solid #b8924e; /* ذهبي */
    }

    /* كروت السجل - أبيض بظل خفيف */
    .history-card {
        background: white !important;
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
        border-right: 5px solid #1a2a6c;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        color: #333 !important;
    }

    /* أزرار الإدارة - ذهبي */
    div.stButton > button {
        background: linear-gradient(90deg, #b8924e, #8e6d2d) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold;
        transition: 0.3s;
    }
    
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 10px rgba(184, 146, 78, 0.4);
    }

    /* تنبيهات الحالة */
    .status-debt { background: #ffdce0 !important; color: #af1921 !important; padding: 10px; border-radius: 8px; font-weight: bold; }
    .status-paid { background: #d4edda !important; color: #155724 !important; padding: 10px; border-radius: 8px; font-weight: bold; }
    
    /* العناوين */
    h1, h2, h3 { color: #1a2a6c !important; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_db(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f: return json.load(f)
    return default

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_db("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_db("techs.json", [])

def get_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (QR) ==================
params = st.query_params
if "id" in params:
    c_id = int(params["id"])
    c = next((x for x in st.session_state.data if x['id'] == c_id), None)
    if c:
        st.markdown(f"<h1 style='text-align:center;'>POWER LIFE 💧</h1>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='main-card'>
            <h2 style='color:white !important; margin:0;'>👤 {c['name']}</h2>
            <p>الجهاز: {c.get('device_type', 'صيانة دورية')}</p>
            <hr style='border-color: #b8924e;'>
            <h3 style='color:#b8924e !important;'>المبلغ المتبقي: {get_balance(c['history']):,.2f} ج.م</h3>
        </div>
        """, unsafe_allow_html=True)
        
        for h in reversed(c['history']):
            rem = float(h.get('debt', 0)) - float(h.get('price', 0))
            st.markdown(f"""
            <div class='history-card'>
                <p style='margin:0; font-size:0.8em; color:#666;'>📅 {h['date']} | الفني: {h.get('tech','الإدارة')}</p>
                <b style='font-size:1.1em;'>{h['note']}</b><br>
                {f"<span class='status-debt'>متبقي من العملية: {rem} ج.م</span>" if rem > 0 else "<span class='status-paid'>تم السداد ✅</span>"}
            </div>
            """, unsafe_allow_html=True)
        st.stop()

# ================== 4. السيستم الداخلي (إدارة + فنيين) ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>نظام إدارة باور لايف</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("💻 لوحة الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    with c2: 
        if st.button("🛠️ لوحة الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- لوحة الإدارة ---
if st.session_state.role == "admin":
    tab1, tab2, tab3 = st.tabs(["👥 العملاء والأقساط", "🆕 إضافة جهاز/عميل", "💰 الحصالة والتقارير"])
    
    with tab1:
        search = st.text_input("بحث بالاسم")
        for c in st.session_state.data:
            if not search or search in c['name']:
                with st.expander(f"{c['name']} - المتبقي: {get_balance(c['history'])}"):
                    st.write(f"النوع: {c.get('device_type')}")
                    with st.form(f"adj_{c['id']}"):
                        st.subheader("تعديل حساب العميل (إضافة/خصم)")
                        add_debt = st.number_input("زيادة مديونية (+)", 0.0)
                        pay_debt = st.number_input("تحصيل مبلغ (-)", 0.0)
                        note = st.text_input("السبب (قسط شهر كذا / صيانة)")
                        if st.form_submit_button("تحديث الحساب"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": note, "debt": add_debt, "price": pay_debt, "tech": "الإدارة"})
                            save_db("customers.json", st.session_state.data); st.rerun()

    with tab2:
        with st.form("new_customer"):
            st.subheader("إضافة عميل بجهاز جديد")
            n = st.text_input("الاسم")
            p = st.text_input("التليفون")
            dt = st.selectbox("نوع الجهاز", ["7 مراحل", "5 مراحل", "خارجي"])
            total = st.number_input("سعر الجهاز/التعاقد", 0.0)
            paid = st.number_input("المقدم", 0.0)
            if st.form_submit_button("حفظ"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "device_type": dt, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": f"تعاقد {dt}", "debt": total, "price": paid}]})
                save_db("customers.json", st.session_state.data); st.success("تم!")

    with tab3:
        st.subheader("إجمالي مبالغ الفنيين")
        all_logs = []
        for c in st.session_state.data:
            for h in c['history']:
                if h.get('tech') and h['tech'] != "الإدارة":
                    all_logs.append({"الفني": h['tech'], "المحصل": float(h['price']), "التاريخ": h['date']})
        if all_logs: st.table(all_logs)

# --- لوحة الفني ---
if st.session_state.role == "tech_p":
    st.header(f"أهلاً فني: {st.session_state.c_tech}")
    target_name = st.selectbox("اختر العميل", [c['name'] for c in st.session_state.data])
    target = next(c for c in st.session_state.data if c['name'] == target_name)
    
    with st.form("tech_visit"):
        cost = st.number_input("تكلفة الزيارة", 0.0)
        paid = st.number_input("المبلغ اللي العميل دفعه", 0.0)
        note = st.text_area("تفاصيل العمل")
        if st.form_submit_button("إرسال التقرير"):
            target['history'].append({"date": datetime.now().strftime("%y-%m-%d"), "note": note, "debt": cost, "price": paid, "tech": st.session_state.c_tech})
            save_db("customers.json", st.session_state.data); st.success("تم الإرسال")

# تسجيل الدخول
if st.session_state.role == "admin_login":
    if st.text_input("الباسورد", type="password") == "123": st.session_state.role = "admin"; st.rerun()
elif st.session_state.role == "tech_login":
    user = st.selectbox("الفني", ["أحمد", "محمد", "علي"]) # تقدر تعدلها
    if st.text_input("الباسورد", type="password") == "123": 
        st.session_state.role = "tech_p"; st.session_state.c_tech = user; st.rerun()
