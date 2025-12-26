import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق (أسود وأزرق) ثابت ومحمي من الـ Dark Mode ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
        direction: rtl;
    }
    * { font-family: 'Cairo', sans-serif; color: #ffffff !important; }
    .main-card {
        background: #111111 !important; border: 2px solid #007bff;
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 0 10px rgba(0, 123, 255, 0.3);
    }
    .history-card {
        background: #1a1a1a !important; border-radius: 10px; padding: 15px;
        margin-top: 10px; border-right: 5px solid #007bff;
    }
    div.stButton > button {
        background: #007bff !important; color: white !important;
        border-radius: 8px !important; width: 100%; font-weight: bold;
    }
    input, textarea, select {
        background-color: #222 !important; color: white !important;
        border: 1px solid #007bff !important;
    }
    .debt-text { color: #ff4b4b !important; font-weight: bold; }
    .paid-text { color: #00ffcc !important; font-weight: bold; }
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
if 'techs' not in st.session_state: st.session_state.techs = load_db("techs.json", [{"name":"أحمد", "pass":"123"}])

def get_total_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        c = next((x for x in st.session_state.data if x['id'] == c_id), None)
        if c:
            st.markdown("<h1 style='text-align:center;'>POWER LIFE 💧</h1>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='main-card'>
                <h2 style='margin:0;'>👤 {c['name']}</h2>
                <p>نوع التعاقد: <b>{c.get('device_type', 'صيانة')}</b></p>
                <hr style='border-color:#333;'>
                <p style='margin:0;'>إجمالي الحساب المتبقي:</p>
                <h1 class='debt-text'>{get_total_balance(c['history']):,.1f} ج.م</h1>
            </div>
            """, unsafe_allow_html=True)
            
            for h in reversed(c['history']):
                cost, paid = float(h.get('debt', 0)), float(h.get('price', 0))
                rem = cost - paid
                st.markdown(f"""
                <div class='history-card'>
                    <div style='color:#007bff; font-weight:bold;'>🔹 {h['note']}</div>
                    <small>📅 {h['date']} | الفني: {h.get('tech','الإدارة')}</small><br>
                    {f"⚙️ شمع مستهلك: {h.get('shama',0)}<br>" if h.get('shama') else ""}
                    {f"<span class='debt-text'>متبقي من هذه العملية: {rem} ج.م</span>" if rem > 0 else "<span class='paid-text'>تم السداد ✅</span>"}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. نظام الإدارة والفنيين ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>نظام الإدارة - باور لايف</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    with c2:
        if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- لوحة الإدارة ---
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "🆕 إضافة عميل/جهاز", "📊 تقرير الحصالة والشمع", "🚪 خروج"])
    
    if menu == "👥 العملاء":
        search = st.text_input("🔍 ابحث عن عميل")
        for c in st.session_state.data:
            if not search or search in c['name']:
                with st.expander(f"👤 {c['name']} | الحساب: {get_total_balance(c['history'])}"):
                    st.write(f"📱 الهاتف: {c.get('phone')} | 🏗️ النوع: {c.get('device_type')}")
                    
                    # وظيفه تعديل الأقساط (زيادة أو إزالة)
                    with st.form(f"admin_edit_{c['id']}"):
                        st.subheader("إدارة الحساب والأقساط")
                        d_plus = st.number_input("إضافة مديونية (قسط جديد/زيادة) (+)", 0.0)
                        d_minus = st.number_input("خصم من الحساب (سداد/تحصيل) (-)", 0.0)
                        txt = st.text_input("بيان العملية (مثال: قسط شهر فبراير)")
                        if st.form_submit_button("تحديث الحساب"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": txt, "debt": d_plus, "price": d_minus, "tech": "الإدارة"})
                            save_db("customers.json", st.session_state.data); st.rerun()

    elif menu == "🆕 إضافة عميل/جهاز":
        with st.form("new_client"):
            st.subheader("إضافة عميل جديد للسيستم")
            n = st.text_input("اسم العميل")
            p = st.text_input("رقم الموبايل")
            dt = st.selectbox("نوع التعاقد", ["جهاز 7 مراحل جديد", "جهاز 5 مراحل جديد", "عميل خارجي (صيانة فقط)"])
            total = st.number_input("السعر الكلي (مديونية البداية)", 0.0)
            paid = st.number_input("المقدم المدفوع", 0.0)
            if st.form_submit_button("حفظ العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "device_type": dt, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": f"تعاقد {dt}", "debt": total, "price": paid, "tech": "الإدارة"}]})
                save_db("customers.json", st.session_state.data); st.success("تم تسجيل العميل بنجاح!")

    elif menu == "📊 تقرير الحصالة والشمع":
        st.subheader("تحصيل الفنيين واستهلاك الشمع")
        tech_data = []
        for c in st.session_state.data:
            for h in c['history']:
                if h.get('tech') != "الإدارة":
                    tech_data.append({"الفني": h.get('tech'), "المبلغ": float(h.get('price', 0)), "شمع": h.get('shama', 0), "التاريخ": h['date']})
        if tech_data: st.table(tech_data)
        else: st.info("لا توجد مبالغ محصلة حالياً")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# --- لوحة الفني ---
elif st.session_state.role == "tech_p":
    st.header(f"🛠️ الفني: {st.session_state.c_tech}")
    c_names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("اختر العميل", list(c_names.keys()), format_func=lambda x: c_names[x])
    target = next(c for c in st.session_state.data if c['id'] == sid)
    
    with st.form("tech_visit"):
        cost = st.number_input("تكلفة الزيارة", 0.0)
        paid = st.number_input("المبلغ اللي استلمته", 0.0)
        shama = st.number_input("عدد الشمع المركب", 0)
        note = st.text_area("تفاصيل العمل")
        if st.form_submit_button("حفظ التقرير"):
            target['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "debt": cost, "price": paid, "shama": shama, "tech": st.session_state.c_tech})
            save_db("customers.json", st.session_state.data); st.success("تم الحفظ!")
    if st.button("خروج"): del st.session_state.role; st.rerun()

# --- تسجيل الدخول ---
if st.session_state.role == "admin_login":
    if st.text_input("كود المدير", type="password") == "123": st.session_state.role = "admin"; st.rerun()
elif st.session_state.role == "tech_login":
    t_name = st.selectbox("اختر اسمك", [t['name'] for t in st.session_state.techs])
    if st.text_input("كود الفني", type="password") == "123": 
        st.session_state.role = "tech_p"; st.session_state.c_tech = t_name; st.rerun()
