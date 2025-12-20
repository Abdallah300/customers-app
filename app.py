import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import qrcode
from io import BytesIO

# ================== 1. إعدادات النظام ==================
st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
        text-align: right;
        direction: rtl;
    }
    .report-table {
        width: 100%;
        border-collapse: collapse;
        background-color: white;
        color: black;
        margin-bottom: 20px;
    }
    .report-table th, .report-table td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: center;
    }
    .report-table th {
        background-color: #28a745;
        color: white;
    }
    .qr-box {
        border: 2px dashed #28a745;
        padding: 15px;
        text-align: center;
        background: #f0fff0;
        border-radius: 10px;
        max-width: 320px;
        margin: auto;
    }
</style>
""", unsafe_allow_html=True)

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

# حساب المدير
if not any(u['username'] == "Abdallah" for u in users):
    users.append({"username": "Abdallah", "password": "772001", "role": "admin"})
    save_data(USERS_FILE, users)

# ================== 2. صفحة العميل (عن طريق الباركود) ==================
query_params = st.query_params
if "id" in query_params:
    cust_id = int(query_params["id"])
    customer = next((c for c in customers if c['id'] == cust_id), None)

    if customer:
        st.title(f"💧 حساب العميل: {customer['name']}")

        history = customer.get("history", [])
        total_paid = sum(h['التكلفة'] for h in history)
        visits = len(history)
        technicians = list(set(h['الفني'] for h in history))

        col1, col2, col3 = st.columns(3)
        col1.metric("رقم العميل", f"PL-{customer['id']:04d}")
        col2.metric("عدد الزيارات", visits)
        col3.metric("إجمالي المدفوعات", f"{total_paid} ج.م")

        st.subheader("🧑‍🔧 الفنيين الذين قاموا بالزيارة")
        st.write("، ".join(technicians) if technicians else "لا يوجد")

        if history:
            df = pd.DataFrame(history)
            st.subheader("🛠️ سجل الصيانات")
            st.table(df)
        else:
            st.info("لا توجد صيانة مسجلة.")

    st.stop()

# ================== 3. تسجيل الدخول ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("💧 Power Life Ultra - دخول")
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        user = next((x for x in users if x["username"] == u and x["password"] == p), None)
        if user:
            st.session_state.logged_in = True
            st.session_state.current_user = user
            st.rerun()
        else:
            st.error("بيانات غير صحيحة")

# ================== 4. النظام ==================
else:
    user_now = st.session_state.current_user
    st.sidebar.title("💧 القائمة")

    menu = ["📋 قائمة العملاء", "➕ إضافة عميل", "🛠️ إضافة صيانة", "💰 أرباح الشركة"]
    if user_now['role'] == "admin":
        menu.extend(["👤 إضافة فني", "🚪 خروج"])
    else:
        menu.append("🚪 خروج")

    choice = st.sidebar.radio("انتقل إلى:", menu)

    # ================== إضافة عميل ==================
    if choice == "➕ إضافة عميل":
        st.subheader("➕ تسجيل عميل جديد")
        with st.form("add"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الهاتف")
            gov = st.text_input("المحافظة")
            ctype = st.selectbox("نوع الجهاز", ["7 مراحل", "5 مراحل", "جامبو", "عادي"])
            submit = st.form_submit_button("حفظ وإصدار باركود")

        if submit and name:
            new_id = max([c['id'] for c in customers], default=0) + 1
            link = f"https://powerlife.streamlit.app/?id={new_id}"

            new_customer = {
                "id": new_id,
                "name": name,
                "phone": phone,
                "gov": gov,
                "type": ctype,
                "history": [],
                "created_at": str(datetime.now().date())
            }

            customers.append(new_customer)
            save_data(CUSTOMERS_FILE, customers)

            # توليد QR
            qr = qrcode.make(link)
            buf = BytesIO()
            qr.save(buf, format="PNG")

            st.success("تم تسجيل العميل بنجاح")

            st.markdown("<div class='qr-box'>", unsafe_allow_html=True)
            st.image(buf.getvalue(), width=200)
            st.write(f"**{name}**")
            st.write(f"كود العميل: PL-{new_id:04d}")

            st.download_button(
                "⬇️ تحميل الباركود",
                data=buf.getvalue(),
                file_name=f"PL-{new_id:04d}.png",
                mime="image/png"
            )
            st.markdown("</div>", unsafe_allow_html=True)

    # ================== إضافة صيانة ==================
    elif choice == "🛠️ إضافة صيانة":
        if customers:
            cust = st.selectbox("اختر العميل", customers, format_func=lambda x: x['name'])
            with st.form("service"):
                work = st.text_input("العمل المنجز")
                price = st.number_input("المبلغ", min_value=0)
                if st.form_submit_button("حفظ"):
                    cust['history'].append({
                        "التاريخ": str(datetime.now().date()),
                        "الفني": user_now['username'],
                        "العمل": work,
                        "التكلفة": price
                    })
                    save_data(CUSTOMERS_FILE, customers)
                    st.success("تم تسجيل الصيانة")

    elif choice == "📋 قائمة العملاء":
        st.table(pd.DataFrame(customers)[['id','name','phone','gov','type']])

    elif choice == "💰 أرباح الشركة":
        total = sum(h['التكلفة'] for c in customers for h in c.get('history', []))
        st.metric("إجمالي الدخل", f"{total} ج.م")

    elif choice == "👤 إضافة فني":
        with st.form("tech"):
            u = st.text_input("اسم الفني")
            p = st.text_input("كلمة المرور")
            if st.form_submit_button("إضافة"):
                users.append({"username": u, "password": p, "role": "technician"})
                save_data(USERS_FILE, users)
                st.success("تمت الإضافة")

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
