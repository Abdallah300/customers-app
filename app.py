import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-header { background: linear-gradient(135deg, #001f3f 0%, #000b1a 100%); border-radius: 20px; padding: 25px; border: 1px solid #007bff; text-align: center; margin-bottom: 30px; }
    .balance-tag { font-size: 26px; font-weight: bold; color: #00ffcc; background: rgba(0, 255, 204, 0.1); padding: 10px 20px; border-radius: 12px; border: 1px solid #00ffcc; display: inline-block; }
    .after-op-bal { background: rgba(0, 212, 255, 0.1); border: 1px dashed #00d4ff; border-radius: 10px; padding: 10px; margin-top: 10px; color: #00d4ff; font-weight: bold; font-size: 16px; text-align: center; }
    .logo-text { font-size: 45px; font-weight: bold; color: #00d4ff; text-align: center; display: block; text-shadow: 2px 2px 10px #007bff; padding: 10px; }
    header, footer {visibility: hidden;}
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
    try: return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
    except: return 0.0

# ================== 3. واجهة الباركود (العميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
            total_bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><h2 style='color:white;'>مرحباً بك: {c['name']}</h2><div class='balance-tag'>إجمالي المتبقي: {total_bal:,.0f} ج.م</div></div>", unsafe_allow_html=True)
            
            running_balance = 0
            history_with_bal = []
            for h in c.get('history', []):
                running_balance += (float(h.get('debt', 0)) - float(h.get('price', 0)))
                h_copy = h.copy(); h_copy['running_bal'] = running_balance
                history_with_bal.append(h_copy)
            
            for h in reversed(history_with_bal):
                p, d = float(h.get('price', 0)), float(h.get('debt', 0))
                with st.container():
                    st.write(f"📅 {h.get('date','')}")
                    st.write(f"📝 {h.get('note','-')}")
                    if p > 0: st.success(f"💰 تم دفع: {p:,.0f} ج.م")
                    if d > 0: st.error(f"🛠️ تكلفة: {d:,.0f} ج.م")
                    st.markdown(f"<div class='after-op-bal'>المتبقي بعد العملية: {h['running_bal']:,.0f} ج.م</div>", unsafe_allow_html=True)
                    st.markdown("---")
            st.stop()
    except: st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_names) if t_names else st.error("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech_data = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech_data['pass']: st.session_state.role = "tech_panel"; st.session_state.current_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الإدارة (المالية الجديدة) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## Power Life 💧")
    menu = st.sidebar.radio("التحكم", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث...")
        if search:
            s_clean = search.strip().lower()
            filtered = [c for c in st.session_state.data if (s_clean.isdigit() and str(c['id']) == s_clean) or (not s_clean.isdigit() and (s_clean in c['name'].lower() or s_clean in str(c.get('phone',''))))]
            for c in filtered:
                bal = calculate_balance(c.get('history', []))
                st.info(f"👤 {c['name']} | كود: {c['id']} | الرصيد: {bal:,.0f} ج.م")
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    with st.expander("⚙️ تعديل البيانات"):
                        c['name'] = st.text_input("الاسم", c['name'], key=f"un{c['id']}")
                        c['phone'] = st.text_input("الفون", c.get('phone',''), key=f"up{c['id']}")
                        c['gps'] = st.text_input("GPS", c.get('gps',''), key=f"ug{c['id']}")
                        if st.button("حفظ", key=f"us{c['id']}"): save_json("customers.json", st.session_state.data); st.success("تم")
                with col2:
                    with st.expander("💸 عملية جديدة"):
                        d1 = st.number_input("صيانة (+)", key=f"d{c['id']}"); d2 = st.number_input("تحصيل (-)", key=f"r{c['id']}")
                        note = st.text_input("البيان", key=f"nt{c['id']}")
                        if st.button("حفظ", key=f"t{c['id']}"):
                            c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": "المدير", "debt": d1, "price": d2})
                            save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "📊 المالية":
        st.subheader("📊 التقرير المالي العام للمؤسسة")
        
        # حسابات مالية دقيقة
        total_out = 0.0    # ديون بره
        total_income = 0.0 # كل اللي دخل الشركة
        total_services = 0.0 # قيمة الخدمات اللي قدمناها
        
        for c in st.session_state.data:
            hists = c.get('history', [])
            total_out += calculate_balance(hists)
            total_income += sum(float(h.get('price', 0)) for h in hists)
            total_services += sum(float(h.get('debt', 0)) for h in hists)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("إجمالي المديونية (لينا بره)", f"{total_out:,.0f} ج.م", delta_color="inverse")
        m2.metric("إجمالي الدخل (المحصل فعلياً)", f"{total_income:,.0f} ج.م")
        m3.metric("صافي القيمة السوقية", f"{(total_income + total_out):,.0f} ج.م")
        
        st.write("---")
        # إضافة رسم بياني بسيط أو تفصيل إضافي
        st.subheader("💰 تحليل الأرباح")
        estimated_profit = total_income - (total_services * 0.4) # افتراضي أن التكلفة 40% والباقي مكسب
        st.write(f"بناءً على العمليات المسجلة، إجمالي مبيعات الخدمات والقطع هو: **{total_services:,.0f} ج.م**")
        st.info(f"إجمالي المبالغ التي تم تحصيلها في خزينة الشركة هي: **{total_income:,.0f} ج.م**")

    elif menu == "🛠️ تقارير الفنيين":
        all_visits = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') and h.get('tech') != "المدير":
                    all_visits.append({"الفني": h['tech'], "العميل": c['name'], "التاريخ": h['date'], "المحصل": h.get('price', 0)})
        if all_visits:
            df = pd.DataFrame(all_visits)
            st.table(df)
            st.table(df.groupby('الفني')['المحصل'].sum().reset_index())
        with st.expander("➕ إضافة فني"):
            tn = st.text_input("الاسم"); tp = st.text_input("الباسورد")
            if st.button("حفظ"): st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new"):
            n = st.text_input("الاسم"); p = st.text_input("التليفون"); loc = st.text_input("GPS"); d = st.number_input("مديونية سابقة")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم! الكود: {new_id}")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️: {st.session_state.current_tech}")
    target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: f"{x['id']} - {x['name']}")
    if target.get('gps'): st.link_button("📍 موقع العميل", target['gps'])
    with st.form("visit"):
        v_d, v_p, v_n = st.number_input("التكلفة"), st.number_input("المحصل"), st.text_area("البيان")
        if st.form_submit_button("إرسال"):
            for x in st.session_state.data:
                if x['id'] == target['id']: x.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": v_n, "tech": st.session_state.current_tech, "debt": v_d, "price": v_p})
            save_json("customers.json", st.session_state.data); st.success("تم")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
