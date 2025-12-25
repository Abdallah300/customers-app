import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق العام (UI/UX) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

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
    .tech-tag { background: #007bff; color: white; padding: 4px 10px; border-radius: 8px; font-size: 14px; font-weight: bold; }
    .part-tag { background: #28a745; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left: 2px; }
    .money-row { display: flex; justify-content: space-between; margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1); }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات (Storage) ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تحميل البيانات في الجلسة
if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance_at_step(history, index):
    """حساب المديونية التراكمية في لحظة معينة من السجل"""
    sub_history = history[:index+1]
    return sum(float(h.get('debt', 0)) for h in sub_history) - sum(float(h.get('price', 0)) for h in sub_history)

# ================== 3. واجهة العميل (بعد مسح الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            history = c.get('history', [])
            total_bal = sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
            
            st.markdown(f"""
                <div class='client-card'>
                    <h2 style='text-align:center;'>{c['name']}</h2>
                    <p style='text-align:center; font-size:24px; color:#00ffcc;'>إجمالي المتبقي: {total_bal:,.0f} ج.م</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📋 سجل الصيانة والمدفوعات")
            for i in range(len(history)-1, -1, -1):
                h = history[i]
                parts_html = "".join([f'<span class="part-tag">{p}</span>' for p in h.get('parts', [])])
                running_bal = calculate_balance_at_step(history, i)
                st.markdown(f"""
                    <div class="history-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <b>📅 {h['date']}</b>
                            <span class="tech-tag">الفني: {h.get('tech','غير مسجل')}</span>
                        </div>
                        <div style="margin-top:10px;">🛠️ <b>القطع:</b> {parts_html if parts_html else "زيارة متابعة/تحصيل"}</div>
                        <div style="margin-top:5px;">📝 <b>ملاحظة:</b> {h.get('note','')}</div>
                        <div class="money-row">
                            <span>💸 تكلفة: {h.get('debt',0)}</span>
                            <span>✅ دفع: {h.get('price',0)}</span>
                            <span style="color:#00ffcc; font-weight:bold;">📉 متبقي: {running_bal:,.0f} ج.م</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            st.stop()
    except Exception as e:
        st.error(f"خطأ في الرابط: {e}")
        st.stop()

# ================== 4. نظام تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>نظام إدارة القوة 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 لوحة المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول للنظام"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
        else: st.error("بيانات خاطئة")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_names) if t_names else st.error("لا يوجد فنيين مسجلين")
    p = st.text_input("باسورد الفني", type="password")
    if st.button("دخول"):
        tech = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech['pass']:
            st.session_state.role = "tech_panel"
            st.session_state.c_tech = t_user
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة (المدير) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة الرئيسية", ["👥 إدارة العملاء", "🛠️ مراقبة الفنيين", "📊 التقارير المالية", "🚪 تسجيل خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث بالاسم أو التليفون...")
        
        # إضافة عميل جديد
        with st.expander("➕ إضافة عميل جديد"):
            with st.form("add_new_cust"):
                n = st.text_input("اسم العميل"); p = st.text_input("رقم التليفون"); loc = st.text_input("رابط GPS"); d = st.number_input("المديونية الافتتاحية", 0.0)
                if st.form_submit_button("إضافة للسيستم"):
                    new_id = int(datetime.now().timestamp())
                    st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": loc, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح حساب", "tech": "المدير", "debt": d, "price": 0, "parts": []}]})
                    save_json("customers.json", st.session_state.data); st.success("تمت الإضافة"); st.rerun()

        # عرض البحث
        for i, c in enumerate(st.session_state.data):
            if not search or search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                with st.container():
                    st.markdown('<div class="client-card">', unsafe_allow_html=True)
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        # الباركود
                        qr_url = f"https://{st.query_params.get('host', 'xpt.streamlit.app')}/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_url}")
                        if st.button("🗑️ حذف", key=f"del{c['id']}"):
                            st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()
                    with col2:
                        st.subheader(f"👤 {c['name']}")
                        st.write(f"📞 {c.get('phone','---')}")
                        if c.get('gps'): st.link_button("📍 تتبع الموقع", c['gps'])
                        bal = sum(float(h.get('debt', 0)) for h in c['history']) - sum(float(h.get('price', 0)) for h in c['history'])
                        st.info(f"💰 المديونية الحالية: {bal:,.0f} ج.م")
                    st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "🛠️ مراقبة الفنيين":
        st.subheader("🛠️ إدارة الفنيين")
        with st.form("add_tech"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("كلمة السر")
            if st.form_submit_button("تسجيل فني"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_json("techs.json", st.session_state.techs); st.rerun()
        
        st.divider()
        st.subheader("📋 تقارير العمليات اليومية")
        all_logs = []
        for c in st.session_state.data:
            for h in c['history']:
                if h.get('tech') and h['tech'] != "المدير":
                    all_logs.append({"التاريخ": h['date'], "الفني": h['tech'], "العميل": c['name'], "المحصل": h['price'], "الصيانة": h['debt']})
        if all_logs: st.table(all_logs)

    elif menu == "📊 التقارير المالية":
        total_m = sum(sum(float(h.get('debt', 0)) for h in c['history']) - sum(float(h.get('price', 0)) for h in c['history']) for c in st.session_state.data)
        st.metric("💰 إجمالي المديونية في السوق", f"{total_m:,.0f} ج.م")

    elif menu == "🚪 تسجيل خروج": del st.session_state.role; st.rerun()

# ================== 6. لوحة الفني (تسجيل الزيارة) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.title(f"🛠️ الفني: {st.session_state.c_tech}")
    target = st.selectbox("اختر العميل المستهدف", st.session_state.data, format_func=lambda x: x['name'])
    
    if target.get('gps'): st.link_button("📍 فتح GPS العميل", target['gps'], use_container_width=True)
    
    with st.form("visit_form"):
        st.subheader("📝 تسجيل صيانة / تحصيل")
        pts = st.multiselect("القطع المستبدلة", ["ش1", "ش2", "ش3", "ش4 ممبرين", "ش5", "ش6", "ش7", "موتور", "خزان", "أداكتور", "هاي بريشر", "لو بريشر"])
        v_debt = st.number_input("تكلفة الصيانة الحالية (تضاف للمديونية)", 0.0)
        v_price = st.number_input("المبلغ المحصل الآن (يخصم من المديونية)", 0.0)
        v_note = st.text_area("ملاحظات الفني")
        
        if st.form_submit_button("إرسال التقرير"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "tech": st.session_state.c_tech,
                        "parts": pts,
                        "note": v_note,
                        "debt": v_debt,
                        "price": v_price
                    })
                    break
            save_json("customers.json", st.session_state.data)
            st.success("✅ تم حفظ الزيارة بنجاح!")
            
    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()
