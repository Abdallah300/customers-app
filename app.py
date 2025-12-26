import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Power Life Pro", layout="wide")

# دالة لجلب البيانات مع محاولة إصلاح الرابط تلقائياً
def get_data(url):
    try:
        # التأكد من أن الرابط بتنسيق التصدير الصحيح
        if "edit" in url:
            url = url.split("/edit")[0] + "/export?format=csv&gid=0"
        
        # محاولة قراءة صفحة العملاء
        df = pd.read_csv(url)
        return df, None
    except Exception as e:
        return None, str(e)

st.title("💧 نظام Power Life")

# 1. محاولة الربط من الـ Secrets أولاً
url_from_secrets = st.secrets.get("connections", {}).get("gsheets", {}).get("spreadsheet", "")

if url_from_secrets:
    df, err = get_data(url_from_secrets)
    if df is not None:
        st.success("✅ تم الاتصال بنجاح من الإعدادات!")
        st.session_state.df_c = df
    else:
        st.error(f"❌ فشل الاتصال بالرابط الموجود في Secrets: {err}")
        # خيار يدوي في حالة فشل الـ Secrets
        manual_url = st.text_input("أدخل رابط جوجل شيت هنا يدوياً للتجربة:")
        if manual_url:
            df_m, err_m = get_data(manual_url)
            if df_m is not None:
                [span_2](start_span)st.write("بيانات العميل من الرابط اليدوي[span_2](end_span):")
                st.dataframe(df_m)
else:
    st.warning("⚠️ الرابط مش موجود في الـ Secrets.. حطه هنا عشان نجرب:")
    manual_url = st.text_input("رابط جوجل شيت:")
    if manual_url:
        df_m, err_m = get_data(manual_url)
        if df_m is not None:
            st.success("الاتصال اليدوي شغال!")
            st.dataframe(df_m)
