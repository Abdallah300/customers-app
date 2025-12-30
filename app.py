import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# ================== 1. إعدادات النظام والمظهر ==================
st.set_page_config(page_title="Power Life Pro v3", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { direction: rtl; background-color: #f0f2f6; color: #1f1f1f; }
    * { font-family: 'Cairo', sans-serif; }
    
    .metric-card {
        background: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;
        border-right: 5px solid #0056b3; margin-bottom: 10px;
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #0056b3; }
    .metric-label { color: #666; font-size: 14px; }
    
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .success-text { color: #28a745; font-weight: bold; }
    .danger-text { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================== 2. محرك البيانات (قاعدة البيانات) ==================
FILES = {
    "customers": "customers_v3.json",
    "techs": "techs_v3.json",
    "inventory": "inventory_v3.json"
}

def load_data():
    data = {}
    for key, file in FILES.items():
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                try: data[key] = json.load(f)
                except: data[key] = []
        else:
            data[key] = []
    return data

def save_data(key, new_data):
    with open(FILES[key], "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    st.session_state.db[key] = new_data

if 'db' not in st.session_state:
    st.session_state.db = load_data()

def get_balance(history):
    debt = sum(float(h.get('debt', 0)) for h in history)
    paid = sum(float(h.get('paid', 0)) for h in history)
    return debt - paid

# ================== 3. واجهة العميل (QR Code) ==================
if "id" in st.query_params:
    cid = int(st.query_params["id"])
    cust = next((c for c in st.session_state.db['customers'] if c['id'] == cid), None)
    if cust:
        st.markdown(f"<h2 style='text-align:center;'>مرحباً {cust['name']} 👋</h2>", unsafe_allow_html=True)
        bal = get_balance(cust.get('history', []))
        
        st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>حالة الحساب</div>
                <div class='metric-value' style='color: {"#dc3545" if bal > 0 else "#28a745"}'>{bal:,.0f} ج.م</div>
                <small>{'عليك مبالغ مستحقة' if bal > 0 else 'حسابك خالص تماماً'}</small>
            </div>
        """, unsafe_allow_html=True)
        
        # الجدول الزمني للصيانة
        if cust.get('next_visit'):
            days_left = (datetime.strptime(cust['next_visit'], "%Y-%m-%d") - datetime.now()).days
            color = "red" if days_left < 0 else "green"
            st.info(f"📅 موعد الصيانة القادم: {cust['next_visit']} (باقي {days_left} يوم)")

        with st.expander("📜 كشف الحساب التفصيلي"):
            df = pd.DataFrame(cust.get('history', []))
            if not df.empty:
                st.table(df[['date', 'item', 'debt', 'paid']].rename(columns={
                    'date': 'التاريخ', 'item': 'البيان', 'debt': 'مطلوب', 'paid': 'مدفوع'
                }))
    else:
        st.error("رابط غير صحيح")
    st.stop()

# ================== 4. بوابة الدخول الموحدة ==================
if "role" not in st.session_state:
    c1, c2 = st.columns(2)
    with c1:
        st.image("https://cdn-icons-png.flaticon.com/512/906/906343.png", width=100)
        st.title("بوابة الإدارة")
        if st.button("دخول الإدارة"):
            st.session_state.auth_step = "admin"
            st.rerun()
    with c2:
        st.image("https://cdn-icons-png.flaticon.com/512/1995/1995429.png", width=100)
        st.title("بوابة الفنيين")
        if st.button("دخول الفنيين"):
            st.session_state.auth_step = "tech"
            st.rerun()
    
    # حقل الإدخال حسب الاختيار
    if "auth_step" in st.session_state:
        st.divider()
        if st.session_state.auth_step == "admin":
            pw = st.text_input("كلمة مرور المدير", type="password")
            if st.button("تأكيد الدخول"):
                if pw == "admin123": # غيرها لاحقاً
                    st.session_state.role = "admin"
                    st.rerun()
                else: st.error("خطأ!")
                
        elif st.session_state.auth_step == "tech":
            tnames = [t['name'] for t in st.session_state.db['techs']]
            u = st.selectbox("اسم الفني", tnames) if tnames else None
            p = st.text_input("الكود السري", type="password")
            if st.button("تسجيل الدخول"):
                tech = next((t for t in st.session_state.db['techs'] if t['name'] == u), None)
                if tech and tech['pass'] == p:
                    st.session_state.role = "tech"
                    st.session_state.user = u
                    st.rerun()
                else: st.error("بيانات خاطئة")
    st.stop()

# ================== 5. لوحة الإدارة الذكية ==================
if st.session_state.role == "admin":
    with st.sidebar:
        st.title("⚡ Power Pro")
        menu = st.radio("القائمة", ["الرئيسية", "العملاء والمواعيد", "المخازن", "الفنيين", "تقارير"])
        if st.button("خروج"):
            st.session_state.clear()
            st.rerun()

    # --- الصفحة الرئيسية ---
    if menu == "الرئيسية":
        st.header("📊 نظرة عامة")
        # حسابات
        all_hist = [h for c in st.session_state.db['customers'] for h in c.get('history', [])]
        total_income = sum(h['paid'] for h in all_hist)
        total_debt = sum(get_balance(c.get('history', [])) for c in st.session_state.db['customers'])
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='metric-card'><div class='metric-value'>{total_income:,.0f}</div><div class='metric-label'>إجمالي المقبوضات</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='metric-card'><div class='metric-value' style='color:red'>{total_debt:,.0f}</div><div class='metric-label'>ديون بالسوق</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='metric-card'><div class='metric-value'>{len(st.session_state.db['customers'])}</div><div class='metric-label'>عدد العملاء</div></div>", unsafe_allow_html=True)

        st.subheader("🚨 تنبيهات الصيانة (الأسبوع الحالي)")
        today = datetime.now()
        upcoming = []
        for c in st.session_state.db['customers']:
            if c.get('next_visit'):
                d = datetime.strptime(c['next_visit'], "%Y-%m-%d")
                if 0 <= (d - today).days <= 7:
                    upcoming.append(c)
        
        if upcoming:
            for up in upcoming:
                st.warning(f"🔔 العميل {up['name']} - الموعد: {up['next_visit']} (📞 {up['phone']})")
        else:
            st.success("لا توجد صيانات مستحقة هذا الأسبوع")

    # --- العملاء ---
    elif menu == "العملاء والمواعيد":
        st.header("👥 قاعدة العملاء")
        tab1, tab2 = st.tabs(["بحث وإدارة", "إضافة عميل"])
        
        with tab1:
            q = st.text_input("🔍 بحث (اسم/هاتف)")
            for c in st.session_state.db['customers']:
                if q in c['name'] or q in c['phone'] or q == "":
                    with st.expander(f"{c['name']} | {get_balance(c.get('history', [])):,.0f} ج.م"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"📱 {c['phone']}")
                            if c.get('gps'): st.markdown(f"[📍 موقع العميل]({c['gps']})")
                            
                            # زر الواتساب
                            msg = f"مرحباً {c['name']}، نود تذكيركم بموعد الصيانة."
                            wa_link = f"https://wa.me/2{c['phone']}?text={msg}"
                            st.link_button("💬 مراسلة واتساب", wa_link)

                        with col2:
                            # تحديد موعد قادم
                            new_date = st.date_input("تحديث موعد الصيانة القادم", key=f"d_{c['id']}")
                            if st.button("حفظ الموعد", key=f"btn_{c['id']}"):
                                c['next_visit'] = str(new_date)
                                save_data("customers", st.session_state.db['customers'])
                                st.success("تم الحفظ")
        
        with tab2:
            with st.form("add_c"):
                n = st.text_input("الاسم")
                p = st.text_input("الهاتف")
                g = st.text_input("رابط الخريطة")
                if st.form_submit_button("حفظ"):
                    nid = max([x['id'] for x in st.session_state.db['customers']], default=0) + 1
                    st.session_state.db['customers'].append({
                        "id": nid, "name": n, "phone": p, "gps": g, "history": [], "next_visit": ""
                    })
                    save_data("customers", st.session_state.db['customers'])
                    st.success("تمت الإضافة")

    # --- المخازن (Inventory) ---
    elif menu == "المخازن":
        st.header("📦 إدارة المخزون")
        
        # عرض المخزون الحالي
        if st.session_state.db['inventory']:
            df_inv = pd.DataFrame(st.session_state.db['inventory'])
            st.dataframe(df_inv, use_container_width=True)
        else:
            st.info("المخزن فارغ")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("إضافة صنف جديد")
            item_name = st.text_input("اسم الصنف (مثال: شمعة مرحلة 1)")
            item_qty = st.number_input("الكمية", min_value=1, value=10)
            item_price = st.number_input("سعر البيع للعميل", value=50)
            if st.button("إضافة للمخزن"):
                st.session_state.db['inventory'].append({"item": item_name, "qty": item_qty, "price": item_price})
                save_data("inventory", st.session_state.db['inventory'])
                st.rerun()

    # --- الفنيين ---
    elif menu == "الفنيين":
        st.header("🛠️ فريق العمل")
        # عرض أداء الفنيين
        tech_data = []
        for t in st.session_state.db['techs']:
            # حساب إجمالي ما حصله الفني
            collected = 0
            visits = 0
            for c in st.session_state.db['customers']:
                for h in c.get('history', []):
                    if h.get('tech') == t['name']:
                        collected += h['paid']
                        visits += 1
            tech_data.append({"الفني": t['name'], "زيارات": visits, "تحصيل": collected})
        
        if tech_data:
            st.table(pd.DataFrame(tech_data))

        with st.expander("➕ إضافة فني جديد"):
            tn = st.text_input("الاسم")
            tp = st.text_input("كلمة السر")
            if st.button("تسجيل الفني"):
                st.session_state.db['techs'].append({"name": tn, "pass": tp})
                save_data("techs", st.session_state.db['techs'])
                st.rerun()

# ================== 6. لوحة الفني (سريعة وعملية) ==================
elif st.session_state.role == "tech":
    st.header(f"أهلاً يا هندسة: {st.session_state.user} 👷")
    
    # اختيار العميل
    cust_options = {c['id']: f"{c['name']}" for c in st.session_state.db['customers']}
    selected_id = st.selectbox("اختر العميل", options=list(cust_options.keys()), format_func=lambda x: cust_options[x])
    
    client = next((c for c in st.session_state.db['customers'] if c['id'] == selected_id), None)
    
    if client:
        st.info(f"💰 الحساب القديم: {get_balance(client.get('history', []))} ج.م")
        if client.get('gps'): st.link_button("📍 اذهب للموقع (GPS)", client['gps'], use_container_width=True)
        
        st.markdown("### 📝 تسجيل الزيارة")
        
        with st.form("tech_visit"):
            # اختيار قطع الغيار من المخزن
            inv_names = [i['item'] for i in st.session_state.db['inventory']]
            used_items = st.multiselect("قطع غيار مستخدمة (سيتم خصمها)", inv_names)
            
            # حساب التكلفة التلقائي
            auto_cost = 0
            for u in used_items:
                item = next((i for i in st.session_state.db['inventory'] if i['item'] == u), None)
                if item: auto_cost += item['price']
            
            st.caption(f"التكلفة المحسوبة للقطع: {auto_cost} ج.م")
            
            service_cost = st.number_input("مصنعية / تكلفة إضافية", value=0.0)
            total_req = auto_cost + service_cost
            
            paid_now = st.number_input("المبلغ المدفوع الآن", value=total_req)
            notes = st.text_area("ملاحظات")
            next_date = st.date_input("موعد الصيانة القادم (للتذكير)", value=datetime.now() + timedelta(days=90))
            
            if st.form_submit_button("✅ إتمام الزيارة"):
                # 1. تحديث المخزون
                for u_item in used_items:
                    for inv in st.session_state.db['inventory']:
                        if inv['item'] == u_item:
                            inv['qty'] -= 1
                save_data("inventory", st.session_state.db['inventory'])
                
                # 2. تحديث سجل العميل
                desc = f"زيارة: {', '.join(used_items)} | {notes}"
                client.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "item": desc,
                    "debt": total_req,
                    "paid": paid_now,
                    "tech": st.session_state.user
                })
                client['next_visit'] = str(next_date)
                save_data("customers", st.session_state.db['customers'])
                
                st.success("تم تسجيل العملية وخصم المخزون وتحديد الموعد القادم!")
                st.balloons()
