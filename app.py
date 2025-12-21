import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import urllib.parse

# ================== 1. إعدادات المظهر والتحكم ==================
st.set_page_config(page_title="Power Life", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .client-report { background: rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 25px; border: 1px solid #007bff; margin-bottom: 20px; }
    .data-row { border-bottom: 1px solid rgba(255,255,255,0.1); padding: 12px 0; display: flex; justify-content: space-between; }
    .history-card { background: rgba(0, 123, 255, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 5px solid #00d4ff; text-align: right; }
    .settlement-card { background: rgba(0, 255, 127, 0.15); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-right: 5px solid #00ff7f; text-align: right; }
    .finance-card { background: rgba(0, 255, 127, 0.1); border: 1px solid #00ff7f; padding: 15px; border-radius: 15px; text-align: center; }
    .debt-card { background: rgba(255, 69, 0, 0.1); border: 1px solid #ff4500; padding: 15px; border-radius: 15px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف البيانات وقوائم الإعدادات ==================
def load_data():
    if os.path.exists("customers.json"):
        with open("customers.json", "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return []
    return []

def save_data(data):
    with open("customers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state:
    st.session_state.data = load_data()

EGYPT_GOVS = ["القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "الشرقية", "المنوفية", "القليوبية", "البحيرة", "الغربية", "بور سعيد", "دمياط", "الإسماعيلية", "السويس", "كفر الشيخ", "الفيوم", "بني سويف", "المنيا", "أسيوط", "سوهاج", "قنا", "الأقصر", "أسوان"]

# قائمة الفنيين
TECHNICIANS = ["أحمد", "محمد", "محمود", "إبراهيم", "سعيد", "هاني", "مصطفى"]

# ================== 3. صفحة العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        customer = next((c for c in st.session_state.data if c['id'] == cust_id), None)
        if customer:
            st.markdown("<h1 style='text-align:center;'>Power Life 💧</h1>", unsafe_allow_html=True)
            history = customer.get('history', [])
            total_paid = sum(float(h.get('price', 0)) for h in history)
            total_debt = sum(float(h.get('debt', 0)) for h in history)

            col1, col2 = st.columns(2)
            col1.markdown(f"<div class='finance-card'>💰 إجمالي المدفوع<br><h2>{total_paid:,.0f}</h2></div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='debt-card'>⚠️ المديونية الحالية<br><h2>{total_debt:,.0f}</h2></div>", unsafe_allow_html=True)

            st.markdown(f"<div class='client-report'><div class='data-row'>👤 العميل: <b>{customer.get('name')}</b></div><div class='data-row'>🆔 الكود: <b>PL-{customer.get('id', 0):04d}</b></div></div>", unsafe_allow_html=True)
            
            st.subheader("🗓️ سجل الصيانات والتحصيلات")
            for h in reversed(history):
                is_admin = h.get('tech') == "الإدارة"
                card_style = "settlement-card" if is_admin else "history-card"
                st.markdown(f"""<div class='{card_style}'>
                    <b>📅 {h.get('date')}</b><br>
                    📝 {h.get('note')}<br>
                    ✅ تم تحصيل: {h.get('price')} ج.م
                </div>""", unsafe_allow_html=True)
            st.stop()
    except: pass

# ================== 4. لوحة الإدارة ==================
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h2 style='text-align:center;'>دخول الإدارة</h2>", unsafe_allow_html=True)
    u = st.text_input("المستخدم")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123":
            st.session_state.auth = True
            st.rerun()
else:
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تسجيل صيانة", "📊 حسابات عامة", "🚪 خروج"])

    if menu == "➕ إضافة عميل":
        with st.form("add"):
            name = st.text_input("الاسم")
            phone = st.text_input("رقم الموبايل")
            gov = st.selectbox("المحافظة", EGYPT_GOVS)
            loc = st.text_input("العنوان")
            device = st.selectbox("نوع الجهاز", ["جهاز جديد", "جهاز قديم", "جهاز خارجي"])
            if st.form_submit_button("حفظ العميل"):
                new_id = max([c['id'] for c in st.session_state.data], default=0) + 1
                st.session_state.data.append({"id": new_id, "name": name, "phone": phone, "gov": gov, "loc": loc, "device_type": device, "history": []})
                save_data(st.session_state.data)
                st.success("تم الحفظ")

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("بحث بالاسم...")
        for i, c in enumerate(st.session_state.data):
            if search in c.get('name', ''):
                with st.expander(f"👤 {c['name']} | 📱 {c['phone']}"):
                    current_debt = sum(float(h.get('debt', 0)) for h in c.get('history', []))
                    st.warning(f"المديونية الحالية: {current_debt} ج.م")

                    with st.form(f"edit_{c['id']}"):
                        st.write("🔧 تعديل البيانات وتحصيل المديونية")
                        n_name = st.text_input("الاسم", value=c.get('name'))
                        n_phone = st.text_input("الموبايل", value=c.get('phone'))
                        
                        st.write("---")
                        st.write("💰 **تحصيل مديونية قديمة:**")
                        pay_amount = st.number_input("المبلغ المدفوع", min_value=0.0)
                        
                        # طرق الدفع المطلوبة
                        pay_method = st.selectbox("طريقة الدفع", 
                                                ["فودافون كاش", "تحويل بنكي", "كاش للمكتب", "عن طريق فني"])
                        
                        # يظهر اختيار الفني فقط في حالة اختيار "عن طريق فني"
                        selected_tech = ""
                        if pay_method == "عن طريق فني":
                            selected_tech = st.selectbox("اختر الفني المستلم", TECHNICIANS)
                        
                        if st.form_submit_button("تحديث وحفظ التحصيل"):
                            c['name'], c['phone'] = n_name, n_phone
                            if pay_amount > 0:
                                if pay_method == "عن طريق فني":
                                    tech_display = f"الفني: {selected_tech}"
                                else:
                                    tech_display = "تحويل للشركة (مباشر)"
                                
                                c['history'].append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "note": f"تنزيل مديونية بقيمة ({pay_amount}) - طريقة الدفع: {pay_method} ({tech_display})",
                                    "tech": "الإدارة",
                                    "price": pay_amount,
                                    "debt": -pay_amount
                                })
                            save_data(st.session_state.data)
                            st.success("تم التحديث والحفظ")
                            st.rerun()

                    c1, c2, c3 = st.columns(3)
                    if c1.button("🖼️ باركود", key=f"q_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    
                    wa_msg = urllib.parse.quote(f"بيانات حسابك: https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                    c2.markdown(f'<a href="https://wa.me/2{c["phone"]}?text={wa_msg}" target="_blank"><button style="background:#25D366; color:white; border:none; padding:10px; border-radius:5px; width:100%;">🟢 واتساب</button></a>', unsafe_allow_html=True)
                    
                    if c3.button("🗑️ حذف العميل", key=f"del_{c['id']}"):
                        st.session_state.data.pop(i)
                        save_data(st.session_state.data)
                        st.rerun()

    elif menu == "🛠️ تسجيل صيانة":
        target = st.selectbox("اختر العميل", st.session_state.data, format_func=lambda x: f"{x['name']} ({x['phone']})")
        with st.form("serv_form"):
            note = st.text_area("وصف الصيانة")
            tech = st.selectbox("الفني القائم بالصيانة", TECHNICIANS)
            price = st.number_input("المبلغ المدفوع الآن", min_value=0.0)
            debt = st.number_input("المبلغ المتبقي دين", min_value=0.0)
            if st.form_submit_button("حفظ الزيارة"):
                for x in st.session_state.data:
                    if x['id'] == target['id']:
                        x['history'].append({"date": str(datetime.now().date()), "note": note, "tech": tech, "price": price, "debt": debt})
                save_data(st.session_state.data)
                st.success("تم تسجيل الصيانة")

    elif menu == "📊 حسابات عامة":
        all_p = sum(sum(float(h.get('price', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        all_d = sum(sum(float(h.get('debt', 0)) for h in c.get('history', [])) for c in st.session_state.data)
        st.metric("إجمالي التحصيل العام", f"{all_p:,.0f} ج.م")
        st.metric("إجمالي الديون المتأخرة", f"{all_d:,.0f} ج.م")

    elif menu == "🚪 خروج":
        st.session_state.auth = False
        st.rerun()
