import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. إعدادات الهوية والألوان الثابتة ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_base64_logo("1000357687.jpg")

# CSS لإجبار التطبيق على ألوان محددة تمنع تداخل الوضع الليلي
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* إجبار الخلفية والألوان */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: #f8fbff !important;
        direction: rtl;
    }}
    
    * {{ font-family: 'Cairo', sans-serif; text-align: right; color: #1e293b; }}
    
    .main-card {{ 
        background: white !important; border: 2px solid #0056b3; 
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }}
    
    .history-card {{ 
        background: white !important; border-radius: 12px; padding: 15px; 
        margin-top: 10px; border-right: 6px solid #00aaff;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        color: #1e293b !important;
    }}
    
    /* تنبيهات الحسابات */
    .status-box {{ padding: 10px; border-radius: 8px; font-weight: bold; margin-top: 10px; }}
    .status-paid {{ background-color: #e8f5e9 !important; color: #2e7d32 !important; }}
    .status-debt {{ background-color: #ffebee !important; color: #c62828 !important; }}
    .status-partial {{ background-color: #fff3e0 !important; color: #ef6c00 !important; }}
    
    div.stButton > button {{ 
        background-color: #0056b3 !important; color: white !important; 
        border-radius: 10px; font-weight: bold; width: 100%;
    }}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_db(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f: return json.load(f)
    return default

def save_db(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_db("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_db("techs.json", [])

def get_total_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        c = next((x for x in st.session_state.data if x['id'] == c_id), None)
        if c:
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=180)
            st.markdown(f"<h1 style='text-align:center; color:#0056b3;'>Power Life 💧</h1>", unsafe_allow_html=True)
            
            history = c.get('history', [])
            st.markdown(f"""
            <div class='main-card'>
                <h2 style='text-align:center;'>{c['name']}</h2>
                <p style='text-align:center; color:#666;'>نوع الجهاز: {c.get('device_type', 'غير محدد')}</p>
                <hr>
                <div style='text-align:center;'>
                    <p style='margin:0;'>إجمالي المبلغ المتبقي (المديونية)</p>
                    <h1 style='color:#d32f2f;'>{get_total_balance(history):,.1f} ج.م</h1>
                </div>
            </div>
            <h3>📜 سجل العمليات والمبالغ</h3>
            """, unsafe_allow_html=True)
            
            for h in reversed(history):
                cost = float(h.get('debt', 0))
                paid = float(h.get('price', 0))
                rem = cost - paid
                
                if cost > 0 and paid > 0 and rem > 0:
                    msg = f"<div class='status-box status-partial'>🚩 متبقي من هذه العملية: {rem:,.1f} ج.م (دفع {paid} من {cost})</div>"
                elif cost > 0 and paid == 0:
                    msg = f"<div class='status-box status-debt'>⚠️ مديونية كاملة عن العملية: {cost:,.1f} ج.م</div>"
                elif cost == 0 and paid > 0:
                    msg = f"<div class='status-box status-paid'>💰 سداد مبلغ: {paid:,.1f} ج.م</div>"
                else:
                    msg = f"<div class='status-box status-paid'>✅ تم السداد بالكامل: {paid:,.1f} ج.م</div>"

                st.markdown(f"""
                <div class='history-card'>
                    <small>📅 {h['date']} | 🛠️ {h.get('tech', 'الإدارة')}</small><br>
                    <b>📝 {h['note']}</b>
                    {msg}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. نظام الإدارة الموحد ==================
if "role" not in st.session_state:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", use_container_width=True)
        st.markdown("<h2 style='text-align:center;'>نظام الإدارة الموحد 🔒</h2>", unsafe_allow_html=True)
        if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
        if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- لوحة الإدارة ---
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["العملاء", "إضافة عميل/جهاز جديد", "تقارير الفنيين", "خروج"])
    
    if menu == "العملاء":
        search = st.text_input("🔍 ابحث عن عميل")
        for c in st.session_state.data:
            if not search or search in c['name']:
                with st.expander(f"👤 {c['name']} - جهاز: {c.get('device_type', 'غير محدد')}"):
                    st.write(f"💰 الحساب الحالي: {get_total_balance(c['history'])} ج.م")
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                    st.image(qr_url)
                    
                    st.subheader("إضافة عملية (قسط / صيانة / مديونية)")
                    with st.form(f"admin_form_{c['id']}"):
                        cost = st.number_input("إضافة مبلغ على العميل (+)", 0.0)
                        paid = st.number_input("تحصيل مبلغ من العميل (-)", 0.0)
                        note = st.text_input("البيان (مثال: قسط شهر 12 / تركيب شمع)")
                        if st.form_submit_button("حفظ العملية"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": note, "debt": cost, "price": paid, "tech": "الإدارة"})
                            save_db("customers.json", st.session_state.data); st.rerun()

    elif menu == "إضافة عميل/جهاز جديد":
        with st.form("add_client"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم التلفون")
            device = st.selectbox("نوع التعاقد/الجهاز", ["جهاز جديد 7 مراحل", "جهاز جديد 5 مراحل", "صيانة عميل خارجي", "أخرى"])
            price_start = st.number_input("سعر الجهاز/التعاقد الكلي", 0.0)
            paid_start = st.number_input("المقدم المدفوع", 0.0)
            if st.form_submit_button("إضافة العميل للسيستم"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                new_c = {
                    "id": new_id, "name": name, "phone": phone, "device_type": device,
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": f"تعاقد {device}", "debt": price_start, "price": paid_start, "tech": "الإدارة"}]
                }
                st.session_state.data.append(new_c)
                save_db("customers.json", st.session_state.data); st.success("تم تسجيل العميل بنجاح!")

    elif menu == "خروج": del st.session_state.role; st.rerun()

# --- لوحة الفني ---
elif st.session_state.role == "tech_p":
    st.header(f"🛠️ الفني: {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("اختر العميل", list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    
    if target:
        with st.form("tech_visit"):
            st.write(f"📝 نوع جهاز العميل: {target.get('device_type')}")
            cost = st.number_input("تكلفة الزيارة/الصيانة", 0.0)
            paid = st.number_input("المبلغ المحصل فعلياً", 0.0)
            note = st.text_area("تفاصيل الصيانة (مثال: تغيير شمعة 1 و 3)")
            if st.form_submit_button("إرسال التقرير"):
                target['history'].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid
                })
                save_db("customers.json", st.session_state.data); st.success("تم الحفظ!")
    if st.button("خروج"): del st.session_state.role; st.rerun()

# --- تسجيل الدخول (Logic) ---
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
elif st.session_state.role == "tech_login":
    tn = [t['name'] for t in st.session_state.techs]
    user = st.selectbox("الاسم", tn) if tn else st.error("لا فنيين")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        t = next((x for x in st.session_state.techs if x['name'] == user), None)
        if t and p == t['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = user; st.rerun()
