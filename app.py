import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. إعدادات الهوية والـ CSS ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# تأكد أن الصورة باسم 1000357687.jpg موجودة بجانب الملف
logo_b64 = get_base64_logo("1000357687.jpg")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ direction: rtl; background-color: #f0f4f8; }}
    * {{ font-family: 'Cairo', sans-serif; text-align: right; }}
    
    .main-card {{ 
        background: white; border: 2px solid #0056b3; 
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    .history-card {{ 
        background: white; border-radius: 12px; padding: 15px; 
        margin-top: 15px; border-right: 8px solid #00aaff;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }}
    .status-box {{ 
        font-weight: bold; padding: 10px; border-radius: 8px; 
        margin-top: 10px; line-height: 1.6;
    }}
    .status-paid {{ background-color: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9; }}
    .status-debt {{ background-color: #ffebee; color: #c62828; border: 1px solid #ffcdd2; }}
    .status-partial {{ background-color: #fff3e0; color: #ef6c00; border: 1px solid #ffe0b2; }}
    
    .login-box {{ text-align: center; padding: 40px; background: #ffffff; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); }}
    header, footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ================== 2. نظام إدارة البيانات ==================
def load_json(file, default):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f: return json.load(f)
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calc_total_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        client = next((x for x in st.session_state.data if x['id'] == c_id), None)
        if client:
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=180)
            st.markdown("<h1 style='text-align:center; color:#0056b3; margin-top:-10px;'>Power Life 💧</h1>", unsafe_allow_html=True)
            
            history = client.get('history', [])
            st.markdown(f"""
            <div class='main-card'>
                <h2 style='text-align:center;'>{client['name']}</h2>
                <div style='text-align:center;'>
                    <p style='color:#666;'>إجمالي المديونية الحالية</p>
                    <h1 style='color:#d32f2f;'>{calc_total_balance(history):,.1f} ج.م</h1>
                </div>
            </div>
            <h3 style='border-bottom: 2px solid #00aaff; display:inline-block; padding-bottom:5px;'>📜 سجل الصيانة والتحصيل</h3>
            """, unsafe_allow_html=True)
            
            for h in reversed(history):
                cost = float(h.get('debt', 0))
                paid = float(h.get('price', 0))
                rem = cost - paid
                
                # منطق عرض تفاصيل "المتبقي من كل زيارة"
                if cost > 0 and paid > 0 and rem > 0:
                    status_html = f"""<div class='status-box status-partial'>
                        🔹 تكلفة الزيارة: {cost:,.1f} ج.م | تم دفع: {paid:,.1f} ج.م<br>
                        🚩 المتبقي من هذه الزيارة: {rem:,.1f} ج.م
                    </div>"""
                elif cost > 0 and paid == 0:
                    status_html = f"<div class='status-box status-debt'>⚠️ مديونية الزيارة بالكامل: {cost:,.1f} ج.م</div>"
                elif cost > 0 and rem <= 0:
                    status_html = f"<div class='status-box status-paid'>✅ تم سداد كامل تكلفة الزيارة ({paid:,.1f} ج.م)</div>"
                elif cost == 0 and paid > 0:
                    status_html = f"<div class='status-box status-paid'>💰 سداد مديونية سابقة بمبلغ: {paid:,.1f} ج.م</div>"
                else: status_html = ""

                st.markdown(f"""
                <div class="history-card">
                    <div style='display:flex; justify-content:space-between; color:#888; font-size:12px;'>
                        <span>📅 {h["date"]}</span>
                        <span>🛠️ الفني: {h.get('tech', 'إدارة')}</span>
                    </div>
                    <div style='margin:10px 0; font-weight:bold;'>📝 {h["note"]}</div>
                    {status_html}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. صفحة الدخول الرئيسية ==================
if "role" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='login-box'>", unsafe_allow_html=True)
        if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", use_container_width=True)
        st.markdown("<h1 style='color:#0056b3; margin-top:0;'>Power Life</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#666;'>نظام إدارة صيانة الفلاتر 🔒</p>", unsafe_allow_html=True)
        if st.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
        st.write("")
        if st.button("🛠️ دخول الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================== 5. لوحة التحكم (المدير / الفني) ==================
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()

elif st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_names) if t_names else st.warning("لا يوجد فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()

elif st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "🚪 خروج"])
    if menu == "👥 العملاء":
        search = st.text_input("🔍 ابحث عن عميل...")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower():
                with st.expander(f"👤 {c['name']} (الرصيد: {calc_total_balance(c.get('history', []))})"):
                    col_qr, col_act = st.columns([1, 2])
                    with col_qr:
                        qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        st.image(qr, caption="QR العميل")
                    with col_act:
                        d1 = st.number_input("التكلفة (+)", 0.0, key=f"d{c['id']}")
                        d2 = st.number_input("تحصيل (-)", 0.0, key=f"r{c['id']}")
                        nt = st.text_input("ملاحظة", key=f"n{c['id']}")
                        if st.button("حفظ العملية", key=f"b{c['id']}"):
                            c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": nt, "debt": d1, "price": d2, "tech": "الإدارة"})
                            save_json("customers.json", st.session_state.data); st.rerun()
    elif menu == "➕ إضافة عميل":
        with st.form("add"):
            n = st.text_input("الاسم"); p = st.text_input("الهاتف"); g = st.text_input("لوكيشن GPS")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تم بنجاح")
    elif menu == "🛠️ الفنيين":
        with st.form("t"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("الباسورد")
            if st.form_submit_button("إضافة فني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs); st.rerun()
    elif menu == "خروج": del st.session_state.role; st.rerun()

elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ مرحبا، {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        if target.get('gps'): st.link_button("📍 فتح الموقع", target['gps'])
        with st.form("visit"):
            cost = st.number_input("التكلفة الكلية", 0.0); paid = st.number_input("المحصل من العميل", 0.0)
            note = st.text_area("تفاصيل الزيارة")
            if st.form_submit_button("✅ حفظ وإرسال"):
                target.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid})
                save_json("customers.json", st.session_state.data); st.success("تم تسجيل البيانات!")
    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
