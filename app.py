import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. الهوية والتنسيق (CSS) ==================
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
    
    /* كارت العميل */
    .main-card {{ 
        background: white; border: 2px solid #0056b3; 
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    
    /* كارت كل عملية صيانة */
    .history-card {{ 
        background: #ffffff; border-radius: 12px; padding: 15px; 
        margin-top: 15px; border-right: 8px solid #00aaff;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}
    
    /* مبالغ العملية الواحدة */
    .status-box {{ 
        font-weight: bold; padding: 8px 12px; border-radius: 8px; 
        display: inline-block; margin-top: 10px; width: 100%;
    }}
    .status-paid {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
    .status-debt {{ background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
    .status-partial {{ background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}

    header, footer {{ visibility: hidden; }}
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

def get_total_bal(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة الباركود للعميل ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == c_id), None)
        if c:
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=200)
            st.markdown(f"<h1 style='text-align:center; color:#0056b3;'>Power Life 💧</h1>", unsafe_allow_html=True)
            
            history = c.get('history', [])
            
            st.markdown(f"""
            <div class='main-card'>
                <h2 style='text-align:center; margin-bottom:5px;'>{c['name']}</h2>
                <div style='text-align:center;'>
                    <p style='color:#666; font-size:18px;'>إجمالي المديونية الحالية</p>
                    <h1 style='color:#d32f2f; font-size:45px;'>{get_total_bal(history):,.1f} ج.م</h1>
                </div>
            </div>
            <h3 style='padding-right:10px;'>📜 سجل عمليات الصيانة والتحصيل</h3>
            """, unsafe_allow_html=True)
            
            for h in reversed(history):
                # حسابات العملية الواحدة (المطلوب هنا)
                cost = float(h.get('debt', 0))
                paid = float(h.get('price', 0))
                rem = cost - paid
                
                # منطق رسالة المتبقي لكل عملية
                if cost > 0 and rem == 0:
                    msg = f"<div class='status-box status-paid'>✅ تم سداد كامل تكلفة الزيارة ({paid:,.1f} ج.م)</div>"
                elif cost > 0 and paid == 0:
                    msg = f"<div class='status-box status-debt'>⚠️ مديونية الزيارة بالكامل: {cost:,.1f} ج.م</div>"
                elif cost > 0 and rem > 0:
                    msg = f"<div class='status-box status-partial'>🔹 دفع جزء: {paid:,.1f} ج.م | 🚩 المتبقي من هذه الزيارة: {rem:,.1f} ج.م</div>"
                elif cost == 0 and paid > 0:
                    msg = f"<div class='status-box status-paid'>💰 سداد مديونية سابقة بمبلغ: {paid:,.1f} ج.م</div>"
                else:
                    msg = ""

                st.markdown(f"""
                <div class="history-card">
                    <div style='display:flex; justify-content:space-between; color:#888; font-size:12px;'>
                        <span>📅 {h["date"]}</span>
                        <span>🛠️ الفني: {h.get('tech', 'إدارة')}</span>
                    </div>
                    <div style='margin:10px 0; font-weight:bold; font-size:16px;'>📝 {h["note"]}</div>
                    {msg}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. صفحة الدخول (اللوجو والاسم) ==================
if "role" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0056b3; margin-top:-20px;'>Power Life</h1>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center; color:#666;'>نظام الإدارة الموحد 🔐</h4>", unsafe_allow_html=True)
        st.write("---")
        if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
        if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# ================== 5. لوحة المدير ==================
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "📊 التقارير", "🚪 خروج"])
    if menu == "👥 العملاء":
        search = st.text_input("🔍 ابحث عن عميل بالاسم...")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower():
                with st.container():
                    st.markdown(f"<div class='main-card'><h3>👤 {c['name']}</h3>", unsafe_allow_html=True)
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        st.image(qr_url, caption="QR العميل")
                        st.write(f"💰 الحساب: {get_total_bal(c.get('history', []))}")
                    with col_b:
                        with st.expander("📝 إضافة عملية أو تحصيل"):
                            d1 = st.number_input("التكلفة (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("التحصيل (-)", 0.0, key=f"r{c['id']}")
                            nt = st.text_input("ملاحظة", key=f"n{c['id']}")
                            if st.button("حفظ", key=f"b{c['id']}"):
                                c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %I:%M %p"), "note": nt, "debt": d1, "price": d2, "tech": "المدير"})
                                save_db("customers.json", st.session_state.data); st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
    elif menu == "➕ إضافة عميل":
        with st.form("add"):
            n = st.text_input("الاسم"); p = st.text_input("الهاتف"); g = st.text_input("لوكيشن")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_db("customers.json", st.session_state.data); st.success("تم!")
    elif menu == "🛠️ الفنيين":
        with st.form("t"):
            tn = st.text_input("الاسم"); tp = st.text_input("السر")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_db("techs.json", st.session_state.techs); st.rerun()
        st.write("📋 الفنيين:")
        for t in st.session_state.techs: st.text(f"• {t['name']}")
    elif menu == "خروج": del st.session_state.role; st.rerun()

# ================== 6. لوحة الفني ==================
if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("الفني", t_names) if t_names else st.warning("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_p":
    st.markdown(f"### 🛠️ الفني: {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("العميل", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        if target.get('gps'): st.link_button("📍 فتح GPS", target['gps'])
        with st.form("tech_v"):
            cost = st.number_input("التكلفة الإجمالية", 0.0)
            paid = st.number_input("المبلغ المحصل الآن", 0.0)
            note = st.text_area("وصف الزيارة")
            if st.form_submit_button("✅ إرسال التقرير"):
                target.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %I:%M %p"), "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid})
                save_db("customers.json", st.session_state.data); st.success("تم الحفظ!")
    if st.button("خروج"): del st.session_state.role; st.rerun()
