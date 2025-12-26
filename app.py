import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. إعدادات الصفحة والهوية ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# محاولة تحميل اللوجو
logo_b64 = get_base64_logo("1000357687.jpg")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ direction: rtl; background-color: #f9f9f9; }}
    * {{ font-family: 'Cairo', sans-serif; text-align: right; }}
    
    /* تنسيق صفحة الدخول */
    .login-header {{ text-align: center; padding: 20px; }}
    .login-title {{ color: #0056b3; font-size: 32px; font-weight: bold; margin-bottom: 5px; }}
    
    /* تنسيق الكروت */
    .client-card {{ 
        background: white; border: 2px solid #0056b3; 
        border-radius: 15px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    .history-card {{ 
        background: white; border-radius: 10px; padding: 15px; 
        margin-top: 10px; border-right: 8px solid #00aaff;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    
    /* مبالغ وحالات */
    .price-box {{ font-size: 16px; font-weight: bold; margin-top: 10px; padding: 8px; border-radius: 5px; }}
    .full-paid {{ background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
    .debt-box {{ background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
    .partial-box {{ background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_data()
if 'techs' not in st.session_state:
    if os.path.exists("techs.json"):
        with open("techs.json", "r", encoding="utf-8") as f: st.session_state.techs = json.load(f)
    else: st.session_state.techs = []

def calculate_total_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. عرض الباركود (للعميل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            # عرض اللوجو والاسم فوق خالص
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=180)
            st.markdown(f"<h1 style='text-align:center; color:#0056b3;'>Power Life 💧</h1>", unsafe_allow_html=True)
            
            history = c.get('history', [])
            total_bal = calculate_total_balance(history)
            
            st.markdown(f"""
            <div class='client-card'>
                <h2 style='text-align:center;'>{c['name']}</h2>
                <div style='text-align:center;'>
                    <p style='color:#666; margin-bottom:0;'>إجمالي المديونية الكلية المتبقية</p>
                    <h1 style='color:#d9534f; margin-top:0;'>{total_bal:,.1f} ج.م</h1>
                </div>
            </div>
            <h3 style='border-bottom: 2px solid #00aaff; padding-bottom: 5px;'>📋 سجل الصيانات والتحصيل</h3>
            """, unsafe_allow_html=True)
            
            for h in reversed(history):
                debt = float(h.get('debt', 0))   # التكلفة المطلوبة
                paid = float(h.get('price', 0))  # المحصل فعلياً
                remain = debt - paid             # المتبقي من العملية دي
                
                # تحديد جملة الحالة
                if debt > 0 and remain == 0:
                    status_html = f"<div class='price-box full-paid'>✅ تم تحصيل كامل المبلغ: {paid:,.1f} ج.م</div>"
                elif debt > 0 and paid == 0:
                    status_html = f"<div class='price-box debt-box'>⚠️ مديونية بالكامل: {debt:,.1f} ج.م</div>"
                elif debt > 0 and remain > 0:
                    status_html = f"<div class='price-box partial-box'>🔹 المدفوع: {paid:,.1f} ج.م | 🚩 المتبقي من العملية: {remain:,.1f} ج.م</div>"
                else:
                    status_html = f"<div class='price-box'>💰 توريد مبلغ: {paid:,.1f} ج.م</div>"

                st.markdown(f"""
                <div class="history-card">
                    <div style='display:flex; justify-content:space-between; font-size:13px; color:#777;'>
                        <span>📅 {h["date"]}</span>
                        <span>👤 الفني: {h.get('tech', 'إدارة')}</span>
                    </div>
                    <div style='margin:10px 0; font-weight:bold;'>📝 {h["note"]}</div>
                    {status_html}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. صفحة الدخول (اللوجو والاسم) ==================
if "role" not in st.session_state:
    st.markdown("<div class='login-header'>", unsafe_allow_html=True)
    if logo_b64:
        st.image(f"data:image/jpeg;base64,{logo_b64}", width=250)
    st.markdown("<h1 class='login-title'>Power Life</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666;'>نظام إدارة صيانة الفلاتر</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    with col2:
        if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# --- منطق تسجيل الدخول وإدارة المدير والفني (تكملة الكود) ---
# (يتم إضافة باقي الكود الخاص بالمدير والفني هنا للتأكد من عمل النظام بالكامل)
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("إلغاء"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسم الفني", t_names) if t_names else st.warning("لا فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("إلغاء"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["إدارة العملاء", "إضافة عميل", "الفنيين", "خروج"])
    if menu == "إدارة العملاء":
        search = st.text_input("ابحث عن عميل")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower():
                with st.expander(f"👤 {c['name']} - الرصيد: {calculate_total_balance(c.get('history', []))}"):
                    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                    st.image(qr_url)
                    d1 = st.number_input("التكلفة (+)", 0.0, key=f"d{c['id']}")
                    d2 = st.number_input("التحصيل (-)", 0.0, key=f"r{c['id']}")
                    n = st.text_input("ملاحظة", key=f"n{c['id']}")
                    if st.button("حفظ", key=f"b{c['id']}"):
                        c.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": n, "debt": d1, "price": d2, "tech": "المدير"})
                        save_data(st.session_state.data); st.rerun()
    elif menu == "إضافة عميل":
        with st.form("add"):
            n = st.text_input("الاسم"); p = st.text_input("الهاتف"); g = st.text_input("GPS")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "gps": g, "history": []})
                save_data(st.session_state.data); st.success("تم")
    elif menu == "الفنيين":
        with st.form("t"):
            tn = st.text_input("اسم الفني"); tp = st.text_input("السر")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                with open("techs.json", "w") as f: json.dump(st.session_state.techs, f)
                st.rerun()
    elif menu == "خروج": del st.session_state.role; st.rerun()

elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ الفني: {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("العميل", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        with st.form("visit"):
            cost = st.number_input("التكلفة الكلية", 0.0); paid = st.number_input("المحصل من العميل", 0.0)
            note = st.text_area("تفاصيل الصيانة")
            if st.form_submit_button("إرسال"):
                target.setdefault('history', []).append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid})
                save_data(st.session_state.data); st.success("تم!")
    if st.button("خروج"): del st.session_state.role; st.rerun()
