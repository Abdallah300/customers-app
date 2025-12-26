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
    .history-card { 
        background: rgba(0, 80, 155, 0.2); border-radius: 8px; 
        padding: 12px; margin-top: 8px; border-right: 4px solid #00d4ff; 
    }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. الربط مع Google Sheets ==================
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # جلب البيانات من الجداول
    df_customers = conn.read(worksheet="Customers", ttl=0)
    df_techs = conn.read(worksheet="Techs", ttl=0)
    return df_customers, df_techs

# تهيئة البيانات في الحالة (Session State)
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

# --- واجهة تسجيل دخول المدير ---
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123":
            st.session_state.role = "admin"
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# --- واجهة تسجيل دخول الفني ---
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
    menu = st.sidebar.radio("القائمة", ["👥 البحث والإدارة", "➕ إضافة عميل", "🛠️ إضافة فني", "📊 التقارير", "🚪 خروج"])
    
    if menu == "👥 البحث والإدارة":
        st.subheader("🔍 إدارة العملاء")
        search = st.text_input("ابحث بالاسم أو رقم الهاتف...")
        df = st.session_state.df_c
        
        for i, row in df.iterrows():
            if not search or search.lower() in str(row['name']).lower() or search in str(row['phone']):
                with st.container():
                    st.markdown(f'<div class="client-card">', unsafe_allow_html=True)
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.write(f"👤 **الاسم:** {row['name']}")
                        st.write(f"📞 **الهاتف:** {row['phone']}")
                        st.write(f"💰 **الرصيد:** {calculate_balance(row['history'])} ج.م")
                    with col_b:
                        if st.button("حذف العميل", key=f"del_{row['id']}"):
                            new_df = df.drop(i)
                            save_data(new_df); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ إضافة عميل":
        with st.form("new_client"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم التليفون")
            gps = st.text_input("رابط GPS")
            if st.form_submit_button("إضافة"):
                new_id = int(st.session_state.df_c['id'].max() + 1) if not st.session_state.df_c.empty else 1
                new_data = pd.DataFrame([{"id": new_id, "name": name, "phone": phone, "gps": gps, "history": "[]"}])
                save_data(pd.concat([st.session_state.df_c, new_data], ignore_index=True))
                st.success("تمت الإضافة بنجاح!")

    elif menu == "🛠️ إضافة فني":
        with st.form("new_tech"):
            t_name = st.text_input("اسم الفني")
            t_pass = st.text_input("كلمة السر")
            if st.form_submit_button("إضافة فني"):
                new_t = pd.DataFrame([{"name": t_name, "pass": t_pass}])
                conn.update(worksheet="Techs", data=pd.concat([st.session_state.df_t, new_t], ignore_index=True))
                st.success("تم إضافة الفني بنجاح!")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 5. واجهة الفني (Technician) ==================
elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ الفني: {st.session_state.user_name}")
    df_c = st.session_state.df_c
    
    target_name = st.selectbox("🎯 اختر العميل", df_c['name'].tolist())
    row_idx = df_c[df_c['name'] == target_name].index[0]
    client_row = df_c.iloc[row_idx]

    # أزرار اتصال سريعة
    c1, c2 = st.columns(2)
    c1.markdown(f'<a href="tel:{client_row["phone"]}" style="background:#007bff; color:white; display:block; text-align:center; padding:10px; border-radius:8px; text-decoration:none;">📞 اتصال</a>', unsafe_allow_html=True)
    if client_row['gps']:
        c2.markdown(f'<a href="{client_row["gps"]}" style="background:#ff4b4b; color:white; display:block; text-align:center; padding:10px; border-radius:8px; text-decoration:none;">📍 الموقع</a>', unsafe_allow_html=True)

    with st.form("visit_form"):
        st.write("📝 تسجيل زيارة")
        v_debt = st.number_input("تكلفة الصيانة (عليه)", 0.0)
        v_price = st.number_input("المبلغ المدفوع (منه)", 0.0)
        v_note = st.text_area("ماذا فعلت؟")
        v_next = st.date_input("موعد الزيارة القادمة", value=datetime.now() + timedelta(days=90))
        
        if st.form_submit_button("✅ حفظ وإرسال تقرير"):
            # تحديث السجل
            history = json.loads(client_row['history']) if isinstance(client_row['history'], str) else []
            history.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "note": f"{v_note} | القادمة: {v_next}",
                "tech": st.session_state.user_name,
                "debt": v_debt, "price": v_price
            })
            df_c.at[row_idx, 'history'] = json.dumps(history, ensure_ascii=False)
            save_data(df_c)
            
            # رابط واتساب
            msg = f"*Power Life 💧*\nالعميل: {target_name}\nتمت الصيانة: {v_note}\nالمحصل: {v_price} ج.م\nالموعد القادم: {v_next}\nشكراً لتعاملكم معنا."
            wa_link = f"https://wa.me/2{client_row['phone']}?text={urllib.parse.quote(msg)}"
            st.success("تم الحفظ!")
            st.markdown(f'<a href="{wa_link}" target="_blank" class="btn-wa">📱 إرسال الفاتورة عبر واتساب</a>', unsafe_allow_html=True)

    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
