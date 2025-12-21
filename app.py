import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. التنسيق العام (Power Life Style) ==================
# تم تعديل initial_sidebar_state لتكون القائمة مفتوحة تلقائياً
st.set_page_config(
    page_title="Power Life System", 
    page_icon="💧", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    /* تحسين التمرير وتنسيق الخلفية */
    html, body, [data-testid="stAppViewContainer"] { 
        overflow-y: auto !important; 
    }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق الكروت المالية */
    .metric-container { 
        background: rgba(0, 212, 255, 0.1); 
        border: 2px solid #00d4ff; 
        border-radius: 15px; 
        padding: 20px; 
        text-align: center; 
        margin: 10px; 
    }
    .metric-title { color: #ffffff; font-size: 18px; font-weight: bold; }
    .metric-value { color: #00d4ff; font-size: 28px; font-weight: bold; }

    .balance-box { 
        background: rgba(0, 255, 204, 0.15); 
        border: 1px solid #00ffcc; 
        border-radius: 10px; 
        padding: 15px; 
        text-align: center; 
        margin: 10px 0; 
    }
    
    .logo-text { 
        font-size: 45px; 
        font-weight: bold; 
        color: #00d4ff; 
        text-align: center; 
        display: block; 
        text-shadow: 2px 2px 10px #007bff; 
        padding: 10px; 
    }
    
    /* تحسين رؤية مربعات الإدخال */
    .stTextInput input, .stNumberInput input, .stSelectbox div { 
        background-color: #ffffff !important; 
        color: #000000 !important; 
        font-weight: bold !important;
    }

    /* إخفاء التذييل فقط وترك الهيدر لضمان ظهور زر القائمة الجانبية */
    footer {visibility: hidden;}
    
    /* تعديل اتجاه القائمة الجانبية لتناسب اللغة العربية */
    [data-testid="stSidebar"] {
        direction: rtl;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_and_refresh(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # تحديث الحالة اللحظية
    st.session_state.data = load_json("customers.json", []) 

if 'data' not in st.session_state or st.sidebar.button("🔄 تحديث البيانات"):
    st.session_state.data = load_json("customers.json", [])
    st.session_state.techs = load_json("techs.json", [])
    if 'data' in st.session_state: st.toast("تم مزامنة البيانات ✅")

def calculate_balance(history):
    try: 
        return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
    except: 
        return 0.0

# ================== 3. واجهة الباركود للعملاء ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"""
                <div style='text-align:center; background:rgba(0,212,255,0.1); padding:20px; border-radius:15px; border:1px solid #00d4ff;'>
                    <h2 style='color:white;'>مرحباً: {c['name']}</h2>
                    <h1 style='color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</h1>
                </div>
            """, unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.write(f"📅 {h.get('date','')}")
                if float(h.get('price', 0)) > 0: st.success(f"💰 تم دفع: {h['price']}")
                if float(h.get('debt', 0)) > 0: st.error(f"🛠️ تكلفة: {h['debt']}")
                st.write(f"📝 {h.get('note','-')}")
                st.markdown("---")
            st.stop()
    except: st.stop()

# ================== 4. نظام تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    if col1.button("🔑 المدير", use_container_width=True): 
        st.session_state.role = "admin_login"
        st.rerun()
    if col2.button("🛠️ الفنيين", use_container_width=True): 
        st.session_state.role = "tech_login"
        st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": 
            st.session_state.role = "admin"
            st.rerun()
        else: st.error("بيانات خاطئة")
    if st.button("رجوع"): 
        del st.session_state.role
        st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    if not t_names:
        st.error("لا يوجد فنيين مسجلين، يرجى مراجعة المدير")
    else:
        t_user = st.selectbox("اختر اسمك", t_names)
        p = st.text_input("كلمة السر", type="password")
        if st.button("دخول"):
            tech_data = next(t for t in st.session_state.techs if t['name'] == t_user)
            if p == tech_data['pass']: 
                st.session_state.role = "tech_panel"
                st.session_state.current_tech = t_user
                st.rerun()
            else: st.error("كلمة سر خاطئة")
    if st.button("رجوع"): 
        del st.session_state.role
        st.rerun()
    st.stop()

# ================== 5. واجهة المدير ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## ⚙️ لوحة التحكم")
    menu = st.sidebar.radio("انتقل إلى:", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📊 المالية":
        t_out = sum(calculate_balance(c['history']) for c in st.session_state.data)
        t_in = sum(sum(float(h.get('price', 0)) for h in c['history']) for c in st.session_state.data)
        t_serv = sum(sum(float(h.get('debt', 0)) for h in c['history']) for c in st.session_state.data)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-container'><div class='metric-title'>مديونية بره</div><div class='metric-value'>{t_out:,.0f}</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'><div class='metric-title'>المحصل كاش</div><div class='metric-value'>{t_in:,.0f}</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-container'><div class='metric-title'>صافي الربح تقريبي</div><div class='metric-value'>{(t_in - (t_serv * 0.4)):,.0f}</div></div>", unsafe_allow_html=True)

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث (اسم/كود/فون)...")
        q = search.strip().lower()
        filtered = [c for c in st.session_state.data if (q in c['name'].lower()) or (q == str(c['id'])) or (q in str(c.get('phone','')))]
        
        for c in filtered:
            bal = calculate_balance(c['history'])
            with st.expander(f"👤 {c['name']} | كود: {c['id']} | الرصيد: {bal:,.0f}"):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    if st.button("🗑️ حذف العميل", key=f"del{c['id']}"):
                        st.session_state.data.remove(c)
                        save_and_refresh("customers.json", st.session_state.data)
                        st.rerun()
                with col2:
                    with st.form(key=f"adm_form_{c['id']}", clear_on_submit=True):
                        a_d = st.number_input("تكلفة (+)", 0.0, key=f"ad{c['id']}")
                        a_p = st.number_input("تحصيل (-)", 0.0, key=f"ap{c['id']}")
                        a_f = st.multiselect("الشمع:", ["1", "2", "3", "4", "5", "6", "7", "ممبرين"], key=f"f{c['id']}")
                        a_n = st.text_input("البيان", key=f"an{c['id']}")
                        if st.form_submit_button("حفظ العملية 🚀"):
                            c['history'].append({
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                                "note": f"{a_n} - شمع: {', '.join(a_f)}", 
                                "tech": "المدير", "debt": a_d, "price": a_p, "filters": a_f
                            })
                            save_and_refresh("customers.json", st.session_state.data)
                            st.success("تم الحفظ")
                            st.rerun()

    elif menu == "🛠️ تقارير الفنيين":
        all_visits = []
        all_filters = []
        for c in st.session_state.data:
            for h in c['history']:
                if h.get('tech') and h.get('tech') != "المدير":
                    all_visits.append({"الفني": h['tech'], "العميل": c['name'], "المحصل": h.get('price', 0), "التاريخ": h['date']})
                    if h.get('filters'):
                        for f in h['filters']: all_filters.append({"الفني": h['tech'], "الشمعة": f})
        
        st.write("### سجل الزيارات")
        if all_visits: st.table(pd.DataFrame(all_visits))
        
        with st.expander("➕ إضافة فني جديد"):
            tn = st.text_input("اسم الفني الجديد")
            tp = st.text_input("كلمة السر للفني")
            if st.button("حفظ الفني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_and_refresh("techs.json", st.session_state.techs)
                st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n = st.text_input("اسم العميل")
            p = st.text_input("رقم التليفون")
            d = st.number_input("مديونية افتتاحية (إن وجد)")
            if st.form_submit_button("إضافة"):
                nid = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": nid, "name": n, "phone": p, 
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح الحساب", "debt": d, "price": 0, "tech": "المدير"}]
                })
                save_and_refresh("customers.json", st.session_state.data)
                st.success(f"تمت إضافة {n} بنجاح!")
                st.rerun()

    if menu == "🚪 خروج" or st.sidebar.button("تسجيل الخروج"):
        del st.session_state.role
        st.rerun()

# ================== 6. واجهة الفني ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: **{st.session_state.current_tech}**")
    t_menu = st.sidebar.radio("القائمة", ["📋 تنفيذ مهمة", "💰 محفظتي", "🚪 خروج"])

    if t_menu == "📋 تنفيذ مهمة":
        cust_list = {f"{c['id']} - {c['name']}": c for c in st.session_state.data}
        choice = st.selectbox("🔍 ابحث واختر العميل:", [""] + list(cust_list.keys()))
        if choice:
            selected = cust_list[choice]
            st.markdown(f"<div class='balance-box'><h3>رصيد العميل: {calculate_balance(selected['history']):,.0f} ج.م</h3></div>", unsafe_allow_html=True)
            with st.form("t_form"):
                v_d = st.number_input("تكلفة الصيانة (+)")
                v_p = st.number_input("المحصل من العميل (-)")
                v_f = st.multiselect("الشمع المستبدل:", ["1", "2", "3", "4", "5", "6", "7", "ممبرين"])
                v_n = st.text_area("ملاحظات")
                if st.form_submit_button("إرسال التقرير 🚀"):
                    selected['history'].append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "note": f"{v_n} - شمع: {', '.join(v_f)}",
                        "tech": st.session_state.current_tech, "debt": v_d, "price": v_p, "filters": v_f
                    })
                    save_and_refresh("customers.json", st.session_state.data)
                    st.success("تم الإرسال بنجاح ✅")
                    st.rerun()

    elif t_menu == "💰 محفظتي":
        cash = sum(float(h.get('price', 0)) for c in st.session_state.data for h in c['history'] if h.get('tech') == st.session_state.current_tech)
        st.metric("إجمالي الكاش معك", f"{cash:,.0f} ج.م")

    if t_menu == "🚪 خروج":
        del st.session_state.role
        st.rerun()
