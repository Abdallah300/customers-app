import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. الألوان (أسود وأزرق) ثابتة ==================
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
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 123, 255, 0.4);
    }
    .history-card {
        background: #1a1a1a !important; border-radius: 10px; padding: 15px;
        margin-top: 15px; border-right: 6px solid #007bff;
    }
    div.stButton > button {
        background: #007bff !important; color: white !important;
        border-radius: 8px !important; width: 100%; font-weight: bold; border: none;
    }
    input, textarea, select {
        background-color: #222 !important; color: white !important;
        border: 1px solid #007bff !important;
    }
    .debt-text { color: #ff4b4b !important; font-weight: bold; font-size: 1.6em; }
    .paid-text { color: #00ffcc !important; font-weight: bold; }
    .blue-label { color: #007bff !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_db():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f: return json.load(f)
    return []

def save_db(data):
    with open("customers.json", "w", encoding="utf-8") as f: 
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state:
    st.session_state.data = load_db()

def get_total_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. نظام "صفحة العميل" (تفتح بالباركود) ==================
# هذا الجزء هو المسؤول عن ظهور صفحة العميل عند مسح الـ QR
query_params = st.query_params
if "id" in query_params:
    try:
        cust_id = int(query_params["id"])
        customer = next((x for x in st.session_state.data if x['id'] == cust_id), None)
        if customer:
            st.markdown("<h1 style='text-align:center; color:#007bff;'>POWER LIFE 💧</h1>", unsafe_allow_html=True)
            total_rem = get_total_balance(customer['history'])
            
            st.markdown(f"""
            <div class='main-card'>
                <h2 style='margin:0;'>👤 {customer['name']}</h2>
                <p class='blue-label'>نوع التعاقد: {customer.get('device_type', 'صيانة')}</p>
                <hr style='border-color:#333;'>
                <p style='margin:0;'>إجمالي المبلغ المتبقي (المديونية):</p>
                <div class='debt-text'>{total_rem:,.1f} ج.م</div>
            </div>
            <h3 style='color:#007bff; border-bottom: 1px solid #333; padding-bottom:10px;'>📜 سجل العمليات</h3>
            """, unsafe_allow_html=True)
            
            for h in reversed(customer['history']):
                h_debt = float(h.get('debt', 0))
                h_paid = float(h.get('price', 0))
                h_rem = h_debt - h_paid
                
                st.markdown(f"""
                <div class='history-card'>
                    <div style='display:flex; justify-content:space-between;'>
                        <span class='blue-label'>🔹 {h['note']}</span>
                        <small style='color:#888;'>📅 {h['date']}</small>
                    </div>
                    <p style='margin:5px 0; font-size:0.9em;'>الفني المسؤول: {h.get('tech','الإدارة')}</p>
                    {f"<p style='margin:0; color:#00ffcc;'>⚙️ شمع مستهلك: {h['shama']}</p>" if h.get('shama') else ""}
                    <div style='margin-top:10px;'>
                        {f"<span class='debt-text' style='font-size:1em;'>🚩 متبقي من هذه العملية: {h_rem} ج.م</span>" if h_rem > 0 else "<span class='paid-text'>✅ تم السداد بالكامل</span>"}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.stop() # إيقاف التنفيذ هنا لعرض صفحة العميل فقط
    except Exception as e:
        st.error("عذراً، حدث خطأ في تحميل بيانات العميل.")

# ================== 4. لوحة الإدارة والفنيين ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; color:#007bff;'>نظام باور لايف المطور</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 لوحة الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    with col2:
        if st.button("🛠️ لوحة الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- قسم الإدارة ---
if st.session_state.role == "admin":
    menu = st.sidebar.radio("التحكم", ["قائمة العملاء", "إضافة عميل/جهاز", "تقارير الحصالة", "خروج"])
    
    if menu == "قائمة العملاء":
        search = st.text_input("🔍 بحث عن عميل بالاسم")
        for c in st.session_state.data:
            if not search or search in c['name']:
                with st.expander(f"👤 {c['name']} | الحساب: {get_total_balance(c['history'])} ج.م"):
                    st.write(f"📞 هاتف: {c.get('phone')} | 🏗️ نوع الجهاز: {c.get('device_type')}")
                    
                    # وظيفه تعديل الأقساط (زيادة أو إزالة)
                    with st.form(f"admin_ctrl_{c['id']}"):
                        st.markdown("<p class='blue-label'>إضافة أو خصم مبالغ يدوياً</p>", unsafe_allow_html=True)
                        d_add = st.number_input("إضافة مديونية/قسط (+)", 0.0)
                        d_sub = st.number_input("خصم مبلغ/تحصيل (-)", 0.0)
                        reason = st.text_input("السبب (قسط شهر كذا / صيانة)")
                        if st.form_submit_button("تحديث الحساب"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": reason, "debt": d_add, "price": d_sub, "tech": "الإدارة"})
                            save_db(st.session_state.data); st.rerun()
                    
                    if st.button(f"🗑️ حذف {c['name']}", key=f"del_{c['id']}"):
                        st.session_state.data.remove(c); save_db(st.session_state.data); st.rerun()

    elif menu == "إضافة عميل/جهاز":
        with st.form("add_new"):
            st.subheader("تسجيل عميل جديد")
            name = st.text_input("الاسم بالكامل")
            phone = st.text_input("رقم الهاتف")
            dtype = st.selectbox("نوع الجهاز/الحالة", ["جهاز 7 مراحل جديد", "جهاز 5 مراحل جديد", "عميل صيانة خارجي"])
            price = st.number_input("السعر الإجمالي (أو المديونية)", 0.0)
            paid = st.number_input("المقدم المدفوع", 0.0)
            if st.form_submit_button("تسجيل في القاعدة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": new_id, "name": name, "phone": phone, "device_type": dtype,
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": f"بداية تعاقد {dtype}", "debt": price, "price": paid, "tech": "الإدارة"}]
                })
                save_db(st.session_state.data); st.success("تم الحفظ بنجاح!")

    elif menu == "تقارير الحصالة":
        st.subheader("💰 مبالغ تحصيل الفنيين")
        t_data = []
        for c in st.session_state.data:
            for h in c['history']:
                if h.get('tech') and h['tech'] != "الإدارة":
                    t_data.append({"الفني": h['tech'], "المحصل": h['price'], "شمع": h.get('shama', 0), "التاريخ": h['date'], "العميل": c['name']})
        if t_data: st.table(t_data)
        else: st.info("لا توجد تحصيلات بعد.")

    elif menu == "خروج": del st.session_state.role; st.rerun()

# --- قسم الفني ---
if st.session_state.role == "tech_p":
    st.header(f"🛠️ فني: {st.session_state.tech_name}")
    selected_name = st.selectbox("اختر العميل", [c['name'] for c in st.session_state.data])
    target = next(c for c in st.session_state.data if c['name'] == selected_name)
    
    with st.form("tech_log"):
        cost = st.number_input("تكلفة الزيارة", 0.0)
        paid = st.number_input("المبلغ المحصل", 0.0)
        shama = st.number_input("عدد الشمع المركب", 0)
        note = st.text_area("تفاصيل العمل")
        if st.form_submit_button("إرسال التقرير"):
            target['history'].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "note": note, "debt": cost, "price": paid, "shama": shama, "tech": st.session_state.tech_name
            })
            save_db(st.session_state.data); st.success("تم الحفظ!")
    if st.button("خروج"): del st.session_state.role; st.rerun()

# --- لوجيك تسجيل الدخول ---
if st.session_state.role == "admin_login":
    if st.text_input("كود المدير", type="password") == "123": st.session_state.role = "admin"; st.rerun()
elif st.session_state.role == "tech_login":
    name = st.selectbox("اسم الفني", ["أحمد", "محمد", "علي"])
    if st.text_input("كود الفني", type="password") == "123":
        st.session_state.role = "tech_p"; st.session_state.tech_name = name; st.rerun()
