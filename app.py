import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# ================== 1. إعدادات الصفحة والتصميم ==================
st.set_page_config(page_title="Power Life ERP", page_icon="💧", layout="wide")

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
    
    /* تنسيق الكروت */
    .metric-card {
        background-color: #1a1f2b;
        border: 1px solid #2b313e;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-value { font-size: 28px; font-weight: bold; color: #00d4ff; }
    .metric-label { color: #aaa; font-size: 14px; }

    /* أزرار التواصل */
    .action-btn {
        text-decoration: none;
        padding: 8px 15px;
        border-radius: 5px;
        color: white !important;
        margin-left: 5px;
        font-size: 14px;
        display: inline-block;
    }
    .whatsapp-btn { background-color: #25D366; }
    .call-btn { background-color: #34b7f1; }
    .maps-btn { background-color: #db4437; }

    /* تحسين الجداول */
    [data-testid="stDataFrame"] { direction: rtl; }
    
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================
CUSTOMERS_FILE = "customers.json"
TECHS_FILE = "techs.json"

def load_data(filename, default_data):
    if not os.path.exists(filename):
        save_data(filename, default_data)
        return default_data
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return default_data

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_data(CUSTOMERS_FILE, [])
if 'techs' not in st.session_state: st.session_state.techs = load_data(TECHS_FILE, [])

def calculate_totals(data):
    total_debt = 0
    total_paid = 0
    for c in data:
        for h in c.get('history', []):
            total_debt += float(h.get('debt', 0))
            total_paid += float(h.get('price', 0))
    return total_debt, total_paid

# ================== 3. واجهة تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<br><h1 style='text-align:center; color:#00d4ff;'>Power Life System 💧</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛠️ فني ميداني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    with c2:
        if st.button("👔 إدارة ومتابعة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    st.stop()

# --- Login Logic ---
if st.session_state.role == "admin_login":
    with st.form("a_log"):
        st.subheader("دخول المدير")
        if st.form_submit_button("دخول"): st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    if not t_names: st.error("لا يوجد فنيين"); st.stop()
    user = st.selectbox("اختر اسمك", t_names)
    pw = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech = next((t for t in st.session_state.techs if t['name'] == user), None)
        if tech and tech['pass'] == pw:
            st.session_state.role = "tech_p"; st.session_state.c_tech = user; st.rerun()
        else: st.error("خطأ")
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 4. لوحة الإدارة المتقدمة ==================
if st.session_state.role == "admin":
    with st.sidebar:
        st.title("التحكم الرئيسي")
        menu = st.radio("القائمة", ["📊 الإحصائيات والتقارير", "👥 إدارة العملاء", "➕ إضافة عميل", "⚙️ الإعدادات"], index=0)
        if st.button("خروج", type="primary"): del st.session_state.role; st.rerun()

    # --- 1. الإحصائيات (Dashboard) ---
    if menu == "📊 الإحصائيات والتقارير":
        st.header("لوحة القيادة (Dashboard)")
        
        # حسابات سريعة
        tot_req, tot_col = calculate_totals(st.session_state.data)
        net_balance = tot_req - tot_col
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-card"><div class="metric-value">{len(st.session_state.data)}</div><div class="metric-label">عدد العملاء</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="metric-value">{tot_col:,.0f}</div><div class="metric-label">إجمالي التحصيل</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ff4b4b">{net_balance:,.0f}</div><div class="metric-label">مديونيات بالسوق</div></div>', unsafe_allow_html=True)
        
        # عملاء يحتاجون صيانة (افتراض: مر 3 شهور على آخر زيارة)
        needs_maintain = []
        for c in st.session_state.data:
            if c.get('history'):
                last_date_str = c['history'][-1]['date']
                try:
                    # نأخذ التاريخ فقط بدون الوقت للمقارنة
                    last_date = datetime.strptime(last_date_str.split(" ")[0], "%Y-%m-%d")
                    if (datetime.now() - last_date).days > 90:
                        needs_maintain.append({"الاسم": c['name'], "آخر زيارة": last_date_str, "التليفون": c.get('phone')})
                except: pass
        
        c4.markdown(f'<div class="metric-card"><div class="metric-value">{len(needs_maintain)}</div><div class="metric-label">عملاء مستحقين للصيانة</div></div>', unsafe_allow_html=True)

        st.markdown("---")
        
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.subheader("⚠️ عملاء تأخرت صيانتهم (+90 يوم)")
            if needs_maintain:
                st.dataframe(pd.DataFrame(needs_maintain), use_container_width=True)
            else:
                st.info("الجميع تم زيارتهم حديثاً.")

        with col_d2:
            st.subheader("📥 تصدير البيانات")
            # تجهيز الداتا للإكسيل
            export_list = []
            for c in st.session_state.data:
                h_debt = sum(float(x['debt']) for x in c.get('history', []))
                h_paid = sum(float(x['price']) for x in c.get('history', []))
                export_list.append({
                    "ID": c['id'], "Name": c['name'], "Phone": c.get('phone'),
                    "Total Debt": h_debt, "Total Paid": h_paid, "Balance": h_debt - h_paid
                })
            
            df = pd.DataFrame(export_list)
            st.download_button("تحميل ملف Excel 📗", df.to_csv(index=False).encode('utf-8-sig'), "customers_data.csv", "text/csv", use_container_width=True)

    # --- 2. إدارة العملاء ---
    elif menu == "👥 إدارة العملاء":
        search = st.text_input("بحث سريع (اسم / تليفون)", placeholder="اكتب للبحث...")
        
        # الفلترة
        results = [c for c in st.session_state.data if search in c['name'] or search in str(c.get('phone',''))]
        
        for c in results:
            with st.expander(f"👤 {c['name']}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    new_n = st.text_input("الاسم", c['name'], key=f"n_{c['id']}")
                    new_p = st.text_input("الهاتف", c.get('phone',''), key=f"p_{c['id']}")
                    new_loc = st.text_input("رابط الموقع (Google Maps)", c.get('location',''), key=f"l_{c['id']}")
                    
                    if st.button("حفظ التعديلات", key=f"s_{c['id']}"):
                        c['name'] = new_n; c['phone'] = new_p; c['location'] = new_loc
                        save_data(CUSTOMERS_FILE, st.session_state.data)
                        st.success("تم الحفظ")
                
                with col2:
                    st.write("QR Code للعميل:")
                    url = f"https://your-app.com/?id={c['id']}" # استبدل برابطك الحقيقي
                    st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={url}")

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            st.write("بيانات العميل الجديد")
            n = st.text_input("الاسم")
            p = st.text_input("الهاتف")
            l = st.text_input("رابط اللوكيشن (اختياري)")
            if st.form_submit_button("إضافة"):
                new_id = max([x['id'] for x in st.session_state.data], default=1000) + 1
                st.session_state.data.append({"id": new_id, "name": n, "phone": p, "location": l, "history": []})
                save_data(CUSTOMERS_FILE, st.session_state.data)
                st.success("تم!")

    elif menu == "⚙️ الإعدادات":
        st.write("إدارة الفنيين")
        with st.form("add_tech"):
            tn = st.text_input("اسم الفني")
            tp = st.text_input("كلمة السر")
            if st.form_submit_button("إضافة فني"):
                st.session_state.techs.append({"name": tn, "pass": tp})
                save_data(TECHS_FILE, st.session_state.techs)
                st.success("تم")
        
        st.write("---")
        st.write("قائمة الفنيين:")
        for t in st.session_state.techs:
            st.code(f"{t['name']} - Pass: {t['pass']}")

# ================== 5. واجهة الفني (Technician Pro) ==================
elif st.session_state.role == "tech_p":
    st.header(f"أهلاً {st.session_state.c_tech} 🔧")
    
    search_q = st.text_input("🔍 بحث عن عميل", placeholder="ابحث بالاسم...")
    
    # اختيار العميل
    filtered = [c for c in st.session_state.data if search_q in c['name'] or search_q in str(c.get('phone',''))]
    
    if filtered:
        c_dict = {c['id']: f"{c['name']}" for c in filtered}
        cid = st.selectbox("اختر العميل", list(c_dict.keys()), format_func=lambda x: c_dict[x])
        target = next((x for x in st.session_state.data if x['id'] == cid), None)
        
        if target:
            # --- أدوات التواصل السريع ---
            st.markdown("#### 📞 أدوات التواصل")
            ph = target.get('phone', '')
            loc = target.get('location', '')
            
            # أزرار HTML مخصصة
            btns_html = ""
            if ph:
                btns_html += f'<a href="tel:{ph}" class="action-btn call-btn">📞 اتصال</a>'
                btns_html += f'<a href="https://wa.me/2{ph}" target="_blank" class="action-btn whatsapp-btn">💬 واتساب</a>'
            if loc:
                btns_html += f'<a href="{loc}" target="_blank" class="action-btn maps-btn">📍 الموقع</a>'
            
            st.markdown(btns_html if btns_html else "⚠️ لا توجد بيانات تواصل مسجلة", unsafe_allow_html=True)
            
            st.markdown("---")
            
            # --- نموذج الزيارة ---
            st.subheader("📝 تسجيل الزيارة")
            with st.form("visit_form"):
                note = st.text_area("تقرير الصيانة والقطع المستهلكة")
                d1, d2 = st.columns(2)
                cost = d1.number_input("المطلوب (التكلفة)", 0.0, step=10.0)
                paid = d2.number_input("المدفوع (الكاش)", 0.0, step=10.0)
                
                next_v = st.date_input("ميعاد الصيانة القادمة (تذكير)", value=datetime.now()+timedelta(days=90))
                
                if st.form_submit_button("✅ إتمام الزيارة"):
                    target.setdefault('history', []).append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "note": f"{note} (الموعد القادم: {next_v})",
                        "debt": cost,
                        "price": paid,
                        "tech": st.session_state.c_tech
                    })
                    save_data(CUSTOMERS_FILE, st.session_state.data)
                    st.success("تم الحفظ!")
            
            # سجل سريع
            with st.expander("سجل الزيارات السابق"):
                for h in reversed(target.get('history', [])):
                    st.caption(f"{h['date']} - {h['tech']}")
                    st.write(f"{h['note']} (مدفوع: {h.get('price',0)})")
                    st.divider()
    else:
        st.info("ابحث عن عميل للبدء")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("خروج"): del st.session_state.role; st.rerun()
