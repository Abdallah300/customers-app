import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. الهوية والتنسيق (الألوان المتناسقة مع اللوجو) ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

# دالة تحويل اللوجو لضمان ظهوره دائماً
def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_base64_logo("1000357687.jpg")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ direction: rtl; background-color: #f0f7ff; }}
    * {{ font-family: 'Cairo', sans-serif; text-align: right; }}
    
    /* كروت العملاء */
    .client-card {{ 
        background: white; border: 2px solid #0056b3; 
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: #002d5a;
    }}
    
    /* الأزرار */
    div.stButton > button {{ 
        width: 100% !important; border-radius: 10px; height: 48px; 
        background-color: #0056b3; color: white; font-weight: bold; border: none;
    }}
    div.stButton > button:hover {{ background-color: #004494; border: none; }}
    
    /* سجل العمليات */
    .history-card {{ 
        background: #eef6ff; border-radius: 8px; padding: 12px; 
        margin-top: 8px; border-right: 5px solid #00aaff; color: #333;
    }}
    
    header, footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات (نفس المنطق الأصلي) ==================
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

# ================== 3. نظام الباركود (موجود كما هو) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=180)
            st.markdown(f"<h1 style='text-align:center; color:#0056b3;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-card'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:28px; color:#d9534f;'>المتبقي: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            st.subheader("📜 سجل الصيانات والعمليات")
            for h in reversed(c.get('history', [])):
                st.markdown(f'<div class="history-card"><b>📅 {h["date"]}</b><br>📝 {h["note"]}<br>💰 المبلغ: {float(h.get("debt",0)) - float(h.get("price",0))} ج.م</div>', unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. الشعار وصفحة الدخول ==================
if logo_b64:
    st.image(f"data:image/jpeg;base64,{logo_b64}", use_container_width=True)
else:
    st.markdown("<h1 style='text-align:center; color:#0056b3;'>Power Life 💧</h1>", unsafe_allow_html=True)

if "role" not in st.session_state:
    st.markdown("<h3 style='text-align:center; color:#002d5a;'>نظام الإدارة الموحد 🔒</h3>", unsafe_allow_html=True)
    if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- منطق تسجيل الدخول ---
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("تأكيد الدخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("إلغاء"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسم الفني", t_names) if t_names else st.info("لا يوجد فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول الفني"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("إلغاء"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة المدير (كاملة المميزات) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة الرئيسية", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "📊 التقارير", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث عن عميل (الاسم أو الرقم)...")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                with st.container():
                    st.markdown(f'<div class="client-card">', unsafe_allow_html=True)
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                        st.write(f"**الرصيد:** {calculate_balance(c.get('history', []))} ج.م")
                        if c.get('gps'): st.link_button("📍 موقع العميل", c['gps'])
                    with col2:
                        st.subheader(f"👤 {c['name']}")
                        with st.expander("⚙️ تحكم وإضافة عمليات"):
                            c['name'] = st.text_input("تعديل الاسم", value=c['name'], key=f"n{c['id']}")
                            d1 = st.number_input("إضافة مبلغ (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("تحصيل مبلغ (-)", 0.0, key=f"r{c['id']}")
                            if st.button("حفظ وحساب", key=f"b{c['id']}"):
                                c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل رصيد", "debt": d1, "price": d2})
                                save_json("customers.json", st.session_state.data); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ إضافة عميل":
        with st.form("new_customer"):
            n = st.text_input("اسم العميل الجديد"); p = st.text_input("رقم الهاتف"); g = st.text_input("رابط لوكيشن جوجل")
            if st.form_submit_button("إضافة العميل للنظام"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تمت الإضافة!")

    elif menu == "🛠️ الفنيين":
        st.subheader("إدارة طاقم الفنيين")
        with st.form("add_tech"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("كلمة سر الفني")
            if st.form_submit_button("إضافة فني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs); st.rerun()
        st.divider()
        st.write("📋 سجل حركة الفنيين:")
        for c in st.session_state.data:
            for h in c.get('history', []):
                if h.get('tech'): st.write(f"🔹 {h['tech']} زار {c['name']} بتاريخ {h['date']}")

    elif menu == "📊 التقارير":
        total_debt = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي التحصيلات المتأخرة", f"{total_debt:,.0f} ج.م")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (كاملة المميزات) ==================
elif st.session_state.role == "tech_p":
    st.markdown(f"<h2 style='color:#0056b3;'>🛠️ أهلاً فني: {st.session_state.c_tech}</h2>", unsafe_allow_html=True)
    
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل الذي تزوره الآن", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    
    if target:
        if target.get('gps'): st.link_button("📍 افتح الموقع على الخريطة", target['gps'], use_container_width=True)
        with st.form("tech_visit"):
            cost = st.number_input("تكلفة الصيانة/القطع", 0.0)
            paid = st.number_input("المبلغ المحصل فعلياً", 0.0)
            note = st.text_area("ملاحظاتك عن الزيارة (مثلاً: تغيير شمعة)")
            if st.form_submit_button("✅ إرسال التقرير"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid
                })
                save_json("customers.json", st.session_state.data); st.success("تم تسجيل الزيارة بنجاح!")
    
    if st.button("🚪 تسجيل خروج"): del st.session_state.role; st.rerun()
