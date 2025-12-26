import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. ستايل الألوان (أسود وأزرق) مع الحفاظ على الهيكل الأصلي ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* الخلفية السوداء */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
        direction: rtl;
    }
    
    /* النصوص والخطوط */
    * { font-family: 'Cairo', sans-serif; color: #ffffff !important; }
    
    /* الكروت الزرقاء */
    .main-card {
        background: #111111 !important; border: 2px solid #007bff;
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
    }
    
    .history-card {
        background: #1a1a1a !important; border-radius: 10px; padding: 15px;
        margin-top: 10px; border-right: 5px solid #007bff;
    }

    /* الأزرار الزرقاء */
    div.stButton > button {
        background: #007bff !important; color: white !important;
        border-radius: 8px !important; width: 100%; font-weight: bold;
    }

    /* حقول الإدخال */
    input, textarea, select {
        background-color: #222 !important; color: white !important;
        border: 1px solid #007bff !important;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. قاعدة البيانات (الهيكل الأصلي) ==================
def load_data():
    if os.path.exists("data.json"):
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"customers": [], "techs": [{"name": "المدير", "pass": "123"}]}

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# ================== 3. وظيفة صفحة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    customer_id = int(params["id"])
    customer = next((c for c in st.session_state.db["customers"] if c["id"] == customer_id), None)
    
    if customer:
        st.markdown(f"<h1 style='text-align:center;'>POWER LIFE 💧</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='main-card'><h2>👤 {customer['name']}</h2><h3>نوع الجهاز: {customer.get('device', 'غير محدد')}</h3></div>", unsafe_allow_html=True)
        
        st.subheader("📜 سجل الصيانات والمدفوعات")
        total_debt = 0
        for record in customer["history"]:
            total_debt += (float(record.get("price", 0)) - float(record.get("paid", 0)))
            st.markdown(f"""
            <div class='history-card'>
                <b>📅 التاريخ: {record['date']}</b><br>
                <span>🛠️ العمل: {record['note']}</span><br>
                <span style='color:#00ffcc;'>💰 المدفوع: {record['paid']} ج.م</span> | 
                <span style='color:#ff4b4b;'>🚩 المتبقي: {float(record['price']) - float(record['paid'])} ج.م</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"<div class='main-card'><h2 style='text-align:center; color:#ff4b4b;'>إجمالي المديونية: {total_debt} ج.م</h2></div>", unsafe_allow_html=True)
        st.stop()

# ================== 4. لوحة التحكم (الإدارة والفنيين) ==================
st.title("نظام إدارة باور لايف 💧")

menu = st.sidebar.selectbox("القائمة الرئيسية", ["تسجيل دخول", "إدارة العملاء", "إضافة عميل جديد", "تقرير الحصالة"])

if menu == "تسجيل دخول":
    st.info("الرجاء اختيار التبويب المطلوب من القائمة الجانبية")
    if st.button("خروج"):
        st.session_state.clear()
        st.rerun()

elif menu == "إضافة عميل جديد":
    with st.form("add_client"):
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الهاتف")
        device_type = st.selectbox("نوع الجهاز/التعاقد", ["جهاز جديد 7 مراحل", "جهاز جديد 5 مراحل", "صيانة خارجي"])
        initial_price = st.number_input("السعر الكلي", value=0.0)
        initial_paid = st.number_input("المقدم المدفوع", value=0.0)
        if st.form_submit_button("حفظ العميل"):
            new_id = len(st.session_state.db["customers"]) + 1
            st.session_state.db["customers"].append({
                "id": new_id, "name": name, "phone": phone, "device": device_type,
                "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "تعاقد ابتدائي", "price": initial_price, "paid": initial_paid}]
            })
            save_data(st.session_state.db)
            st.success(f"تمت إضافة العميل بنجاح. كود العميل: {new_id}")

elif menu == "إدارة العملاء":
    search = st.text_input("بحث عن عميل")
    for c in st.session_state.db["customers"]:
        if not search or search in c["name"]:
            with st.expander(f"{c['name']} (كود: {c['id']})"):
                st.write(f"رقم الهاتف: {c['phone']}")
                st.write(f"نوع الجهاز: {c['device']}")
                
                # إضافة سجل جديد أو قسط
                with st.form(f"form_{c['id']}"):
                    st.write("📝 إضافة عملية جديدة (صيانة أو قسط)")
                    note = st.text_input("بيان العمل")
                    price = st.number_input("المبلغ المطلوب", value=0.0)
                    paid = st.number_input("المبلغ المدفوع", value=0.0)
                    if st.form_submit_button("تحديث الحساب"):
                        c["history"].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": note, "price": price, "paid": paid})
                        save_data(st.session_state.db)
                        st.rerun()

elif menu == "تقرير الحصالة":
    st.subheader("💰 ملخص التحصيلات")
    total_all = 0
    for c in st.session_state.db["customers"]:
        for r in c["history"]:
            total_all += float(r.get("paid", 0))
    st.metric("إجمالي حصالة الشركة", f"{total_all} ج.م")
