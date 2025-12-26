import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات الصفحة والتصميم (Dark Modern UI) ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="centered")

# CSS محسّن لدعم العربية والموبايل بشكل أفضل
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif;
        background-color: #0e1117;
        color: #ffffff;
        direction: rtl;
        text-align: right;
    }
    
    /* كارت العميل الرئيسي */
    .main-header-card {
        background: linear-gradient(135deg, #002b5c 0%, #001a35 100%);
        border: 1px solid #00d4ff;
        border-radius: 20px;
        padding: 25px 15px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
    }
    .client-name-title { font-size: 24px; font-weight: 700; color: #fff; margin: 10px 0; }
    .total-balance-text {
        font-size: 18px; font-weight: 600; color: #ff4b4b;
        background: rgba(255, 75, 75, 0.15); padding: 8px 15px; border-radius: 10px;
        display: inline-block; margin-top: 5px;
    }
    .safe-balance-text {
        font-size: 18px; font-weight: 600; color: #00e676;
        background: rgba(0, 230, 118, 0.15); padding: 8px 15px; border-radius: 10px;
        display: inline-block; margin-top: 5px;
    }

    /* كروت السجل */
    .history-card {
        background-color: #1a1f2b;
        border-right: 4px solid #00d4ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #2b313e;
        transition: transform 0.2s;
    }
    .history-card:hover { transform: translateY(-2px); }
    
    .history-top { display: flex; justify-content: space-between; margin-bottom: 10px; border-bottom: 1px solid #363c4a; padding-bottom: 8px; }
    .tech-badge { background-color: #00d4ff; color: #000; padding: 2px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; }
    .date-text { font-size: 12px; color: #aaa; dir: ltr; }
    
    .history-footer { background-color: #11151c; padding: 10px; border-radius: 8px; margin-top: 10px; }
    .money-row { display: flex; justify-content: space-between; font-size: 14px; font-weight: bold; }
    
    /* تحسينات عامة */
    div.stButton > button { width: 100%; border-radius: 8px; font-weight: bold; margin-top: 5px; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        direction: rtl; text-align: right;
    }
    
    /* إخفاء الهيدر والفوتر الافتراضي */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات والملفات ==================
CUSTOMERS_FILE = "customers.json"
TECHS_FILE = "techs.json"

def load_data(filename, default_data):
    if not os.path.exists(filename):
        save_data(filename, default_data)
        return default_data
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return default_data

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تحميل البيانات في الـ Session State
if 'data' not in st.session_state:
    st.session_state.data = load_data(CUSTOMERS_FILE, [])
if 'techs' not in st.session_state:
    st.session_state.techs = load_data(TECHS_FILE, [])

def calculate_balance(history):
    # المديونية = (مجموع المطلوب debt) - (مجموع المدفوع price)
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل العامة (QR Code View) ==================
# استخدام الطريقة الحديثة للتعامل مع الروابط
query_params = st.query_params
if "id" in query_params:
    try:
        cust_id = int(query_params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        
        if c:
            bal = calculate_balance(c.get('history', []))
            
            # عرض الرصيد بشكل ملون حسب الحالة
            balance_html = f'<div class="total-balance-text">🔴 عليك: {bal:,.0f} ج.م</div>' if bal > 0 else f'<div class="safe-balance-text">🟢 خالص: {abs(bal):,.0f} ج.م</div>'

            st.markdown(f"""
            <div class="main-header-card">
                <div style="font-size:45px; margin-bottom:-10px;">💧</div>
                <div class="client-name-title">{c['name']}</div>
                <div style="color:#aaa; font-size:14px;">{c.get('phone', '')}</div>
                {balance_html}
            </div>
            <div style="text-align:right; font-weight:bold; margin-bottom:15px; color:#00d4ff; border-bottom: 1px solid #333; padding-bottom:10px;">
                📜 سجل الزيارات والعمليات:
            </div>
            """, unsafe_allow_html=True)

            if not c.get('history'):
                st.info("لا توجد سجلات سابقة لهذا العميل.")
            
            for h in reversed(c.get('history', [])):
                debt_val = float(h.get('debt', 0))
                paid_val = float(h.get('price', 0))
                remaining = debt_val - paid_val
                
                status_html = ""
                if remaining > 0:
                    status_html = f'<div style="color:#ff4b4b; margin-top:5px; font-weight:bold; border-top:1px dashed #333; padding-top:5px;">⚠️ متبقي من الزيارة: {remaining:,.0f}</div>'
                elif debt_val > 0 and remaining <= 0:
                    status_html = '<div style="color:#00e676; margin-top:5px; font-weight:bold; border-top:1px dashed #333; padding-top:5px;">✅ مدفوعة بالكامل</div>'
                elif debt_val == 0 and paid_val > 0:
                     status_html = '<div style="color:#00e676; margin-top:5px; font-weight:bold; border-top:1px dashed #333; padding-top:5px;">💰 دفعة نقدية (تحصيل)</div>'

                st.markdown(f"""
                <div class="history-card">
                    <div class="history-top">
                        <span class="tech-badge">👤 {h.get('tech', 'غير مسجل')}</span>
                        <span class="date-text">{h["date"]}</span>
                    </div>
                    <div style="color:#e6e6e6; margin-bottom:10px;">{h["note"]}</div>
                    <div class="history-footer">
                        <div class="money-row">
                            <span style="color:#aaa;">مطلوب: {debt_val:,.0f}</span>
                            <span style="color:#00d4ff;">مدفوع: {paid_val:,.0f}</span>
                        </div>
                        {status_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.stop() # إيقاف التنفيذ هنا للعميل العام
        else:
            st.error("❌ لم يتم العثور على العميل، تأكد من الرابط الصحيح.")
            st.stop()
    except Exception as e:
        st.error(f"حدث خطأ في الرابط: {e}")
        st.stop()

# ================== 4. شاشة تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<br><div style='text-align:center;'><h1>Power Life System 💧</h1></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("للمهندسين والفنيين")
        if st.button("🛠️ دخول الفنيين"): st.session_state.role = "tech_login"; st.rerun()
    with col2:
        st.warning("للإدارة فقط")
        if st.button("🔐 دخول الإدارة"): st.session_state.role = "admin_login"; st.rerun()
    st.stop()

# -- نموذج دخول المدير --
if st.session_state.role == "admin_login":
    st.markdown("### 🔐 تسجيل دخول المدير")
    with st.form("admin_auth"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            if u == "admin" and p == "admin123": # يفضل تغييرها لمتغيرات بيئة
                st.session_state.role = "admin"
                st.rerun()
            else: st.error("بيانات خاطئة")
    if st.button("⬅️ رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# -- نموذج دخول الفني --
if st.session_state.role == "tech_login":
    st.markdown("### 🛠️ تسجيل دخول الفنيين")
    t_names = [t['name'] for t in st.session_state.techs]
    
    if not t_names:
        st.error("لا يوجد فنيين مسجلين في النظام. يرجى مراجعة الإدارة.")
        if st.button("رجوع"): del st.session_state.role; st.rerun()
        st.stop()
        
    t_user = st.selectbox("اختر اسمك", t_names)
    p = st.text_input("كلمة المرور الخاصة بك", type="password")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        if st.button("دخول"):
            tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
            if tech and tech['pass'] == p:
                st.session_state.role = "tech_p"
                st.session_state.c_tech = t_user
                st.rerun()
            else: st.error("كلمة المرور غير صحيحة")
    with col_l2:
        if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة (Admin Dashboard) ==================
if st.session_state.role == "admin":
    with st.sidebar:
        st.title("لوحة التحكم ⚙️")
        menu = st.radio("القائمة", ["👥 إدارة العملاء والبحث", "➕ إضافة عميل جديد", "🛠️ إدارة الفنيين"], index=0)
        st.markdown("---")
        if st.button("🚪 تسجيل خروج", type="primary"):
            del st.session_state.role; st.rerun()

    if menu == "👥 إدارة العملاء والبحث":
        st.header("سجل العملاء")
        search = st.text_input("🔍 بحث (الاسم / الهاتف / الرقم التعريفي)", placeholder="اكتب للبحث...")
        
        # فلترة النتائج
        results = [c for c in st.session_state.data if search.lower() in str(c['name']).lower() or search in str(c.get('phone','')) or search == str(c['id'])]
        
        if not results and search:
            st.warning("لم يتم العثور على نتائج.")
            
        for c in results:
            balance = calculate_balance(c.get('history', []))
            color = "red" if balance > 0 else "green"
            
            with st.expander(f"👤 {c['name']} | 📱 {c.get('phone','-')} | رصيد: :{color}[{balance:,.0f}]"):
                # أدوات سريعة
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.write("**QR Code للعميل:**")
                    # تأكد من تغيير الرابط أدناه لرابط تطبيقك الفعلي
                    base_url = "https://YOUR-APP-URL.streamlit.app" 
                    url = f"{base_url}/?id={c['id']}"
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={url}", width=120)
                
                with col_b:
                    st.markdown("#### تعديل البيانات")
                    new_n = st.text_input("الاسم", c['name'], key=f"n_{c['id']}")
                    new_p = st.text_input("الهاتف", c.get('phone', ''), key=f"p_{c['id']}")
                    
                    if st.button("💾 حفظ التعديلات", key=f"save_{c['id']}"):
                        c['name'] = new_n
                        c['phone'] = new_p
                        save_data(CUSTOMERS_FILE, st.session_state.data)
                        st.success("تم التحديث!")
                        st.rerun()

                st.markdown("---")
                st.markdown("#### ➕ تسجيل عملية (إداري)")
                with st.form(key=f"form_{c['id']}"):
                    c1, c2 = st.columns(2)
                    req = c1.number_input("المبلغ المطلوب (دين)", 0.0, step=50.0)
                    pai = c2.number_input("المبلغ المدفوع (تحصيل)", 0.0, step=50.0)
                    not_txt = st.text_input("ملاحظة", "تحديث من الإدارة")
                    
                    if st.form_submit_button("تسجيل"):
                        c.setdefault('history', []).append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": not_txt,
                            "debt": req,
                            "price": pai,
                            "tech": "الإدارة (Admin)"
                        })
                        save_data(CUSTOMERS_FILE, st.session_state.data)
                        st.success("تم تسجيل العملية")
                        st.rerun()
                
                # زر خطير للحذف
                if st.checkbox("تفعيل الحذف", key=f"del_chk_{c['id']}"):
                    if st.button("🗑️ حذف العميل نهائياً", key=f"del_btn_{c['id']}", type="primary"):
                        st.session_state.data.remove(c)
                        save_data(CUSTOMERS_FILE, st.session_state.data)
                        st.rerun()

    elif menu == "➕ إضافة عميل جديد":
        st.header("تسجيل عميل جديد")
        with st.form("add_c_form"):
            n = st.text_input("اسم العميل")
            p = st.text_input("رقم الهاتف")
            if st.form_submit_button("إضافة"):
                if n:
                    new_id = max([x['id'] for x in st.session_state.data], default=1000) + 1
                    st.session_state.data.append({
                        "id": new_id, 
                        "name": n, 
                        "phone": p, 
                        "history": [{
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "note": "تسجيل العميل في النظام",
                            "debt": 0, "price": 0, "tech": "Admin"
                        }]
                    })
                    save_data(CUSTOMERS_FILE, st.session_state.data)
                    st.success(f"تم إضافة العميل {n} بنجاح! ID: {new_id}")
                else:
                    st.error("يجب كتابة الاسم على الأقل.")

    elif menu == "🛠️ إدارة الفنيين":
        st.header("فريق العمل")
        
        # إضافة فني
        with st.expander("➕ إضافة فني جديد", expanded=True):
            with st.form("add_t"):
                tn = st.text_input("اسم الفني")
                tp = st.text_input("كلمة السر للدخول")
                if st.form_submit_button("حفظ"):
                    if tn and tp:
                        st.session_state.techs.append({"name": tn, "pass": tp})
                        save_data(TECHS_FILE, st.session_state.techs)
                        st.success("تم الإضافة")
                        st.rerun()
                    else:
                        st.error("أدخل البيانات كاملة")

        # عرض وحذف الفنيين
        st.markdown("### الفنيين الحاليين:")
        if not st.session_state.techs:
            st.info("لا يوجد فنيين.")
        else:
            for i, t in enumerate(st.session_state.techs):
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.write(f"👤 **{t['name']}**")
                c2.write(f"🔑 {t['pass']}")
                if c3.button("حذف", key=f"del_tech_{i}"):
                    st.session_state.techs.pop(i)
                    save_data(TECHS_FILE, st.session_state.techs)
                    st.rerun()

# ================== 6. لوحة الفني (Technician Dashboard) ==================
elif st.session_state.role == "tech_p":
    st.markdown(f"### مرحباً يا هندسة ({st.session_state.c_tech}) 👋")
    
    # 1. فلتر البحث لاختيار العميل (مهم جداً إذا كان العدد كبير)
    search_query = st.text_input("🔍 ابحث عن العميل (بالاسم أو الرقم)", placeholder="اكتب هنا لتضييق القائمة...")
    
    # تصفية القائمة بناءً على البحث
    filtered_customers = [c for c in st.session_state.data if search_query.lower() in c['name'].lower() or search_query in str(c['id']) or search_query in str(c.get('phone',''))]
    
    if not filtered_customers:
        st.warning("لا يوجد عميل يطابق البحث.")
    else:
        # إنشاء قاموس للاختيار
        c_map = {c['id']: f"{c['name']} - {c.get('phone','')}" for c in filtered_customers}
        sid = st.selectbox("اختر العميل من القائمة:", list(c_map.keys()), format_func=lambda x: c_map[x])
        
        target = next((x for x in st.session_state.data if x['id'] == sid), None)
        
        if target:
            st.markdown("---")
            curr_bal = calculate_balance(target.get('history', []))
            
            # عرض بيانات مختصرة للعميل للفني
            st.markdown(f"""
            <div style="background:#1a1f2b; padding:15px; border-radius:10px; border-right:4px solid #00d4ff;">
                <h3 style="margin:0; color:#fff;">{target['name']}</h3>
                <p style="margin:5px 0; color:#aaa;">{target.get('phone', 'لا يوجد رقم')}</p>
                <p style="margin:0; font-weight:bold;">الرصيد الحالي: <span style="color:{'#ff4b4b' if curr_bal > 0 else '#00e676'}">{curr_bal:,.0f} ج.م</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("#### 📝 تقرير الزيارة الجديد")
            with st.form("tech_action_form"):
                note = st.text_area("تفاصيل الصيانة / القطع المركبة", placeholder="مثال: تغيير شمعات 1 و 2 و 3...")
                
                c1, c2 = st.columns(2)
                val_debt = c1.number_input("💰 التكلفة المطلوبة (قيمة الشغل)", min_value=0.0, step=10.0, help="المبلغ الذي يجب على العميل دفعه مقابل هذا العمل")
                val_paid = c2.number_input("💵 المبلغ المستلم (الكاش)", min_value=0.0, step=10.0, help="المبلغ الذي استلمته في يدك فعلياً")
                
                if st.form_submit_button("✅ حفظ وإرسال التقرير"):
                    if not note:
                        st.error("يرجى كتابة تفاصيل الصيانة.")
                    else:
                        target.setdefault('history', []).append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": note,
                            "debt": val_debt,
                            "price": val_paid,
                            "tech": st.session_state.c_tech
                        })
                        save_data(CUSTOMERS_FILE, st.session_state.data)
                        st.balloons()
                        st.success("تم تسجيل الزيارة وتحديث الحساب بنجاح!")
                        # تفريغ الشاشة
                        st.session_state.temp_submit = True 
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("تسجيل خروج", type="secondary"):
        del st.session_state.role
        st.rerun() 
