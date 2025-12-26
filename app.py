import streamlit as st
import json
import os
import base64
import pandas as pd
from datetime import datetime

# ================== 1. الإعدادات والتنسيق ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_base64_logo("1000357687.jpg")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ direction: rtl; background-color: #f8fafc; }}
    * {{ font-family: 'Cairo', sans-serif; text-align: right; }}
    .status-box {{ padding: 12px; border-radius: 10px; margin-top: 10px; font-weight: bold; border: 1px solid; }}
    .status-paid {{ background-color: #dcfce7; color: #166534; border-color: #bbf7d0; }}
    .status-debt {{ background-color: #fee2e2; color: #991b1b; border-color: #fecaca; }}
    .status-partial {{ background-color: #fef9c3; color: #854d0e; border-color: #fef08a; }}
    .main-card {{ background: white; border-radius: 15px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }}
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

# ================== 3. واجهة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        c = next((x for x in st.session_state.data if x['id'] == c_id), None)
        if c:
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=150)
            st.title(f"مرحباً، {c['name']}")
            
            history = c.get('history', [])
            total_rem = sum(float(h.get('debt', 0)) - float(h.get('price', 0)) for h in history)
            
            st.markdown(f"<div class='main-card'><h3 style='text-align:center;'>إجمالي المديونية: {total_rem:,.1f} ج.م</h3></div>", unsafe_allow_html=True)
            
            st.subheader("📋 سجل الصيانات")
            for h in reversed(history):
                cost = float(h.get('debt', 0))
                paid = float(h.get('price', 0))
                rem = cost - paid
                shama = h.get('shama', 0)
                
                if cost > 0 and rem > 0 and paid > 0:
                    msg = f"<div class='status-box status-partial'>🚩 متبقي من الزيارة: {rem:,.1f} ج.م (دفع {paid} من {cost})</div>"
                elif cost > 0 and paid == 0:
                    msg = f"<div class='status-box status-debt'>⚠️ مديونية كاملة: {cost:,.1f} ج.م</div>"
                else:
                    msg = f"<div class='status-box status-paid'>✅ تم السداد: {paid:,.1f} ج.م</div>"
                
                st.markdown(f"""
                <div class='main-card' style='margin-bottom:10px;'>
                    <p style='color:#64748b; font-size:0.8em;'>📅 {h['date']} | 🛠️ الفني: {h.get('tech', 'الإدارة')}</p>
                    <p><b>📝 الملاحظة:</b> {h['note']}</p>
                    <p style='color:#0369a1;'><b>🪛 الشمع المستهلك:</b> {shama} شمعة</p>
                    {msg}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. نظام الإدارة والتقارير ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>Power Life System</h1>", unsafe_allow_html=True)
    if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=250)
    if st.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if st.button("🛠️ دخول الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- لوحة الإدارة ---
if st.session_state.role == "admin":
    menu = st.sidebar.radio("الرئيسية", ["العملاء", "إضافة عميل", "تقارير الفنيين (الحصالة)", "الفنيين", "خروج"])
    
    if menu == "العملاء":
        search = st.text_input("بحث بالاسم")
        for c in st.session_state.data:
            if not search or search in c['name']:
                with st.expander(f"👤 {c['name']}"):
                    st.write(f"📞 هاتف: {c['phone']}")
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    # إضافة تحصيل من المدير
                    with st.form(f"f{c['id']}"):
                        d1 = st.number_input("تكلفة", 0.0); d2 = st.number_input("تحصيل", 0.0)
                        sh = st.number_input("شمع", 0); nt = st.text_input("ملاحظة")
                        if st.form_submit_button("حفظ"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": nt, "debt": d1, "price": d2, "shama": sh, "tech": "المدير"})
                            save_db("customers.json", st.session_state.data); st.rerun()

    elif menu == "تقارير الفنيين (الحصالة)":
        st.subheader("💰 حصالة الفنيين واستهلاك الشمع")
        reports = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                reports.append({
                    "الفني": h.get('tech', 'الإدارة'),
                    "المبلغ المحصل": float(h.get('price', 0)),
                    "شمع مستهلك": int(h.get('shama', 0)),
                    "التاريخ": h.get('date')
                })
        if reports:
            df = pd.DataFrame(reports)
            st.table(df.groupby("الفني")[["المبلغ المحصل", "شمع مستهلك"]].sum())
        else: st.info("لا توجد بيانات حالياً")

    elif menu == "خروج": del st.session_state.role; st.rerun()

# --- لوحة الفني ---
elif st.session_state.role == "tech_p":
    st.header(f"🛠️ فني: {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("اختر العميل", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    
    if target:
        with st.form("tech_form"):
            st.info(f"📍 موقع العميل: {target.get('gps', 'غير مسجل')}")
            cost = st.number_input("إجمالي تكلفة الزيارة", 0.0)
            paid = st.number_input("المبلغ اللي استلمته (الحصالة)", 0.0)
            shama = st.number_input("عدد الشمع المستهلك", 0, step=1)
            note = st.text_area("وصف العمل (مثال: تغيير شمعة 1 و 2)")
            if st.form_submit_button("✅ إرسال التقرير النهائي"):
                target['history'].append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note,
                    "tech": st.session_state.c_tech,
                    "debt": cost,
                    "price": paid,
                    "shama": shama
                })
                save_db("customers.json", st.session_state.data); st.success("تم الحفظ وتحديث حصالتك!")
    
    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()

# --- تسجيل دخول (Logic) ---
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
elif st.session_state.role == "tech_login":
    tn = [t['name'] for t in st.session_state.techs]
    user = st.selectbox("اسم الفني", tn) if tn else st.error("لا فنيين")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        t = next((x for x in st.session_state.techs if x['name'] == user), None)
        if t and p == t['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = user; st.rerun()
