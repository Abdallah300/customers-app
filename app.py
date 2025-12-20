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
    .report-table { width: 100%; border-collapse: collapse; background-color: white; color: black; margin-bottom: 20px; }
    .report-table th, .report-table td { border: 1px solid #ddd; padding: 10px; text-align: center; }
    .report-table th { background-color: #28a745; color: white; }
    .qr-box { border: 2px dashed #28a745; padding: 15px; text-align: center; background: #f0fff0; border-radius: 10px; max-width: 300px; margin: auto; }
</style>
""", unsafe_allow_html=True)

# إدارة ملفات البيانات
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

def load_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)

# تأمين حساب المدير
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin"})
    save_data(USERS_FILE, users)

# ================== 2. ميزة الباركود: صفحة العميل العامة ==================
# البحث عن معامل "id" في الرابط (لتمكين العميل من رؤية بياناته)
query_params = st.query_params
if "id" in query_params:
    cust_id = int(query_params["id"])
    target_cust = next((c for c in customers if c['id'] == cust_id), None)
    
    if target_cust:
        st.title(f"💧 مرحباً بك: {target_cust['name']}")
        st.subheader("سجل الصيانة والمدفوعات الخاص بك")
        
        col1, col2 = st.columns(2)
        total_paid = sum(h['التكلفة'] for h in target_cust.get('history', []))
        
        with col1:
            st.metric("رقم العميل", f"PL-{target_cust['id']:04d}")
        with col2:
            st.metric("إجمالي ما تم دفعه", f"{total_paid} ج.م")
            
        if target_cust.get('history'):
            rows = "".join([f"<tr><td>{h['التاريخ']}</td><td>{h['العمل']}</td><td>{h['التكلفة']} ج.م</td><td>{h['الفني']}</td></tr>" for h in target_cust['history']])
            st.markdown(f"""
            <table class='report-table'>
                <thead>
                    <tr><th>التاريخ</th><th>العمل المنجز</th><th>المبلغ</th><th>الفني</th></tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.info("لا توجد سجلات صيانة حالية.")
        st.stop()

# ================== 3. نظام دخول الموظفين ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life Ultra - دخول")
    u_in = st.text_input("اسم المستخدم")
    p_in = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u_in and x["password"] == p_in), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 القائمة")
    menu = ["📋 قائمة العملاء", "➕ إضافة عميل", "🛠️ إضافة صيانة", "🔍 بحث وتعديل", "💰 أرباح الشركة"]
    if user_now['role'] == "admin":
        menu.extend(["👤 إضافة فني جديد", "🚪 خروج"])
    else:
        menu.append("🚪 خروج")
        
    choice = st.sidebar.radio("انتقل إلى:", menu)

    # --- إضافة عميل جديد ---
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        with st.form("add_form"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الهاتف")
            gov = st.selectbox("المحافظة", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "أخرى"])
            village = st.text_input("القرية/المركز")
            ctype = st.selectbox("نوع الجهاز", ["7 مراحل", "5 مراحل", "جامبو", "فلتر عادي"])
            submit = st.form_submit_button("حفظ وإصدار الباركود")
            
            if submit and name and phone:
                new_id = max([c['id'] for c in customers], default=0) + 1
                # ملاحظة: استبدل الرابط أدناه برابط موقعك الحقيقي عند الرفع
                qr_link = f"https://powerlife.streamlit.app/?id={new_id}"
                
                new_cust = {
                    "id": new_id, "name": name, "phone": phone, "gov": gov,
                    "village": village, "type": ctype, "history": [],
                    "created_at": str(datetime.now().date())
                }
                customers.append(new_cust)
                save_data(CUSTOMERS_FILE, customers)
                
                st.success(f"تم تسجيل {name} بنجاح!")
                
                # عرض الباركود فوراً
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_link}"
                st.markdown(f"""
                <div class="qr-box">
                    <h4>كارت متابعة عميل</h4>
                    <img src="{qr_url}">
                    <p><b>{name}</b></p>
                    <p>كود العميل: PL-{new_id:04d}</p>
                </div>
                """, unsafe_allow_html=True)

    # --- إضافة صيانة ---
    elif choice == "🛠️ إضافة صيانة":
        st.subheader("🛠️ تسجيل صيانة")
        if customers:
            target = st.selectbox("اختر العميل", customers, format_func=lambda x: f"{x['name']} - {x['phone']}")
            with st.form("service"):
                work = st.multiselect("الأعمال", ["شمعة 1", "شمعة 2", "شمعة 3", "ممبرين", "كربون", "موتور", "تغيير خزان"])
                price = st.number_input("المبلغ المدفوع", min_value=0)
                if st.form_submit_button("حفظ"):
                    entry = {
                        "التاريخ": str(datetime.now().date()),
                        "الفني": user_now['username'],
                        "العمل": ", ".join(work),
                        "التكلفة": price
                    }
                    for c in customers:
                        if c['id'] == target['id']:
                            c.setdefault('history', []).append(entry)
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم الحفظ!")
        else:
            st.warning("لا يوجد عملاء.")

    # --- قائمة العملاء ---
    elif choice == "📋 قائمة العملاء":
        st.subheader("📋 سجل العملاء")
        if customers:
            df = pd.DataFrame(customers)
            st.table(df[['id', 'name', 'phone', 'gov', 'type']])
        else:
            st.info("لا توجد بيانات.")

    # --- أرباح الشركة ---
    elif choice == "💰 أرباح الشركة":
        st.subheader("💰 الحسابات")
        all_money = 0
        all_entries = []
        for c in customers:
            for h in c.get('history', []):
                all_entries.append(h)
                all_money += h['التكلفة']
        
        st.metric("إجمالي الدخل", f"{all_money} ج.م")
        if all_entries:
            st.table(pd.DataFrame(all_entries))

    elif choice == "👤 إضافة فني جديد":
        with st.form("fani"):
            u = st.text_input("اسم الفني")
            p = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة"):
                users.append({"username": u, "password": p, "role": "technician"})
                save_data(USERS_FILE, users)
                st.success("تم!")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
