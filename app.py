import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd

FILE_NAME = "customers.json"

def load_customers():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_customers(customers):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=2)

customers = load_customers()

st.set_page_config(page_title="إدارة عملاء", layout="wide")
st.title("💧 إدارة عملاء - شركة فلاتر المياه")

menu = st.sidebar.radio("القائمة", ["إضافة عميل", "عرض العملاء", "بحث", "تذكير بالزيارات"])

if menu == "إضافة عميل":
    st.subheader("➕ إضافة عميل")
    with st.form("add_form"):
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم التليفون")
        location = st.text_input("العنوان أو رابط Google Maps")
        notes = st.text_area("ملاحظات")
        category = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
        last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())
        if st.form_submit_button("إضافة"):
            customers.append({
                "id": len(customers) + 1,
                "name": name,
                "phone": phone,
                "location": location,
                "notes": notes,
                "category": category,
                "last_visit": str(last_visit)
            })
            save_customers(customers)
            st.success(f"✅ تم إضافة {name} بنجاح.")

elif menu == "عرض العملاء":
    st.subheader("📋 قائمة العملاء")
    if customers:
        df = pd.DataFrame(customers)
        st.dataframe(df)
    else:
        st.info("لا يوجد عملاء بعد.")

elif menu == "بحث":
    st.subheader("🔎 البحث عن عميل")
    keyword = st.text_input("اكتب اسم أو رقم")
    if keyword:
        results = [c for c in customers if keyword in c.get("name","") or keyword in c.get("phone","")]
        if results:
            st.write(pd.DataFrame(results))
        else:
            st.warning("لا يوجد نتائج.")

elif menu == "تذكير بالزيارات":
    st.subheader("⏰ العملاء المطلوب زيارتهم (أكثر من 30 يوم)")
    today = datetime.today()
    reminders = []
    for c in customers:
        try:
            last = datetime.strptime(c.get("last_visit",""), "%Y-%m-%d")
            if today - last >= timedelta(days=30):
                reminders.append(c)
        except:
            pass
    if reminders:
        st.write(pd.DataFrame(reminders))
    else:
        st.success("لا يوجد عملاء تحتاج زيارة.")