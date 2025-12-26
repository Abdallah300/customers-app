import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import json

# --- 1. إعداد الصفحة ---
st.set_page_config(page_title="Power Life Pro", layout="wide")

# --- 2. الربط الذكي مع جوجل شيت ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # قراءة البيانات ومعالجة الخانات الفاضية فوراً
    df_c = conn.read(worksheet="Customers", ttl=0).fillna("")
    df_t = conn.read(worksheet="Techs", ttl=0).fillna("")
    
    # تنظيف الأسماء من أي مسافات زائدة قد تسبب خطأ في الدخول
    df_t['name'] = df_t['name'].astype(str).str.strip()
    df_t['pass'] = df_t['pass'].astype(str).str.strip()
    
    st.session_state.df_c = df_c
    st.session_state.df_t = df_t
except Exception as e:
    st.error("خطأ في جلب البيانات. تأكد من إعدادات Secrets.")
    st.stop()

# --- 3. نظام الدخول ---
if "role" not in st.session_state:
    st.title("💧 نظام Power Life Pro")
    col1, col2 = st.columns(2)
    if col1.button("🔑 دخول المدير"): st.session_state.role = "admin_login"
    if col2.button("🛠️ دخول الفني"): st.session_state.role = "tech_login"
    st.stop()

# واجهة دخول الفني (admin / 123)
if st.session_state.role == "tech_login":
    st.subheader("تسجيل دخول الفني")
    t_list = st.session_state.df_t['name'].tolist()
    user_t = st.selectbox("اختر اسمك", t_list)
    pass_t = st.text_input("كلمة السر", type="password")
    
    if st.button("دخول"):
        # فحص المطابقة مع تجاهل المسافات
        match = st.session_state.df_t[
            (st.session_state.df_t['name'] == user_t) & 
            (st.session_state.df_t['pass'] == pass_t.strip())
        ]
        if not match.empty:
            st.session_state.role = "tech_p"
            st.session_state.user_name = user_t
            st.rerun()
        else:
            st.error("الباسورد غير صحيح")
    if st.button("رجوع"): del st.session_state.role; st.rerun()

# --- 4. واجهة العرض بعد الدخول ---
if st.session_state.get("role") == "tech_p":
    st.success(f"مرحباً يا {st.session_state.user_name}")
    st.write("قائمة العملاء الحالية:")
    # عرض بيانات عبدالله منصور
    st.table(st.session_state.df_c[['name', 'phone']])
    
    if st.button("تسجيل خروج"):
        del st.session_state.role
        st.rerun()
