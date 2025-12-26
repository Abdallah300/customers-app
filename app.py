import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# ================== 1. التنسيق (نفس كودك بالظبط) ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-x: hidden !important; direction: rtl; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .client-card { 
        background: #001f3f; border: 2px solid #007bff; 
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
        width: 100% !important; display: block;
    }
    /* أزرار التواصل الجديدة */
    .btn-call { background-color: #007bff; color: white !important; padding: 8px 15px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 5px; }
    .btn-wa { background-color: #25d366; color: white !important; padding: 8px 15px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 5px; }
    
    div.stButton > button { width: 100% !important; border-radius: 8px; height: 45px; }
    .stSelectbox, .stTextInput, .stNumberInput { width: 100% !important; margin-bottom: 10px; }
    .history-card { background: rgba(0, 80, 155, 0.2); border-radius: 8px; padding: 12px; margin-top: 8px; border-right: 4px solid #00d4ff; }
    header, footer {visibility: hidden;}
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
    st.cache_data.clear()

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة الباركود للعميل (بدون أي تعديل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div class='client-card'><h2 style='text-align:center;'>{c['name']}</h2><p style='text-align:center; font-size:25px; color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</p></div>", unsafe_allow_html=True)
            for h in reversed(c.get('history', [])):
                st.markdown(f'<div class="history-card"><b>📅 {h["date"]}</b><br>📝 {h["note"]}<br>💰 العملية: {float(h.get("debt",0)) - float(h.get("price",0))} ج.م</div>', unsafe_allow_html=True)
            st.stop()
    except:
        st.error("خطأ في البيانات.")
        st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:30px;'>Power Life System 🔒</h2>", unsafe_allow_html=True)
    if st.button("🔑 دخول المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if st.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم"); p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_list) if t_list else st.write("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and p == tech['pass']: st.session_state.role = "tech_p"; st.session_state.c_tech = t_user; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    if st.button("🔄 تحديث ومزامنة البيانات", use_container_width=True):
        refresh_all_data(); st.rerun()
    menu = st.sidebar.radio("القائمة", ["👥 البحث والإدارة", "➕ إضافة عميل", "🛠️ مراقبة الفنيين", "📊 التقارير", "🚪 خروج"])
    
    if menu == "👥 البحث والإدارة":
        client_base_url = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"
        search = st.text_input("🔍 ابحث بالاسم أو التليفون...")
        
        for c in st.session_state.data:
            if not search or search.lower() in c['name'].lower() or search in str(c.get('phone','')):
                with st.container():
                    st.markdown(f'<div class="client-card">', unsafe_allow_html=True)
                    st.subheader(f"👤 {c['name']}")
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        qr_data = f"{client_base_url}/?id={c['id']}"
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={qr_data}")
                        if c.get('gps'): st.link_button("📍 موقع العميل", c['gps'])
                        st.write(f"💰 الرصيد: {calculate_balance(c.get('history', []))} ج.م")
                    
                    with col2:
                        with st.expander("📝 تعديل البيانات"):
                            c['name'] = st.text_input("الاسم", value=c['name'], key=f"n{c['id']}")
                            c['phone'] = st.text_input("التليفون", value=c.get('phone',''), key=f"p{c['id']}")
                            c['gps'] = st.text_input("رابط GPS", value=c.get('gps',''), key=f"g{c['id']}")
                            if st.button("حفظ التعديلات", key=f"s{c['id']}"): 
                                save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
                        
                        with st.expander("💸 عملية سريعة"):
                            d1 = st.number_input("إضافة مبلغ (+)", 0.0, key=f"d{c['id']}")
                            d2 = st.number_input("تحصيل مبلغ (-)", 0.0, key=f"r{c['id']}")
                            if st.button("تسجيل العملية", key=f"t{c['id']}"):
                                c.setdefault('history', []).append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "note": "تعديل إداري مباشر", "tech": "المدير", "debt": d1, "price": d2
                                })
                                save_json("customers.json", st.session_state.data); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            name = st.text_input("اسم العميل الجديد")
            phone = st.text_input("رقم التليفون")
            gps = st.text_input("رابط موقع Google Maps")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "gps": gps, "history": []})
                save_json("customers.json", st.session_state.data); st.success("تمت الإضافة!")

    elif menu == "🛠️ مراقبة الفنيين":
        st.write("🔧 إدارة الفنيين")
        with st.form("add_tech"):
            tn = st.text_input("اسم الفني الجديد"); tp = st.text_input("السر")
            if st.form_submit_button("إضافة فني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs); st.rerun()
        
        st.divider()
        st.write("📋 آخر العمليات المنفذة:")
        all_ops = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                all_ops.append({"التاريخ": h['date'], "الفني": h.get('tech',''), "العميل": c['name'], "ملاحظات": h['note']})
        if all_ops: st.table(reversed(all_ops))

    elif menu == "📊 التقارير":
        total = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي الديون الخارجية", f"{total:,.0f} ج.م")
        
        st.divider()
        st.subheader("📥 تصدير البيانات")
        df_list = []
        for c in st.session_state.data:
            df_list.append({"الاسم": c['name'], "التليفون": c.get('phone',''), "الرصيد": calculate_balance(c.get('history', []))})
        if df_list:
            df = pd.DataFrame(df_list)
            st.download_button("تحميل كشف العملاء (Excel)", df.to_csv(index=False).encode('utf-8-sig'), "PowerLife_Report.csv", "text/csv")

    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (مع أزرار التواصل وموعد الصيانة) ==================
elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ حساب الفني: {st.session_state.c_tech}")
    if st.button("🔄 تحديث القائمة", use_container_width=True): refresh_all_data(); st.rerun()
    
    customer_names = {c['id']: c['name'] for c in st.session_state.data}
    selected_id = st.selectbox("🎯 اختر العميل", options=list(customer_names.keys()), format_func=lambda x: customer_names[x])
    target = next((x for x in st.session_state.data if x['id'] == selected_id), None)
    
    if target:
        # أزرار تواصل سريعة للفني
        col_c1, col_c2 = st.columns(2)
        if target.get('phone'):
            with col_c1: st.markdown(f'<a href="tel:{target["phone"]}" class="btn-call">📞 اتصال هاتفى</a>', unsafe_allow_html=True)
            with col_c2: st.markdown(f'<a href="https://wa.me/2{target["phone"]}" class="btn-wa">💬 واتساب</a>', unsafe_allow_html=True)
        
        if target.get('gps'): st.link_button("📍 توجه إلى موقع العميل", target['gps'], use_container_width=True)
        
        st.divider()
        with st.form("visit_form"):
            v_add = st.number_input("تكلفة الصيانة/القطع", 0.0)
            v_rem = st.number_input("المحصل من العميل", 0.0)
            note = st.text_area("ملاحظات الفني")
            next_date = st.date_input("موعد الصيانة القادم المتوقع", value=datetime.now() + timedelta(days=90))
            
            if st.form_submit_button("✅ إرسال التقرير"):
                full_note = f"{note} | موعد الزيارة القادمة: {next_date}"
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x.setdefault('history', []).append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": full_note, "tech": st.session_state.c_tech, "debt": v_add, "price": v_rem
                        })
                save_json("customers.json", st.session_state.data); refresh_all_data(); st.success("تم الحفظ!")
    
    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
