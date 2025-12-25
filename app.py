import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات الصفحة ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ⚠️ تأكد أن هذا الرابط هو نفس الرابط الذي يظهر في المتصفح عندك
BASE_URL = "https://xpt.streamlit.app"

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { min-width: 300px !important; background-color: #0e1626 !important; border-left: 3px solid #00d4ff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* وضوح البحث */
    .stTextInput input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        font-size: 20px !important;
        border: 2px solid #00d4ff !important;
    }

    /* تصميم كارت العميل (الصفحة التي تفتح بالباركود) */
    .customer-portal {
        background: linear-gradient(145deg, #0e1626, #1a263e);
        border: 2px solid #00d4ff;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,212,255,0.2);
    }
    .status-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 10px 20px;
        border-radius: 50px;
        font-size: 24px;
        font-weight: bold;
        display: inline-block;
        margin: 15px 0;
    }
    .history-card {
        background: rgba(255, 255, 255, 0.05);
        border-right: 6px solid #00ffcc;
        padding: 15px;
        margin-top: 10px;
        border-radius: 10px;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

def get_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. نظام استقبال الباركود (صفحة العميل) ==================
# قراءة المعاملات من الرابط (الطريقة الجديدة لـ Streamlit)
q_params = st.query_params

if "id" in q_params:
    customer_id = q_params["id"]
    # البحث عن العميل في الداتا
    target_cust = next((c for c in st.session_state.data if str(c['id']) == str(customer_id)), None)
    
    if target_cust:
        # إخفاء كل شيء وإظهار صفحة العميل فقط
        st.markdown("<h1 style='text-align:center;'>💧 نظام متابعة صيانة باور لايف</h1>", unsafe_allow_html=True)
        
        current_bal = get_balance(target_cust['history'])
        
        st.markdown(f"""
        <div class="customer-portal">
            <h2 style="color:#00d4ff;">مرحباً، {target_cust['name']}</h2>
            <p style="font-size:20px;">كود المشترك: {target_cust['id']}</p>
            <div class="status-badge">المبلغ المطلوب سداده: {current_bal:,.0f} ج.م</div>
            <p style="color:#888;">آخر تحديث: {datetime.now().strftime('%Y-%m-%d')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("🛠️ سجل الزيارات والصيانات")
        
        if target_cust['history']:
            for h in reversed(target_cust['history']):
                st.markdown(f"""
                <div class="history-card">
                    <p style="margin:0; color:#00ffcc;">📅 <b>تاريخ الزيارة:</b> {h.get('date')}</p>
                    <p style="margin:5px 0;">📝 <b>ما تم تنفيذه:</b> {h.get('note', 'صيانة دورية')}</p>
                    <p style="margin:0; font-size:14px; color:#aaa;">👤 <b>الفني المسؤول:</b> {h.get('tech', 'إدارة الشركة')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("لا توجد سجلات صيانة مسجلة حالياً.")
        
        # زر للرجوع (اختياري للمدير فقط)
        if st.button("العودة للرئيسية"):
            st.query_params.clear()
            st.rerun()
            
        st.stop() # هذا السطر يمنع ظهور لوحة التحكم للعميل نهائياً

# ================== 4. لوحة الإدارة (في حال عدم وجود ID في الرابط) ==================
with st.sidebar:
    st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life</h1>", unsafe_allow_html=True)
    menu = st.radio("انتقل إلى:", ["🔍 بحث سريع", "➕ إضافة عميل", "📂 تصدير البيانات"])
    st.markdown("---")
    st.caption("نظام إدارة فلاتر المياه v3.0")

if menu == "🔍 بحث سريع":
    st.title("البحث عن ملف عميل")
    # خانة البحث بيضاء وواضحة جداً
    s_query = st.text_input("اكتب (الاسم / الكود / التليفون) للبحث...").strip().lower()
    
    if s_query:
        # فلترة النتائج
        results = [c for c in st.session_state.data if s_query in c['name'].lower() or s_query in str(c.get('phone','')) or s_query == str(c['id'])]
        
        if results:
            for c in results:
                c_bal = get_balance(c['history'])
                with st.expander(f"👤 {c['name']} | كود: {c['id']} | رصيد: {c_bal:,.0f}"):
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        with st.form(f"add_visit_{c['id']}"):
                            st.write("➕ إضافة زيارة/تحصيل جديد")
                            debt = st.number_input("تكلفة الصيانة (+)", min_value=0.0)
                            paid = st.number_input("المبلغ المحصل (-)", min_value=0.0)
                            tech_name = st.text_input("اسم الفني القائم بالعمل")
                            work_note = st.text_area("تفاصيل الزيارة (تغيير شمعات، إلخ)")
                            if st.form_submit_button("حفظ الزيارة ✅"):
                                c['history'].append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "note": work_note, "debt": debt, "price": paid, "tech": tech_name
                                })
                                save_data(st.session_state.data)
                                st.success("تم الحفظ بنجاح")
                                st.rerun()
                    with col2:
                        # إنشاء رابط الباركود الصحيح
                        full_qr_url = f"{BASE_URL}/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={full_qr_url}")
                        st.caption("باركود صفحة العميل الشخصية")
                        if st.button(f"🗑️ حذف {c['id']}", key=f"del_{c['id']}"):
                            st.session_state.data.remove(c)
                            save_data(st.session_state.data)
                            st.rerun()
        else:
            st.error("لم يتم العثور على نتائج.")
    else:
        st.info("💡 بانتظار كتابة بيانات البحث...")

elif menu == "➕ إضافة عميل":
    st.title("تسجيل عميل جديد")
    with st.form("new_entry"):
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم الموبايل")
        init_debt = st.number_input("الرصيد الافتتاحي (مديونية سابقة)", min_value=0.0)
        if st.form_submit_button("إضافة العميل للداتا"):
            new_id = max([x['id'] for x in st.session_state.data], default=1000) + 1
            st.session_state.data.append({
                "id": new_id, "name": name, "phone": phone,
                "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "debt": init_debt, "price": 0}]
            })
            save_data(st.session_state.data)
            st.success(f"تم التسجيل بنجاح. كود العميل الجديد: {new_id}")

elif menu == "📂 تصدير البيانات":
    st.title("النسخ الاحتياطي")
    json_data = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
    st.download_button("📥 تحميل ملف العملاء (Backup)", json_data, "power_life_backup.json")
