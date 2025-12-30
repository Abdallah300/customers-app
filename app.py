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
        border: 2px solid #007bff; border-radius: 15px; padding: 25px; margin-bottom: 20px;
    }
    .history-card { 
        background: rgba(255, 255, 255, 0.07); border-radius: 10px; padding: 15px; 
        margin-top: 10px; border-right: 5px solid #00d4ff; 
    }
    .money-plus { color: #ff4b4b; font-weight: bold; } /* مديونية */
    .money-minus { color: #00ffcc; font-weight: bold; } /* تحصيل */
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. محرك البيانات المطور ==================
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تحميل البيانات وضمان تحديثها
if 'data' not in st.session_state: st.session_state.data = load_data("customers.json")
if 'techs' not in st.session_state: st.session_state.techs = load_data("techs.json")

# دالة حساب الرصيد الدقيق
def calculate_client_balance(history):
    total_debt = sum(float(h.get('debt', 0)) for h in history)
    total_paid = sum(float(h.get('price', 0)) for h in history)
    return total_debt - total_paid

# ================== 3. واجهة العميل (التدقيق المالي) ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        cust = next((c for c in st.session_state.data if c['id'] == c_id), None)
        if cust:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            current_bal = calculate_client_balance(cust.get('history', []))
            
            st.markdown(f"""
            <div class='client-card'>
                <h2 style='text-align:center;'>العميل: {cust['name']}</h2>
                <hr>
                <h3 style='text-align:center;'>الحساب المتبقي: 
                <span style='color: {"#00ffcc" if current_bal <= 0 else "#ff4b4b"}'>{current_bal:,.2f} ج.م</span></h3>
                <p style='text-align:center;'>📅 موعد الصيانة القادم: {cust.get('next_visit', 'قريباً')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📑 كشف حساب العمليات")
            for h in reversed(cust.get('history', [])):
                val = float(h.get('debt', 0)) - float(h.get('price', 0))
                st.markdown(f"""
                <div class="history-card">
                    <b>📅 {h['date']}</b> | 👤 الفني: {h.get('tech', 'الإدارة')}<br>
                    📝 البيان: {h['note']}<br>
                    ➕ مديونية: {h.get('debt', 0)} | ➖ مدفوع: {h.get('price', 0)}<br>
                    🏁 صافي العملية: <b>{val:,.2f} ج.م</b>
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except:
        st.error("خطأ في جلب البيانات")
        st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; padding-top:50px;'>نظام إدارة باور لايف</h2>", unsafe_allow_html=True)
    if st.button("🔑 لوحة المدير"): st.session_state.role = "admin_login"
    if st.button("🛠️ لوحة الفني"): st.session_state.role = "tech_login"
    st.stop()

# (تسهيلاً للكود تم دمج الدخول المباشر للتجربة)
if st.session_state.role == "admin_login":
    if st.text_input("باسورد المدير", type="password") == "1010": 
        if st.button("دخول"): st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    u = st.selectbox("اسم الفني", t_names) if t_names else st.error("لا يوجد فنيين")
    if st.button("دخول"): st.session_state.role = "tech"; st.session_state.user = u; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "📊 تقرير مالي", "🛠️ الفنيين", "🚪 خروج"])
    
    if menu == "👥 العملاء":
        st.header("إدارة العملاء والباركود")
        if st.button("➕ إضافة عميل جديد"):
            new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
            st.session_state.data.append({"id": new_id, "name": f"عميل {new_id}", "history": [], "next_visit": ""})
            save_data("customers.json", st.session_state.data); st.rerun()

        for c in st.session_state.data:
            with st.expander(f"👤 {c['name']} | الحساب: {calculate_client_balance(c.get('history', [])):,.0f}"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    qr_link = f"{BASE_URL}/?id={c['id']}"
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_link}")
                    st.caption("كود صفحة العميل")
                with c2:
                    c['name'] = st.text_input("تعديل الاسم", c['name'], key=f"nm{c['id']}")
                    if st.button("حفظ الاسم", key=f"sv{c['id']}"): 
                        save_data("customers.json", st.session_state.data); st.success("تم")

    elif menu == "📊 تقرير مالي":
        total_d = sum(calculate_client_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي الديون عند العملاء", f"{total_d:,.2f} ج.م")

    elif menu == "🛠️ الفنيين":
        st.subheader("إضافة فني")
        new_t = st.text_input("اسم الفني الجديد")
        if st.button("إضافة"):
            st.session_state.techs.append({"name": new_t, "pass": "123"})
            save_data("techs.json", st.session_state.techs); st.rerun()
        st.table(st.session_state.techs)

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. لوحة الفني (التحديث المالي الدقيق) ==================
elif st.session_state.role == "tech":
    st.header(f"🛠️ الفني: {st.session_state.user}")
    
    c_names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل", options=list(c_names.keys()), format_func=lambda x: c_names[x])
    target = next((c for c in st.session_state.data if c['id'] == sid), None)
    
    if target:
        current_bal = calculate_client_balance(target.get('history', []))
        st.error(f"الحساب المتبقي القديم على العميل: {current_bal:,.2f} ج.م")
        
        with st.form("tech_entry"):
            st.markdown("### سجل زيارة جديدة")
            note = st.text_area("وصف الصيانة (مثلاً: تغيير شمعات 1,2,3)")
            
            col1, col2 = st.columns(2)
            debt_val = col1.number_input("تكلفة الزيارة/القطع (+)", value=0.0)
            paid_val = col2.number_input("المبلغ المحصل الآن (-)", value=0.0)
            
            next_v = st.date_input("موعد الصيانة القادم", value=datetime.now() + timedelta(days=90))
            
            if st.form_submit_button("✅ حفظ وتحديث الحساب فوراً"):
                # إضافة السجل الجديد
                new_entry = {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note,
                    "tech": st.session_state.user,
                    "debt": float(debt_val),
                    "price": float(paid_val)
                }
                
                # البحث عن العميل وتحديث سجلاته
                for c in st.session_state.data:
                    if c['id'] == target['id']:
                        if 'history' not in c: c['history'] = []
                        c['history'].append(new_entry)
                        c['next_visit'] = str(next_v)
                        break
                
                # حفظ البيانات وإعادة التحميل
                save_data("customers.json", st.session_state.data)
                st.success("تم التحديث! الحساب الجديد سيظهر للعميل فوراً.")
                st.rerun()

    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
