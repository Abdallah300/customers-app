import streamlit as st
import json, os, uuid
from datetime import datetime

st.set_page_config("نظام شركة فلاتر", layout="wide")

DB_FILE = "db.json"

# ================= أدوات =================
def load_db():
    if os.path.exists(DB_FILE):
        return json.load(open(DB_FILE, "r", encoding="utf8"))
    return {
        "admin": {"user": "admin", "pass": "admin123"},
        "techs": [
            {"user": "ahmed", "pass": "1111", "device": None, "active": True}
        ],
        "customers": []
    }

def save_db(db):
    json.dump(db, open(DB_FILE, "w", encoding="utf8"), ensure_ascii=False, indent=2)

db = load_db()

def balance(c):
    return sum(x["debt"] for x in c["history"]) - sum(x["paid"] for x in c["history"])

# ============== جهاز =================
if "device_id" not in st.session_state:
    st.session_state.device_id = str(uuid.uuid4())

# ============== تسجيل الدخول ============
if "role" not in st.session_state:
    st.title("🔐 تسجيل الدخول")

    user = st.text_input("اسم المستخدم")
    pw = st.text_input("كلمة السر", type="password")

    if st.button("دخول"):
        # مدير
        if user == db["admin"]["user"] and pw == db["admin"]["pass"]:
            st.session_state.role = "admin"
            st.rerun()

        # فني
        tech = next((t for t in db["techs"] if t["user"] == user), None)
        if tech and tech["pass"] == pw and tech["active"]:
            if tech["device"] is None:
                tech["device"] = st.session_state.device_id
                save_db(db)
            elif tech["device"] != st.session_state.device_id:
                st.error("❌ هذا الحساب مربوط بجهاز آخر")
                st.stop()

            st.session_state.role = "tech"
            st.session_state.user = user
            st.rerun()

        st.error("بيانات غير صحيحة")

    st.stop()

# ================== المدير ==================
if st.session_state.role == "admin":
    st.sidebar.title("👨‍💼 المدير")
    m = st.sidebar.radio("القائمة", ["العملاء", "الفنيين", "خروج"])

    if m == "العملاء":
        st.header("👥 العملاء")

        name = st.text_input("اسم عميل جديد")
        if st.button("إضافة عميل"):
            db["customers"].append({
                "id": len(db["customers"]) + 1,
                "name": name,
                "history": []
            })
            save_db(db)
            st.success("تم")

        for c in db["customers"]:
            with st.expander(c["name"]):
                st.metric("الرصيد", balance(c))
                d = st.number_input("زيادة", 0, key=f"d{c['id']}")
                p = st.number_input("خصم", 0, key=f"p{c['id']}")
                if st.button("حفظ", key=c["id"]):
                    c["history"].append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "debt": d,
                        "paid": p,
                        "tech": "المدير"
                    })
                    save_db(db)
                    st.success("تم")

    if m == "الفنيين":
        st.header("🧑‍🔧 الفنيين")

        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة السر")
        if st.button("إضافة فني"):
            db["techs"].append({
                "user": u,
                "pass": p,
                "device": None,
                "active": True
            })
            save_db(db)
            st.success("تم")

        for t in db["techs"]:
            col1, col2, col3 = st.columns(3)
            col1.write(t["user"])
            col2.write("🟢 مفعل" if t["active"] else "🔴 موقوف")
            if col3.button("إيقاف / تشغيل", key=t["user"]):
                t["active"] = not t["active"]
                t["device"] = None
                save_db(db)
                st.rerun()

    if m == "خروج":
        st.session_state.clear()
        st.rerun()

# ================== الفني ==================
if st.session_state.role == "tech":
    st.sidebar.title("🧑‍🔧 الفني")
    st.write("الفني:", st.session_state.user)

    c = st.selectbox("اختر عميل", db["customers"], format_func=lambda x: x["name"])

    d = st.number_input("مديونية", 0)
    p = st.number_input("تحصيل", 0)
    if st.button("تسجيل"):
        c["history"].append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "debt": d,
            "paid": p,
            "tech": st.session_state.user
        })
        save_db(db)
        st.success("تم")

    if st.button("خروج"):
        st.session_state.clear()
        st.rerun()
