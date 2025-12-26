import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. الهوية والتنسيق ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

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
    .client-card {{ 
        background: white; border: 2px solid #0056b3; 
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); color: #002d5a;
    }}
    .info-box {{
        background: #fff; border-right: 5px solid #0056b3;
        padding: 10px; margin: 5px 0; border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    div.stButton > button {{ 
        width: 100% !important; border-radius: 10px; height: 48px; 
        background-color: #0056b3; color: white; font-weight: bold; border: none;
    }}
    .history-card {{ 
        background: #eef6ff; border-radius: 8px; padding: 12px; 
        margin-top: 8px; border-right: 5px solid #00aaff; color: #333;
    }}
    header, footer {{ visibility: hidden; }}
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

# ================== 3. واجهة الباركود (التعديل المطلوب هنا) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=180)
            st.markdown(f"<h1 style='text-align:center; color:#0056b3;'>Power Life 💧</h1>", unsafe_allow_html=True)
            
            # حسابات المديونية
            history = c.get('history', [])
            total_bal = calculate_balance(history)
            
            # الحصول على بيانات آخر صيانة
            last_op = history[-1] if history else {}
            last_tech = last_op.get('tech', 'غير مسجل')
            # مديونية آخر صيانة = (التكلفة - المحصل) في آخر عملية
            last_debt = float(last_op.get('debt', 0)) - float(last_op.get('price', 0))

            st.markdown(f"""
            <div class='client-card'>
                <h2 style='text-align:center; margin-bottom:20px;'>{c['name']}</h2>
                <div class='info-box'>👤 <b>فني آخر صيانة:</b> {last_tech}</div>
                <div class='info-box'>💸 <b>مديونية آخر صيانة:</b> {last_debt:,.1f} ج.م</div>
                <hr>
                <div style='text-align:center;'>
                    <p style='font-size:18px; color:#666; margin-bottom:5px;'>إجمالي المديونية الكلية</p>
                    <h1 style='color:#d9534f; margin-top:0;'>{total_bal:,.1f} ج.م</h1>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📜 سجل الصيانة والعمليات")
            for h in reversed(history):
                op_val = float(h.get('debt', 0)) - float(h.get('price', 0))
                st.markdown(f"""
                <div class="history-card">
                    <b>📅 {h["date"]}</b> | 🛠️ الفني: {h.get('tech', 'إدارة')} <br>
                    📝 {h["note"]} <br>
                    💰 قيمة العملية: {op_val:,.1f} ج.م
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. باقي الكود (نظام الإدارة) ==================
if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", use_container_width=True)

if "role" not in st.session_state:
    st.markdown("<h3 style='text-align:center; color:#002d5a;'>نظام الإدارة الموحد 🔒</h3>", unsafe_allow_html=True)
    if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (نفس منطق تسجيل الدخول والإدارة والفنيين في الكود السابق دون تغيير)
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

if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة الرئيسية", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "📊 التقارير", "🚪 خروج"])
    if menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث عن عميل...")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower():
                with st.container():
                    st.markdown('<div class="client-card">', unsafe_allow_html=True)
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                        st.write(f"**الرصيد:** {calculate_balance(c.get('history', []))}")
                    with col2:
                        st.subheader(f"👤 {c['name']}")
                        with st.expander("⚙️ عمليات"):
                            d1 = st.number_input("إضافة (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("تحصيل (-)", 0.0, key=f"r{c['id']}")
                            if st.button("حفظ", key=f"b{c['id']}"):
                                c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل رصيد", "debt": d1, "price": d2, "tech": "المدير"})
                                save_json("customers.json", st.session_state.data); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("الاسم"); p = st.text_input("الهاتف"); g = st.text_input("GPS")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تم!")
    elif menu == "🛠️ الفنيين":
        with st.form("add_t"):
            tn = st.text_input("الاسم"); tp = st.text_input("السر")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs); st.rerun()
    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ الفني: {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("اختر العميل", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        with st.form("visit"):
            cost = st.number_input("التكلفة", 0.0); paid = st.number_input("المحصل", 0.0); note = st.text_area("ملاحظات")
            if st.form_submit_button("إرسال التقرير"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid
                })
                save_json("customers.json", st.session_state.data); st.success("تم التسجيل!")
    if st.button("خروج"): del st.session_state.role; st.rerun()
