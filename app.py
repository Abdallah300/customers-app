import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. الهوية البصرية والألوان الثابتة ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_base64_logo("1000357687.jpg")

# تنسيق الألوان (أزرق احترافي + خلفيات ملونة ثابتة)
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* إجبار الخلفية العامة على لون مريح */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: #eef2f7 !important;
        direction: rtl;
    }}
    
    * {{ font-family: 'Cairo', sans-serif; text-align: right; }}

    /* كارت العميل الرئيسي */
    .main-card {{ 
        background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%) !important;
        border: 2px solid #0056b3; 
        border-radius: 20px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        color: #1e293b !important;
    }}
    
    /* كروت العمليات */
    .history-card {{ 
        background: #ffffff !important; border-radius: 15px; padding: 15px; 
        margin-top: 15px; border-right: 10px solid #00aaff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        color: #1e293b !important;
    }}

    /* بوكسات الحالة الملونة */
    .status-box {{ padding: 12px; border-radius: 10px; font-weight: bold; margin-top: 10px; border: 1px solid; }}
    .status-paid {{ background-color: #dcfce7 !important; color: #15803d !important; border-color: #bbf7d0; }}
    .status-debt {{ background-color: #fee2e2 !important; color: #b91c1c !important; border-color: #fecaca; }}
    .status-partial {{ background-color: #fef9c3 !important; color: #a16207 !important; border-color: #fef08a; }}

    /* الأزرار */
    div.stButton > button {{ 
        background: linear-gradient(90deg, #0056b3, #00aaff) !important;
        color: white !important; border-radius: 12px; border: none; padding: 10px 20px;
    }}
</style>
""", unsafe_allow_html=True)

# ================== 2. نظام البيانات ==================
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

# ================== 3. واجهة العميل (باركود) ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        c = next((x for x in st.session_state.data if x['id'] == c_id), None)
        if c:
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=180)
            st.markdown(f"<h1 style='color:#0056b3; text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            
            history = c.get('history', [])
            st.markdown(f"""
            <div class='main-card'>
                <h2 style='margin:0;'>👤 {c['name']}</h2>
                <p style='color:#555;'>نوع التعاقد: <b>{c.get('device_type', 'صيانة')}</b></p>
                <div style='background:#f8d7da; padding:15px; border-radius:12px; margin-top:10px;'>
                    <p style='margin:0; color:#721c24;'>إجمالي المتبقي عليك حالياً:</p>
                    <h1 style='margin:0; color:#d32f2f;'>{get_total_balance(history):,.1f} ج.م</h1>
                </div>
            </div>
            <h3 style='color:#0056b3;'>📜 سجل العمليات</h3>
            """, unsafe_allow_html=True)
            
            for h in reversed(history):
                cost = float(h.get('debt', 0))
                paid = float(h.get('price', 0))
                rem = cost - paid
                shama = h.get('shama', 0)
                
                # حساب رسالة المبلغ المتبقي لكل عملية
                if cost > 0 and rem > 0 and paid > 0:
                    status = f"<div class='status-box status-partial'>🚩 متبقي من هذه الزيارة: {rem:,.1f} ج.م (دفع {paid} من {cost})</div>"
                elif cost > 0 and paid == 0:
                    status = f"<div class='status-box status-debt'>⚠️ لم يتم دفع أي مبلغ (مديونية: {cost:,.1f})</div>"
                elif cost == 0 and paid > 0:
                    status = f"<div class='status-box status-paid'>💰 سداد مديونية سابقة بمبلغ: {paid:,.1f} ج.م</div>"
                else:
                    status = f"<div class='status-box status-paid'>✅ عملية مسددة بالكامل ({paid:,.1f} ج.م)</div>"

                st.markdown(f"""
                <div class='history-card'>
                    <div style='display:flex; justify-content:space-between; font-size:0.8em; color:#888;'>
                        <span>📅 {h['date']}</span>
                        <span>🛠️ الفني: {h.get('tech', 'الإدارة')}</span>
                    </div>
                    <p style='font-size:1.1em; margin:10px 0;'>📝 {h['note']}</p>
                    {f"<p style='color:#0056b3;'><b>⚙️ الشمع المستهلك:</b> {shama}</p>" if shama else ""}
                    {status}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. لوحة الإدارة والفنيين ==================
if "role" not in st.session_state:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", use_container_width=True)
        st.markdown("<h1 style='text-align:center; color:#0056b3;'>نظام Power Life 💧</h1>", unsafe_allow_html=True)
        if st.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
        st.write("")
        if st.button("🛠️ دخول الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- الإدارة ---
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "➕ إضافة عميل/جهاز", "📊 تقارير الحصالة", "🚪 خروج"])
    
    if menu == "👥 العملاء":
        search = st.text_input("🔍 ابحث عن عميل")
        for c in st.session_state.data:
            if not search or search in c['name']:
                with st.expander(f"👤 {c['name']} (الحساب: {get_total_balance(c['history'])})"):
                    st.write(f"📱 الهاتف: {c.get('phone')}")
                    st.write(f"🏗️ النوع: {c.get('device_type')}")
                    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                    st.image(qr, caption="QR العميل")
                    
                    with st.form(f"admin_act_{c['id']}"):
                        st.write("🔧 إضافة عملية يدوية (قسط أو صيانة)")
                        d1 = st.number_input("إضافة مبلغ (+)", 0.0)
                        d2 = st.number_input("تحصيل مبلغ (-)", 0.0)
                        sh = st.number_input("شمع مستهلك", 0)
                        nt = st.text_input("ملاحظات")
                        if st.form_submit_button("حفظ"):
                            c['history'].append({"date": datetime.now().strftime("%Y-%m-%d"), "note": nt, "debt": d1, "price": d2, "shama": sh, "tech": "الإدارة"})
                            save_db("customers.json", st.session_state.data); st.rerun()

    elif menu == "➕ إضافة عميل/جهاز":
        with st.form("new_device"):
            name = st.text_input("الاسم")
            phone = st.text_input("الموبايل")
            dtype = st.selectbox("نوع الجهاز/التعاقد", ["جهاز جديد 7 مراحل", "جهاز جديد 5 مراحل", "عميل خارجي", "أخرى"])
            total_p = st.number_input("السعر الكلي (أو المديونية الأولى)", 0.0)
            down_p = st.number_input("المبلغ المدفوع مقدمًا", 0.0)
            if st.form_submit_button("تسجيل العميل"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": new_id, "name": name, "phone": phone, "device_type": dtype,
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": f"بداية تعاقد {dtype}", "debt": total_p, "price": down_p, "tech": "الإدارة"}]
                })
                save_db("customers.json", st.session_state.data); st.success("تم الإضافة!")

    elif menu == "📊 تقارير الحصالة":
        st.header("💰 تقرير تحصيل الفنيين")
        all_h = []
        for c in st.session_state.data:
            for h in c['history']:
                all_h.append({"الفني": h.get('tech'), "المبلغ": float(h.get('price', 0)), "شمع": h.get('shama', 0)})
        import pandas as pd
        df = pd.DataFrame(all_h)
        if not df.empty:
            st.table(df.groupby("الفني").sum())
        else: st.info("لا توجد بيانات")

    elif menu == "خروج": del st.session_state.role; st.rerun()

# --- الفني ---
elif st.session_state.role == "tech_p":
    st.title(f"🛠️ فني: {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("اختر العميل", list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        with st.form("visit"):
            st.info(f"نوع الجهاز: {target.get('device_type')}")
            cost = st.number_input("تكلفة الزيارة", 0.0)
            paid = st.number_input("المبلغ اللي استلمته", 0.0)
            shama = st.number_input("عدد الشمع", 0)
            note = st.text_area("ماذا تم في الزيارة؟")
            if st.form_submit_button("إرسال التقرير"):
                target['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "debt": cost, "price": paid, "shama": shama, "tech": st.session_state.c_tech})
                save_db("customers.json", st.session_state.data); st.success("تم!")
    if st.button("خروج"): del st.session_state.role; st.rerun()

# --- تسجيل الدخول (Backend) ---
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
