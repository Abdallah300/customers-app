import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر (أزرق في أسود) ==================
st.set_page_config(page_title="Power Life CRM Ultra", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stat-card { background: rgba(255, 255, 255, 0.05); border: 1px solid #007bff; padding: 20px; border-radius: 15px; text-align: center; }
    .qr-container { background: white; padding: 20px; border-radius: 15px; display: inline-block; border: 5px solid #007bff; color: black; text-align: center; }
    .client-box { background: rgba(255, 255, 255, 0.07); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 5px solid #007bff; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_data(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'customers' not in st.session_state:
    st.session_state.customers = load_data("customers.json", [])

# ================== 3. صفحة العميل (الباركود الخارجي) ==================
if "id" in st.query_params:
    cust_id = int(st.query_params["id"])
    c = next((item for item in st.session_state.customers if item["id"] == cust_id), None)
    if c:
        st.title(f"💧 ملف العميل: {c['name']}")
        st.info(f"📍 {c['gov']} - {c['village']}")
        if c.get('history'): st.table(pd.DataFrame(c['history']))
        st.stop()

# ================== 4. تسجيل الدخول ==================
if "logged_in" not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>Power Life Login</h1>", unsafe_allow_html=True)
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else: st.error("خطأ في البيانات")
else:
    # ================== 5. القائمة الرئيسية ==================
    st.sidebar.title("💎 Power Life Ultra")
    menu = ["📊 الإحصائيات", "👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة", "🚪 خروج"]
    choice = st.sidebar.radio("القائمة", menu)

    # --- إضافة عميل جديد ---
    if choice == "➕ إضافة عميل":
        st.subheader("📝 تسجيل عميل جديد")
        with st.form("new_cust"):
            name = st.text_input("الاسم")
            phone = st.text_input("الموبايل")
            gov = st.selectbox("المحافظة", ["المنوفية", "الغربية", "القاهرة", "الجيزة"])
            village = st.text_input("القرية")
            if st.form_submit_button("حفظ"):
                new_id = max([c['id'] for c in st.session_state.customers], default=0) + 1
                st.session_state.customers.append({"id": new_id, "name": name, "phone": phone, "gov": gov, "village": village, "history": []})
                save_data("customers.json", st.session_state.customers)
                st.success("تم الحفظ بنجاح")

    # --- إدارة العملاء (التعديل المطلوب) ---
    elif choice == "👥 إدارة العملاء":
        st.title("👥 قائمة العملاء والتحكم")
        search = st.text_input("🔍 ابحث باسم العميل أو الرقم")
        
        filtered_docs = [c for c in st.session_state.customers if search.lower() in c['name'].lower() or search in c['phone']]

        for idx, c in enumerate(filtered_docs):
            with st.container():
                st.markdown(f"""<div class='client-box'>
                    <h4>{c['name']} (PL-{c['id']:04d})</h4>
                    <p>📱 {c['phone']} | 📍 {c['gov']} - {c['village']}</p>
                </div>""", unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 2, 6])
                
                # زر إظهار الباركود
                with col1:
                    if st.button(f"🖼️ باركود", key=f"qr_{c['id']}"):
                        site_url = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"
                        qr_link = f"{site_url}/?id={c['id']}"
                        qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}"
                        st.markdown(f"<div class='qr-container'><img src='{qr_api}'><br><b>{c['name']}</b></div>", unsafe_allow_html=True)

                # زر الحذف
                with col2:
                    if st.button(f"🗑️ حذف", key=f"del_{c['id']}"):
                        st.session_state.customers = [cust for cust in st.session_state.customers if cust['id'] != c['id']]
                        save_data("customers.json", st.session_state.customers)
                        st.warning(f"تم حذف {c['name']}")
                        st.rerun()
                st.divider()

    elif choice == "📊 الإحصائيات":
        st.title("📊 الإحصائيات العامة")
        st.metric("إجمالي العملاء", len(st.session_state.customers))

    elif choice == "🚪 خروج":
        st.session_state.logged_in = False
        st.rerun()
