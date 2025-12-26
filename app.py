import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
import urllib.parse
import json

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .client-card { background: #001f3f; border: 2px solid #007bff; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
    .btn-wa { background-color: #25d366; color: white !important; padding: 10px; border-radius: 8px; text-decoration: none; display: block; text-align: center; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. الربط مع Google Sheets (معالجة الأخطاء) ---
def load_all_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # [span_0](start_span)[span_1](start_span)قراءة البيانات من الشيت[span_0](end_span)[span_1](end_span)
        df_c = conn.read(worksheet="Customers", ttl=0).fillna("")
        df_t = conn.read(worksheet="Techs", ttl=0).fillna("")
        return df_c, df_t, True
    except Exception as e:
        return None, None, False

if 'df_c' not in st.session_state:
    df_c, df_t, success = load_all_data()
    if success:
        st.session_state.df_c = df_c
        st.session_state.df_t = df_t
    else:
        st.error("❌ عذراً، تعذر الاتصال بجوجل شيت. تأكد من إعدادات الرابط في Secrets.")
        st.stop()

def save_data(df):
    conn = st.connection("gsheets", type=GSheetsConnection)
    conn.update(worksheet="Customers", data=df)
    st.cache_data.clear()
    st.session_state.df_c = df

# --- 3. نظام الدخول ---
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>Power Life System 💧</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول المدير", use_container_width=True): st.session_state.role = "admin_login"
    if c2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"
    st.stop()

# دخول المدير
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123":
            st.session_state.role = "admin"
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# دخول الفني (باستخدام بيانات الشيت)
if st.session_state.role == "tech_login":
    # [span_2](start_span)جلب أسماء الفنيين من جدول Techs[span_2](end_span)
    names = st.session_state.df_t['name'].astype(str).str.strip().tolist()
    user_t = st.selectbox("اختر اسمك", names)
    pass_t = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        # [span_3](start_span)التأكد من مطابقة الاسم والباسورد[span_3](end_span)
        match = st.session_state.df_t[
            (st.session_state.df_t['name'].astype(str).str.strip() == user_t) & 
            (st.session_state.df_t['pass'].astype(str).str.strip() == pass_t.strip())
        ]
        if not match.empty:
            st.session_state.role = "tech_p"
            st.session_state.user_name = user_t
            st.rerun()
        else: st.error("بيانات الدخول غير صحيحة")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# --- 4. واجهة الفني (التسجيل والواتساب) ---
if st.session_state.role == "tech_p":
    st.subheader(f"🛠️ الفني: {st.session_state.user_name}")
    # [span_4](start_span)اختيار العميل من القائمة[span_4](end_span)
    target = st.selectbox("🎯 اختر العميل", st.session_state.df_c['name'].tolist())
    row_idx = st.session_state.df_c[st.session_state.df_c['name'] == target].index[0]
    client = st.session_state.df_c.iloc[row_idx]

    with st.form("visit"):
        cost = st.number_input("تكلفة الصيانة", 0.0)
        paid = st.number_input("المبلغ المدفوع", 0.0)
        note = st.text_area("تفاصيل الزيارة")
        next_v = st.date_input("موعد الزيارة القادمة", value=datetime.now() + timedelta(days=90))
        if st.form_submit_button("✅ حفظ وإرسال"):
            # تحديث السجل وحفظه
            new_df = st.session_state.df_c.copy()
            new_df.at[row_idx, 'history'] = str(note) + f" | القادم: {next_v}"
            save_data(new_df)
            # [span_5](start_span)تجهيز رابط واتساب[span_5](end_span)
            msg = f"*Power Life 💧*\nالعميل: {target}\nتم عمل: {note}\nالموعد القادم: {next_v}"
            wa_url = f"https://wa.me/2{client['phone']}?text={urllib.parse.quote(msg)}"
            st.success("تم الحفظ!")
            st.markdown(f'<a href="{wa_url}" target="_blank" class="btn-wa">📱 إرسال واتساب</a>', unsafe_allow_html=True)

    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
