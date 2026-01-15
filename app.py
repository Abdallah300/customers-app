import streamlit as st
import pandas as pd
from datetime import date

# إنشاء أو تحميل قاعدة بيانات بسيطة
if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame(columns=['اسم العميل', 'تاريخ التغيير القادم', 'نوع الشمع', 'ملاحظات'])

st.title("نظام متابعة العملاء وتغيير الشمع")

# إدخال بيانات العميل
with st.form("add_customer"):
    name = st.text_input("اسم العميل")
    next_change = st.date_input("تاريخ التغيير القادم", min_value=date.today())
    filter_type = st.text_input("نوع الشمع")
    notes = st.text_area("ملاحظات إضافية")
    submitted = st.form_submit_button("إضافة العميل")

    if submitted:
        new_entry = {'اسم العميل': name, 'تاريخ التغيير القادم': next_change, 'نوع الشمع': filter_type, 'ملاحظات': notes}
        st.session_state.customers = st.session_state.customers.append(new_entry, ignore_index=True)
        st.success("تم إضافة العميل بنجاح!")

# عرض البيانات
st.write("### قائمة العملاء")
st.dataframe(st.session_state.customers)
