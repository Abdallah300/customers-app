import streamlit as st
import json
import os
from datetime import datetime, timedelta

# ================== 1. إعدادات النظام ==================
# 🔴 هام: ضع رابط تطبيقك هنا بعد الرفع ليعمل الباركود
APP_URL = "https://your-app-name.streamlit.app" 

st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-x: hidden !important; direction: rtl; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    
    /* تصميم الكروت */
    .client-card { 
        background: linear-gradient(145deg, #001f3f, #001529); 
        border: 1px solid #007bff; 
        border-radius: 15px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.1);
    }
    
    /* الأزرار والحقول */
    div.stButton > button { width: 100% !important; border-radius: 10px; height: 50px; font-weight: bold; }
    .stSelectbox, .stTextInput, .stNumberInput, .stDateInput { margin-bottom: 10px; }
    
    /* سجل العمليات */
    .history-card { 
        background: rgba(255, 255, 255, 0.05); 
        border-radius: 8px; padding: 12px; margin-top: 8px; 
        border-right: 4px solid #00d4ff; font-size: 14px;
    }
    .status-ok { color: #00d4ff; font-weight: bold; }
    .status-alert { color: #ff4b4b; font-weight: bold; }
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

def refresh_all_data():
    st.session_state.data = load_json("customers.json", [])
    st.session_state.techs = load_json("techs.json", [])

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (QR View) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            
            # عرض موعد الصيانة القادم للعميل
            next_v = c.get('next_visit', 'غير محدد')
            
            st.markdown(f"""
            <div class='client-card'>
                <h2 style='text-align:center;'>{c['name']}</h2>
                <hr style='border-color: #007bff;'>
                <p style='text-align:center; font-size:20px;'>المتبقي عليك: <span class='status-alert'>{bal:,.0f} ج.م</span></p>
                <p style='text-align:center; font-size:16px;'>📅 موعد الصيانة القادم: <span class='status-ok'>{next_v}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("📝 سجل الزيارات السابق:")
            for h in reversed(c.get('history', [])):
                st.markdown(f'<div class="history-card"><b>📅 {h["date"]}</b><br>🛠️ {h.get("note", "")}<br>💰 الحساب: {float(h.get("debt",0)) - float(h.get("price",0))} ج.م</div>', unsafe_allow_html=True)
            st.stop()
    except:
        st.error("رابط غير صالح")
        st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<br><br><h1 style='text-align:center;'>⚡ Power Life System</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    with c2:
        if st.button("🛠️ الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    st.markdown("### دخول المدير")
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        if p == "admin123": st.session_state.role = "admin"; st.rerun()
        else: st.error("خطأ")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    st.markdown("### دخول الفنيين")
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_list) if t_list else st.write("لا يوجد فنيين")
    p = st.text_input("الكود السري", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']:
            st.session_state.role = "tech_p"
            st.session_state.c_tech = t_user
            st.rerun()
        else: st.error("بيانات خاطئة")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    with st.sidebar:
        st.title("لوحة التحكم")
        menu = st.radio("القائمة", ["👥 العملاء", "➕ إضافة عميل", "🛠️ الفنيين", "🚪 خروج"])
        st.markdown("---")
        if st.button("تحديث البيانات"): refresh_all_data(); st.rerun()

    if menu == "👥 العملاء":
        search = st.text_input("🔍 بحث (الاسم / الهاتف)")
        
        # تنبيهات المواعيد
        st.caption("🔔 عملاء يحتاجون صيانة قريباً:")
        today = datetime.now().date()
        for c in st.session_state.data:
            if c.get('next_visit'):
                d_obj = datetime.strptime(c['next_visit'], "%Y-%m-%d").date()
                if 0 <= (d_obj - today).days <= 7:
                    st.warning(f"العميل: {c['name']} | الموعد: {c['next_visit']}")

        st.divider()

        for c in st.session_state.data:
            if not search or search in c['name'] or search in str(c.get('phone','')):
                with st.expander(f"👤 {c['name']} (متبقي: {calculate_balance(c.get('history', []))} ج.م)"):
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        # توليد الباركود
                        qr_url = f"{APP_URL}/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={qr_url}")
                        st.caption("امسح الكود لعرض الحساب")
                        if c.get('gps'): st.link_button("📍 اللوكيشن", c['gps'])
                    
                    with c2:
                        # تعديل البيانات الأساسية
                        new_name = st.text_input("الاسم", c['name'], key=f"n_{c['id']}")
                        new_phone = st.text_input("الهاتف", c.get('phone',''), key=f"p_{c['id']}")
                        new_date = st.date_input("موعد الصيانة القادم", 
                                                 value=datetime.strptime(c['next_visit'], "%Y-%m-%d") if c.get('next_visit') else None,
                                                 key=f"d_{c['id']}")
                        
                        if st.button("حفظ التعديلات", key=f"s_{c['id']}"):
                            c['name'] = new_name
                            c['phone'] = new_phone
                            c['next_visit'] = str(new_date)
                            save_json("customers.json", st.session_state.data)
                            st.success("تم الحفظ")
                            st.rerun()
                        
                        # عملية مالية سريعة
                        st.markdown("---")
                        col_a, col_b = st.columns(2)
                        d_in = col_a.number_input("مطلوب (+)", 0.0, key=f"in_{c['id']}")
                        d_out = col_b.number_input("تم دفع (-)", 0.0, key=f"out_{c['id']}")
                        if st.button("تسجيل عملية يدوية", key=f"proc_{c['id']}"):
                            c.setdefault('history', []).append({
                                "date": datetime.now().strftime("%Y-%m-%d"),
                                "note": "تسجيل إداري", "tech": "Admin", "debt": d_in, "price": d_out
                            })
                            save_json("customers.json", st.session_state.data)
                            st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new_client"):
            n = st.text_input("اسم العميل")
            p = st.text_input("رقم الهاتف")
            g = st.text_input("رابط الخريطة")
            d = st.date_input("تاريخ أول صيانة قادمة", value=datetime.now() + timedelta(days=90))
            if st.form_submit_button("حفظ العميل"):
                nid = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": nid, "name": n, "phone": p, "gps": g, 
                    "history": [], "next_visit": str(d)
                })
                save_json("customers.json", st.session_state.data)
                st.success("تم!")

    elif menu == "🛠️ الفنيين":
        with st.form("add_t"):
            name = st.text_input("اسم الفني")
            pw = st.text_input("كلمة السر")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": name, "pass": pw})
                save_json("techs.json", st.session_state.techs)
                st.success("تم")
        
        st.write("📊 تقرير أداء الفنيين:")
        report = []
        for t in st.session_state.techs:
            count = 0
            money = 0
            for c in st.session_state.data:
                for h in c.get('history', []):
                    if h.get('tech') == t['name']:
                        count += 1
                        money += float(h.get('price', 0))
            report.append({"الفني": t['name'], "الزيارات": count, "التحصيل": money})
        st.table(report)

    elif menu == "🚪 خروج":
        del st.session_state.role; st.rerun()

# ================== 6. لوحة الفني ==================
elif st.session_state.role == "tech_p":
    st.info(f"👤 الفني الحالي: {st.session_state.c_tech}")
    
    # اختيار العميل
    names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("اختر العميل", list(names.keys()), format_func=lambda x: names[x])
    target = next((c for c in st.session_state.data if c['id'] == sid), None)
    
    if target:
        if target.get('gps'): st.link_button("📍 فتح الخريطة", target['gps'], use_container_width=True)
        
        st.markdown(f"<div class='client-card'>الرصيد السابق: {calculate_balance(target.get('history', []))} ج.م</div>", unsafe_allow_html=True)
        
        with st.form("tech_action"):
            note = st.text_area("تفاصيل الصيانة / القطع المركبة")
            cost = st.number_input("التكلفة المطلوبة", 0.0)
            paid = st.number_input("المبلغ المستلم", 0.0)
            next_d = st.date_input("موعد الصيانة القادم", value=datetime.now() + timedelta(days=90))
            
            if st.form_submit_button("✅ حفظ الزيارة"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note, "tech": st.session_state.c_tech,
                    "debt": cost, "price": paid
                })
                target['next_visit'] = str(next_d)
                save_json("customers.json", st.session_state.data)
                st.success("تم الحفظ وتحديث الموعد!")
                
    if st.button("خروج"): del st.session_state.role; st.rerun()
