import streamlit as st
import json
import os
import pandas as pd
import pydeck as pdk
from datetime import datetime

# --------------------------
# تحميل / حفظ العملاء
# --------------------------
CUSTOMERS_FILE = "customers.json"

def load_customers():
    if os.path.exists(CUSTOMERS_FILE):
        with open(CUSTOMERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_customers(customers):
    with open(CUSTOMERS_FILE, "w", encoding="utf-8") as f:
        json.dump(customers, f, ensure_ascii=False, indent=4)

customers = load_customers()

# --------------------------
# واجهة التطبيق
# --------------------------
st.set_page_config(page_title="💧 Baro Life - العملاء", layout="wide")

st.title("💧 Baro Life ترحب بكم")

menu = st.sidebar.radio("القائمة", ["➕ إضافة العميل", "📋 عرض العملاء"])

# --------------------------
# إضافة العميل
# --------------------------
if menu == "➕ إضافة العميل":
    st.subheader("➕ إضافة عميل")
    with st.form("add_form"):
        name = st.text_input("اسم العميل")
        phone = st.text_input("رقم التليفون")
        lat = st.text_input("Latitude (مثال: 30.1234)")
        lon = st.text_input("Longitude (مثال: 31.5678)")
        location = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else ""
        governorate = st.text_input("المحافظة")
        line = st.text_input("الخط")
        notes = st.text_area("ملاحظات")
        category = st.selectbox("التصنيف", ["منزل", "شركة", "مدرسة"])
        last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())

        if st.form_submit_button("إضافة"):
            customers.append({
                "id": len(customers) + 1,
                "name": name,
                "phone": phone,
                "lat": lat,
                "lon": lon,
                "location": location,
                "governorate": governorate,
                "line": line,
                "notes": notes,
                "category": category,
                "last_visit": str(last_visit)
            })
            save_customers(customers)
            st.success(f"✅ تم إضافة {name} بنجاح.")

            # إعادة تحميل العملاء بعد الحفظ
            customers = load_customers()

    # --------------------------
    # عرض الخريطة مباشرة بعد إضافة عميل
    # --------------------------
    st.subheader("🗺️ خريطة العملاء (مباشرة)")

    locations = []
    for c in customers:
        try:
            if c.get("lat") and c.get("lon"):
                lat = float(str(c["lat"]).strip())
                lon = float(str(c["lon"]).strip())
                locations.append({
                    "name": c["name"],
                    "lat": lat,
                    "lon": lon,
                    "info": f"{c['phone']} - {c.get('governorate','')} - {c.get('line','')}"
                })
        except:
            pass

    if locations:
        df = pd.DataFrame(locations)

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v11',
            initial_view_state=pdk.ViewState(
                latitude=df["lat"].mean(),
                longitude=df["lon"].mean(),
                zoom=10,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_color='[200, 30, 0, 160]',
                    get_radius=300,
                    pickable=True
                ),
                pdk.Layer(
                    'TextLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_text='name',
                    get_color='[0, 0, 0, 200]',
                    get_size=14,
                    get_alignment_baseline="'bottom'"
                )
            ],
            tooltip={"text": "{name}\n{info}"}
        ))
    else:
        st.info("❌ لا يوجد عملاء مسجل لهم موقع بعد.")

# --------------------------
# عرض العملاء في جدول
# --------------------------
elif menu == "📋 عرض العملاء":
    st.subheader("📋 قائمة العملاء")

    if customers:
        df = pd.DataFrame(customers)
        st.dataframe(df)

        # --------------------------
        # عرض الخريطة لكل العملاء
        # --------------------------
        st.subheader("🗺️ خريطة جميع العملاء")

        locations = []
        for c in customers:
            try:
                if c.get("lat") and c.get("lon"):
                    lat = float(str(c["lat"]).strip())
                    lon = float(str(c["lon"]).strip())
                    locations.append({
                        "name": c["name"],
                        "lat": lat,
                        "lon": lon,
                        "info": f"{c['phone']} - {c.get('governorate','')} - {c.get('line','')}"
                    })
            except:
                pass

        if locations:
            df = pd.DataFrame(locations)

            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/streets-v11',
                initial_view_state=pdk.ViewState(
                    latitude=df["lat"].mean(),
                    longitude=df["lon"].mean(),
                    zoom=10,
                    pitch=0,
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=df,
                        get_position='[lon, lat]',
                        get_color='[0, 100, 200, 160]',
                        get_radius=300,
                        pickable=True
                    ),
                    pdk.Layer(
                        'TextLayer',
                        data=df,
                        get_position='[lon, lat]',
                        get_text='name',
                        get_color='[0, 0, 0, 200]',
                        get_size=14,
                        get_alignment_baseline="'bottom'"
                    )
                ],
                tooltip={"text": "{name}\n{info}"}
            ))
        else:
            st.info("❌ لا يوجد مواقع عملاء لعرضها على الخريطة.")
    else:
        st.info("❌ لا يوجد عملاء بعد.")
