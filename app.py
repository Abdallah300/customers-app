import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime

# ================== 1. إعدادات المظهر المطور ==================
st.set_page_config(page_title="Power Life Pro v2", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; background-color: #0e1117; }
    * { font-family: 'Cairo', sans-serif; }
    
    /* كروت الإحصائيات */
    .metric-card {
        background: linear-gradient(135deg, #001529 0%, #003366 100%);
        border-radius: 15px; padding: 20px; border: 1px solid #0056b3;
        text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* تنسيق الجداول والكروت */
    .stExpander { border-radius: 10px !important; border: 1px solid #1e293b !important; margin-bottom: 10px; }
    .status-debt { color: #ff4b4b; font-weight: bold; }
    .status-paid { color: #00eb93; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================== 2. محرك البيانات ==================
def load_data():
    customers = []
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            try: customers = json.load(f)
            except: customers = []
    techs = []
    if os.path.exists("techs.json"):
        with open("techs.json", "r", encoding="utf-8") as f:
            try: techs = json.load(f)
            except: techs = []
    return customers, techs

def save_all(customers=None, techs=None):
    if customers is not None:
        with open("customers.json", "w", encoding="utf-8") as f:
            json.dump(customers, f, ensure_ascii=False, indent=2)
    if techs is not None:
        with open("techs.json", "w", encoding="utf-8") as f:
            json.dump(techs, f, ensure_ascii=False, indent=2)

# تحميل البيانات في الحالة (Session State)
if 'data' not in st.session_state:
    st.session_state.data, st.session_state.techs = load_data()

def get_balance(history):
    debt = sum(float(h.get('debt', 0)) for h in history)
    paid = sum(float(h.get('price', 0)) for h in history)
    return debt - paid

# ================== 3. واجهة العميل (الباركود) ==================
if "id" in st.query_params:
    cid = int(st.query_params["id"])
    cust = next((c for c in st.session_state.data if c['id'] == cid), None)
    if cust:
        st.markdown(f"<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
        bal = get_balance(cust.get('history', []))
        st.markdown(f"""
            <div class='metric-card'>
                <h3>أهلاً، {cust['name']}</h3>
                <h1 style='color: {"#ff4b4b" if bal > 0 else "#00eb93"}'>{bal:,.0f} ج.م</h1>
                <p>إجمالي الحساب المتبقي</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📑 سجل العمليات الأخير")
        for h in reversed(cust.get('history', [])):
            with st.container():
                st.info(f"📅 {h['date']} | 🛠️ {h['tech']} \n\n 📝 {h['note']} \n\n 💰 القيمة: {float(h['debt'])-float(h['price'])} ج.م")
    st.stop()

# ================== 4. نظام تسجيل الدخول ==================
if "role" not in st.session_state:
    st.title("⚡ Power Life Pro v2")
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

# --- حماية الدخول ---
if st.session_state.role == "admin_auth":
    pw = st.text_input("كلمة مرور المدير", type="password")
    if st.button("دخول"):
        if pw == "admin123":
            st.session_state.role = "admin"
            st.rerun()
    if st.button("رجوع"):
        del st.session_state.role
        st.rerun()
    st.stop()

if st.session_state.role == "tech_auth":
    t_names = [t['name'] for t in st.session_state.techs]
    user = st.selectbox("اختر اسمك", t_names) if t_names else st.error("لا يوجد فنيين مسجلين")
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

# ================== 5. لوحة تحكم المدير (المطورة) ==================
if st.session_state.role == "admin":
    st.sidebar.title("التحكم الذكي")
    page = st.sidebar.selectbox("الانتقال إلى", ["📊 لوحة المعلومات", "👥 إدارة العملاء", "🛠️ إدارة الفنيين"])
    
    if st.sidebar.button("🚪 تسجيل الخروج"):
        del st.session_state.role
        st.rerun()

    if page == "📊 لوحة المعلومات":
        st.header("📊 ملخص حالة العمل")
        # حسابات سريعة
        total_out = sum(get_balance(c.get('history', [])) for c in st.session_state.data)
        total_cust = len(st.session_state.data)
        
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("إجمالي الديون بالخارج", f"{total_out:,.0f} ج.م")
        with c2: st.metric("عدد العملاء", total_cust)
        with c3: st.metric("عمليات الشهر", "قيد الحساب")

        # عرض سريع للعملاء الأكثر مديونية
        st.subheader("⚠️ عملاء عليهم مبالغ مرتفعة")
        top_debtors = sorted(st.session_state.data, key=lambda x: get_balance(x.get('history', [])), reverse=True)[:5]
        for td in top_debtors:
            b = get_balance(td.get('history', []))
            if b > 0:
                st.warning(f"العميل: {td['name']} | المبلغ: {b:,.0f} ج.م")

    elif page == "👥 إدارة العملاء":
        st.header("👥 قاعدة بيانات العملاء")
        tab1, tab2 = st.tabs(["بحث وتعديل", "➕ إضافة عميل جديد"])
        
        with tab1:
            search = st.text_input("🔍 ابحث بالاسم أو رقم التليفون")
            for c in st.session_state.data:
                if not search or search in c['name'] or search in str(c['phone']):
                    bal = get_balance(c.get('history', []))
                    with st.expander(f"👤 {c['name']} (الحساب: {bal:,.0f} ج.م)"):
                        col_a, col_b = st.columns([2, 1])
                        with col_a:
                            st.write(f"📞 التليفون: {c['phone']}")
                            if c.get('gps'): st.link_button("📍 موقع العميل", c['gps'])
                        with col_b:
                            # توليد رابط الباركود
                            link = f"https://{st.query_params.get('host', 'yourapp')}.streamlit.app/?id={c['id']}"
                            st.write("🔗 رابط العميل المباشر")
                            st.code(link)
                        
                        st.divider()
                        # إضافة عملية إدارية
                        with st.form(f"admin_action_{c['id']}"):
                            st.write("➕ إضافة عملية (صيانة / تحصيل)")
                            c1, c2 = st.columns(2)
                            d = c1.number_input("مبلغ مستحق (+)", 0.0)
                            p = c2.number_input("مبلغ محصل (-)", 0.0)
                            n = st.text_input("ملاحظات العملية")
                            if st.form_submit_button("تحديث الحساب"):
                                c.setdefault('history', []).append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "note": n, "tech": "المدير", "debt": d, "price": p
                                })
                                save_all(customers=st.session_state.data)
                                st.success("تم التحديث!")
                                st.rerun()

        with tab2:
            with st.form("new_client"):
                n = st.text_input("اسم العميل")
                p = st.text_input("رقم الهاتف")
                g = st.text_input("رابط لوكيشن جوجل")
                if st.form_submit_button("إضافة العميل"):
                    new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                    st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                    save_all(customers=st.session_state.data)
                    st.success("تم الحفظ!")

    elif page == "🛠️ إدارة الفنيين":
        st.header("🛠️ إدارة الطاقم")
        # كود إضافة فني وعرض تقاريرهم
        with st.form("add_tech"):
            name = st.text_input("اسم الفني")
            code = st.text_input("كلمة مرور الفني")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": name, "pass": code})
                save_all(techs=st.session_state.techs)
                st.rerun()

# ================== 6. لوحة الفني (السرعة هي الأهم) ==================
elif st.session_state.role == "tech_panel":
    st.header(f"مرحباً، {st.session_state.user} 🛠️")
    if st.button("🚪 خروج"):
        del st.session_state.role
        st.rerun()
        
    st.divider()
    # اختيار عميل سريع
    names = {c['id']: f"{c['name']} (📞 {c['phone']})" for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل الذي تزوره الآن", options=list(names.keys()), format_func=lambda x: names[x])
    
    target = next((c for c in st.session_state.data if c['id'] == sid), None)
    
    if target:
        st.markdown(f"### 📍 العميل: {target['name']}")
        if target.get('gps'):
            st.link_button("🚀 فتح الخريطة للتوجه للعميل", target['gps'], use_container_width=True)
            
        bal = get_balance(target.get('history', []))
        st.info(f"💰 حساب العميل الحالي المتبقي: {bal:,.0f} ج.م")
        
        with st.form("visit_report"):
            st.write("📝 تقرير الزيارة")
            v_debt = st.number_input("تكلفة الزيارة / قطع الغيار (+)", 0.0)
            v_paid = st.number_input("المبلغ الذي قبضته من العميل (-)", 0.0)
            v_note = st.text_area("ماذا فعلت في هذه الزيارة؟")
            
            if st.form_submit_button("✅ إرسال التقرير وحفظ"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": v_note,
                    "tech": st.session_state.user,
                    "debt": v_debt,
                    "price": v_paid
                })
                save_all(customers=st.session_state.data)
                st.success("تم تسجيل العملية بنجاح!")
                st.balloons()
