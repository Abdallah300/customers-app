import streamlit as st
import json
import os
from datetime import datetime

# ================== 1. إعدادات المظهر ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
.stApp { background: #000b1a; color: #ffffff; }
* { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
.client-header {
    background: #001f3f; border-radius: 15px;
    padding: 20px; border: 2px solid #007bff; margin-bottom: 25px;
}
header {visibility: hidden;}
footer {visibility: hidden;}
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

if 'data' not in st.session_state:
    st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state:
    st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة الباركود ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center;color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)
            current_bal = calculate_balance(c.get('history', []))

            st.markdown(f"""
            <div class='client-header'>
            <div>👤 <b>العميل:</b> {c['name']}</div>
            <div>📍 {c.get('gov','---')} | 🏛️ {c.get('branch','---')}</div>
            <hr>
            <div style='text-align:center'>
            <p>إجمالي المديونية</p>
            <p style='font-size:35px;color:#00ffcc'>{current_bal:,.0f} ج.م</p>
            </div>
            </div>
            """, unsafe_allow_html=True)

            st.subheader("📋 سجل الحركات")
            running = 0
            for h in reversed(c.get('history', [])):
                running += float(h.get('debt',0)) - float(h.get('price',0))
                st.markdown("---")
                st.markdown(f"📝 {h.get('note')}")
                st.markdown(f"📅 {h.get('date')} | 👤 {h.get('tech')}")
                st.info(f"💰 الرصيد بعد العملية: {running:,.0f} ج.م")
            st.stop()
    except:
        st.stop()

# ================== 4. تسجيل الدخول ==================
if "role" not in st.session_state:
    c1, c2 = st.columns(2)
    if c1.button("🔑 لوحة الإدارة"): st.session_state.role="admin_login"; st.rerun()
    if c2.button("🛠️ لوحة الفني"): st.session_state.role="tech_login"; st.rerun()
    st.stop()

if st.session_state.role=="admin_login":
    u=st.text_input("اسم المستخدم")
    p=st.text_input("كلمة السر",type="password")
    if st.button("دخول"):
        if u=="admin" and p=="admin123":
            st.session_state.role="admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role=="tech_login":
    t_list=[t['name'] for t in st.session_state.techs]
    t_user=st.selectbox("اختر الفني",t_list)
    p=st.text_input("السر",type="password")
    if st.button("دخول"):
        tech=next(t for t in st.session_state.techs if t['name']==t_user)
        if p==tech['pass']:
            st.session_state.role="tech"
            st.session_state.tech_name=t_user
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 5. لوحة الإدارة ==================
if st.session_state.role=="admin":
    st.sidebar.title("💎 الإدارة")
    menu=st.sidebar.radio("القائمة",["👥 إدارة العملاء","➕ إضافة عميل","📊 الحسابات","🛠️ الفنيين","🚪 خروج"])

    if menu=="👥 إدارة العملاء":
        for c in st.session_state.data:
            with st.expander(f"{c['name']} | رصيد {calculate_balance(c['history'])}"):
                if st.button("🗑️ حذف العميل نهائيًا",key=f"del_{c['id']}"):
                    st.session_state.confirm_delete=c['id']

        if "confirm_delete" in st.session_state:
            cid=st.session_state.confirm_delete
            st.warning("هل أنت متأكد من الحذف النهائي؟")
            col1,col2=st.columns(2)
            if col1.button("نعم"):
                st.session_state.data=[x for x in st.session_state.data if x['id']!=cid]
                save_json("customers.json",st.session_state.data)
                del st.session_state.confirm_delete
                st.success("تم الحذف"); st.rerun()
            if col2.button("إلغاء"):
                del st.session_state.confirm_delete; st.rerun()

    elif menu=="➕ إضافة عميل":
        with st.form("new"):
            n=st.text_input("اسم العميل")
            g=st.text_input("المحافظة")
            b=st.text_input("الفرع")
            d=st.number_input("مديونية افتتاحية",min_value=0.0)
            if st.form_submit_button("إضافة"):
                nid=max([x['id'] for x in st.session_state.data],default=0)+1
                st.session_state.data.append({
                    "id":nid,"name":n,"gov":g,"branch":b,
                    "history":[{"date":datetime.now().strftime("%Y-%m-%d"),"note":"رصيد افتتاحي","tech":"الإدارة","debt":d,"price":0}] if d>0 else []
                })
                save_json("customers.json",st.session_state.data)
                st.success("تمت الإضافة")

    elif menu=="📊 الحسابات":
        total=sum(calculate_balance(c['history']) for c in st.session_state.data)
        st.metric("إجمالي المديونيات",f"{total:,.0f} ج.م")

    elif menu=="🛠️ الفنيين":
        with st.form("addtech"):
            tn=st.text_input("اسم الفني")
            tp=st.text_input("كلمة السر",type="password")
            if st.form_submit_button("إضافة"):
                st.session_state.techs.append({"name":tn,"pass":tp})
                save_json("techs.json",st.session_state.techs)
                st.success("تم إضافة الفني")

        for t in st.session_state.techs:
            with st.expander(t['name']):
                for c in st.session_state.data:
                    for h in c.get('history',[]):
                        if h.get('tech')==t['name']:
                            st.write(c['name'],h['note'],h['debt'],h['price'],h['date'])

    elif menu=="🚪 خروج":
        del st.session_state.role; st.rerun()

# ================== 6. لوحة الفني ==================
elif st.session_state.role=="tech":
    st.sidebar.title(st.session_state.tech_name)
    target=st.selectbox("اختر العميل",st.session_state.data,format_func=lambda x:x['name'])

    with st.form("visit"):
        op=st.selectbox("نوع العملية",["🔧 صيانة","🔁 تغيير شمع","⚖️ تسوية حساب"])
        add=st.number_input("مديونية",min_value=0.0)
        rem=st.number_input("تحصيل",min_value=0.0)
        note=st.text_area("الوصف")
        if st.form_submit_button("حفظ"):
            for x in st.session_state.data:
                if x['id']==target['id']:
                    x['history'].append({
                        "date":datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "note":f"{op} - {note}",
                        "tech":st.session_state.tech_name,
                        "debt":add,
                        "price":rem
                    })
            save_json("customers.json",st.session_state.data)
            st.success("تم التسجيل")

    if st.sidebar.button("🚪 خروج"):
        del st.session_state.role; st.rerun()
