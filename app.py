import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات المظهر (إصلاح التمرير الكامل) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* السماح بالتمرير بشكل مطلق وإلغاء أي قيود */
    html, body, [data-testid="stsidebar"] {
        overflow: auto !important;
    }
    
    .stApp { 
        background: #000b1a; 
        color: #ffffff;
    }
    
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* كارت العميل */
    .client-header { 
        background: #001f3f; border-radius: 15px; 
        padding: 20px; border: 2px solid #007bff; margin-bottom: 25px; 
    }
    
    /* إخفاء الهيدر لزيادة مساحة الرؤية */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* جعل السكرول بار واضح وسهل الاستخدام */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #000b1a; }
    ::-webkit-scrollbar-thumb { background: #007bff; border-radius: 5px; border: 1px solid #ffffff; }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة الباركود (صفحة العميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            current_bal = calculate_balance(c.get('history', []))

            st.markdown(f"""
            <div class='client-header'>
                <div style='font-size:18px;'>👤 <b>العميل:</b> {c['name']}</div>
                <div style='font-size:15px; color:#00d4ff;'>📍 {c.get('gov', '---')} | 🏛️ {c.get('branch', '---')}</div>
                <hr style='border: 0.5px solid #007bff; opacity: 0.3;'>
                <div style='text-align:center;'>
                    <p style='margin:0;'>إجمالي المديونية الحالية</p>
                    <p style='font-size:35px; color:#00ffcc; font-weight:bold; margin:0;'>{current_bal:,.0f} ج.م</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("📋 سجل الحركات المالي التفصيلي")

            if c.get('history'):
                running_balance = 0
                history_with_balance = []
                for h in c['history']:
                    running_balance += (float(h.get('debt', 0)) - float(h.get('price', 0)))
                    h_copy = h.copy()
                    h_copy['after_bal'] = running_balance
                    history_with_balance.append(h_copy)

                for h in reversed(history_with_balance):
                    with st.container():
                        st.markdown("---")
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.markdown(f"**📝 {h.get('note', 'عملية مالية')}**")
                            if float(h.get('debt', 0)) > 0: st.markdown(f"🔴 مضاف للحساب: `{h.get('debt')} ج.م`")
                            if float(h.get('price', 0)) > 0: st.markdown(f"🟢 مبلغ محصل: `{h.get('price')} ج.م`")
                        with col2:
                            st.markdown(f"📅 `{h.get('date', '---')}`")
                            st.markdown(f"👤 `{h.get('tech', 'الإدارة')}`")

                        st.info(f"💰 المديونية بعد العملية: {h['after_bal']:,.0f} ج.م")
            else:
                st.info("لا توجد عمليات مسجلة.")
            st.stop()
    except:
        st.stop()

# ================== 4. لوحة التحكم (الدخول) ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life Control 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 لوحة الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ لوحة الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر الفني", t_list) if t_list else st.error("لا يوجد فنيين")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech"; st.session_state.tech_name = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الإدارة الكاملة ==================
if st.session_state.role == "admin":
    st.sidebar.title("💎 لوحة الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "📊 الحسابات", "🛠️ الفنيين", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم...")
        # تأكد من عرض كل العملاء مع إمكانية التمرير
        for i, c in enumerate(st.session_state.data):
            if search in c['name']:
                with st.expander(f"👤 {c['name']} (حساب: {calculate_balance(c.get('history', []))})"):
                    with st.form(f"adm_f_{c['id']}"):
                        c['gov'] = st.text_input("المحافظة", value=c.get('gov', ''))
                        c['branch'] = st.text_input("الفرع", value=c.get('branch', ''))
                        a_add = st.number_input("إضافة مديونية (+)", min_value=0.0)
                        a_rem = st.number_input("خصم مبلغ (تحصيل) (-)", min_value=0.0)
                        note = st.text_input("بيان العملية", value="تسويه إدارية")
                        if st.form_submit_button("حفظ الحركات"):
                            if a_add > 0 or a_rem > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": "الإدارة", "debt": a_add, "price": a_rem})
                            save_json("customers.json", st.session_state.data); st.success("تم الحفظ"); st.rerun()
                    if st.button("🖼️ إظهار الباركود", key=f"qr_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")

    elif menu == "➕ إضافة عميل":
        with st.form("new_c_form"):
            n = st.text_input("اسم العميل الجديد")
            g = st.text_input("المحافظة")
            b = st.text_input("الفرع")
            d = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("إضافة للسيستم"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "gov": g, "branch": b,
                                             "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "debt": d, "price": 0}] if d > 0 else []})
                save_json("customers.json", st.session_state.data); st.success("تمت الإضافة بنجاح")

    elif menu == "📊 الحسابات":
        total = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي مديونيات السوق", f"{total:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني الكاملة ==================
elif st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ {st.session_state.tech_name}")
    target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: x['name'])
    with st.form("tech_visit_form"):
        v_add = st.number_input("تكلفة الصيانة", min_value=0.0)
        v_rem = st.number_input("المبلغ المحصل", min_value=0.0)
        note = st.text_area("وصف الزيارة")
        if st.form_submit_button("حفظ الزيارة"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                         "note": note, "tech": st.session_state.tech_name, "debt": v_add, "price": v_rem})
            save_json("customers.json", st.session_state.data); st.success("تم حفظ البيانات")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
