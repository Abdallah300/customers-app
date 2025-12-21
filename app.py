import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق (الأزرق الملكي) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-header { background: #001f3f; border-radius: 15px; padding: 20px; border: 2px solid #007bff; margin-bottom: 25px; }
    header, footer {visibility: hidden;}
    .stExpander { background: rgba(0, 31, 63, 0.5); border-radius: 10px; border: 1px solid #007bff; }
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

# ================== 3. واجهة الباركود (للعميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-header'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:25px;'>المديونية: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.write(f"📅 {h['date']} | {h['note']} | 💰 {float(h['debt'])-float(h['price'])} ج.م")
            st.stop()
    except: st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life Control 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الإدارة (طلبك الأساسي هنا) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "🚪 خروج"])

    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث باسم العميل أو رقم التليفون لفتح بياناته...")
        
        if search:
            found = False
            for i, c in enumerate(st.session_state.data):
                # البحث بالاسم أو التليفون
                if search.lower() in c['name'].lower() or search in str(c.get('phone', '')):
                    found = True
                    with st.container():
                        st.markdown(f"### 👤 عميل: {c['name']} (كود: {c['id']})")
                        
                        col1, col2 = st.columns([1, 2])
                        with col1:
                            # عرض الباركود فوراً عند البحث
                            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                            st.write(f"💰 الرصيد الحالي: **{calculate_balance(c.get('history', [])):,.0f} ج.م**")
                            if st.button("🗑️ حذف العميل نهائياً", key=f"del_{c['id']}", type="primary"):
                                st.session_state.data.pop(i); save_json("customers.json", st.session_state.data); st.rerun()

                        with col2:
                            with st.expander("📝 تعديل البيانات الأساسية", expanded=True):
                                c['name'] = st.text_input("تغيير الاسم", value=c['name'], key=f"n_{c['id']}")
                                c['phone'] = st.text_input("تعديل رقم التليفون", value=c.get('phone', ''), key=f"p_{c['id']}")
                                c['gov'] = st.text_input("تعديل المحافظة", value=c.get('gov', ''), key=f"g_{c['id']}")
                                c['branch'] = st.text_input("تعديل الفرع", value=c.get('branch', ''), key=f"b_{c['id']}")
                                if st.button("حفظ التعديلات", key=f"sv_{c['id']}"):
                                    save_json("customers.json", st.session_state.data); st.success("تم التحديث")

                            with st.expander("💸 إدارة المديونية والملاحظات"):
                                a_debt = st.number_input("زيادة مديونية (+ صيانة/قطع)", min_value=0.0, key=f"ad_{c['id']}")
                                a_price = st.number_input("إزالة مديونية (- تحصيل مبلغ)", min_value=0.0, key=f"ap_{c['id']}")
                                a_note = st.text_area("إضافة ملاحظات العملية", key=f"an_{c['id']}")
                                if st.button("تسجيل العملية الماليّة", key=f"tr_{c['id']}"):
                                    if a_debt > 0 or a_price > 0:
                                        c['history'].append({
                                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                            "note": a_note if a_note else "تعديل إداري",
                                            "tech": "الإدارة",
                                            "debt": a_debt,
                                            "price": a_price
                                        })
                                        save_json("customers.json", st.session_state.data); st.rerun()
            if not found:
                st.warning("لم يتم العثور على عميل بهذا الاسم أو الرقم.")
        else:
            st.info("الرجاء كتابة اسم العميل في خانة البحث بالأعلى لتظهر بياناته.")

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("اسم العميل الجديد")
            p = st.text_input("رقم التليفون")
            g = st.text_input("المحافظة")
            d = st.number_input("المديونية الافتتاحية", min_value=0.0)
            if st.form_submit_button("إضافة للسيستم"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gov": g, "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "debt": d, "price": 0}]})
                save_json("customers.json", st.session_state.data); st.success("تمت الإضافة")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# (باقي كود الفني كما هو لضمان عدم الحذف)
elif st.session_state.role == "tech":
    st.sidebar.title(f"الفني: {st.session_state.tech_name}")
    target = st.selectbox("العميل", st.session_state.data, format_func=lambda x: x['name'])
    with st.form("tech_f"):
        v1 = st.number_input("تكلفة صيانة", 0.0); v2 = st.number_input("تحصيل", 0.0); note = st.text_area("الملاحظات")
        if st.form_submit_button("حفظ"):
            for x in st.session_state.data:
                if x['id'] == target['id']:
                    x['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.tech_name, "debt": v1, "price": v2})
            save_json("customers.json", st.session_state.data); st.success("تم")
    if st.sidebar.button("خروج"): del st.session_state.role; st.rerun()
