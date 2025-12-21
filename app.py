import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق (Power Life Style) ==================
st.set_page_config(page_title="Power Life Dashboard", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-header { background: #001f3f; border-radius: 15px; padding: 20px; border: 2px solid #007bff; text-align: center; }
    .balance-tag { font-size: 20px; font-weight: bold; color: #00ffcc; background: rgba(0, 255, 204, 0.1); padding: 5px 15px; border-radius: 8px; border: 1px solid #00ffcc; }
    .logo-text { font-size: 45px; font-weight: bold; color: #00d4ff; text-align: center; display: block; text-shadow: 2px 2px 10px #007bff; }
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
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة الباركود (صفحة العميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown(f"<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><h2>{c['name']}</h2><div class='balance-tag'>المديونية المتبقية: {bal:,.0f} ج.م</div></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:10px; margin-bottom:5px; border-radius:5px; border-right:3px solid #00d4ff;">📅 {h["date"]} | {h["note"]} | 🛠️ {h.get("tech","")}</div>', unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. تسجيل الدخول ==================
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

# ================== 5. واجهة الإدارة ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## Power Life 💧")
    menu = st.sidebar.radio("التحكم", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بالكود أو الاسم...")
        if search:
            search_clean = search.strip().lower()
            filtered = [c for c in st.session_state.data if (search_clean.isdigit() and str(c['id']) == search_clean) or (not search_clean.isdigit() and (search_clean in c['name'].lower() or search_clean in str(c.get('phone',''))))]
            for c in filtered:
                bal = calculate_balance(c.get('history', []))
                st.markdown(f"### {c['name']} (ID: {c['id']})")
                st.markdown(f"<div class='balance-tag'>الرصيد: {bal:,.0f} ج.م</div>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    with st.expander("📍 تعديل البيانات والـ GPS"):
                        c['name'] = st.text_input("الاسم", c['name'], key=f"n{c['id']}")
                        c['phone'] = st.text_input("الفون", c.get('phone',''), key=f"p{c['id']}")
                        c['gps'] = st.text_input("GPS", c.get('gps',''), key=f"g{c['id']}")
                        if st.button("حفظ", key=f"s{c['id']}"): save_json("customers.json", st.session_state.data); st.success("تم")
                with col2:
                    with st.expander("💸 عملية مالية"):
                        d1 = st.number_input("صيانة (+)", key=f"d{c['id']}"); d2 = st.number_input("تحصيل (-)", key=f"r{c['id']}")
                        note = st.text_input("البيان", key=f"nt{c['id']}")
                        if st.button("تسجيل", key=f"t{c['id']}"):
                            c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": "المدير", "debt": d1, "price": d2})
                            save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "🛠️ تقارير الفنيين":
        st.subheader("🛠️ مراقبة أداء الفنيين والزيارات")
        
        # تجميع كل الزيارات من كل العملاء في جدول واحد للتحليل
        all_visits = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') and h.get('tech') != "المدير":
                    all_visits.append({
                        "الفني": h['tech'],
                        "كود العميل": c['id'],
                        "اسم العميل": c['name'],
                        "التاريخ": h['date'],
                        "البيان (شمع/صيانة)": h['note'],
                        "التكلفة (+)": h.get('debt', 0),
                        "المحصل (-)": h.get('price', 0)
                    })
        
        if all_visits:
            df = pd.DataFrame(all_visits)
            
            # فلاتر البحث في التقارير
            col_f1, col_f2 = st.columns(2)
            tech_filter = col_f1.multiselect("فلتر باسم الفني", df['الفني'].unique())
            if tech_filter: df = df[df['الفني'].isin(tech_filter)]
            
            st.dataframe(df, use_container_width=True)
            
            # ملخص أداء
            st.markdown("---")
            st.subheader("📊 ملخص مالي للفنيين")
            summary = df.groupby('الفني').agg({'التكلفة (+)': 'sum', 'المحصل (-)': 'sum'}).reset_index()
            st.table(summary)
        else:
            st.info("لا توجد زيارات مسجلة بواسطة الفنيين حتى الآن.")
            
        with st.expander("➕ إضافة فني جديد للنظام"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("باسورد"); 
            if st.button("تسجيل الفني"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new"):
            n = st.text_input("الاسم"); p = st.text_input("الفون"); loc = st.text_input("GPS"); d = st.number_input("رصيد سابق")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح", "debt": d, "price": 0}]})
                save_json("customers.json", st.session_state.data); st.success(f"تم! الكود: {new_id}")

    elif menu == "📊 المالية":
        total = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي المديونية في السوق", f"{total:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (إضافة زيارة) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: {st.session_state.current_tech}")
    target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: f"{x['id']} - {x['name']}")
    if target.get('gps'): st.link_button("📍 فتح الخريطة", target['gps'], use_container_width=True)
    with st.form("visit"):
        v_d = st.number_input("تكلفة الشمع/الصيانة", 0.0); v_p = st.number_input("المبلغ المحصل", 0.0); v_n = st.text_area("ماذا تم في الزيارة؟ (مثال: تغيير شمعة 1 و 2)")
        if st.form_submit_button("إرسال التقرير"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": v_n, "tech": st.session_state.current_tech, "debt": v_d, "price": v_p})
            save_json("customers.json", st.session_state.data); st.success("تم الحفظ بنجاح")
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
