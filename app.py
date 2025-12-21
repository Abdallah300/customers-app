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
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق كارت العميل */
    .client-report { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 25px; border: 1px solid #007bff; margin-top: 20px; }
    .data-row { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 10px 0; display: flex; justify-content: space-between; }
    .history-card { background: rgba(0, 123, 255, 0.1); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 5px solid #00d4ff; }
    
    /* إخفاء القائمة الجانبية للعملاء */
    [data-testid="stSidebarNav"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
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

# ================== 3. صفحة العميل (تظهر عند مسح الباركود فقط) ==================
query_params = st.query_params
if "id" in query_params:
    try:
        cust_id = int(query_params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        
        if customer:
            # عرض بيانات العميل فقط
            st.markdown(f"<h1 style='text-align:center;'>💧 Power Life</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align:center;'>مرحباً بك: {customer['name']}</h3>", unsafe_allow_html=True)
            
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
                        <b>التاريخ:</b> {h['date']} <br>
                        <b>العمل المنجز:</b> {h.get('note', 'صيانة دورية')} <br>
                        <b>الفني:</b> {h.get('tech', 'فني Power Life')} <br>
                        <b>المبلغ المدفوع:</b> {h.get('price', 0)} ج.م
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("لا يوجد سجل صيانات سابقة.")
            
            st.success("Power Life تتمنى لكم دائماً مياه صحية ونقية 💧")
            
            # --- السطر السحري ---
            st.stop() # هذا السطر يمنع ظهور أي شيء آخر (يمنع ظهور تسجيل الدخول)
            
    except Exception as e:
        st.error("عذراً، الرابط غير صحيح.")

# ================== 4. نظام دخول المدير (يظهر فقط في الموقع الأساسي) ==================
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    # إظهار القائمة الجانبية فقط عند تسجيل الدخول
    st.markdown("<style>[data-testid='stSidebarNav'] { display: none !important; }</style>", unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center;'>لوحة تحكم Power Life</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1,2,1])
    with col_m:
        user = st.text_input("اسم المستخدم")
        pw = st.text_input("كلمة المرور", type="password")
        if st.button("دخول الإدارة"):
            if user == "admin" and pw == "admin123":
                st.session_state.auth = True
                st.rerun()
            else: st.error("البيانات خاطئة")
else:
    # إظهار المنيو الجانبي للمدير فقط
    st.markdown("<style>[data-testid='stSidebarNav'] { display: block !important; }</style>", unsafe_allow_html=True)
    
    st.sidebar.title("💧 Power Life Admin")
    page = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة", "📊 تقارير", "🚪 خروج"])

    if page == "➕ إضافة عميل":
        st.subheader("تسجيل عميل جديد")
        with st.form("add"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الموبايل")
            loc = st.text_input("العنوان")
            if st.form_submit_button("حفظ"):
                new_id = max([c['id'] for c in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "loc": loc, "history": []})
                save_data(st.session_state.data)
                st.success("تم الحفظ")

    elif page == "👥 إدارة العملاء":
        st.subheader("قاعدة البيانات")
        search = st.text_input("ابحث بالاسم...")
        for c in st.session_state.data:
            if search in c['name']:
                col_a, col_b, col_c = st.columns([3, 1, 1])
                col_a.write(f"👤 {c['name']} (PL-{c['id']})")
                with col_b:
                    if st.button("🖼️ باركود", key=f"q_{c['id']}"):
                        url = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={url}"
                        st.image(qr, caption=f"باركود العميل {c['name']}")
                with col_c:
                    if st.button("🗑️ حذف", key=f"d_{c['id']}"):
                        st.session_state.data = [x for x in st.session_state.data if x['id'] != c['id']]
                        save_data(st.session_state.data)
                        st.rerun()

    elif page == "🛠️ تسجيل صيانة":
        st.subheader("تحديث بيانات الصيانة")
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
        with st.form("serv"):
            note = st.text_area("تفاصيل الزيارة")
            tech = st.text_input("اسم الفني")
            price = st.number_input("المبلغ المدفوع", min_value=0)
            if st.form_submit_button("حفظ"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({"date": str(datetime.now().date()), "note": note, "tech": tech, "price": price})
                save_data(st.session_state.data)
                st.success("تم التحديث")

    elif page == "📊 تقارير":
        st.subheader("إحصائيات")
        st.metric("إجمالي العملاء", len(st.session_state.data))
        st.write("جدول البيانات:")
        st.dataframe(pd.DataFrame(st.session_state.data).drop(columns=['history']))

    elif page == "🚪 خروج":
        st.session_state.auth = False
        st.rerun()
