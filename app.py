import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق الاحترافي (Dark Modern UI) ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="centered")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Cairo', sans-serif;
        background-color: #0e1117;
        color: #ffffff;
        direction: rtl;
    }
    
    /* كارت العميل الرئيسي */
    .main-header-card {
        background: linear-gradient(135deg, #002b5c 0%, #001a35 100%);
        border: 1px solid #00d4ff;
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.15);
    }
    .client-name-title {
        font-size: 26px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .total-balance-text {
        font-size: 22px;
        font-weight: 600;
        color: #ff4b4b;
        background: rgba(255, 75, 75, 0.1);
        padding: 10px 20px;
        border-radius: 12px;
        display: inline-block;
    }

    /* كروت السجل */
    .history-card {
        background-color: #1a1f2b;
        border-right: 4px solid #00d4ff;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        border: 1px solid #2b313e;
    }
    
    .history-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        border-bottom: 1px solid #363c4a;
        padding-bottom: 8px;
    }
    .tech-badge {
        background-color: #00d4ff;
        color: #000;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
    }
    .date-text { font-size: 12px; color: #a0a0a0; }
    
    .history-body { font-size: 15px; margin-bottom: 12px; color: #e6e6e6; }
    
    .history-footer {
        background-color: #11151c;
        padding: 10px;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }
    
    .money-row {
        display: flex;
        justify-content: space-between;
        font-size: 14px;
    }
    
    .status-badge-red {
        color: #ff4b4b;
        font-weight: bold;
        text-align: center;
        margin-top: 5px;
        border-top: 1px dashed #333;
        padding-top: 5px;
    }
    .status-badge-green {
        color: #00e676;
        font-weight: bold;
        text-align: center;
        margin-top: 5px;
        border-top: 1px dashed #333;
        padding-top: 5px;
    }

    div.stButton > button { width: 100%; border-radius: 10px; background-color: #00d4ff; color: #000; font-weight: bold; border: none; }
    div.stButton > button:hover { background-color: #00aacc; color: #fff; }
    
    /* إخفاء القوائم الافتراضية */
    header, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ================== 2. دوال البيانات ==================
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
    # المديونية = (مجموع المطلوب) - (مجموع المدفوع)
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة العميل (التصميم الجديد والمنطق المعدل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            bal = calculate_balance(c.get('history', []))
            
            # 1. كارت الهيدر الرئيسي
            st.markdown(f"""
            <div class="main-header-card">
                <div style="font-size:40px; margin-bottom:-10px;">💧</div>
                <div class="client-name-title">{c['name']}</div>
                <div class="total-balance-text">إجمالي المديونية الحالية: {bal:,.0f} ج.م</div>
            </div>
            <div style="text-align:right; font-weight:bold; margin-bottom:10px; color:#00d4ff;">📝 سجل العمليات والزيارات:</div>
            """, unsafe_allow_html=True)

            # 2. عرض السجل
            for h in reversed(c.get('history', [])):
                debt_val = float(h.get('debt', 0))   # تكلفة الصيانة (المطلوب)
                paid_val = float(h.get('price', 0))  # اللي دفعه العميل
                remaining = debt_val - paid_val      # المتبقي من العملية دي
                
                # تحديد حالة السداد بناءً على المتبقي
                if remaining > 0:
                    status_html = f'<div class="status-badge-red">⚠️ متبقي من الزيارة دي: {remaining:,.0f} ج.م</div>'
                elif remaining == 0 and debt_val > 0:
                    status_html = '<div class="status-badge-green">✅ تم سداد تكلفة الزيارة بالكامل</div>'
                else:
                    # الحالة لو كانت مجرد عملية دفع (بدون تكلفة صيانة) أو المتبقي صفر
                    if debt_val == 0 and paid_val > 0:
                        status_html = '<div class="status-badge-green">💰 دفعة نقدية (تحصيل)</div>'
                    else:
                        status_html = '<div class="status-badge-green">✅ مكتملة</div>'

                tech_name = h.get('tech', 'غير مسجل')

                st.markdown(f"""
                <div class="history-card">
                    <div class="history-top">
                        <span class="tech-badge">👤 {tech_name}</span>
                        <span class="date-text">{h["date"]} 📅</span>
                    </div>
                    <div class="history-body">
                        {h["note"]}
                    </div>
                    <div class="history-footer">
                        <div class="money-row">
                            <span style="color:#aaa;">💵 المطلوب: {debt_val:,.0f}</span>
                            <span style="color:#00d4ff;">💰 المدفوع: {paid_val:,.0f}</span>
                        </div>
                        {status_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.stop()
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
        st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<br><h1 style='text-align:center; color:#00d4ff;'>Power Life System</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛠️ دخول فني"): st.session_state.role = "tech_login"; st.rerun()
    with col2:
        if st.button("🔑 دخول إدارة"): st.session_state.role = "admin_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    st.markdown("### 🔐 دخول المدير")
    u = st.text_input("User")
    p = st.text_input("Password", type="password")
    if st.button("تسجيل دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
        else: st.error("بيانات خاطئة")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    st.markdown("### 🛠️ دخول الفنيين")
    t_names = [t['name'] for t in st.session_state.techs]
    if not t_names: st.warning("لا يوجد فنيين مسجلين")
    t_user = st.selectbox("اختر اسمك", t_names) if t_names else None
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == t_user), None)
        if tech and tech['pass'] == p:
            st.session_state.role = "tech_p"
            st.session_state.c_tech = t_user
            st.rerun()
        else: st.error("كلمة المرور خطأ")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["الإدارة والبحث", "إضافة عميل", "الفنيين", "خروج"])
    
    if menu == "خروج":
        del st.session_state.role; st.rerun()
        
    elif menu == "الإدارة والبحث":
        st.header("👥 إدارة العملاء")
        search = st.text_input("بحث بالاسم أو الرقم", placeholder="اكتب هنا...")
        
        for c in st.session_state.data:
            if not search or search in c['name'] or search in str(c.get('phone','')):
                with st.expander(f"👤 {c['name']} (م: {calculate_balance(c.get('history', []))})"):
                    # QR Code
                    url = f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}"
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={url}", width=100)
                    
                    # تعديل سريع
                    new_n = st.text_input("تعديل الاسم", c['name'], key=f"n_{c['id']}")
                    if new_n != c['name']:
                        c['name'] = new_n; save_json("customers.json", st.session_state.data); st.success("تم")
                    
                    # إضافة عملية
                    st.write("---")
                    c1, c2 = st.columns(2)
                    req = c1.number_input("مبلغ مطلوب (دين)", 0.0, key=f"req_{c['id']}")
                    pai = c2.number_input("مبلغ مدفوع (تحصيل)", 0.0, key=f"pai_{c['id']}")
                    not_txt = st.text_input("ملاحظة", "تحديث إداري", key=f"not_{c['id']}")
                    
                    if st.button("تسجيل العملية", key=f"btn_{c['id']}"):
                        c.setdefault('history', []).append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": not_txt,
                            "debt": req,
                            "price": pai,
                            "tech": "Admin"
                        })
                        save_json("customers.json", st.session_state.data)
                        st.rerun()

    elif menu == "إضافة عميل":
        with st.form("add_c"):
            n = st.text_input("الاسم")
            p = st.text_input("التليفون")
            if st.form_submit_button("حفظ"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "history": []})
                save_json("customers.json", st.session_state.data)
                st.success("تم")

    elif menu == "الفنيين":
        with st.form("add_t"):
            tn = st.text_input("اسم الفني")
            tp = st.text_input("كلمة السر")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_json("techs.json", st.session_state.techs)
                st.success("تم")

# ================== 6. واجهة الفني ==================
elif st.session_state.role == "tech_p":
    st.header(f"أهلاً يا هندسة ({st.session_state.c_tech}) 🔧")
    
    # اختيار العميل
    c_names = {c['id']: c['name'] for c in st.session_state.data}
    sid = st.selectbox("اختر العميل", list(c_names.keys()), format_func=lambda x: c_names[x])
    
    target = next((x for x in st.session_state.data if x['id'] == sid), None)
    if target:
        st.info(f"العميل: {target['name']}")
        with st.form("tech_form"):
            val_debt = st.number_input("💰 تكلفة الصيانة/القطع (المبلغ المطلوب من العميل)", min_value=0.0)
            val_paid = st.number_input("💵 المبلغ اللي استلمته في إيدك (المدفوع)", min_value=0.0)
            note = st.text_area("📝 تقرير الصيانة")
            
            if st.form_submit_button("✅ حفظ وإرسال"):
                target.setdefault('history', []).append({
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "note": note,
                    "debt": val_debt,
                    "price": val_paid,
                    "tech": st.session_state.c_tech
                })
                save_json("customers.json", st.session_state.data)
                st.success("تم تسجيل الزيارة بنجاح!")
    
    if st.button("تسجيل خروج"): del st.session_state.role; st.rerun() 
