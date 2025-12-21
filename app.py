import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر والهوية ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* الخلفية والتنسيق العام */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #001f3f 100%);
        color: #ffffff;
    }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* بطاقة العميل */
    .customer-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #007bff;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    
    /* الباركود */
    .qr-box {
        background: white; padding: 10px; border-radius: 10px;
        text-align: center; color: black; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# ================== 3. نظام الدخول ==================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>💧 Power Life</h1>", unsafe_allow_html=True)
    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if user == "admin" and pw == "admin123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("البيانات غير صحيحة")
else:
    # ================== 4. القائمة الجانبية ==================
    st.sidebar.title("💧 Power Life")
    page = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ صيانة", "📊 تقارير", "🚪 خروج"])

    # --- إضافة عميل ---
    if page == "➕ إضافة عميل":
        st.subheader("تسجيل عميل جديد")
        with st.form("add_form"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الموبايل")
            loc = st.text_input("العنوان (المحافظة/القرية)")
            if st.form_submit_button("حفظ"):
                new_id = max([c['id'] for c in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "loc": loc, "history": []})
                save_data(st.session_state.data)
                st.success("تمت الإضافة")

    # --- إدارة العملاء (طلبك الأساسي) ---
    elif page == "👥 إدارة العملاء":
        st.subheader("قائمة عملاء Power Life")
        search = st.text_input("بحث بالاسم أو الرقم")
        
        for c in st.session_state.data:
            if search in c['name'] or search in c['phone']:
                with st.container():
                    st.markdown(f"""<div class='customer-card'>
                        <b>الاسم:</b> {c['name']} | <b>الموبايل:</b> {c['phone']} | <b>الكود:</b> PL-{c['id']}
                    </div>""", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button(f"🖼️ باركود", key=f"q_{c['id']}"):
                            url = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                            qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={url}"
                            st.markdown(f"<div class='qr-box'><img src='{qr}'><br>PL-{c['id']}</div>", unsafe_allow_html=True)
                    
                    with col2:
                        if st.button(f"🗑️ حذف", key=f"d_{c['id']}"):
                            st.session_state.data = [x for x in st.session_state.data if x['id'] != c['id']]
                            save_data(st.session_state.data)
                            st.rerun()
                    st.divider()

    # --- الصيانة ---
    elif page == "🛠️ صيانة":
        st.subheader("تسجيل عملية صيانة")
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
        with st.form("service"):
            note = st.text_area("وصف الصيانة")
            price = st.number_input("المبلغ", min_value=0)
            if st.form_submit_button("حفظ الصيانة"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({"date": str(datetime.now().date()), "note": note, "price": price})
                save_data(st.session_state.data)
                st.success("تم الحفظ")

    # --- التقارير ---
    elif page == "📊 تقارير":
        st.subheader("إحصائيات Power Life")
        st.metric("عدد العملاء", len(st.session_state.data))
        if st.session_state.data:
            df = pd.DataFrame(st.session_state.data).drop(columns=['history'])
            st.table(df)

    elif page == "🚪 خروج":
        st.session_state.auth = False
        st.rerun()
