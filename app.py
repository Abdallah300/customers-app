import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر الفاخر ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق كارت العميل */
    .client-report { background: rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 25px; border: 1px dashed #007bff; margin-bottom: 20px; }
    .data-row { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 12px 0; display: flex; justify-content: space-between; }
    .history-card { background: rgba(0, 123, 255, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 5px solid #00d4ff; }
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

# ================== 3. المحرك الذكي (فصل صفحة العميل عن الإدارة) ==================
query_params = st.query_params

# لو الرابط فيه ID، اعرض صفحة العميل واقفل الموقع فوراً
if "id" in query_params:
    try:
        cust_id = int(query_params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        
        if customer:
            st.markdown(f"<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center; color:#00d4ff;'>مرحباً بك: {customer['name']}</h2>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class='client-report'>
                <div class='data-row'><span>📍 العنوان:</span> <b>{customer.get('loc', 'غير مسجل')}</b></div>
                <div class='data-row'><span>📱 رقم الموبايل:</span> <b>{customer['phone']}</b></div>
                <div class='data-row'><span>🆔 كود العميل:</span> <b>PL-{customer['id']:04d}</b></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🗓️ سجل الصيانات السابقة")
            if customer.get('history'):
                for h in reversed(customer['history']):
                    st.markdown(f"""
                    <div class='history-card'>
                        <div style='display:flex; justify-content:space-between;'>
                            <span>📅 <b>التاريخ:</b> {h['date']}</span>
                            <span style='color:#00d4ff;'>💰 {h.get('price', 0)} ج.م</span>
                        </div>
                        <p style='margin-top:10px;'>🛠️ <b>العمل المنجز:</b> {h.get('note', 'صيانة دورية')}</p>
                        <small>👤 الفني: {h.get('tech', 'فني الشركة')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا يوجد سجل صيانات حالياً.")
            
            st.success("Power Life تتمنى لكم مياه نقية وصحة جيدة 💧")
            
            # --- القفل النهائي ---
            st.stop() # هذا الأمر يمنع ظهور خانات اليوزر والباسورد للعميل
            
    except Exception as e:
        st.error("عذراً، الرابط غير صحيح.")
        st.stop()

# ================== 4. لوحة الإدارة (تظهر فقط للمدير) ==================
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>لوحة تحكم Power Life</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1,2,1])
    with col_m:
        user = st.text_input("اسم المستخدم")
        pw = st.text_input("كلمة المرور", type="password")
        if st.button("دخول الإدارة", use_container_width=True):
            if user == "admin" and pw == "admin123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("البيانات خاطئة")
else:
    # القائمة الإدارية
    st.sidebar.title("💧 Power Life Admin")
    page = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة", "📊 تقارير", "🚪 خروج"])

    if page == "➕ إضافة عميل":
        st.subheader("تسجيل عميل جديد")
        with st.form("add"):
            n = st.text_input("اسم العميل")
            p = st.text_input("الموبايل")
            l = st.text_input("العنوان")
            if st.form_submit_button("حفظ"):
                new_id = max([c['id'] for c in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "loc": l, "history": []})
                save_data(st.session_state.data)
                st.success(f"تم الحفظ بنجاح كود: PL-{new_id}")

    elif page == "👥 إدارة العملاء":
        st.subheader("إدارة والتحكم في العملاء")
        search = st.text_input("بحث بالاسم...")
        for c in st.session_state.data:
            if search in c['name']:
                col_a, col_b, col_c = st.columns([3, 1, 1])
                col_a.write(f"👤 {c['name']} (PL-{c['id']})")
                with col_b:
                    if st.button("🖼️ باركود", key=f"q_{c['id']}"):
                        url = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        qr = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={url}"
                        st.image(qr, caption=f"باركود {c['name']}")
                with col_c:
                    if st.button("🗑️ حذف", key=f"d_{c['id']}"):
                        st.session_state.data = [x for x in st.session_state.data if x['id'] != c['id']]
                        save_data(st.session_state.data)
                        st.rerun()

    elif page == "🛠️ تسجيل صيانة":
        st.subheader("تحديث سجل صيانة")
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
        with st.form("serv"):
            note = st.text_area("تفاصيل العمل والشمعات")
            tech = st.text_input("اسم الفني")
            price = st.number_input("المبلغ", min_value=0)
            if st.form_submit_button("تحديث السجل"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({"date": str(datetime.now().date()), "note": note, "tech": tech, "price": price})
                save_data(st.session_state.data)
                st.success("تم التحديث بنجاح")

    elif page == "🚪 خروج":
        st.session_state.auth = False
        st.rerun()
