import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. الإعدادات والتنسيق (تثبيت القائمة) ==================
st.set_page_config(page_title="Power Life System", layout="wide", initial_sidebar_state="expanded")

# رابط تطبيقك (عدله ليطابق رابط الـ streamlit الخاص بك)
APP_URL = "https://xpt.streamlit.app" 

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { min-width: 300px !important; background-color: #0e1626 !important; border-left: 3px solid #00d4ff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stTextInput input { background-color: #ffffff !important; color: #000000 !important; font-weight: bold !important; font-size: 18px !important; border: 2px solid #00d4ff !important; }
    [data-testid="sidebar-close"] { display: none; }
    .cust-card { background: rgba(0, 212, 255, 0.1); border: 1px solid #00d4ff; border-radius: 10px; padding: 15px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# ================== 2. نظام حفظ البيانات الذكي ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.session_state.data = data

if 'data' not in st.session_state:
    st.session_state.data = load_data()

def get_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. القائمة الجانبية الثابتة ==================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#00d4ff;'>باور لايف 💧</h2>", unsafe_allow_html=True)
    menu = st.radio("القائمة الرئيسية:", ["👥 البحث عن عميل", "➕ إضافة عميل جديد", "📊 نسخة احتياطية", "🚪 خروج"])

# ================== 4. المحرك الأساسي (البحث والظهور الشرطي) ==================
if menu == "👥 البحث عن عميل":
    st.markdown("### 🔍 ابحث للوصول لبيانات العميل")
    search_input = st.text_input("أدخل الاسم أو الكود أو رقم التليفون هنا:", placeholder="ابحث هنا...").strip().lower()

    # حل مشكلة ظهور كل العملاء: لا يتم البحث إلا إذا تم كتابة شيء
    if search_input:
        results = [
            c for c in st.session_state.data 
            if search_input in c['name'].lower() 
            or search_input in str(c.get('phone','')) 
            or search_input == str(c['id'])
        ]
        
        if results:
            st.success(f"تم العثور على {len(results)} نتيجة")
            for c in results:
                bal = get_balance(c['history'])
                with st.container():
                    st.markdown(f"""<div class='cust-card'>
                        <h3>👤 {c['name']} (كود: {c['id']})</h3>
                        <p style='color:#00ffcc; font-size:20px;'>الرصيد الحالي: {bal:,.0f} ج.م</p>
                    </div>""", unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        with st.expander("📝 تسجيل عملية جديدة (صيانة/تحصيل)"):
                            with st.form(f"form_{c['id']}"):
                                d = st.number_input("تكلفة الصيانة (+)")
                                p = st.number_input("المبلغ المحصل (-)")
                                n = st.text_area("تفاصيل العمل")
                                if st.form_submit_button("حفظ وإرسال"):
                                    c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": n, "debt": d, "price": p})
                                    save_data(st.session_state.data)
                                    st.success("تم الحفظ بنجاح")
                                    st.rerun()
                        
                        with st.expander("🕒 سجل الصيانات السابقة"):
                            for h in reversed(c['history']):
                                st.write(f"📅 {h['date']} | 🛠️ {h['note']} | 💰 {h['debt']-h['price']}")
                    
                    with col2:
                        # الباركود الآن يحتوي على رابط العميل المباشر
                        qr_link = f"{APP_URL}?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}", caption="باركود العميل المباشر")
        else:
            st.warning("⚠️ لا يوجد عميل مطابق لهذا البحث")
    else:
        st.info("💡 بانتظار كتابة بيانات العميل للبحث...")

# ================== 5. إضافة عميل ونسخ احتياطي ==================
elif menu == "➕ إضافة عميل جديد":
    with st.form("add_new"):
        n = st.text_input("اسم العميل"); p = st.text_input("رقم الهاتف"); d = st.number_input("مديونية سابقة")
        if st.form_submit_button("إضافة"):
            new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
            st.session_state.data.append({"id": new_id, "name": n, "phone": p, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "debt": d, "price": 0}]})
            save_data(st.session_state.data)
            st.success(f"تمت إضافة العميل بكود: {new_id}")

elif menu == "📊 نسخة احتياطية":
    st.subheader("تحميل نسخة من البيانات")
    json_str = json.dumps(st.session_state.data, ensure_ascii=False, indent=2)
    st.download_button(label="📥 تحميل ملف العملاء (Backup)", data=json_str, file_name=f"backup_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json")
