import streamlit as st
import json, os
from datetime import datetime

st.set_page_config("💧 شركة فلاتر المياه", layout="wide")

DATA_FILE = "database.json"

# ================== أدوات ==================
def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf8") as f:
            return json.load(f)
    return {
        "customers": [],
        "techs": []
    }

def save(data):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

db = load()

def get_balance(c):
    return sum(x["debt"] for x in c["history"]) - sum(x["paid"] for x in c["history"])

# ================== الواجهة ==================
st.title("💧 نظام إدارة شركة فلاتر المياه")

tab_admin, tab_tech, tab_customer = st.tabs(
    ["👨‍💼 المدير", "🧑‍🔧 الفني", "🧑‍💼 العميل"]
)

# =================================================
# ================== المدير ========================
# =================================================
with tab_admin:
    st.header("👨‍💼 لوحة المدير")

    col1, col2, col3 = st.columns(3)
    col1.metric("عدد العملاء", len(db["customers"]))
    col2.metric("عدد الفنيين", len(db["techs"]))
    col3.metric(
        "إجمالي المديونية",
        sum(get_balance(c) for c in db["customers"])
    )

    st.divider()

    # إضافة فني
    st.subheader("🛠️ إضافة فني")
    tech_name = st.text_input("اسم الفني")
    if st.button("إضافة فني"):
        if tech_name:
            db["techs"].append({"name": tech_name})
            save(db)
            st.success("تم إضافة الفني")

    st.divider()

    # إضافة عميل
    st.subheader("👥 إضافة عميل")
    cust_name = st.text_input("اسم العميل")
    if st.button("إضافة عميل"):
        if cust_name:
            db["customers"].append({
                "id": len(db["customers"]) + 1,
                "name": cust_name,
                "history": [],
                "next": "غير محدد"
            })
            save(db)
            st.success("تم إضافة العميل")

    st.divider()

    # عرض العملاء
    st.subheader("📋 العملاء")
    for c in db["customers"]:
        with st.expander(f"{c['name']} | الرصيد: {get_balance(c)}"):
            st.write("الصيانة القادمة:", c["next"])
            for h in c["history"]:
                st.write(h)

# =================================================
# ================== الفني =========================
# =================================================
with tab_tech:
    st.header("🧑‍🔧 لوحة الفني")

    if not db["customers"]:
        st.warning("لا يوجد عملاء")
    else:
        tech = st.text_input("اسم الفني")
        customer = st.selectbox(
            "اختر العميل",
            db["customers"],
            format_func=lambda x: x["name"]
        )

        st.metric("رصيد العميل", get_balance(customer))

        service = st.selectbox(
            "نوع الخدمة",
            ["تغيير شمعات", "صيانة دورية", "تصليح"]
        )
        debt = st.number_input("مديونية", 0)
        paid = st.number_input("مدفوع", 0)
        next_date = st.date_input("الصيانة القادمة")

        if st.button("حفظ الصيانة"):
            customer["history"].append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "tech": tech,
                "service": service,
                "debt": debt,
                "paid": paid
            })
            customer["next"] = str(next_date)
            save(db)
            st.success("تم تسجيل الصيانة")

# =================================================
# ================== العميل ========================
# =================================================
with tab_customer:
    st.header("🧑‍💼 صفحة العميل")

    if not db["customers"]:
        st.warning("لا يوجد بيانات")
    else:
        c = st.selectbox(
            "اختر اسمك",
            db["customers"],
            format_func=lambda x: x["name"]
        )

        bal = get_balance(c)
        st.metric("رصيدك الحالي", bal)
        st.write("📅 الصيانة القادمة:", c["next"])

        st.subheader("📜 سجل الصيانة")
        for h in c["history"]:
            st.write(
                f"🛠 {h['date']} | {h['service']} | "
                f"+{h['debt']} -{h['paid']} | الفني: {h['tech']}"
        )
