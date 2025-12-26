import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. إعدادات الهوية البصرية ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

# وظيفة لتحويل الصورة لكود (Base64) عشان تظهر غصب عن أي متصفح
def get_image_base64(path):
    try:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

logo_data = get_image_base64("1000357687.jpg")

# تنسيق الشكل العام (الخطوط والألوان)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ direction: rtl; background-color: #f5f9ff; }}
    * {{ font-family: 'Cairo', sans-serif; text-align: right; }}
    
    .main-box {{ background: white; border: 2px solid #0056b3; border-radius: 15px; padding: 20px; margin-bottom: 20px; }}
    .visit-card {{ background: white; border-radius: 12px; padding: 15px; margin-top: 10px; border-right: 6px solid #00aaff; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
    
    /* ألوان الحالة المادية */
    .msg {{ font-weight: bold; padding: 5px 10px; border-radius: 5px; display: inline-block; margin-top: 5px; }}
    .paid {{ background-color: #e8f5e9; color: #2e7d32; }}
    .debt {{ background-color: #ffebee; color: #c62828; }}
    .partial {{ background-color: #fff3e0; color: #ef6c00; }}
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

# ================== 3. عرض صفحة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        client = next((x for x in st.session_state.data if x['id'] == c_id), None)
        if client:
            # عرض اللوجو
            if logo_data: st.image(f"data:image/jpeg;base64,{logo_data}", width=200)
            st.markdown(f"<h1 style='text-align:center; color:#0056b3;'>Power Life 💧</h1>", unsafe_allow_html=True)
            
            history = client.get('history', [])
            st.markdown(f"""
            <div class='main-box'>
                <h2 style='text-align:center;'>{client['name']}</h2>
                <div style='text-align:center;'>
                    <p style='color:#666;'>إجمالي المديونية المتبقية</p>
                    <h1 style='color:#d32f2f;'>{get_total_balance(history):,.1f} ج.م</h1>
                </div>
            </div>
            <h3>📜 سجل الصيانات والمبالغ</h3>
            """, unsafe_allow_html=True)
            
            for h in reversed(history):
                cost = float(h.get('debt', 0)) # التكلفة
                paid = float(h.get('price', 0)) # المدفوع
                rem = cost - paid # المتبقي من العملية
                
                # منطق عرض الرسائل بناءً على المبالغ
                if cost > 0 and rem == 0:
                    status = f"<div class='msg paid'>✅ تم تحصيل كامل المبلغ: {paid:,.1f} ج.م</div>"
                elif cost > 0 and paid == 0:
                    status = f"<div class='msg debt'>⚠️ المدونية على العميل: {cost:,.1f} ج.م</div>"
                elif cost > 0 and rem > 0:
                    status = f"<div class='msg partial'>🔸 المبلغ المدفوع: {paid:,.1f} | 🚩 المبلغ المتبقي: {rem:,.1f} ج.م</div>"
                else:
                    status = f"<div class='msg paid'>💰 تم تحصيل مبلغ: {paid:,.1f} ج.م</div>"

                st.markdown(f"""
                <div class="visit-card">
                    <div style='display:flex; justify-content:space-between; font-size:12px; color:#888;'>
                        <span>📅 {h["date"]}</span>
                        <span>🛠️ الفني: {h.get('tech', 'إدارة')}</span>
                    </div>
                    <div style='margin:10px 0;'><b>📝 ملاحظة:</b> {h["note"]}</div>
                    {status}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. صفحة الدخول الرئيسية ==================
if "role" not in st.session_state:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if logo_data: st.image(f"data:image/jpeg;base64,{logo_data}", use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0056b3;'>Power Life</h1>", unsafe_allow_html=True)
        st.write("---")
        if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
        if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# ================== 5. نظام المدير والفني (باقي الكود) ==================
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("تأكيد"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("الفني", t_names) if t_names else st.warning("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "🚪 خروج"])
    if menu == "👥 العملاء":
        search = st.text_input("🔍 ابحث عن عميل")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower():
                with st.expander(f"👤 {c['name']} (الرصيد: {get_total_balance(c.get('history', []))})"):
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    d1 = st.number_input("تكلفة (+)", 0.0, key=f"d{c['id']}")
                    d2 = st.number_input("تحصيل (-)", 0.0, key=f"r{c['id']}")
                    nt = st.text_input("ملاحظة", key=f"n{c['id']}")
                    if st.button("حفظ", key=f"b{c['id']}"):
                        c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": nt, "debt": d1, "price": d2, "tech": "المدير"})
                        save_db("customers.json", st.session_state.data); st.rerun()
    elif menu == "➕ إضافة عميل":
        with st.form("add_c"):
            n = st.text_input("الاسم"); p = st.text_input("الهاتف"); g = st.text_input("لوكيشن")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_db("customers.json", st.session_state.data); st.success("تم")
    elif menu == "الفنيين":
        with st.form("t"):
            tn = st.text_input("اسم الفني"); tp = st.text_input("الباسورد")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_db("techs.json", st.session_state.techs); st.rerun()
    elif menu == "خروج": del st.session_state.role; st.rerun()

elif st.session_state.role == "tech_p":
    st.markdown(f"### 🛠️ الفني: {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        if target.get('gps'): st.link_button("📍 فتح الموقع", target['gps'])
        with st.form("tech_f"):
            cost = st.number_input("التكلفة الكلية", 0.0); paid = st.number_input("المحصل فعلياً", 0.0)
            note = st.text_area("وصف الزيارة")
            if st.form_submit_button("✅ حفظ وإرسال"):
                target.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid})
                save_db("customers.json", st.session_state.data); st.success("تم الحفظ!")
    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
