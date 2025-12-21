import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر المخصص للموبايل ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; font-size: 14px; } /* تصغير الخط العام */
    
    .report-box { 
        background: rgba(255, 255, 255, 0.05); 
        border-radius: 8px; 
        padding: 12px; 
        border: 1px solid #007bff; 
        margin-bottom: 10px; 
    }
    .balance-text { font-size: 22px; color: #00d4ff; font-weight: bold; text-align: center; }
    .info-text { font-size: 13px; margin: 2px 0; }
    
    /* تحسين الجدول للموبايل */
    div[data-testid="stTable"] { font-size: 11px !important; }
    header {visibility: hidden;}
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

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

EGYPT_GOVS = ["القاهرة", "الجيزة", "الإسكندرية", "الدقهلية", "الشرقية", "المنوفية", "القليوبية", "البحيرة", "الغربية", "بور سعيد", "دمياط", "الإسماعيلية", "السويس", "كفر الشيخ", "الفيوم", "بني سويف", "المنيا", "أسيوط", "سوهاج", "قنا", "الأقصر", "أسوان"]

def calculate_balance(history):
    total_added = sum(float(h.get('debt', 0)) for h in history)
    total_removed = sum(float(h.get('price', 0)) for h in history)
    return total_added - total_removed

# ================== 3. واجهة الباركود (مصغرة للموبايل) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h3 style='text-align:center;'>Power Life 💧</h3>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            
            st.markdown(f"""
            <div class='report-box'>
                <div class='info-text'>👤 <b>الاسم:</b> {c['name']}</div>
                <div class='info-text'>📍 <b>المحافظة:</b> {c.get('gov', 'غير محدد')}</div>
                <div class='info-text'>🏛️ <b>الفرع:</b> {c.get('branch', 'غير محدد')}</div>
                <div class='info-text'>🔧 <b>الجهاز:</b> {c.get('device_type', '---')}</div>
                <hr style='margin: 8px 0; opacity: 0.2;'>
                <div style='text-align:center; font-size:12px;'>المديونية الحالية</div>
                <div class='balance-text'>{bal:,.0f} ج.م</div>
            </div>
            """, unsafe_allow_html=True)
            
            if c.get('history'):
                hist_list = []
                for h in reversed(c['history']):
                    # عرض التاريخ بشكل مختصر (يوم/شهر) لتوفير مساحة
                    full_date = h.get('date', '---')
                    short_date = full_date.split(' ')[0] if ' ' in full_date else full_date
                    
                    hist_list.append({
                        "التاريخ": short_date,
                        "البيان": h.get('note', 'صيانة'),
                        "(+)": f"{h.get('debt', 0)}",
                        "(-)": f"{h.get('price', 0)}",
                        "الفني": h.get('tech', 'الأدمن')
                    })
                st.table(pd.DataFrame(hist_list))
            st.stop()
    except:
        st.stop()

# ================== 4. تسجيل الدخول (للإدارة والفنيين) ==================
if "role" not in st.session_state:
    st.markdown("<h4 style='text-align:center; margin-top:30px;'>Power Life Control</h4>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 إداره", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ فني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (منطق تسجيل الدخول)
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. واجهة الإدارة (إضافة بيانات الفرع والمحافظة) ==================
if st.session_state.role == "admin":
    menu = st.sidebar.radio("القائمة", ["👥 العملاء", "➕ إضافة عميل", "🚪 خروج"])

    if menu == "👥 العملاء":
        search = st.text_input("بحث بالاسم...")
        for i, c in enumerate(st.session_state.data):
            if search in c['name']:
                with st.expander(f"👤 {c['name']}"):
                    with st.form(f"f_{c['id']}"):
                        c['gov'] = st.selectbox("المحافظة", EGYPT_GOVS, index=EGYPT_GOVS.index(c['gov']) if 'gov' in c and c['gov'] in EGYPT_GOVS else 0)
                        c['branch'] = st.text_input("الفرع", value=c.get('branch', ''))
                        a_add = st.number_input("إضافة مديونية", min_value=0.0)
                        a_rem = st.number_input("إزالة مديونية", min_value=0.0)
                        if st.form_submit_button("حفظ التعديلات"):
                            if a_add > 0 or a_rem > 0:
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": "تسويه", "tech": "الإدارة", "debt": a_add, "price": a_rem})
                            save_json("customers.json", st.session_state.data); st.success("تم الحفظ")
                    if st.button("🖼️ باركود", key=f"q_{c['id']}"):
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")

    elif menu == "➕ إضافة عميل":
        with st.form("add"):
            name = st.text_input("اسم العميل")
            gov = st.selectbox("المحافظة", EGYPT_GOVS)
            branch = st.text_input("الفرع")
            debt = st.number_input("مديونية افتتاحية", min_value=0.0)
            if st.form_submit_button("حفظ العميل الجديد"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": new_id, "name": name, "gov": gov, "branch": branch,
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "الإدارة", "debt": debt, "price": 0}] if debt > 0 else []
                })
                save_json("customers.json", st.session_state.data); st.success("تم")
    
    elif menu == "🚪 خروج": del st.session_state.role; st.rerun()
