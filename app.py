import streamlit as st
import json, os
from datetime import datetime, timedelta
import pandas as pd
import pydeck as pdk

# --------------------------
# ملفات التخزين
# --------------------------
CUSTOMERS_FILE = "customers.json"
TECHNICIANS_FILE = "technicians.json"

# --------------------------
# دوال المساعدة
# --------------------------
def load_data(file):
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_next_visit(last_visit, days):
    try:
        last_visit_date = datetime.strptime(last_visit, "%Y-%m-%d")
        next_visit_date = last_visit_date + timedelta(days=int(days))
        return next_visit_date.strftime("%Y-%m-%d")
    except:
        return "غير متوفر"

# --------------------------
# عرض العملاء على الخريطة (أقمار صناعية)
# --------------------------
def render_customer_map(customers):
    if not customers:
        st.info("لا يوجد عملاء لعرضهم على الخريطة حالياً.")
        return

    df_map = pd.DataFrame(customers)

    if df_map.empty or "lat" not in df_map or "lon" not in df_map:
        st.warning("بيانات العملاء لا تحتوي على إحداثيات صحيحة.")
        return

    # تحويل lat/lon لأرقام
    df_map["lat"] = pd.to_numeric(df_map["lat"], errors="coerce")
    df_map["lon"] = pd.to_numeric(df_map["lon"], errors="coerce")
    df_map = df_map.dropna(subset=["lat", "lon"])

    if df_map.empty:
        st.warning("لا يوجد إحداثيات صالحة للعملاء.")
        return

    # حساب مركز الخريطة
    center_lat = df_map["lat"].mean()
    center_lon = df_map["lon"].mean()
    initial_zoom = 6 if len(df_map) == 1 else 8

    # إضافة Tooltip
    df_map["tooltip_text"] = df_map.apply(
        lambda row: f"العميل: {row['name']}\nالمنطقة: {row['region']}\nآخر زيارة: {row['last_visit']}",
        axis=1
    )

    # طبقة العملاء
    layers = [
        pdk.Layer(
            "ScatterplotLayer",
            data=df_map,
            get_position="[lon, lat]",
            get_fill_color="[200, 30, 0, 160]",
            get_radius=4000,
            pickable=True,
        ),
        pdk.Layer(
            "TextLayer",
            data=df_map,
            get_position="[lon, lat]",
            get_text="name",
            get_size=16,
            get_color=[255, 255, 255],
            get_alignment_baseline="'bottom'",
        ),
    ]

    # عرض الخريطة (أقمار صناعية + شوارع)
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/satellite-streets-v11",
        initial_view_state=pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=initial_zoom,
            pitch=0,
        ),
        layers=layers,
        tooltip={"text": "{tooltip_text}"} if not df_map.empty else None
    ))

# --------------------------
# الصفحة الرئيسية
# --------------------------
def main():
    st.set_page_config(page_title="إدارة العملاء والفنيين", layout="wide")
    st.title("📍 إدارة العملاء والفنيين")

    # تحميل البيانات
    customers = load_data(CUSTOMERS_FILE)
    technicians = load_data(TECHNICIANS_FILE)

    menu = st.sidebar.radio("القائمة", ["العملاء", "الفنيين", "خريطة العملاء"])

    # إدارة العملاء
    if menu == "العملاء":
        st.header("إدارة العملاء")
        with st.form("customer_form"):
            name = st.text_input("اسم العميل")
            phone = st.text_input("رقم الهاتف")
            region = st.text_input("المنطقة")
            last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())
            period_days = st.number_input("الفترة بين الزيارات (أيام)", min_value=1, value=30)
            lat = st.text_input("خط العرض (Latitude)")
            lon = st.text_input("خط الطول (Longitude)")

            submitted = st.form_submit_button("إضافة عميل")
            if submitted:
                customer = {
                    "name": name,
                    "phone": phone,
                    "region": region,
                    "last_visit": str(last_visit),
                    "period_days": period_days,
                    "next_visit": calculate_next_visit(str(last_visit), period_days),
                    "lat": lat,
                    "lon": lon
                }
                customers.append(customer)
                save_data(CUSTOMERS_FILE, customers)
                st.success("تمت إضافة العميل بنجاح!")

        # عرض العملاء
        if customers:
            st.subheader("قائمة العملاء")
            df = pd.DataFrame(customers)
            st.dataframe(df)

    # إدارة الفنيين
    elif menu == "الفنيين":
        st.header("إدارة الفنيين")
        with st.form("technician_form"):
            name = st.text_input("اسم الفني")
            phone = st.text_input("رقم الهاتف")
            region = st.text_input("المنطقة")

            submitted = st.form_submit_button("إضافة فني")
            if submitted:
                technician = {
                    "name": name,
                    "phone": phone,
                    "region": region
                }
                technicians.append(technician)
                save_data(TECHNICIANS_FILE, technicians)
                st.success("تمت إضافة الفني بنجاح!")

        # عرض الفنيين
        if technicians:
            st.subheader("قائمة الفنيين")
            df = pd.DataFrame(technicians)
            st.dataframe(df)

    # خريطة العملاء
    elif menu == "خريطة العملاء":
        st.header("🗺️ خريطة العملاء")
        render_customer_map(customers)

if __name__ == "__main__":
    main()
