import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================
st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .report-table { width: 100%; border-collapse: collapse; background-color: white; color: black; margin: 20px 0; border-radius: 10px; overflow: hidden; }
    .report-table th { background-color: #28a745; color: white; padding: 12px; }
    .report-table td { border: 1px solid #ddd; padding: 10px; text-align: center; }
    .qr-container { border: 2px solid #28a745; padding: 20px; text-align: center; background: #fff; border-radius: 15px; max-width: 350px; margin: 20px auto; }
</style>
""", unsafe_allow_html=True)

# إدارة البيانات
FILES = {"users": "users.json", "customers": "customers.json"}

def load_data(key):
    if os.path.exists(FILES[key]):
        with open(FILES[key], "r", encoding="utf-8") as f: return json.load(f)
    return []

def save_data(key, data):
    with open(FILES[key], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data("users")
customers = load_data("customers")

if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin"})
    save_data("users", users)

# ================== 2. نظام الباركود وعرض صفحة العميل ==================
# استخراج معرف العميل من الرابط مباشرة
query_params = st.query_params
if "customer_id" in query_params:
    c_id = int(query_params["customer_id"])
    c = next((item for item in customers if item["id"] == c_id), None)
    
    if c:
        st.balloons()
        st.title(f"💧 ملف العميل: {c['name']}")
        st.success(f"كود العميل: PL-{c['id']:04d}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📍 العنوان: {c['gov']} - {c['village']}")
            st.info(f"📞 الهاتف: {c['phone']}")
        with col2:
            total = sum(h['التكلفة'] for h in c.get('history', []))
            st.metric("إجمالي المدفوعات", f"{total} ج.م")

        st.subheader("📋 سجل الصيانات السابقة")
        if c.get('history'):
            df_hist = pd.DataFrame(c['history'])
            st.table(df_hist[['التاريخ', 'العمل', 'التكلفة', 'الفني']])
        else:
            st.warning("لا توجد صيانات مسجلة حالياً.")
        st.stop()

# ================== 3. واجهة الموظفين والفنيين ==================
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life - دخول النظام")
    user_input = st.text_input("اسم المستخدم")
    pass_input = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        valid_user = next((u for u in users if u["username"] == user_input and u["password"] == pass_input), None)
        if valid_user:
            st.session_state.logged_in = True
            st.session_state.user = valid_user
            st.rerun()
        else: st.error("بيانات الدخول غير صحيحة")
else:
    curr_user = st.session_state.user
    menu = ["📋 قائمة العملاء", "➕ إضافة عميل", "🛠️ إضافة صيانة", "💰 الأرباح", "🚪 خروج"]
    choice = st.sidebar.radio("القائمة", menu)

    # --- إضافة عميل وظهور الباركود ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        with st.form("add_client"):
            n = st.text_input("اسم العميل")
            p = st.text_input("رقم الموبايل")
            g = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية"])
            v = st.text_input("القرية/المركز")
            if st.form_submit_button("حفظ وإظهار الباركود"):
                if n and p:
                    new_id = max([c['id'] for c in customers], default=0) + 1
                    # استبدل الرابط أدناه برابط موقعك الفعلي بعد الرفع
                    base_url = "https://power-life.streamlit.app" 
                    final_link = f"{base_url}/?customer_id={new_id}"
                    
                    customers.append({
                        "id": new_id, "name": n, "phone": p, "gov": g, 
                        "village": v, "history": [], "date": str(datetime.now().date())
                    })
                    save_data("customers", customers)
                    
                    st.success("✅ تم حفظ العميل!")
                    
                    # توليد الباركود وعرضه
                    qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={final_link}"
                    st.markdown(f"""
                    <div class="qr-container">
                        <h2 style="color:#28a745;">Power Life</h2>
                        <img src="{qr_api}" alt="QR Code">
                        <p><b>{n}</b></p>
                        <p>امسح الكود لعرض كشف الحساب</p>
                    </div>
                    """, unsafe_allow_html=True)
                else: st.error("برجاء ملء البيانات الأساسية")

    # --- تسجيل صيانة ---
    elif choice == "🛠️ إضافة صيانة":
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            with st.form("service"):
                work = st.multiselect("الأعمال", ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "كربون"])
                price = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("إضافة السجل"):
                    for c in customers:
                        if c['id'] == target['id']:
                            c['history'].append({
                                "التاريخ": str(datetime.now().date()),
                                "العمل": ", ".join(work),
                                "التكلفة": price,
                                "الفني": curr_user['username']
                            })
                    save_data("customers", customers)
                    st.success("تم التحديث!")
        else: st.info("لا يوجد عملاء مضافين")

    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 سجل العملاء")
        if customers:
            st.table(pd.DataFrame(customers)[['id', 'name', 'phone', 'gov']])
        else: st.info("القائمة فارغة")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
