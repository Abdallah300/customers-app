import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات الصفحة والتنسيق اللوني المحسن ==================
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* تحسين تباين الألوان للرؤية الواضحة */
    [data-testid="stAppViewContainer"] { 
        background-color: #050a14 !important; 
        color: #ffffff !important; 
    }
    
    /* تنسيق القائمة الجانبية لمنع تقطع الكلام */
    [data-testid="stSidebar"] { 
        background-color: #0e1626 !important; 
        min-width: 280px !important;
        border-left: 2px solid #00d4ff;
    }
    
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }

    /* تحسين شكل حقول الإدخال لتكون واضحة جداً */
    .stTextInput input, .stNumberInput input, .stSelectbox div { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important;
        border: 2px solid #00d4ff !important;
    }

    /* تنسيق الكروت المالية */
    .metric-box { 
        background: linear-gradient(135deg, #00d4ff22, #00ffcc22);
        border: 1px solid #00d4ff;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
    }
    
    /* العناوين */
    h1, h2, h3 { color: #00d4ff !important; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات والبحث ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# ================== 3. لوحة التحكم والبحث الفوري ==================
if "role" not in st.session_state:
    st.session_state.role = "admin" # افتراضي للتجربة

if st.session_state.role == "admin":
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;'>نظام باور لايف 💧</h2>", unsafe_allow_html=True)
        menu = st.radio("القائمة الرئيسية", ["👥 إدارة العملاء", "➕ إضافة عميل", "📊 التقارير", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        st.markdown("### 🔍 البحث السريع عن عميل")
        
        # حقل البحث الذي يعمل على (الاسم، الكود، التليفون)
        search_query = st.text_input("اكتب اسم العميل، الكود، أو رقم التليفون للظهور الفوري...", placeholder="ابحث هنا...")
        
        if search_query:
            query = search_query.strip().lower()
            # منطق الفلترة الفورية
            results = [
                c for c in st.session_state.data 
                if query in str(c.get('name', '')).lower() 
                or query == str(c.get('id', ''))
                or query in str(c.get('phone', ''))
            ]
        else:
            results = st.session_state.data

        st.markdown(f"**عدد النتائج الموجودة: {len(results)}**")
        st.write("---")

        # عرض النتائج
        for cust in results:
            with st.expander(f"👤 {cust['name']} | كود: {cust['id']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"""
                    <div class='metric-box'>
                        <p style='margin:0;'>الرصيد الحالي</p>
                        <h2 style='margin:0; color:#00ffcc;'>{cust.get('balance', 0):,.0f} ج.م</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write(f"📞 رقم التليفون: {cust.get('phone', 'غير مسجل')}")
                with col2:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={cust['id']}", caption="QR كود")

    elif menu == "➕ إضافة عميل":
        st.subheader("سجل بيانات عميل جديد")
        with st.form("add_form"):
            name = st.text_input("اسم العميل بالكامل")
            phone = st.text_input("رقم التليفون")
            debt = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("حفظ العميل الجديد"):
                # منطق الحفظ هنا
                st.success(f"تم تسجيل العميل {name} بنجاح")

    # زر تسجيل الخروج
    if menu == "🚪 خروج":
        del st.session_state.role
        st.rerun()
