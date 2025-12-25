import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق اللوني الواضح جداً ==================
st.set_page_config(page_title="Power Life System", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* ألوان واضحة جداً للرؤية في الشمس أو الإضاءة الضعيفة */
    [data-testid="stAppViewContainer"] { background-color: #000b1a; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0e1626 !important; border-left: 3px solid #00d4ff; }
    
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }

    /* جعل مربعات البحث والإدخال بيضاء تماماً والكتابة سوداء عريضة */
    .stTextInput input { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important; 
        font-size: 18px !important;
        border: 3px solid #00d4ff !important;
    }
    
    /* تنسيق كارت العميل */
    .cust-card {
        background: rgba(0, 212, 255, 0.15);
        border: 2px solid #00d4ff;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات المحسنة ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# تحميل البيانات في الحالة (Session State)
if 'data' not in st.session_state:
    st.session_state.data = load_data()

# ================== 3. محرك البحث الذكي (اسم / كود / تليفون) ==================
st.markdown("<h1 style='color:#00d4ff;'>🔍 البحث السريع عن عميل</h1>", unsafe_allow_html=True)

# خانة البحث الأساسية
search_input = st.text_input("أدخل (الاسم) أو (رقم التليفون) أو (الكود) هنا وسيظهر فوراً:", placeholder="مثلاً: 010...")

# منطق الفلترة المطور (حل مشكلة عدم ظهور التليفون)
if search_input:
    s = search_input.strip().lower()
    # البحث في كل الحقول وتحويلها لنصوص للمقارنة
    filtered_results = [
        c for c in st.session_state.data 
        if s in str(c.get('name', '')).lower() 
        or s in str(c.get('phone', '')) 
        or s == str(c.get('id', ''))
    ]
else:
    filtered_results = [] # لا تظهر شيء إذا كانت الخانة فارغة أو يمكنك وضع st.session_state.data لعرض الكل

# ================== 4. عرض النتائج بتنسيق واضح ==================
st.write(f"### عدد النتائج المكتشفة: {len(filtered_results)}")

for cust in filtered_results:
    with st.container():
        st.markdown(f"""
        <div class="cust-card">
            <h2 style='color:#00ffcc; margin:0;'>👤 {cust['name']}</h2>
            <p style='font-size:18px;'>🔢 الكود: {cust['id']} | 📞 التليفون: {cust.get('phone', 'غير مسجل')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.button(f"فتح ملف {cust['name']}", key=f"btn_{cust['id']}")
        with col2:
            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={cust['id']}")
    st.markdown("---")

if search_input and len(filtered_results) == 0:
    st.warning("⚠️ عذراً، لم يتم العثور على أي عميل بهذا الرقم أو الاسم. تأكد من كتابة الرقم بشكل صحيح.")
