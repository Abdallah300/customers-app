import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# ================== 1. إعدادات الرابط والمظهر ==================
# الرابط الخاص بك الذي زودتني به
BASE_URL = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"

st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; background-color: #000b1a; }
    * { font-family: 'Cairo', sans-serif; text-align: right; color: white; }
    
    /* تصميم كروت العملاء */
    .client-card { 
        background: linear-gradient(145deg, #001f3f, #001529); 
        border: 1px solid #007bff; border-radius: 15px; 
        padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2);
    }
    
    /* تنسيق الجداول والسجلات */
    .history-card { 
        background: rgba(255, 255, 255, 0.05); border-radius: 8px; 
        padding: 12px; margin-top: 8px; border-right: 4px solid #00d4ff; 
    }
    
    /* إخفاء شعارات ستريمليت لجمالية التصميم */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* تنسيق الأزرار */
    .stButton>button {
        width: 100%; border-radius: 10px; background-color: #007bff;
        color: white; font-weight: bold; border: none; height: 45px;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. محرك البيانات ==================
def load_data(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تحميل البيانات في الذاكرة
if 'data' not in st.session_state: st.session_state.data = load_data("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_data("techs.json", [])
if 'inventory' not in st.session_state: st.session_state.inventory = load_data("inventory.json", [])

def get_bal(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (تفتح عبر الرابط) ==================
params = st.query_params
if "id" in params:
    try:
        c_id = int(params["id"])
        cust = next((c for c in st.session_state.data if c['id'] == c_id), None)
        if cust:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            balance = get_bal(cust.get('history', []))
            
            st.markdown(f"""
            <div class='client-card'>
                <h2 style='text-align:center;'>أهلاً {cust['name']}</h2>
                <h3 style='text-align:center; color: {"#00ffcc" if balance <= 0 else "#ff4b4b"}'>
                    الحساب المتبقي: {balance:,.0f} ج.م
                </h3>
                <p style='text-align:center;'>📅 موعد الصيانة القادم: {cust.get('next_visit', 'سيتم تحديده قريباً')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("📜 سجل العمليات الأخير")
            for h in reversed(cust.get('history', [])):
                st.markdown(f"""
                <div class='history-card'>
                    <b>📅 التاريخ: {h['date']}</b><br>
                    📝 البيان: {h['note']}<br>
                    💰 القيمة: {float(h.get('debt',0)) - float(h.get('price',0))} ج.م
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except:
        st.error("رابط غير صالح")
        st.stop()

# ================== 4. بوابة الموظفين والإدارة ==================
if "role" not in st.session_state:
    st.markdown("<h1 style='text-align:center; padding: 50px;'>نظام Power Life Pro</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 دخول الإدارة"): st.session_state.role = "admin_auth"
    with col2:
        if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_auth"
    st.stop()

# --- التحقق من الهوية ---
if st.session_state.role == "admin_auth":
    pw = st.text_input("كلمة مرور المدير", type="password")
    if st.button("دخول"):
        if pw == "admin123": # يمكنك تغييرها
            st.session_state.role = "admin"
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_auth":
    t_names = [t['name'] for t in st.session_state.techs]
    u = st.selectbox("اختر اسمك", t_names) if t_names else st.error("لا يوجد فنيين مسجلين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == u), None)
        if tech and tech['pass'] == p:
            st.session_state.role = "tech_panel"
            st.session_state.user = u
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة (Admin) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["📊 التقارير", "👥 إدارة العملاء", "📦 المخازن", "🛠️ الفنيين", "🚪 خروج"])
    
    if menu == "📊 التقارير":
        st.header("📊 حالة الشغل العامة")
        total_out = sum(get_bal(c.get('history', [])) for c in st.session_state.data)
        c1, c2 = st.columns(2)
        c1.metric("إجمالي الديون بالخارج", f"{total_out:,.0f} ج.م")
        c2.metric("عدد العملاء", len(st.session_state.data))
        
        st.subheader("🔔 تنبيهات الصيانة (هذا الأسبوع)")
        today = datetime.now().date()
        for c in st.session_state.data:
            if c.get('next_visit'):
                try:
                    d = datetime.strptime(c['next_visit'], "%Y-%m-%d").date()
                    if 0 <= (d - today).days <= 7:
                        st.warning(f"العميل {c['name']} صيانته يوم {c['next_visit']} (📞 {c['phone']})")
                except: pass

    elif menu == "👥 إدارة العملاء":
        st.header("👤 قاعدة بيانات العملاء")
        tab1, tab2 = st.tabs(["البحث والبيانات", "إضافة عميل"])
        
        with tab1:
            q = st.text_input("🔍 ابحث بالاسم أو التليفون")
            for c in st.session_state.data:
                if not q or q in c['name'] or q in str(c.get('phone','')):
                    with st.expander(f"👤 {c['name']} - (الحساب: {get_bal(c.get('history', [])):,.0f})"):
                        # توليد الرابط الصحيح والباركود
                        personal_link = f"{BASE_URL}/?id={c['id']}"
                        
                        col_a, col_b = st.columns([1, 2])
                        with col_a:
                            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={personal_link}")
                            st.write("رابط العميل المباشر:")
                            st.code(personal_link)
                            if c.get('gps'): st.link_button("📍 موقع جوجل", c['gps'])
                            
                        with col_b:
                            c['phone'] = st.text_input("رقم الهاتف", c.get('phone',''), key=f"ph_{c['id']}")
                            c['next_visit'] = str(st.date_input("موعد الصيانة القادم", 
                                                value=datetime.strptime(c['next_visit'], "%Y-%m-%d") if c.get('next_visit') else datetime.now(),
                                                key=f"dt_{c['id']}"))
                            if st.button("حفظ البيانات", key=f"sv_{c['id']}"):
                                save_data("customers.json", st.session_state.data)
                                st.success("تم التحديث")
                            
                            # زر واتساب سريع
                            msg = f"مرحباً سيد {c['name']}، نذكركم بموعد صيانة الفلتر القادم بتاريخ {c['next_visit']}. باور لايف تتمنى لكم يوماً سعيداً."
                            st.link_button("💬 إرسال تذكير واتساب", f"https://wa.me/2{c['phone']}?text={msg}")

        with tab2:
            with st.form("new_c"):
                name = st.text_input("الاسم")
                phone = st.text_input("الهاتف")
                gps = st.text_input("رابط الموقع (اختياري)")
                if st.form_submit_button("إضافة"):
                    new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                    st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "gps": gps, "history": [], "next_visit": ""})
                    save_data("customers.json", st.session_state.data)
                    st.rerun()

    elif menu == "📦 المخازن":
        st.header("📦 مخزن قطع الغيار")
        col1, col2 = st.columns(2)
        with col1:
            item = st.text_input("اسم القطعة (مثلاً: شمعة 1)")
            price = st.number_input("سعر البيع للعميل", min_value=0)
            if st.button("إضافة للمخزن"):
                st.session_state.inventory.append({"item": item, "price": price})
                save_data("inventory.json", st.session_state.inventory)
                st.rerun()
        with col2:
            st.write("قائمة الأصناف:")
            st.table(st.session_state.inventory)

    elif menu == "🛠️ الفنيين":
        st.header("🛠️ طاقم الفنيين")
        with st.form("t"):
            tn = st.text_input("اسم الفني")
            tp = st.text_input("كلمة السر")
            if st.form_submit_button("إضافة فني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_data("techs.json", st.session_state.techs)
                st.rerun()
        st.table(st.session_state.techs)

    elif menu == "🚪 خروج":
        del st.session_state.role
        st.rerun()

# ================== 6. لوحة الفني (Tech Panel) ==================
elif st.session_state.role == "tech_panel":
    st.header(f"أهلاً {st.session_state.user} 🛠️")
    
    # اختيار العميل
    c_names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("🎯 اختر العميل الذي تزوره", options=list(c_names.keys()), format_func=lambda x: c_names[x])
    target = next((c for c in st.session_state.data if c['id'] == sid), None)
    
    if target:
        st.info(f"💰 الحساب المتبقي على العميل: {get_bal(target.get('history', []))} ج.م")
        if target.get('gps'): st.link_button("🚀 فتح الخريطة للتوجه للعميل", target['gps'])
        
        with st.form("visit"):
            # اختيار القطع من المخزن
            items_list = [i['item'] for i in st.session_state.inventory]
            used = st.multiselect("القطع التي تم تركيبها", items_list)
            
            # حساب تلقائي للتكلفة
            auto_cost = sum(i['price'] for i in st.session_state.inventory if i['item'] in used)
            st.write(f"💵 تكلفة القطع التلقائية: {auto_cost}")
            
            labor = st.number_input("مصنعية إضافية (اختياري)", value=0)
            total_req = auto_cost + labor
            paid = st.number_input("المبلغ الذي تم تحصيله من العميل", value=total_req)
            
            note = st.text_area("ملاحظات الزيارة (مثلاً: تغيير شمعات)")
            next_date = st.date_input("موعد الزيارة القادم", value=datetime.now() + timedelta(days=90))
            
            if st.form_submit_button("✅ حفظ وإرسال التقرير"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": f"{note} (القطع: {', '.join(used)})",
                    "tech": st.session_state.user,
                    "debt": total_req, "price": paid
                })
                target['next_visit'] = str(next_date)
                save_data("customers.json", st.session_state.data)
                st.success("تم تسجيل العملية بنجاح!")
                st.balloons()
                
    if st.button("🚪 تسجيل الخروج"):
        del st.session_state.role
        st.rerun()
