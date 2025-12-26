import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق (أسود كحلي وأزرق) - بناءً على طلبك ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-x: hidden !important; direction: rtl; }
    .stApp { background: #000814; color: #ffffff; } /* أسود ملكي */
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .client-card { 
        background: #001529; border: 2px solid #007bff; 
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2);
    }
    div.stButton > button { 
        background-color: #007bff !important; color: white !important;
        border-radius: 8px; height: 45px; border: none; font-weight: bold;
    }
    .history-card { 
        background: rgba(0, 123, 255, 0.1); border-radius: 8px; 
        padding: 12px; margin-top: 8px; border-right: 4px solid #00d4ff; 
    }
    /* جعل الحقول متناسبة مع الخلفية السوداء */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background-color: #001f3f !important; color: white !important; border: 1px solid #007bff !important;
    }
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات (نفس منطق كودك) ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def refresh_all_data():
    st.session_state.data = load_json("customers.json", [])
    st.session_state.techs = load_json("techs.json", [])
    st.cache_data.clear()

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة الباركود للعميل (نفس المنطق) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-card'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:25px; color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                shama_txt = f"<br>⚙️ شمع: {h.get('shama', 0)}" if h.get('shama') else ""
                st.markdown(f'<div class="history-card"><b>📅 {h["date"]}</b><br>📝 {h["note"]}{shama_txt}<br>💰 العملية: {float(h.get("debt",0)) - float(h.get("price",0))} ج.م</div>', unsafe_allow_html=True)
            st.stop()
    except:
        st.error("خطأ في البيانات."); st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:30px;'>Power Life System 🔒</h2>", unsafe_allow_html=True)
    if st.button("🔑 دخول المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if st.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (تسجيل دخول المدير)
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# (تسجيل دخول الفني)
if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_list) if t_list else st.write("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة (المحدثة بالوظائف المطلوبة) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 البحث والإدارة", "➕ إضافة عميل", "🛠️ مراقبة الفنيين", "📊 التقارير", "🚪 خروج"])
    
    if menu == "👥 البحث والإدارة":
        client_base_url = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"
        search = st.text_input("🔍 ابحث بالاسم أو التليفون...")
        
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                with st.container():
                    st.markdown(f'<div class="client-card">', unsafe_allow_html=True)
                    st.subheader(f"👤 {c['name']} (كود: {c['id']})")
                    st.write(f"🏗️ الجهاز: {c.get('device_type', 'غير محدد')}")
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        qr_data = f"{client_base_url}/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={qr_data}")
                        st.write(f"💰 الرصيد الحالي: {calculate_balance(c.get('history', []))} ج.م")
                    
                    with col2:
                        with st.expander("💸 تعديل الحساب (أقساط / صيانة)"):
                            d1 = st.number_input("إضافة مديونية (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("تحصيل مبلغ (-)", 0.0, key=f"r{c['id']}")
                            note = st.text_input("السبب", key=f"n_ed{c['id']}")
                            if st.button("تسجيل العملية", key=f"t{c['id']}"):
                                c.setdefault('history', []).append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "note": note if note else "تعديل إداري", "tech": "المدير", "debt": d1, "price": d2
                                })
                                save_json("customers.json", st.session_state.data); st.rerun()
                        
                        if st.button(f"🗑️ حذف العميل", key=f"del{c['id']}"):
                            st.session_state.data.remove(c); save_json("customers.json", st.session_state.data); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            name = st.text_input("اسم العميل الجديد")
            phone = st.text_input("رقم التليفون")
            device_type = st.selectbox("بند الجهاز", ["جهاز 7 مراحل جديد", "جهاز 5 مراحل جديد", "صيانة خارجي"])
            full_price = st.number_input("إجمالي السعر / المديونية الأولى", 0.0)
            down_payment = st.number_input("المقدم المدفوع", 0.0)
            gps = st.text_input("رابط GPS")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": new_id, "name": name, "phone": phone, "gps": gps, "device_type": device_type,
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": f"تعاقد {device_type}", "tech": "المدير", "debt": full_price, "price": down_payment}]
                })
                save_json("customers.json", st.session_state.data); st.success("تمت الإضافة!")

    elif menu == "🛠️ مراقبة الفنيين":
        # عرض التحصيل الإجمالي للفنيين والشمع
        all_ops = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech') and h['tech'] != "المدير":
                    all_ops.append({"الفني": h['tech'], "المحصل": h['price'], "شمع": h.get('shama', 0), "العميل": c['name'], "التاريخ": h['date']})
        if all_ops: st.table(all_ops)
        else: st.info("لا توجد عمليات مسجلة للفنيين.")

    elif menu == "📊 التقارير":
        total = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي الديون الخارجية (حصالة الشركة)", f"{total:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (المحدثة بالشمع) ==================
elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ فني: {st.session_state.c_tech}")
    customer_names = {c['id']: c['name'] for c in st.session_state.data}
    selected_id = st.selectbox("🎯 اختر العميل", options=list(customer_names.keys()), format_func=lambda x: customer_names[x])
    target = next((x for x in st.session_state.data if x['id'] == selected_id), None)
    
    if target:
        if target.get('gps'): st.link_button("📍 موقع العميل", target['gps'], use_container_width=True)
        with st.form("visit_form"):
            v_add = st.number_input("تكلفة الصيانة", 0.0); v_rem = st.number_input("المحصل من العميل", 0.0)
            sh_count = st.number_input("عدد الشمع المركب", 0)
            note = st.text_area("تقرير الصيانة")
            if st.form_submit_button("✅ إرسال التقرير"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note, "tech": st.session_state.c_tech, "debt": v_add, "price": v_rem, "shama": sh_count
                })
                save_json("customers.json", st.session_state.data); st.success("تم الحفظ!")
    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
