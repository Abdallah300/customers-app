import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق (Responsive Design) ==================
st.set_page_config(page_title="Power Life System Pro", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    .client-card { 
        background: #001f3f; border: 2px solid #007bff; 
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        width: 100%; box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .history-card { 
        background: rgba(0, 80, 155, 0.2); border-radius: 10px; 
        padding: 15px; margin-bottom: 10px; border-right: 5px solid #00d4ff; 
    }
    .tech-tag { background: #e63946; color: white; padding: 3px 10px; border-radius: 5px; font-size: 14px; font-weight: bold; }
    .part-tag { background: #28a745; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left: 2px; }
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

# ================== 3. واجهة العميل (بعد مسح الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-card'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:22px; color:#00ffcc;'>المديونية المتبقية: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            
            st.subheader("📋 سجل الزيارات الفنية")
            for h in reversed(c.get('history', [])):
                parts_html = "".join([f'<span class="part-tag">{p}</span>' for p in h.get('parts', [])])
                st.markdown(f"""
                    <div class="history-card">
                        <div style="display:flex; justify-content:space-between;">
                            <b>📅 {h['date']}</b>
                            <span class="tech-tag">الفني: {h.get('tech','المدير')}</span>
                        </div>
                        <div style="margin-top:10px;">🛠️ {parts_html if parts_html else "تحصيل/فحص"}</div>
                        <div style="margin-top:5px;">📝 {h.get('note','')}</div>
                        <div style="margin-top:5px; color:#00d4ff; font-weight:bold; text-align:left;">المتبقي بعد هذه العملية: {calculate_balance(c['history'][:c['history'].index(h)+1]):,.0f} ج.م</div>
                    </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life Control 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 لوحة المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_list) if t_list else st.error("لا يوجد فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']: st.session_state.role = "tech_panel"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة (البحث والرقابة) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "🛠️ مراقبة الفنيين", "📊 التقارير المالية", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بـ (الاسم أو الكود أو رقم التليفون)...")
        if search:
            for i, c in enumerate(st.session_state.data):
                # البحث الثلاثي
                match_id = str(c['id']) == search
                match_name = search.lower() in c['name'].lower()
                match_phone = search in str(c.get('phone',''))
                
                if match_id or match_name or match_phone:
                    with st.container():
                        st.markdown('<div class="client-card">', unsafe_allow_html=True)
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                            st.write(f"🆔 كود العميل: {c['id']}")
                        with col2:
                            st.subheader(f"👤 {c['name']}")
                            st.info(f"💰 المديونية: {calculate_balance(c.get('history', [])):,.0f} ج.م")
                            with st.expander("📝 تعديل البيانات"):
                                c['name'] = st.text_input("الاسم", c['name'], key=f"n{c['id']}")
                                c['phone'] = st.text_input("التليفون", c.get('phone',''), key=f"p{c['id']}")
                                if st.button("حفظ", key=f"s{c['id']}"): save_json("customers.json", st.session_state.data); st.success("تم")
                            if st.button("🗑️ حذف", key=f"d{c['id']}", type="primary"):
                                st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            with st.form("new_c"):
                st.write("➕ إضافة عميل جديد")
                n = st.text_input("الاسم"); p_val = st.text_input("رقم التليفون"); d_val = st.number_input("افتتاحي", 0.0)
                if st.form_submit_button("إضافة"):
                    new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                    st.session_state.data.append({"id": new_id, "name": n, "phone": p_val, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "tech": "المدير", "debt": d_val, "price": 0, "parts": []}]})
                    save_json("customers.json", st.session_state.data); st.rerun()

    elif menu == "🛠️ مراقبة الفنيين":
        st.subheader("📋 تقارير الفنيين")
        all_reps = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') and h['tech'] != "المدير":
                    all_reps.append({"الفني": h['tech'], "العميل": c['name'], "التاريخ": h['date'], "المحصل": h.get('price', 0), "القطع": ", ".join(h.get('parts', []))})
        if all_reps: st.table(all_reps)
        
        st.divider()
        with st.form("add_t"):
            st.write("➕ تسجيل فني")
            tn = st.text_input("الاسم"); tp = st.text_input("السر")
            if st.form_submit_button("حفظ"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.success("تم")

    elif menu == "📊 التقارير المالية":
        total_m = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        today = datetime.now().strftime("%Y-%m-%d")
        t_coll = sum(sum(float(h.get('price', 0)) for h in c.get('history', []) if today in str(h['date'])) for c in st.session_state.data)
        st.metric("💰 إجمالي ديون السوق", f"{total_m:,.0f} ج.م")
        st.metric("🟢 تحصيل اليوم", f"{t_coll:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (تسجيل الصيانة + التحصيل) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.title(f"🛠️ الفني: {st.session_state.c_tech}")
    target = st.selectbox("اختر العميل للزيارة", st.session_state.data, format_func=lambda x: f"{x['id']} - {x['name']}")
    
    with st.form("tech_visit"):
        st.subheader("📝 تسجيل صيانة")
        c1, c2, c3 = st.columns(3)
        with c1: s1 = st.checkbox("ش1"); s2 = st.checkbox("ش2"); s3 = st.checkbox("ش3")
        with c2: s4 = st.checkbox("الممبرين"); s5 = st.checkbox("ش5"); s6 = st.checkbox("ش6")
        with c3: s7 = st.checkbox("ش7"); mot = st.checkbox("موتور"); tnk = st.checkbox("خزان")
        
        v_debt = st.number_input("تكلفة الزيارة", 0.0)
        v_price = st.number_input("المبلغ المحصل", 0.0)
        note = st.text_area("ملاحظات")
        
        if st.form_submit_button("حفظ التقرير"):
            selected_parts = []
            if s1: selected_parts.append("ش1"); if s2: selected_parts.append("ش2"); if s3: selected_parts.append("ش3")
            if s4: selected_parts.append("الممبرين"); if s5: selected_parts.append("ش5"); if s6: selected_parts.append("ش6")
            if s7: selected_parts.append("ش7"); if mot: selected_parts.append("موتور"); if tnk: selected_parts.append("خزان")
            
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x.setdefault('history', []).append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "tech": st.session_state.c_tech, # حفظ اسم الفني بدقة هنا
                        "parts": selected_parts,
                        "note": note,
                        "debt": v_debt,
                        "price": v_price
                    })
            save_json("customers.json", st.session_state.data); st.success(f"تم الحفظ بنجاح بواسطة {st.session_state.c_tech}")
            
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
