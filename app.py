import streamlit as st
import json
import os
from datetime import datetime, timedelta

# ================== 1. الإعدادات والرابط ==================
BASE_URL = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"

st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; background-color: #000b1a; }
    * { font-family: 'Cairo', sans-serif; text-align: right; color: white; }
    .client-card { 
        background: linear-gradient(145deg, #001f3f, #001529); 
        border: 1px solid #007bff; border-radius: 15px; padding: 20px; margin-bottom: 20px;
    }
    .history-card { 
        background: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 12px; 
        margin-top: 8px; border-right: 4px solid #00d4ff; 
    }
    .tech-name { color: #00ffcc; font-weight: bold; font-size: 0.9em; }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_data(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_data("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_data("techs.json", [])

def get_bal(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (المحدثة) ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        cust = next((c for c in st.session_state.data if c['id'] == c_id), None)
        if cust:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            balance = get_bal(cust.get('history', []))
            
            st.markdown(f"""
            <div class='client-card'>
                <h2 style='text-align:center;'>{cust['name']}</h2>
                <h3 style='text-align:center; color: #ff4b4b;'>المتبقي: {balance:,.0f} ج.م</h3>
                <p style='text-align:center;'>📅 موعد الصيانة القادم: {cust.get('next_visit', 'قريباً')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📜 سجل الصيانات والتحصيل")
            for h in reversed(cust.get('history', [])):
                # هنا يظهر اسم الفني في صفحة العميل
                tech_display = f"بواسطة: {h.get('tech', 'الإدارة')}"
                st.markdown(f"""
                <div class="history-card">
                    <b>📅 {h['date']}</b> | <span class="tech-name">🛠️ {tech_display}</span><br>
                    📝 {h['note']}<br>
                    💰 القيمة: {float(h.get('debt',0)) - float(h.get('price',0))} ج.م
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except:
        st.error("رابط غير صالح")
        st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; padding-top:50px;'>نظام المتابعة الذكي</h1>", unsafe_allow_html=True)
    if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_auth"
    if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_auth"
    st.stop()

if st.session_state.role == "admin_auth":
    pw = st.text_input("باسورد المدير", type="password")
    if st.button("دخول"):
        if pw == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_auth":
    t_names = [t['name'] for t in st.session_state.techs]
    u = st.selectbox("اختر اسمك", t_names) if t_names else st.error("لا يوجد فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول الفني"):
        tech = next((t for t in st.session_state.techs if t['name'] == u), None)
        if tech and tech['pass'] == p:
            st.session_state.role = "tech_p"; st.session_state.user = u; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "🛠️ الفنيين", "🚪 خروج"])
    
    if menu == "👥 العملاء":
        st.header("إدارة العملاء")
        if st.button("➕ إضافة عميل"):
            new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
            st.session_state.data.append({"id": new_id, "name": "عميل جديد", "history": [], "next_visit": ""})
            save_data("customers.json", st.session_state.data); st.rerun()

        for c in st.session_state.data:
            with st.expander(f"👤 {c['name']} (الحساب: {get_bal(c.get('history', []))})"):
                personal_link = f"{BASE_URL}/?id={c['id']}"
                st.code(personal_link)
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={personal_link}")
                c['name'] = st.text_input("الاسم", c['name'], key=f"n{c['id']}")
                c['phone'] = st.text_input("الهاتف", c.get('phone',''), key=f"p{c['id']}")
                if st.button("حفظ", key=f"s{c['id']}"): 
                    save_data("customers.json", st.session_state.data); st.success("تم")

    elif menu == "🛠️ الفنيين":
        st.header("إضافة فني")
        with st.form("add_tech"):
            tn = st.text_input("الاسم"); tp = st.text_input("السر")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_data("techs.json", st.session_state.techs); st.rerun()
        st.table(st.session_state.techs)

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. لوحة الفني (الربط التلقائي) ==================
elif st.session_state.role == "tech_p":
    st.header(f"🛠️ الفني: {st.session_state.user}")
    
    c_names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل", options=list(c_names.keys()), format_func=lambda x: c_names[x])
    target = next((c for c in st.session_state.data if c['id'] == sid), None)
    
    if target:
        st.warning(f"الحساب الحالي على العميل: {get_bal(target.get('history', []))} ج.م")
        
        with st.form("visit_report"):
            st.subheader("تقرير الزيارة")
            task = st.text_area("ماذا فعلت؟ (مثال: تغيير شمعات 1و2و3)")
            
            col1, col2 = st.columns(2)
            add_debt = col1.number_input("تكلفة الصيانة/القطع (+)", min_value=0.0)
            payment = col2.number_input("المبلغ المحصل من العميل (-)", min_value=0.0)
            
            next_visit = st.date_input("موعد الصيانة القادم", value=datetime.now() + timedelta(days=90))
            
            if st.form_submit_button("✅ إرسال التقرير وتحديث صفحة العميل"):
                # تسجيل العملية وربطها باسم الفني الحالي تلقائياً
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": task,
                    "tech": st.session_state.user, # هنا يتم حفظ اسم الفني
                    "debt": add_debt,
                    "price": payment
                })
                target['next_visit'] = str(next_visit)
                
                save_data("customers.json", st.session_state.data)
                st.success("تم تحديث حساب العميل بنجاح!")
                st.balloons()

    if st.button("🚪 تسجيل خروج"): del st.session_state.role; st.rerun()
