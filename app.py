import streamlit as st
import json, os
from datetime import datetime

st.set_page_config("💧 شركة فلاتر المياه", layout="wide")

DB_FILE = "db.json"

# ================== أدوات ==================
def load_db():
    if os.path.exists(DB_FILE):
        return json.load(open(DB_FILE, "r", encoding="utf8"))
    return {"customers": [], "techs": []}

def save_db(db):
    json.dump(db, open(DB_FILE, "w", encoding="utf8"), ensure_ascii=False, indent=2)

db = load_db()

def balance(c):
    return sum(x["debt"] for x in c["history"]) - sum(x["paid"] for x in c["history"])

# ================== الواجهة ==================
st.title("💧 نظام شركة فلاتر المياه")

tab_admin, tab_tech, tab_customer = st.tabs(
    ["👨‍💼 المدير", "🧑‍🔧 الفني", "🧑‍💼 العميل"]
)

# =================================================
# ================== المدير ========================
# =================================================
with tab_admin:
    st.header("👨‍💼 لوحة المدير")

    col1, col2 = st.columns(2)
    col1.metric("عدد العملاء", len(db["customers"]))
    col2.metric("إجمالي المديونية", sum(balance(c) for c in db["customers"]))

    st.divider()

    # إضافة عميل
    st.subheader("➕ إضافة عميل")
    cname = st.text_input("اسم العميل")
    if st.button("إضافة"):
        if cname:
            db["customers"].append({
                "id": len(db["customers"]) + 1,
                "name": cname,
                "history": [],
                "next": "غير محدد"
            })
            save_db(db)
            st.success("تم إضافة العميل")

    st.divider()

    # إدارة فلوس العميل
    st.subheader("💰 تعديل رصيد عميل")
    if db["customers"]:
        c = st.selectbox("اختر العميل", db["customers"], format_func=lambda x: x["name"])
        st.metric("الرصيد الحالي", balance(c))
        d = st.number_input("زيادة مديونية", 0)
        p = st.number_input("خصم / مدفوع", 0)
        if st.button("حفظ التعديل"):
            c["history"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tech": "المدير",
                "note": "تعديل يدوي",
                "debt": d,
                "paid": p
            })
            save_db(db)
            st.success("تم تعديل الرصيد")

# =================================================
# ================== الفني =========================
# =================================================
with tab_tech:
    st.header("🧑‍🔧 لوحة الفني")

    if not db["customers"]:
        st.warning("لا يوجد عملاء")
    else:
        tech = st.text_input("اسم الفني")
        c = st.selectbox("اختر العميل", db["customers"], format_func=lambda x: x["name"])
        st.metric("رصيد العميل", balance(c))

        service = st.selectbox(
            "نوع الخدمة",
            ["تغيير شمعات", "صيانة دورية", "تصليح"]
        )
        debt = st.number_input("مديونية", 0)
        paid = st.number_input("مدفوع", 0)
        next_date = st.date_input("الصيانة القادمة")

        if st.button("تسجيل صيانة"):
            c["history"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tech": tech,
                "note": service,
                "debt": debt,
                "paid": paid
            })
            c["next"] = str(next_date)
            save_db(db)
            st.success("تم تسجيل الصيانة")

# =================================================
# ================== العميل ========================
# =================================================
with tab_customer:
    st.header("🧑‍💼 صفحة العميل")

    if not db["customers"]:
        st.warning("لا يوجد بيانات")
    else:
        c = st.selectbox("اختر اسمك", db["customers"], format_func=lambda x: x["name"])
        st.metric("رصيدك", balance(c))
        st.write("📅 الصيانة القادمة:", c["next"])

        st.subheader("📜 سجل الصيانة")
        for h in c["history"]:
            st.write(
                f"🛠 {h['date']} | {h['note']} | "
                f"+{h['debt']} -{h['paid']} | {h['tech']}"
            )
