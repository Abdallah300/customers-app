import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime, timedelta
import urllib.parse
import json

# ================== 1. الإعدادات والتنسيق (CSS) ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .client-card { 
        background: #001f3f; border: 2px solid #007bff; 
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
    }
    .btn-wa { 
        background-color: #25d366; color: white !important; 
        padding: 12px; border-radius: 8px; text-decoration: none; 
        display: block; text-align: center; font-weight: bold; margin-top: 10px;
    }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. الربط مع Google Sheets ==================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    df_customers = conn.read(worksheet="Customers", ttl=0)
    df_techs = conn.read(worksheet="Techs", ttl=0)
    return df_customers, df_techs

if 'df_c' not in st.session_state:
    st.session_state.df_c, st.session_state.df_t = load_data()

def save_data(df):
    conn.update(worksheet="Customers", data=df)
    st.cache_data.clear()
    st.session_state.df_c = df

def calculate_balance(history_json):
    try:
        history = json.loads(history_json) if isinstance(history_json, str) else []
        return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
    except: return 0

# ================== 3. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>Power Life System 💧</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if col1.button("🔑 دخول المدير", use_container_width=True): st.session_state.role = "admin_login"
    if col2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"
    st.stop()

# --- دخول المدير ---
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123":
            st.session_state.role = "admin"
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# --- دخول الفني ---
if st.session_state.role == "tech_login":
    t_names = st.session_state.df_t['name'].tolist()
    user_t = st.selectbox("اختر اسمك", t_names)
    pass_t = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech_row = st.session_state.df_t[st.session_state.df_t['name'] == user_t]
        if not tech_row.empty and str(tech_row.iloc[0]['pass']) == pass_t:
            st.session_state.role = "tech_p"
            st.session_state.user_name = user_t
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 4. لوحة الإدارة (Admin) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ إضافة فني", "📊 التقارير", "🚪 خروج"])
    
    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بالاسم أو الهاتف...")
        df = st.session_state.df_c
        for i, row in df.iterrows():
            if not search or search.lower() in str(row['name']).lower() or search in str(row['phone']):
                st.markdown(f'<div class="client-card">👤 <b>{row["name"]}</b><br>📞 {row["phone"]}<br>💰 الرصيد: {calculate_balance(row["history"])} ج.م</div>', unsafe_allow_html=True)
                if st.button(f"حذف {row['name']}", key=f"del_{row['id']}"):
                    save_data(df.drop(i)); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("add_c"):
            n = st.text_input("الاسم")
            p = st.text_input("الهاتف")
            g = st.text_input("رابط الموقع (GPS)")
            if st.form_submit_button("حفظ"):
                new_id = int(st.session_state.df_c['id'].max() + 1) if not st.session_state.df_c.empty else 1
                new_row = pd.DataFrame([{"id": new_id, "name": n, "phone": p, "gps": g, "history": "[]"}])
                save_data(pd.concat([st.session_state.df_c, new_row], ignore_index=True))
                st.success("تم الحفظ!")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 5. واجهة الفني (Technician) ==================
elif st.session_state.role == "tech_p":
    st.subheader(f"مرحباً بك: {st.session_state.user_name}")
    df_c = st.session_state.df_c
    target_client = st.selectbox("🎯 اختر العميل", df_c['name'].tolist())
    row_idx = df_c[df_c['name'] == target_client].index[0]
    client_data = df_c.iloc[row_idx]

    col1, col2 = st.columns(2)
    col1.markdown(f'<a href="tel:{client_data["phone"]}" style="background:#007bff; color:white; display:block; text-align:center; padding:10px; border-radius:8px; text-decoration:none;">📞 اتصال</a>', unsafe_allow_html=True)
    if client_data['gps']:
        col2.markdown(f'<a href="{client_data["gps"]}" style="background:#ff4b4b; color:white; display:block; text-align:center; padding:10px; border-radius:8px; text-decoration:none;">📍 الموقع</a>', unsafe_allow_html=True)

    with st.form("visit"):
        cost = st.number_input("تكلفة الصيانة", 0.0)
        paid = st.number_input("المبلغ المدفوع", 0.0)
        note = st.text_area("وصف العمل")
        next_v = st.date_input("موعد الزيارة القادمة", value=datetime.now() + timedelta(days=90))
        if st.form_submit_button("✅ حفظ وإرسال تقرير"):
            history = json.loads(client_data['history']) if isinstance(client_data['history'], str) else []
            history.append({"date": datetime.now().strftime("%Y-%m-%d"), "note": f"{note} | القادم: {next_v}", "tech": st.session_state.user_name, "debt": cost, "price": paid})
            df_c.at[row_idx, 'history'] = json.dumps(history, ensure_ascii=False)
            save_data(df_c)
            msg = f"*Power Life 💧*\nالعميل: {target_client}\nتمت الصيانة: {note}\nالمحصل: {paid} ج.م\nالموعد القادم: {next_v}"
            wa_url = f"https://wa.me/2{client_data['phone']}?text={urllib.parse.quote(msg)}"
            st.success("تم التسجيل!")
            st.markdown(f'<a href="{wa_url}" target="_blank" class="btn-wa">📱 إرسال للعميل عبر واتساب</a>', unsafe_allow_html=True)

    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
