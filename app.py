import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. إعدادات الهوية والتنسيق ==================
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
    html, body, [data-testid="stAppViewContainer"] {{ direction: rtl; background-color: #f4f7f9; }}
    * {{ font-family: 'Cairo', sans-serif; text-align: right; }}
    .client-card {{ 
        background: white; border: 2px solid #0056b3; 
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .history-card {{ 
        background: white; border-radius: 10px; padding: 15px; 
        margin-top: 10px; border: 1px solid #ddd; border-right: 6px solid #00aaff;
    }}
    .status-paid {{ color: #28a745; font-weight: bold; background: #e8f5e9; padding: 5px 10px; border-radius: 5px; display: inline-block; }}
    .status-debt {{ color: #d9534f; font-weight: bold; background: #ffebee; padding: 5px 10px; border-radius: 5px; display: inline-block; }}
    .status-partial {{ color: #f0ad4e; font-weight: bold; background: #fff3e0; padding: 5px 10px; border-radius: 5px; display: inline-block; }}
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

# ================== 3. واجهة الباركود (المنطق الذكي الجديد) ==================
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
            
            st.markdown(f"""
            <div class='client-card'>
                <h2 style='text-align:center;'>{c['name']}</h2>
                <div style='text-align:center;'>
                    <p style='font-size:18px; color:#666;'>إجمالي المديونية الحالية</p>
                    <h1 style='color:#d9534f;'>{total_bal:,.1f} ج.م</h1>
                </div>
            </div>
            <h3 style='border-bottom: 2px solid #0056b3; padding-bottom: 5px;'>📋 سجل العمليات بالتفصيل</h3>
            """, unsafe_allow_html=True)
            
            for h in reversed(history):
                debt = float(h.get('debt', 0))   # تكلفة الصيانة
                paid = float(h.get('price', 0))  # المبلغ المحصل
                remain = debt - paid             # المتبقي من العملية
                
                # --- تحديد حالة العملية وعرض الرسالة المناسبة ---
                if debt > 0 and paid == debt:
                    status_html = f"<div class='status-paid'>✅ تم تحصيل كامل المبلغ: {paid:,.1f} ج.م</div>"
                elif debt > 0 and paid == 0:
                    status_html = f"<div class='status-debt'>⚠️ المديونية على العميل: {debt:,.1f} ج.م</div>"
                elif debt > 0 and paid < debt:
                    status_html = f"""
                    <div class='status-partial'>
                        🔹 تم دفع جزء: {paid:,.1f} ج.م | 🚩 المتبقي: {remain:,.1f} ج.م
                    </div>
                    """
                elif debt == 0 and paid > 0:
                    status_html = f"<div class='status-paid'>💰 تم تحصيل مبلغ: {paid:,.1f} ج.م (سداد رصيد)</div>"
                else:
                    status_html = ""

                st.markdown(f"""
                <div class="history-card">
                    <div style='display:flex; justify-content:space-between; font-size:14px; color:#555;'>
                        <span>📅 {h["date"]}</span>
                        <span>👤 الفني: {h.get('tech', 'إدارة')}</span>
                    </div>
                    <div style='margin: 10px 0; font-weight: bold;'>📝 {h["note"]}</div>
                    {status_html}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. باقي النظام (المدير والفني) ==================
# ... (باقي الكود الخاص بالدخول وإدارة الفنيين كما هو في النسخ السابقة لضمان الاستقرار)
if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", use_container_width=True)
if "role" not in st.session_state:
    st.markdown("<h3 style='text-align:center;'>نظام الإدارة الموحد 🔒</h3>", unsafe_allow_html=True)
    if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (نظام المدير والفني يتم وضعه هنا - النسخة المستقرة)
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("تأكيد"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("الفني", t_names) if t_names else st.write("لا فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    st.stop()

if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["إدارة العملاء", "إضافة عميل", "الفنيين", "خروج"])
    if menu == "إدارة العملاء":
        search = st.text_input("ابحث بالاسم")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower():
                with st.expander(f"👤 {c['name']} - الرصيد: {calculate_balance(c.get('history', []))}"):
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                    st.image(qr_url)
                    d1 = st.number_input("تكلفة (+)", 0.0, key=f"d{c['id']}")
                    d2 = st.number_input("تحصيل (-)", 0.0, key=f"r{c['id']}")
                    if st.button("حفظ", key=f"b{c['id']}"):
                        c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تعديل إداري", "debt": d1, "price": d2, "tech": "المدير"})
                        save_json("customers.json", st.session_state.data); st.rerun()
    elif menu == "إضافة عميل":
        with st.form("add"):
            n = st.text_input("الاسم"); p = st.text_input("الهاتف"); g = st.text_input("GPS")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تم")
    elif menu == "الفنيين":
        with st.form("add_t"):
            tn = st.text_input("الاسم"); tp = st.text_input("السر")
            if st.form_submit_button("إضافة فني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs); st.rerun()
    elif menu == "خروج": del st.session_state.role; st.rerun()

elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ الفني: {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("اختر العميل", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        if target.get('gps'): st.link_button("📍 موقع العميل", target['gps'])
        with st.form("visit"):
            cost = st.number_input("التكلفة الإجمالية للصيانة", 0.0)
            paid = st.number_input("المبلغ الذي دفعه العميل", 0.0)
            note = st.text_area("وصف الصيانة")
            if st.form_submit_button("حفظ التقرير"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid
                })
                save_json("customers.json", st.session_state.data); st.success("تم الحفظ!")
    if st.button("خروج"): del st.session_state.role; st.rerun()
