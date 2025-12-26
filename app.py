import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. التنسيق المحسن (لوحة عميل احترافية وتصميم عصري) ==================
st.set_page_config(page_title="Power Life Pro", page_icon="💧", layout="wide")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-x: hidden !important; direction: rtl; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    
    /* تنسيق لوحة العميل الرئيسية */
    .client-main-card { 
        background: linear-gradient(135deg, #001f3f, #003366); 
        border: 2px solid #00d4ff; 
        border-radius: 15px; 
        padding: 25px; 
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0, 212, 255, 0.2);
        text-align: center;
    }
    .client-name {
        font-size: 2em;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .total-debt {
        font-size: 1.8em;
        color: #ff4b4b; /* لون أحمر للمديونية */
        font-weight: bold;
    }

    /* تنسيق بطاقات سجل العمليات للعميل */
    .history-card-pro { 
        background: rgba(0, 80, 155, 0.2); 
        border-radius: 12px; 
        padding: 15px; 
        margin-top: 10px; 
        border-right: 5px solid #00d4ff; 
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .history-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        font-size: 0.9em;
        color: #00d4ff;
    }
    .history-details {
        margin-bottom: 10px;
        font-size: 1em;
        color: #e0e0e0;
    }
    .history-financials {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: bold;
    }
    .paid-amount { color: #00ffcc; } /* لون أخضر للمدفوع */
    .remaining-amount { color: #ff4b4b; } /* لون أحمر للمتبقي */
    .fully-paid { color: #00ffcc; } /* لون أخضر للمدفوع بالكامل */

    /* تنسيق عام للأزرار والحقول */
    div.stButton > button { width: 100% !important; border-radius: 8px; height: 45px; }
    .stSelectbox, .stTextInput, .stNumberInput { width: 100% !important; margin-bottom: 10px; }
    header, footer {visibility: hidden;}
    
    /* تنسيق الجدول */
    .stTable {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #007bff;
    }
    .stTable th {
        background-color: #001f3f;
        color: #00d4ff;
        text-align: center !important;
    }
    .stTable td {
        background-color: rgba(0, 80, 155, 0.1);
        color: #ffffff;
        text-align: center !important;
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

# ================== 3. واجهة الباركود للعميل (تصميم احترافي وحسابات صحيحة) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff; margin-bottom: 20px;'>Power Life 💧</h1>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"""
            <div class='client-main-card'>
                <div class='client-name'>👤 {c['name']}</div>
                <div class='total-debt'>إجمالي المتبقي عليك: {bal:,.0f} ج.م</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3 style='text-align:right; color:#00d4ff;'>📜 سجل العمليات:</h3>", unsafe_allow_html=True)
            # هنا التعديل عشان يظهر الفني والمبالغ بالتفصيل والشكل الاحترافي
            for h in reversed(c.get('history', [])):
                cost = float(h.get("debt", 0))   # التكلفة المطلوبة
                paid = float(h.get("price", 0))  # المدفوع
                rem = cost - paid                # المتبقي من العملية دي
                tech_name = h.get("tech", "غير محدد") # اسم الفني
                
                remaining_display = f"<span class='remaining-amount'>🚩 متبقي: {rem:,.0f} ج.م</span>" if rem > 0 else "<span class='fully-paid'>✅ تم السداد بالكامل</span>"

                st.markdown(f"""
                <div class="history-card-pro">
                    <div class="history-header">
                        <span>📅 {h["date"]}</span>
                        <span>👤 الفني: {tech_name}</span>
                    </div>
                    <div class="history-details">
                        📝 {h["note"]}
                    </div>
                    <hr style="margin:10px 0; border-color:#007bff;">
                    <div class="history-financials">
                        <span>💵 المطلوب: {cost:,.0f} ج.م</span>
                        <span class='paid-amount'>✅ المدفوع: {paid:,.0f} ج.م</span>
                        {remaining_display}
                    </div>
                </div>""", unsafe_allow_html=True)
            st.stop()
    except:
        st.error("خطأ في البيانات.")
        st.stop()

# ================== 4. نظام الدخول ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:30px; color:#00d4ff;'>Power Life System 🔒</h2>", unsafe_allow_html=True)
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
                        with st.expander("📝 سجل العمليات بالتفصيل"):
                            # عرض تفاصيل العمليات للمدير كمان
                            for h in reversed(c.get('history', [])):
                                st.write(f"📅 {h['date']} | 👤 {h.get('tech', 'غير محدد')}")
                                st.caption(f"📝 {h['note']}")
                                st.write(f"💵 تكلفة: {h.get('debt',0)} | ✅ دفع: {h.get('price',0)} | 🚩 باقي: {float(h.get('debt',0)) - float(h.get('price',0))}")
                                st.divider()

                        with st.expander("📝 تعديل البيانات الأساسية"):
                            c['name'] = st.text_input("الاسم", value=c['name'], key=f"n{c['id']}")
                            c['phone'] = st.text_input("التليفون", value=c.get('phone',''), key=f"p{c['id']}")
                            c['gps'] = st.text_input("رابط GPS", value=c.get('gps',''), key=f"g{c['id']}")
                            if st.button("حفظ التعديلات", key=f"s{c['id']}"): 
                                save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
                        
                        with st.expander("💸 عملية سريعة (إضافة/تحصيل)"):
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
        st.write("Generation finished.")
        st.write("📋 آخر العمليات المنفذة:")
        all_ops = []
        for c in st.session_state.data:
            for h in c.get('history', []):
                all_ops.append({
                    "التاريخ": h['date'], 
                    "الفني": h.get('tech',''), 
                    "العميل": c['name'], 
                    "المحصل": h.get('price', 0),
                    "الباقي": float(h.get('debt', 0)) - float(h.get('price', 0))
                })
        if all_ops:
            # عرض الجدول بشكل احترافي
            st.table(reversed(all_ops))
        else:
            st.info("لا توجد عمليات مسجلة حتى الآن.")

    elif menu == "📊 التقارير":
        total = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي الديون الخارجية", f"{total:,.0f} ج.م")
    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()

# ================== 6. واجهة الفني (كاملة) ==================
elif st.session_state.role == "tech_p":
    st.subheader(f"🛠️ حساب الفني: {st.session_state.c_tech}")
    if st.button("🔄 تحديث القائمة", use_container_width=True): refresh_all_data(); st.rerun()
    customer_names = {c['id']: c['name'] for c in st.session_state.data}
    selected_id = st.selectbox("🎯 اختر العميل", options=list(customer_names.keys()), format_func=lambda x: customer_names[x])
    target = next((x for x in st.session_state.data if x['id'] == selected_id), None)
    
    if target:
        if target.get('gps'): st.link_button("📍 توجه إلى موقع العميل", target['gps'], use_container_width=True)
        with st.form("visit_form"):
            v_add = st.number_input("تكلفة الصيانة/القطع (المبلغ المطلوب)", 0.0)
            v_rem = st.number_input("المبلغ اللي العميل دفعه (المحصل)", 0.0)
            note = st.text_area("ملاحظات الفني")
            if st.form_submit_button("✅ إرسال التقرير"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x.setdefault('history', []).append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": note, 
                            "tech": st.session_state.c_tech, 
                            "debt": v_add,  # دي التكلفة
                            "price": v_rem  # ده اللي اندفع
                        })
                save_json("customers.json", st.session_state.data); refresh_all_data(); st.success("تم الحفظ!")
    if st.button("🚪 خروج"): del st.session_state.role; st.rerun()
