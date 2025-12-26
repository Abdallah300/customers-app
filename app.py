import streamlit as st
import json
import os
import base64
from datetime import datetime

# ================== 1. الهوية والبصمة البصرية ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

def get_base64_logo(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# تأكد أن اسم ملف الصورة هو 1000357687.jpg في نفس المجلد
logo_b64 = get_base64_logo("1000357687.jpg")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {{ direction: rtl; background-color: #f8fbff; }}
    * {{ font-family: 'Cairo', sans-serif; text-align: right; }}
    
    /* تصميم الكروت */
    .main-card {{ 
        background: white; border: 2px solid #0056b3; 
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }}
    .history-card {{ 
        background: white; border-radius: 12px; padding: 15px; 
        margin-top: 10px; border-right: 6px solid #00aaff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    /* أزرار الدخول */
    div.stButton > button {{ 
        width: 100% !important; border-radius: 12px; height: 55px; 
        background-color: #0056b3; color: white; font-size: 18px; font-weight: bold;
    }}
    
    /* رسائل الحالة */
    .status-msg {{ font-weight: bold; padding: 5px 10px; border-radius: 5px; display: inline-block; margin-top: 5px; }}
    .paid {{ background-color: #e8f5e9; color: #2e7d32; }}
    .debt {{ background-color: #ffebee; color: #c62828; }}
    .partial {{ background-color: #fff3e0; color: #ef6c00; }}
    
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

# ================== 3. واجهة الباركود (العملاء) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            if logo_b64: st.image(f"data:image/jpeg;base64,{logo_b64}", width=200)
            st.markdown(f"<h1 style='text-align:center; color:#0056b3;'>Power Life 💧</h1>", unsafe_allow_html=True)
            
            history = c.get('history', [])
            total_bal = calculate_balance(history)
            
            st.markdown(f"""
            <div class='main-card'>
                <h2 style='text-align:center; margin:0;'>{c['name']}</h2>
                <hr>
                <div style='text-align:center;'>
                    <p style='color:#666; margin:0;'>إجمالي المديونية الكلية</p>
                    <h1 style='color:#d32f2f; margin:0;'>{total_bal:,.1f} ج.م</h1>
                </div>
            </div>
            <h3 style='padding-right:10px;'>📜 سجل عمليات الصيانة والتحصيل</h3>
            """, unsafe_allow_html=True)
            
            for h in reversed(history):
                debt = float(h.get('debt', 0))   # التكلفة المطلوبة
                paid = float(h.get('price', 0))  # المبلغ المحصل
                remain = debt - paid             # المتبقي من هذه العملية
                
                # منطق رسالة الحالة
                if debt > 0 and remain == 0:
                    msg = f"<div class='status-msg paid'>✅ تم تحصيل كامل المبلغ ({paid:,.1f} ج.م)</div>"
                elif debt > 0 and paid == 0:
                    msg = f"<div class='status-msg debt'>⚠️ مديونية بالكامل: {debt:,.1f} ج.م</div>"
                elif debt > 0 and remain > 0:
                    msg = f"<div class='status-msg partial'>🔹 مدفوع: {paid:,.1f} | متبقي من العملية: {remain:,.1f} ج.م</div>"
                elif debt == 0 and paid > 0:
                    msg = f"<div class='status-msg paid'>💰 توريد مبلغ: {paid:,.1f} ج.م</div>"
                else:
                    msg = ""

                st.markdown(f"""
                <div class="history-card">
                    <div style='display:flex; justify-content:space-between; font-size:12px; color:#888;'>
                        <span>📅 {h["date"]}</span>
                        <span>🛠️ الفني: {h.get('tech', 'إدارة')}</span>
                    </div>
                    <div style='margin-top:8px; font-weight:bold;'>📝 {h["note"]}</div>
                    {msg}
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except: st.stop()

# ================== 4. صفحة الدخول (مع اللوجو) ==================
# هنا تم إضافة اللوجو والاسم لصفحة الدخول
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if logo_b64:
        st.image(f"data:image/jpeg;base64,{logo_b64}", use_container_width=True)
    st.markdown("<h1 style='text-align:center; color:#0056b3; margin-top:-20px;'>Power Life</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center; color:#666;'>نظام الإدارة الموحد 🔒</h4>", unsafe_allow_html=True)

if "role" not in st.session_state:
    st.write("---")
    if st.button("🔑 دخول الإدارة"): 
        st.session_state.role = "admin_login"
        st.rerun()
    if st.button("🛠️ دخول الفنيين"): 
        st.session_state.role = "tech_login"
        st.rerun()
    st.stop()

# (باقي كود تسجيل الدخول ولوحة المدير والفني كما هو)
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("تأكيد"):
        if u == "admin" and p == "admin123":
            st.session_state.role = "admin"
            st.rerun()
    if st.button("رجوع"):
        del st.session_state.role
        st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_names) if t_names else st.warning("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']:
            st.session_state.role = "tech_p"
            st.session_state.c_tech = t_user
            st.rerun()
    if st.button("رجوع"):
        del st.session_state.role
        st.rerun()
    st.stop()

# ================== 5. لوحة المدير ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "🚪 خروج"])
    
    if menu == "👥 العملاء":
        search = st.text_input("🔍 ابحث عن عميل...")
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower():
                with st.container():
                    st.markdown(f"<div class='main-card'><h3>👤 {c['name']}</h3>", unsafe_allow_html=True)
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        # رابط الباركود
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                        st.image(qr_url, caption="باركود العميل")
                        st.write(f"💰 المديونية: {calculate_balance(c.get('history', []))}")
                    with col_b:
                        with st.expander("⚙️ إضافة عملية يدوية"):
                            d1 = st.number_input("تكلفة الخدمة (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("المبلغ المحصل (-)", 0.0, key=f"r{c['id']}")
                            note = st.text_input("ملاحظات", key=f"n{c['id']}")
                            if st.button("حفظ العملية", key=f"b{c['id']}"):
                                c.setdefault('history', []).append({
                                    "date": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                                    "note": note, "debt": d1, "price": d2, "tech": "المدير"
                                })
                                save_json("customers.json", st.session_state.data)
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    elif menu == "➕ إضافة عميل":
        with st.form("add_c"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الهاتف")
            gps = st.text_input("رابط الموقع (GPS)")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "gps": gps, "history": []})
                save_json("customers.json", st.session_state.data)
                st.success("تمت إضافة العميل")

    elif menu == "🛠️ الفنيين":
        with st.form("add_t"):
            tn = st.text_input("اسم الفني")
            tp = st.text_input("كلمة السر")
            if st.form_submit_button("إضافة فني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs)
                st.rerun()
        st.write("📋 قائمة الفنيين:")
        for t in st.session_state.techs: st.text(f"• {t['name']}")

    elif menu == "🚪 خروج":
        del st.session_state.role
        st.rerun()

# ================== 6. لوحة الفني ==================
elif st.session_state.role == "tech_p":
    st.markdown(f"### 🛠️ مرحبا، {st.session_state.c_tech}")
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل", options=list(names.keys()), format_func=lambda x: names[x])
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    
    if target:
        if target.get('gps'): st.link_button("📍 فتح اللوكيشن", target['gps'])
        with st.form("tech_visit"):
            cost = st.number_input("إجمالي تكلفة الصيانة", 0.0)
            paid = st.number_input("المبلغ الذي تم تحصيله", 0.0)
            note = st.text_area("ماذا تم في الزيارة؟")
            if st.form_submit_button("✅ حفظ وإرسال التقرير"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %I:%M %p"),
                    "note": note, "tech": st.session_state.c_tech, "debt": cost, "price": paid
                })
                save_json("customers.json", st.session_state.data)
                st.success("تم تسجيل العملية بنجاح!")
    
    if st.button("🚪 تسجيل خروج"):
        del st.session_state.role
        st.rerun()  
