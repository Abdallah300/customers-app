import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات الصفحة والرؤية ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ⚠️ هام جداً: استبدل هذا الرابط برابط تطبيقك الفعلي ليعمل الباركود
APP_URL = "https://power-life-system.streamlit.app" 

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* تنسيق الواجهة الاحترافية */
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { 
        min-width: 300px !important; 
        background-color: #0e1626 !important; 
        border-left: 3px solid #00d4ff; 
    }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* وضوح خانة البحث */
    .stTextInput input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        font-size: 20px !important;
        border: 3px solid #00d4ff !important;
    }

    /* كروت العميل والصيانة */
    .cust-card { 
        background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(0,255,204,0.1));
        border: 1px solid #00d4ff; 
        border-radius: 15px; 
        padding: 25px; 
        text-align: center; 
        margin-bottom: 20px;
    }
    .history-item {
        background: rgba(255, 255, 255, 0.05);
        border-right: 5px solid #00ffcc;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
    }
    
    /* إخفاء زر إغلاق القائمة الجانبية لتثبيتها */
    [data-testid="sidebar-close"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف الداتا والملفات ==================
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

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. نظام الباركود (صفحة العميل الخاصة) ==================
# هذا الجزء يعمل فقط عندما يمسح العميل الباركود الخاص به
query_params = st.query_params
if "id" in query_params:
    cid = query_params["id"]
    cust = next((c for c in st.session_state.data if str(c['id']) == str(cid)), None)
    
    if cust:
        st.markdown(f"<h1 style='text-align:center;'>مرحباً بك في باور لايف 💧</h1>", unsafe_allow_html=True)
        bal = calculate_balance(cust['history'])
        st.markdown(f"""
            <div class='cust-card'>
                <h2>ملف العميل: {cust['name']}</h2>
                <h1 style='color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</h1>
                <p>كود العميل: {cust['id']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🗓️ سجل الصيانات السابقة")
        for h in reversed(cust['history']):
            st.markdown(f"""
                <div class='history-item'>
                    <p style='margin:0;'>📅 <b>التاريخ:</b> {h.get('date')}</p>
                    <p style='margin:0;'>🛠️ <b>البيان:</b> {h.get('note')}</p>
                    <p style='margin:0;'>👤 <b>الفني:</b> {h.get('tech', 'إدارة الشركة')}</p>
                </div>
            """, unsafe_allow_html=True)
        st.stop() # يمنع ظهور لوحة الإدارة للعميل

# ================== 4. لوحة الإدارة (Sidebar) ==================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00d4ff;'>Power Life ⚙️</h2>", unsafe_allow_html=True)
    st.write("---")
    menu = st.radio("القائمة الرئيسية:", ["🔍 بحث عن عميل", "➕ إضافة عميل جديد", "🛠️ إدارة الفنيين", "📥 النسخ الاحتياطي", "🚪 خروج"])

# ================== 5. وظائف الأقسام ==================

if menu == "🔍 بحث عن عميل":
    st.title("البحث عن عميل")
    # البحث الشرطي (لا يظهر شيء إلا بالكتابة)
    query = st.text_input("ابحث بالاسم، رقم التليفون، أو الكود...").strip().lower()
    
    if query:
        results = [c for c in st.session_state.data if query in c['name'].lower() or query in str(c.get('phone','')) or query == str(c['id'])]
        
        if results:
            st.success(f"تم العثور على {len(results)} نتيجة")
            for c in results:
                bal = calculate_balance(c['history'])
                with st.expander(f"👤 {c['name']} | كود: {c['id']} | رصيد: {bal:,.0f}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        with st.form(f"visit_{c['id']}"):
                            st.write("📝 تسجيل زيارة جديدة")
                            d = st.number_input("تكلفة الصيانة (+)", min_value=0.0)
                            p = st.number_input("المبلغ المحصل (-)", min_value=0.0)
                            t = st.text_input("اسم الفني")
                            n = st.text_area("تفاصيل العمل")
                            if st.form_submit_button("حفظ العملية ✅"):
                                c['history'].append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "note": n, "debt": d, "price": p, "tech": t
                                })
                                save_data(st.session_state.data)
                                st.rerun()
                    with col2:
                        qr_url = f"{APP_URL}?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_url}")
                        st.caption("باركود صفحة العميل")
                        if st.button("🗑️ حذف العميل", key=f"del_{c['id']}"):
                            st.session_state.data.remove(c)
                            save_data(st.session_state.data)
                            st.rerun()
        else:
            st.warning("⚠️ لا توجد نتائج مطابقة")
    else:
        st.info("💡 بانتظار كتابة بيانات العميل للبحث...")

elif menu == "➕ إضافة عميل جديد":
    st.title("تسجيل عميل جديد")
    with st.form("add"):
        n = st.text_input("اسم العميل بالكامل")
        p = st.text_input("رقم الهاتف")
        d = st.number_input("مديونية سابقة (رصيد افتتاحي)", min_value=0.0)
        if st.form_submit_button("إضافة العميل"):
            new_id = max([x['id'] for x in st.session_state.data], default=1000) + 1
            st.session_state.data.append({
                "id": new_id, "name": n, "phone": p,
                "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "debt": d, "price": 0}]
            })
            save_data(st.session_state.data)
            st.success(f"تم تسجيل العميل بنجاح. الكود: {new_id}")

elif menu == "📥 النسخ الاحتياطي":
    st.title("حفظ نسخة احتياطية")
    data_str = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 تحميل ملف البيانات (JSON)",
        data=data_str,
        file_name=f"PowerLife_Backup_{datetime.now().strftime('%Y-%m-%d')}.json",
        mime="application/json"
    )

elif menu == "🚪 خروج":
    st.session_state.clear()
    st.rerun()
