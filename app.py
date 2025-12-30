import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ================== 1. إعدادات المظهر ==================
st.set_page_config(page_title="Power Life Pro v2", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; background-color: #0e1117; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stMetric { background: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)

# ================== 2. محرك البيانات (محسن) ==================
def init_files():
    """التأكد من وجود الملفات لتجنب أخطاء التسجيل"""
    for file in ["customers.json", "techs.json"]:
        if not os.path.exists(file):
            with open(file, "w", encoding="utf-8") as f:
                json.dump([], f)

def load_data():
    init_files()
    with open("customers.json", "r", encoding="utf-8") as f:
        customers = json.load(f)
    with open("techs.json", "r", encoding="utf-8") as f:
        techs = json.load(f)
    return customers, techs

def save_all(customers=None, techs=None):
    if customers is not None:
        with open("customers.json", "w", encoding="utf-8") as f:
            json.dump(customers, f, ensure_ascii=False, indent=2)
    if techs is not None:
        with open("techs.json", "w", encoding="utf-8") as f:
            json.dump(techs, f, ensure_ascii=False, indent=2)

# تحميل البيانات فوراً
if 'data' not in st.session_state or 'techs' not in st.session_state:
    st.session_state.data, st.session_state.techs = load_data()

def get_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. نظام تسجيل الدخول ==================
if "role" not in st.session_state:
    st.title("⚡ نظام Power Life")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 بوابة الإدارة", use_container_width=True):
            st.session_state.role = "admin_auth"
            st.rerun()
    with col2:
        if st.button("🛠️ بوابة الفنيين", use_container_width=True):
            st.session_state.role = "tech_auth"
            st.rerun()
    st.stop()

# (حماية الدخول)
if st.session_state.role == "admin_auth":
    pw = st.text_input("كلمة مرور المدير", type="password")
    if st.button("دخول"):
        if pw == "admin123":
            st.session_state.role = "admin"
            st.rerun()
    st.stop()

if st.session_state.role == "tech_auth":
    t_names = [t['name'] for t in st.session_state.techs]
    if not t_names:
        st.error("لا يوجد فنيين مسجلين. اطلب من المدير إضافتك.")
    else:
        user = st.selectbox("اختر اسمك", t_names)
        tpw = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            tech = next((t for t in st.session_state.techs if t['name'] == user), None)
            if tech and tpw == tech['pass']:
                st.session_state.role = "tech_panel"
                st.session_state.user = user
                st.rerun()
    if st.button("رجوع"):
        del st.session_state.role
        st.rerun()
    st.stop()

# ================== 4. لوحة تحكم المدير (إصلاح تسجيل الفنيين) ==================
if st.session_state.role == "admin":
    st.sidebar.title("التحكم")
    page = st.sidebar.selectbox("الانتقال إلى", ["📊 الإحصائيات", "👥 العمال والعملاء", "➕ إضافة فني"])
    
    if st.sidebar.button("🚪 خروج"):
        del st.session_state.role
        st.rerun()

    if page == "📊 الإحصائيات":
        total_out = sum(get_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي المبالغ بالخارج", f"{total_out:,.0f} ج.م")

    elif page == "👥 العمال والعملاء":
        with st.form("new_client"):
            st.write("### ➕ إضافة عميل جديد")
            n = st.text_input("اسم العميل")
            p = st.text_input("رقم الهاتف")
            g = st.text_input("📍 رابط GPS (انسخ الرابط من خرائط جوجل)")
            if st.form_submit_button("حفظ العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_all(customers=st.session_state.data)
                st.success(f"تم تسجيل {n}")

    elif page == "➕ إضافة فني":
        st.write("### 🛠️ تسجيل فني جديد في النظام")
        with st.form("tech_reg", clear_on_submit=True):
            t_name = st.text_input("اسم الفني بالكامل")
            t_pass = st.text_input("كلمة مرور الفني")
            if st.form_submit_button("تسجيل الفني الآن"):
                if t_name and t_pass:
                    # إضافة الفني للقائمة
                    st.session_state.techs.append({"name": t_name, "pass": t_pass})
                    # حفظ في الملف فوراً
                    save_all(techs=st.session_state.techs)
                    st.success(f"تم تسجيل الفني {t_name} بنجاح!")
                else:
                    st.error("برجاء ملء البيانات")

# ================== 5. لوحة الفني (مع ميزة الـ GPS) ==================
elif st.session_state.role == "tech_panel":
    st.header(f"مرحباً {st.session_state.user}")
    
    # اختيار العميل
    c_list = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل المطلوب", options=list(c_list.keys()), format_func=lambda x: c_list[x])
    
    target = next((c for c in st.session_state.data if c['id'] == sid), None)
    
    if target:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"👤 العميل: {target['name']}")
            st.write(f"📞 هاتف: {target['phone']}")
        
        with col2:
            # ميزة الـ GPS
            if target.get('gps') and "http" in target['gps']:
                st.link_button("📍 فتح اللوكيشن (GPS)", target['gps'], use_container_width=True)
            else:
                st.warning("⚠️ لا يوجد موقع مسجل لهذا العميل")

        with st.form("visit_form"):
            st.write("📝 تقرير العمل")
            d = st.number_input("تكلفة الصيانة (+)", 0.0)
            p = st.number_input("المبلغ المحصل (-)", 0.0)
            n = st.text_area("ملاحظات")
            if st.form_submit_button("حفظ وإرسال"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": n, "tech": st.session_state.user, "debt": d, "price": p
                })
                save_all(customers=st.session_state.data)
                st.success("تم الحفظ!")

    if st.button("🚪 خروج"):
        del st.session_state.role
        st.rerun()
