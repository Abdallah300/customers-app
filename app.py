import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق (تحسين الواجهة وتجربة المستخدم) ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    .client-card { 
        background: linear-gradient(145deg, #001f3f, #00152b); 
        border: 2px solid #007bff; border-radius: 15px; 
        padding: 25px; margin-bottom: 20px; width: 100%;
        box-shadow: 0px 4px 15px rgba(0,123,255,0.3);
    }
    .history-card { 
        background: rgba(255, 255, 255, 0.05); border-radius: 10px; 
        padding: 15px; margin-bottom: 10px; border-right: 5px solid #00d4ff;
    }
    .tech-badge {
        background: #007bff; color: white; padding: 2px 8px; 
        border-radius: 5px; font-size: 0.8em; margin-right: 5px;
    }
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

# ================== 3. واجهة العميل (الباركود) - تظهر اسم الفني ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-card'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:25px; color:#00ffcc;'>إجمالي المتبقي: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            
            st.markdown("### 📋 سجل الصيانات والمدفوعات")
            for h in reversed(c.get('history', [])):
                tech_name = h.get('tech', 'غير محدد')
                st.markdown(f"""
                <div class="history-card">
                    <b>📅 {h["date"]}</b> | <span class="tech-badge">الفني: {tech_name}</span><br>
                    📝 {h["note"]}<br>
                    💰 المبلغ: {float(h.get("debt",0)) - float(h.get("price",0))} ج.م
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life System 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (نفس منطق تسجيل الدخول السابق)
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
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: 
            st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 البحث والإدارة", "➕ إضافة عميل", "🛠️ مراقبة الفنيين", "📊 التقارير المالية", "🚪 خروج"])

    if menu == "👥 البحث والإدارة":
        search = st.text_input("🔍 ابحث بالاسم أو التليفون...")
        if search:
            for i, c in enumerate(st.session_state.data):
                if search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                    with st.container():
                        st.markdown(f'<div class="client-card">', unsafe_allow_html=True)
                        st.subheader(f"👤 {c['name']}")
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            # تأكد من تغيير الرابط لرابط تطبيقك الفعلي ليعمل الباركود
                            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={st.query_params.get('url', 'https://powerlife.streamlit.app')}?id={c['id']}")
                            if c.get('gps'): st.link_button("📍 موقع العميل", c['gps'])
                            st.write(f"💰 الرصيد الحالي: {calculate_balance(c.get('history', []))} ج.م")
                        with col2:
                            with st.expander("📝 تعديل البيانات"):
                                c['name'] = st.text_input("الاسم", value=c['name'], key=f"n{c['id']}")
                                c['phone'] = st.text_input("التليفون", value=c.get('phone',''), key=f"p{c['id']}")
                                c['gps'] = st.text_input("GPS", value=c.get('gps',''), key=f"g{c['id']}")
                                if st.button("حفظ التعديلات", key=f"s{c['id']}"): save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
                            with st.expander("💸 تسوية حساب"):
                                d1 = st.number_input("إضافة مبلغ عليه (+)", 0.0, key=f"d{c['id']}")
                                d2 = st.number_input("تحصيل مبلغ منه (-)", 0.0, key=f"r{c['id']}")
                                if st.button("تسجيل العملية", key=f"t{c['id']}"):
                                    c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل إداري", "tech": "المدير", "debt": d1, "price": d2})
                                    save_json("customers.json", st.session_state.data); st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ إضافة عميل":
        with st.form("new_cust"):
            name = st.text_input("اسم العميل الجديد")
            phone = st.text_input("رقم التليفون")
            gps = st.text_input("رابط لوكيشن GPS")
            if st.form_submit_button("إضافة العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "gps": gps, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تم الإضافة بنجاح"); st.rerun()

    elif menu == "🛠️ مراقبة الفنيين":
        st.subheader("🛠️ تقارير أداء الفنيين")
        all_ops = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                all_ops.append({"التاريخ": h['date'], "الفني": h.get('tech','-'), "العميل": c['name'], "المحصل": h.get('price', 0), "التكلفة": h.get('debt', 0), "التفاصيل": h.get('note', '')})
        if all_ops: st.table(reversed(all_ops))
        
        st.divider()
        st.write("➕ إدارة حسابات الفنيين")
        tn = st.text_input("اسم الفني الجديد")
        tp = st.text_input("كلمة مرور الفني")
        if st.button("إضافة الفني للنظام"):
            st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()

    elif menu == "📊 التقارير المالية":
        total_m = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        today = datetime.now().strftime("%Y-%m-%d")
        t_coll = sum(sum(float(h.get('price', 0)) for h in c.get('history', []) if today in str(h['date'])) for c in st.session_state.data)
        st.metric("💰 إجمالي المديونات في السوق", f"{total_m:,.0f} ج.م")
        st.metric("🟢 تحصيل اليوم", f"{t_coll:,.0f} ج.m")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني المحدثة (أسرع وأكثر وضوحاً) ==================
elif st.session_state.role == "tech_p":
    st.markdown(f"<h3 style='text-align:right;'>مرحباً فني: {st.session_state.c_tech} 🛠️</h3>", unsafe_allow_html=True)
    
    # اختيار العميل
    target = st.selectbox("🎯 اختر العميل الذي تزوره الآن", st.session_state.data, format_func=lambda x: f"{x['name']} - {x.get('phone','')}")
    
    if target:
        # عرض معلومات سريعة عن العميل للفني
        current_bal = calculate_balance(target.get('history', []))
        col_a, col_b = st.columns(2)
        with col_a:
            st.info(f"💵 حساب العميل الحالي: {current_bal} ج.م")
        with col_b:
            if target.get('gps'): st.link_button("📍 فتح الخريطة", target['gps'], use_container_width=True)
        
        st.divider()
        
        with st.form("tech_visit_v2"):
            st.write("📝 تسجيل تفاصيل الزيارة")
            v_add = st.number_input("تكلفة الصيانة أو قطع الغيار (إضافة للحساب)", 0.0)
            v_rem = st.number_input("المبلغ الذي استلمته كاش (تحصيل)", 0.0)
            
            st.write("🧼 الشمع المستبدل:")
            sh1, sh2, sh3 = st.columns(3)
            s1 = sh1.checkbox("شمعة 1")
            s2 = sh2.checkbox("شمعة 2")
            s3 = sh3.checkbox("شمعة 3")
            s4, s5, s6, s7 = st.columns(4)
            s4_v = s4.checkbox("4")
            s5_v = s5.checkbox("5")
            s6_v = s6.checkbox("6")
            s7_v = s7.checkbox("7")
            
            note = st.text_area("ملاحظات فنية أخرى (مثل: تغيير موتور، إصلاح تسريب...)")
            
            if st.form_submit_button("✅ حفظ الزيارة وإرسال التقرير"):
                selected_filters = [i for i, val in enumerate([s1, s2, s3, s4_v, s5_v, s6_v, s7_v], 1) if val]
                filter_text = f"تم تغيير شمع: {selected_filters}" if selected_filters else "صيانة عامة"
                full_note = f"{filter_text} | {note}"
                
                # تحديث البيانات
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x.setdefault('history', []).append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": full_note,
                            "tech": st.session_state.c_tech, # حفظ اسم الفني في السجل
                            "debt": v_add,
                            "price": v_rem
                        })
                
                save_json("customers.json", st.session_state.data)
                st.success(f"تم تسجيل الزيارة بنجاح يا {st.session_state.c_tech}!")
                st.balloons()

    if st.sidebar.button("🚪 تسجيل الخروج"): del st.session_state.role; st.rerun()
