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
    html, body, [data-testid="stAppViewContainer"] {{ direction: rtl; background-color: #f8fbff; }}
    * {{ font-family: 'Cairo', sans-serif; text-align: right; }}
    .client-card {{ 
        background: white; border: 2px solid #0056b3; 
        border-radius: 15px; padding: 20px; margin-bottom: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); color: #002d5a;
    }}
    .status-box {{
        padding: 10px; margin: 10px 0; border-radius: 10px;
        background: #f1f7fe; border-right: 5px solid #0056b3;
    }}
    .history-card {{ 
        background: white; border-radius: 12px; padding: 15px; 
        margin-top: 10px; border: 1px solid #e1e8f0; border-right: 6px solid #00aaff;
    }}
    .price-tag {{ color: #d9534f; font-weight: bold; }}
    .collect-tag {{ color: #28a745; font-weight: bold; }}
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

# ================== 3. واجهة الباركود (التعديل المطلوب: إظهار التحصيل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=180)
            st.markdown(f"<h1 style='text-align:center; color:#0056b3;'>Power Life 💧</h1>", unsafe_allow_html=True)
            
            history = c.get('history', [])
            total_bal = calculate_balance(history)
            
            # عرض الكارت الرئيسي
            st.markdown(f"""
            <div class='client-card'>
                <h2 style='text-align:center;'>{c['name']}</h2>
                <div style='text-align:center;'>
                    <p style='font-size:18px; color:#666;'>إجمالي المديونية الكلية</p>
                    <h1 style='color:#d9534f;'>{total_bal:,.1f} ج.م</h1>
                </div>
            </div>
            <h3>📜 سجل الصيانات والتحصيل</h3>
            """, unsafe_allow_html=True)
            
            # عرض السجل مع خانة التحصيل
            for h in reversed(history):
                debt_val = float(h.get('debt', 0))
                price_val = float(h.get('price', 0)) # هذا هو المبلغ المحصل
                net_val = debt_val - price_val
                
                st.markdown(f"""
                <div class="history-card">
                    <div style='display:flex; justify-content:space-between;'>
                        <span><b>📅 {h["date"]}</b></span>
                        <span>🛠️ الفني: {h.get('tech', 'إدارة')}</span>
                    </div>
                    <div style='margin: 10px 0;'>📝 {h["note"]}</div>
                    <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; background: #f9f9f9; padding: 8px; border-radius: 5px;'>
                        <div>💰 قيمة الصيانة: <span class='price-tag'>{debt_val:,.1f}</span></div>
                        <div>✅ المبلغ المحصل: <span class='collect-tag'>{price_val:,.1f}</span></div>
                    </div>
                    <div style='margin-top:5px; font-weight:bold;'>📉 صافي المديونية للزيارة: {net_val:,.1f} ج.م</div>
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. نظام الإدارة والفنيين ==================
# (يتم وضع باقي كود المدير والفني هنا كما هو في النسخ السابقة لضمان عمل النظام بالكامل)
if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", use_container_width=True)
if "role" not in st.session_state:
    st.markdown("<h3 style='text-align:center; color:#002d5a;'>نظام الإدارة الموحد 🔒</h3>", unsafe_allow_html=True)
    if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# تسجيل دخول المدير
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("تأكيد الدخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("إلغاء"): del st.session_state.role; st.rerun()
    st.stop()

# تسجيل دخول الفني
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
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        st.image(qr_url)
                        st.write(f"**الرصيد:** {calculate_balance(c.get('history', []))}")
                    with col2:
                        st.subheader(f"👤 {c['name']}")
                        with st.expander("⚙️ إضافة عملية يدوية"):
                            d1 = st.number_input("قيمة الخدمة (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("المبلغ المدفوع (-)", 0.0, key=f"r{c['id']}")
                            note = st.text_input("ملاحظة", key=f"n{c['id']}")
                            if st.button("حفظ العملية", key=f"b{c['id']}"):
                                c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "debt": d1, "price": d2, "tech": "المدير"})
                                save_json("customers.json", st.session_state.data); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("الاسم"); p = st.text_input("الهاتف"); g = st.text_input("رابط الموقع GPS")
            if st.form_submit_button("إضافة العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تم الحفظ بنجاح")
    elif menu == "🛠️ الفنيين":
        with st.form("add_t"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("كلمة السر")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs); st.rerun()
    elif menu == "📊 التقارير":
        total_debt = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي المديونيات الخارجية", f"{total_debt:,.1f} ج.م")
    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ الفني: {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        if target.get('gps'): st.link_button("📍 فتح موقع العميل", target['gps'], use_container_width=True)
        with st.form("visit"):
            cost = st.number_input("إجمالي تكلفة الصيانة والقطع", 0.0)
            paid = st.number_input("المبلغ المحصل من العميل", 0.0)
            note = st.text_area("تفاصيل ما تم عمله")
            if st.form_submit_button("✅ إرسال التقرير"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid
                })
                save_json("customers.json", st.session_state.data); st.success("تم التسجيل!")
    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()          
