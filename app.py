import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
import urllib.parse
import json

# --- 1. الإعدادات والتصميم ---
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .client-card { background: #001f3f; border: 2px solid #007bff; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
    .btn-wa { background-color: #25d366; color: white !important; padding: 12px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. دالة جلب البيانات ---
def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # قراءة الجداول مع معالجة الخانات الفارغة
        df_customers = conn.read(worksheet="Customers", ttl=0).fillna("")
        df_techs = conn.read(worksheet="Techs", ttl=0).fillna("")
        return df_customers, df_techs, True
    except:
        return None, None, False

# تخزين البيانات في الجلسة
if 'df_c' not in st.session_state:
    df_c, df_t, success = load_data()
    if success:
        st.session_state.df_c = df_c
        st.session_state.df_t = df_t
    else:
        st.error("❌ تعذر الاتصال بجوجل شيت. تأكد من إعدادات الرابط في Secrets.")
        st.stop()

def update_sheet(df):
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(worksheet="Customers", data=df)
    st.cache_data.clear()
    st.session_state.df_c = df

# --- 3. نظام الدخول ---
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>Power Life System 💧</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if col1.button("🔑 دخول المدير", use_container_width=True): st.session_state.role = "admin_login"
    if col2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"
    st.stop()

# شاشة دخول الفني
if st.session_state.role == "tech_login":
    st.subheader("🛠️ دخول الفنيين")
    tech_names = st.session_state.df_t['name'].astype(str).str.strip().tolist()
    user_input = st.selectbox("اختر اسمك", tech_names)
    pass_input = st.text_input("كلمة السر", type="password")
    
    if st.button("دخول"):
        # التحقق من البيانات (admin / 123)
        check = st.session_state.df_t[
            (st.session_state.df_t['name'].astype(str).str.strip() == user_input) & 
            (st.session_state.df_t['pass'].astype(str).str.strip() == pass_input)
        ]
        if not check.empty:
            st.session_state.role = "tech_p"
            st.session_state.user_name = user_input
            st.rerun()
        else:
            st.error("كلمة السر خاطئة!")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# --- 4. واجهة الفني (تسجيل الزيارة + واتساب) ---
if st.session_state.role == "tech_p":
    st.success(f"أهلاً بك يا {st.session_state.user_name}")
    
    # اختيار العميل (سيظهر عبدالله)
    customer_list = st.session_state.df_c['name'].tolist()
    selected_name = st.selectbox("🎯 اختر العميل", customer_list)
    idx = st.session_state.df_c[st.session_state.df_c['name'] == selected_name].index[0]
    client_data = st.session_state.df_c.iloc[idx]
    
    with st.form("service_form"):
        st.write(f"تسجيل صيانة لـ: **{selected_name}**")
        note = st.text_area("ماذا تم في الزيارة؟ (مثلاً: تغيير شمعات)")
        price = st.number_input("المبلغ المحصل", min_value=0)
        next_date = st.date_input("موعد الزيارة القادمة", value=datetime.now() + timedelta(days=90))
        
        if st.form_submit_button("حفظ وإرسال تقرير"):
            # تحديث البيانات في جوجل شيت
            new_df = st.session_state.df_c.copy()
            history_entry = f"[{datetime.now().strftime('%Y-%m-%d')}] {note} | المحصل: {price} | القادم: {next_date}"
            new_df.at[idx, 'history'] = str(new_df.at[idx, 'history']) + " \n " + history_entry
            update_sheet(new_df)
            
            # رابط واتساب تلقائي
            msg = f"*تقرير صيانة Power Life 💧*\nالعميل: {selected_name}\nتم عمل: {note}\nالمبلغ: {price} ج.م\nالزيارة القادمة: {next_date}\nشكراً لثقتكم بنا!"
            encoded_msg = urllib.parse.quote(msg)
            wa_url = f"https://wa.me/2{client_data['phone']}?text={encoded_msg}"
            
            st.success("✅ تم الحفظ بنجاح!")
            st.markdown(f'<a href="{wa_url}" target="_blank" class="btn-wa">📱 إرسال الفاتورة عبر واتساب</a>', unsafe_allow_html=True)

    if st.button("🚪 تسجيل خروج"): del st.session_state.role; st.rerun()

# --- 5. واجهة المدير (إدارة العملاء) ---
if st.session_state.role == "admin":
    st.subheader("👥 إدارة العملاء")
    st.dataframe(st.session_state.df_c[['id', 'name', 'phone', 'history']])
    
    if st.button("🚪 تسجيل خروج"): del st.session_state.role; st.rerun()
