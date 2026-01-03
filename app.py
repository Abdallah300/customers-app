import streamlit as st
import json, os, hashlib
from datetime import datetime, timedelta

# ================== الإعدادات ==================
BASE_URL = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"

st.set_page_config("Power Life Pro 💧", "💧", layout="wide")

# ================== ستايل ==================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {direction: rtl; background:#000b1a;}
* {font-family:Cairo; color:white;}
.card {background:#001529; border:2px solid #007bff; border-radius:15px; padding:20px; margin:15px 0;}
.hist {background:rgba(255,255,255,.07); border-right:5px solid #00d4ff; padding:10px; border-radius:10px; margin:10px 0;}
</style>
""", unsafe_allow_html=True)

# ================== أدوات ==================
def hash_pass(p): return hashlib.sha256(p.encode()).hexdigest()

def load(file):
    if os.path.exists(file):
        with open(file,"r",encoding="utf8") as f:
            try: return json.load(f)
            except: return []
    return []

def save(file,data):
    with open(file,"w",encoding="utf8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

def balance(hist):
    return sum(h["debt"] for h in hist) - sum(h["paid"] for h in hist)

# ================== تحميل ==================
if "customers" not in st.session_state: st.session_state.customers = load("customers.json")
if "techs" not in st.session_state: st.session_state.techs = load("techs.json")

ADMIN_HASH = hash_pass("1010")

# ================== صفحة العميل ==================
params = st.query_params
if "id" in params:
    cid = int(params["id"])
    c = next((x for x in st.session_state.customers if x["id"]==cid),None)
    if not c:
        st.error("العميل غير موجود"); st.stop()

    pin = st.text_input("🔐 أدخل الرقم السري", type="password")
    if pin != c["pin"]:
        st.stop()

    bal = balance(c["history"])
    st.markdown(f"""
    <div class="card">
        <h2 style="text-align:center">{c['name']}</h2>
        <h3 style="text-align:center;color:{'#00ffcc' if bal<=0 else '#ff4b4b'}">
        الرصيد: {bal:,.2f} ج.م
        </h3>
        <p style="text-align:center">📅 الصيانة القادمة: {c['next']}</p>
    </div>
    """,unsafe_allow_html=True)

    for h in reversed(c["history"]):
        st.markdown(f"""
        <div class="hist">
        📅 {h['date']}<br>
        👨‍🔧 {h['tech']}<br>
        📝 {h['note']}<br>
        ➕ {h['debt']} | ➖ {h['paid']}
        </div>
        """,unsafe_allow_html=True)
    st.stop()

# ================== تسجيل الدخول ==================
if "role" not in st.session_state:
    st.title("Power Life 💧")
    if st.button("🔑 مدير"): st.session_state.role="admin_login"
    if st.button("🛠️ فني"): st.session_state.role="tech_login"
    st.stop()

# مدير
if st.session_state.role=="admin_login":
    p = st.text_input("كلمة مرور المدير", type="password")
    if st.button("دخول") and hash_pass(p)==ADMIN_HASH:
        st.session_state.role="admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# فني
if st.session_state.role=="tech_login":
    names=[t["name"] for t in st.session_state.techs]
    u = st.selectbox("اسم الفني", names)
    p = st.text_input("كلمة المرور", type="password")
    if st.button("دخول"):
        t=next(x for x in st.session_state.techs if x["name"]==u)
        if hash_pass(p)==t["pass"]:
            st.session_state.role="tech"
            st.session_state.user=u
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== لوحة المدير ==================
if st.session_state.role=="admin":
    m=st.sidebar.radio("القائمة",["👥 العملاء","🛠️ الفنيين","📊 تقرير","🚪 خروج"])

    if m=="👥 العملاء":
        if st.button("➕ عميل جديد"):
            nid=max([c["id"] for c in st.session_state.customers],default=0)+1
            st.session_state.customers.append({
                "id":nid,"name":f"عميل {nid}","pin":"1234",
                "history":[],"next":"قريبًا"
            })
            save("customers.json",st.session_state.customers)
            st.rerun()

        for c in st.session_state.customers:
            with st.expander(f"{c['name']} | {balance(c['history']):,.0f}"):
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={BASE_URL}/?id={c['id']}")
                c["name"]=st.text_input("الاسم",c["name"],key=c["id"])
                c["pin"]=st.text_input("PIN",c["pin"])
                if st.button("حفظ",key=f"s{c['id']}"):
                    save("customers.json",st.session_state.customers)
                    st.success("تم")

    if m=="🛠️ الفنيين":
        n=st.text_input("اسم الفني")
        p=st.text_input("كلمة المرور",type="password")
        if st.button("إضافة"):
            st.session_state.techs.append({"name":n,"pass":hash_pass(p)})
            save("techs.json",st.session_state.techs)
            st.rerun()
        st.table(st.session_state.techs)

    if m=="📊 تقرير":
        st.metric("إجمالي المديونية",
        sum(balance(c["history"]) for c in st.session_state.customers))

    if m=="🚪 خروج":
        del st.session_state.role; st.rerun()

# ================== لوحة الفني ==================
if st.session_state.role=="tech":
    st.header(f"🛠️ {st.session_state.user}")
    ids={c["id"]:c["name"] for c in st.session_state.customers}
    cid=st.selectbox("اختر العميل",ids,format_func=lambda x:ids[x])
    c=next(x for x in st.session_state.customers if x["id"]==cid)

    st.error(f"الرصيد الحالي: {balance(c['history']):,.2f}")

    with st.form("add"):
        note=st.text_area("الوصف")
        d=st.number_input("مديونية",min_value=0.0)
        p=st.number_input("مدفوع",min_value=0.0)
        nxt=st.date_input("الصيانة القادمة",datetime.now()+timedelta(days=90))
        if st.form_submit_button("حفظ"):
            if p>d+balance(c["history"]):
                st.error("قيمة غير صحيحة"); st.stop()
            c["history"].append({
                "date":datetime.now().strftime("%Y-%m-%d %H:%M"),
                "note":note,"tech":st.session_state.user,
                "debt":d,"paid":p
            })
            c["next"]=str(nxt)
            save("customers.json",st.session_state.customers)
            st.success("تم")
            st.rerun()

    if st.button("🚪 خروج"):
        del st.session_state.role; st.rerun()
