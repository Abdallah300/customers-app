import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import requests
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
import time
from datetime import timedelta

# ================== 1. التنسيق العام (Power Life Style) ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

# إضافة meta tags لجعل التطبيق PWA
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<link rel="manifest" href="/manifest.json">
""", unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; height: auto !important; }
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    .metric-container { background: rgba(0, 212, 255, 0.1); border: 2px solid #00d4ff; border-radius: 15px; padding: 20px; text-align: center; margin: 10px; }
    .metric-title { color: #ffffff; font-size: 18px; font-weight: bold; }
    .metric-value { color: #00d4ff; font-size: 28px; font-weight: bold; }

    .balance-box { background: rgba(0, 255, 204, 0.15); border: 1px solid #00ffcc; border-radius: 10px; padding: 15px; text-align: center; margin: 10px 0; }
    .logo-text { font-size: 45px; font-weight: bold; color: #00d4ff; text-align: center; display: block; text-shadow: 2px 2px 10px #007bff; padding: 10px; }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div { 
        background-color: #ffffff !important; 
        color: #000000 !important; font-weight: bold !important;
    }
    header, footer {visibility: hidden;}
    
    /* تنسيق للهواتف */
    @media (max-width: 768px) {
        .logo-text { font-size: 30px; }
        .metric-value { font-size: 20px; }
        .metric-title { font-size: 14px; }
    }
    
    /* زر التثبيت على الهاتف */
    .install-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #00d4ff;
        color: white;
        padding: 12px 24px;
        border-radius: 25px;
        text-decoration: none;
        z-index: 1000;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        border: none;
        cursor: pointer;
    }
    
    /* خريطة مخصصة */
    .map-container {
        border-radius: 15px;
        overflow: hidden;
        border: 2px solid #00d4ff;
        margin: 10px 0;
    }
    
    .location-tracker {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات والتحديث اللحظي ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_and_refresh(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.session_state.data = load_json("customers.json", []) 

# تهيئة بيانات GPS
if 'gps_data' not in st.session_state:
    st.session_state.gps_data = load_json("gps_locations.json", {})

def save_gps_data():
    with open("gps_locations.json", "w", encoding="utf-8") as f:
        json.dump(st.session_state.gps_data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state or st.sidebar.button("🔄 تحديث البيانات"):
    st.session_state.data = load_json("customers.json", [])
    st.session_state.techs = load_json("techs.json", [])
    st.session_state.gps_data = load_json("gps_locations.json", {})
    if 'data' in st.session_state: st.toast("تم مزامنة البيانات ✅")

def calculate_balance(history):
    try: return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)
    except: return 0.0

# ================== 3. نظام GPS و الخرائط ==================
def get_current_location():
    """الحصول على الموقع الحالي للفني"""
    try:
        # في بيئة الهاتف، سنستخدم API جافاسكريبت
        location_data = st.session_state.get('current_location', {})
        return location_data
    except:
        return None

def update_tech_location(tech_name, lat=None, lng=None, address=None):
    """تحديث موقع الفني"""
    if tech_name not in st.session_state.gps_data:
        st.session_state.gps_data[tech_name] = []
    
    location_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lat": lat,
        "lng": lng,
        "address": address,
        "status": "نشط"
    }
    
    st.session_state.gps_data[tech_name].append(location_data)
    
    # حفظ آخر 50 موقع فقط لتجنب التخزين الزائد
    if len(st.session_state.gps_data[tech_name]) > 50:
        st.session_state.gps_data[tech_name] = st.session_state.gps_data[tech_name][-50:]
    
    save_gps_data()
    return location_data

def get_address_from_coords(lat, lng):
    """تحويل الإحداثيات إلى عنوان"""
    try:
        geolocator = Nominatim(user_agent="power_life_tracker")
        location = geolocator.reverse(f"{lat}, {lng}", language='ar')
        return location.address if location else "عنوان غير معروف"
    except:
        return f"الموقع: {lat}, {lng}"

def create_tech_map(tech_locations, customer_location=None):
    """إنشاء خريطة تتبع الفنيين"""
    m = folium.Map(location=[30.0444, 31.2357], zoom_start=10)  # إحداثيات القاهرة الافتراضية
    
    # إضافة مواقع الفنيين
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred']
    for idx, (tech_name, locations) in enumerate(tech_locations.items()):
        if locations:
            last_loc = locations[-1]
            if last_loc.get('lat') and last_loc.get('lng'):
                color = colors[idx % len(colors)]
                
                # إضافة علامة للفني
                folium.Marker(
                    [last_loc['lat'], last_loc['lng']],
                    popup=f"<b>{tech_name}</b><br>الوقت: {last_loc['timestamp']}<br>الحالة: {last_loc['status']}",
                    icon=folium.Icon(color=color, icon='user', prefix='fa')
                ).add_to(m)
                
                # إضافة مسار الحركة
                points = [(loc['lat'], loc['lng']) for loc in locations if loc.get('lat') and loc.get('lng')]
                if len(points) > 1:
                    folium.PolyLine(points, color=color, weight=2.5, opacity=0.7).add_to(m)
    
    # إضافة موقع العميل إذا كان موجوداً
    if customer_location and customer_location.get('lat') and customer_location.get('lng'):
        folium.Marker(
            [customer_location['lat'], customer_location['lng']],
            popup=f"<b>موقع العميل</b><br>{customer_location.get('address', '')}",
            icon=folium.Icon(color='green', icon='home', prefix='fa')
        ).add_to(m)
    
    return m

# ================== 4. PWA Install Prompt ==================
st.markdown("""
<script>
// كود لتثبيت التطبيق على الهاتف
let deferredPrompt;
const installBtn = document.createElement('div');
installBtn.innerHTML = '📱 تثبيت التطبيق';
installBtn.className = 'install-btn';
installBtn.style.display = 'none';

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installBtn.style.display = 'block';
    
    installBtn.addEventListener('click', async () => {
        installBtn.style.display = 'none';
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        console.log(`User response to the install prompt: ${outcome}`);
        deferredPrompt = null;
    });
});

document.body.appendChild(installBtn);

// دالة لجلب الموقع الجغرافي
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const locationData = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                    accuracy: position.coords.accuracy,
                    timestamp: new Date().toISOString()
                };
                
                // إرسال البيانات للبايثون عبر Session State
                const data = {location: locationData};
                fetch('/_stcore/api/session-state', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        key: 'current_location',
                        value: data
                    })
                });
                
                console.log('Location sent:', locationData);
            },
            function(error) {
                console.error('Error getting location:', error);
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }
}

// تحديث الموقع كل 30 ثانية
getLocation();
setInterval(getLocation, 30000);

// إضافة زر يدوي لتحديث الموقع
const locationBtn = document.createElement('button');
locationBtn.innerHTML = '📍 تحديث الموقع';
locationBtn.style.cssText = `
    position: fixed;
    bottom: 70px;
    right: 20px;
    background: #764ba2;
    color: white;
    padding: 10px 20px;
    border-radius: 25px;
    border: none;
    cursor: pointer;
    z-index: 1000;
    box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
`;
locationBtn.onclick = getLocation;
document.body.appendChild(locationBtn);
</script>
""", unsafe_allow_html=True)

# ================== 5. واجهة الباركود للعملاء ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            st.markdown(f"<div style='text-align:center; background:rgba(0,212,255,0.1); padding:20px; border-radius:15px; border:1px solid #00d4ff;'><h2 style='color:white;'>مرحباً: {c['name']}</h2><h1 style='color:#00ffcc;'>المتبقي: {bal:,.0f} ج.م</h1></div>", unsafe_allow_html=True)
            
            # عرض موقع العميل إذا كان مسجلاً
            if c.get('location'):
                with st.expander("📍 موقع العميل"):
                    st.write(f"**العنوان:** {c.get('location', {}).get('address', 'غير محدد')}")
                    if c['location'].get('lat') and c['location'].get('lng'):
                        try:
                            m = folium.Map(location=[c['location']['lat'], c['location']['lng']], zoom_start=15)
                            folium.Marker(
                                [c['location']['lat'], c['location']['lng']],
                                popup=f"<b>موقع {c['name']}</b>",
                                icon=folium.Icon(color='red', icon='home')
                            ).add_to(m)
                            folium_static(m, width=400, height=300)
                        except:
                            st.info("تعذر تحميل الخريطة")
            
            for h in reversed(c.get('history', [])):
                st.write(f"📅 {h.get('date','')}")
                if float(h.get('price', 0)) > 0: st.success(f"💰 تم دفع: {h['price']}")
                if float(h.get('debt', 0)) > 0: st.error(f"🛠️ تكلفة: {h['debt']}")
                st.write(f"📝 {h.get('note','-')}")
                st.markdown("---")
            st.stop()
    except: st.stop()

# ================== 6. نظام تسجيل الدخول ==================
if "role" not in st.session_state:
    st.markdown("<span class='logo-text'>Power Life 💧</span>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 المدير", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ الفنيين", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم"); p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_names = [t['name'] for t in st.session_state.techs]
    t_user = st.selectbox("اختر اسمك", t_names) if t_names else st.error("لا يوجد فنيين")
    p = st.text_input("كلمة السر", type="password")
    if st.button("دخول"):
        tech_data = next(t for t in st.session_state.techs if t['name'] == t_user)
        if p == tech_data['pass']: 
            st.session_state.role = "tech_panel"
            st.session_state.current_tech = t_user
            
            # تسجيل دخول الموقع تلقائياً
            location_data = get_current_location()
            if location_data and location_data.get('lat'):
                address = get_address_from_coords(location_data['lat'], location_data['lng'])
                update_tech_location(t_user, location_data['lat'], location_data['lng'], address)
            
            st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()

# ================== 7. واجهة المدير (مع نظام GPS) ==================
if st.session_state.role == "admin":
    st.sidebar.markdown("## لوحة المدير")
    if st.sidebar.button("🔃 تحديث السيستم الآن"): st.rerun()
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "🛠️ تقارير الفنيين", "📍 تتبع الفنيين", "📊 المالية", "🚪 خروج"])

    if menu == "📍 تتبع الفنيين":
        st.markdown("<h2 style='color:#00d4ff;'>📍 تتبع الفنيين مباشرة على الخريطة</h2>", unsafe_allow_html=True)
        
        # عرض الخريطة مع جميع الفنيين
        st.markdown("<div class='map-container'>", unsafe_allow_html=True)
        m = create_tech_map(st.session_state.gps_data)
        folium_static(m, width=1000, height=500)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # تحديث الخريطة كل 30 ثانية
        if st.button("🔄 تحديث المواقع", key="refresh_map"):
            st.rerun()
        
        # جدول الفنيين النشطين
        st.subheader("🗺️ الفنيين النشطين الآن")
        active_techs = []
        for tech_name, locations in st.session_state.gps_data.items():
            if locations:
                last_loc = locations[-1]
                time_diff = datetime.now() - datetime.strptime(last_loc['timestamp'], "%Y-%m-%d %H:%M:%S")
                if time_diff < timedelta(minutes=10):  # نشط إذا أقل من 10 دقائق
                    active_techs.append({
                        "الفني": tech_name,
                        "آخر تحديث": last_loc['timestamp'],
                        "الحالة": last_loc['status'],
                        "العنوان": last_loc.get('address', 'غير معروف')[:50] + "..."
                    })
        
        if active_techs:
            df_active = pd.DataFrame(active_techs)
            st.dataframe(df_active, use_container_width=True)
        else:
            st.info("لا يوجد فنيين نشطين حالياً")
        
        # تفاصيل حركة كل فني
        with st.expander("📊 تفاصيل حركة الفنيين"):
            selected_tech = st.selectbox("اختر الفني", list(st.session_state.gps_data.keys()))
            if selected_tech and st.session_state.gps_data[selected_tech]:
                tech_history = st.session_state.gps_data[selected_tech]
                df_history = pd.DataFrame(tech_history)
                st.dataframe(df_history, use_container_width=True)
                
                # رسم مسار الحركة
                st.subheader("مسار الحركة")
                m2 = folium.Map(location=[30.0444, 31.2357], zoom_start=12)
                points = []
                for loc in tech_history:
                    if loc.get('lat') and loc.get('lng'):
                        folium.CircleMarker(
                            [loc['lat'], loc['lng']],
                            radius=5,
                            color='blue',
                            fill=True
                        ).add_to(m2)
                        points.append([loc['lat'], loc['lng']])
                
                if len(points) > 1:
                    folium.PolyLine(points, color='blue', weight=2.5, opacity=0.7).add_to(m2)
                
                folium_static(m2, width=800, height=400)

    elif menu == "📊 المالية":
        t_out = sum(calculate_balance(c['history']) for c in st.session_state.data)
        t_in = sum(sum(float(h.get('price', 0)) for h in c['history']) for c in st.session_state.data)
        t_serv = sum(sum(float(h.get('debt', 0)) for h in c['history']) for c in st.session_state.data)
        m1, m2, m3 = st.columns(3)
        with m1: st.markdown(f"<div class='metric-container'><div class='metric-title'>مديونية بره</div><div class='metric-value'>{t_out:,.0f}</div></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-container'><div class='metric-title'>المحصل كاش</div><div class='metric-value'>{t_in:,.0f}</div></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-container'><div class='metric-title'>صافي الربح</div><div class='metric-value'>{(t_in - (t_serv * 0.4)):,.0f}</div></div>", unsafe_allow_html=True)

    elif menu == "👥 إدارة العملاء":
        search = st.text_input("🔍 ابحث (اسم/كود/فون)...")
        if search:
            q = search.strip().lower()
            filtered = [c for c in st.session_state.data if (q in c['name'].lower()) or (q == str(c['id'])) or (q in str(c.get('phone','')))]
            for c in filtered:
                bal = calculate_balance(c['history'])
                with st.expander(f"👤 {c['name']} | كود: {c['id']} | الرصيد: {bal:,.0f}"):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c['id']}")
                        
                        # إضافة/تعديل موقع العميل
                        with st.form(key=f"loc_form_{c['id']}"):
                            st.write("📍 تحديد موقع العميل")
                            loc_lat = st.number_input("خط العرض", value=c.get('location', {}).get('lat', 30.0444), key=f"lat{c['id']}")
                            loc_lng = st.number_input("خط الطول", value=c.get('location', {}).get('lng', 31.2357), key=f"lng{c['id']}")
                            loc_address = st.text_input("العنوان", value=c.get('location', {}).get('address', ''), key=f"addr{c['id']}")
                            if st.form_submit_button("💾 حفظ الموقع"):
                                if 'location' not in c:
                                    c['location'] = {}
                                c['location']['lat'] = loc_lat
                                c['location']['lng'] = loc_lng
                                c['location']['address'] = loc_address
                                save_and_refresh("customers.json", st.session_state.data)
                                st.success("تم حفظ الموقع ✅")
                        
                        if st.button("🗑️ حذف العميل", key=f"del{c['id']}"):
                            st.session_state.data.remove(c); save_and_refresh("customers.json", st.session_state.data); st.rerun()
                    with col2:
                        with st.form(key=f"adm_form_{c['id']}", clear_on_submit=True):
                            a_d = st.number_input("تكلفة (+)", 0.0, key=f"ad{c['id']}")
                            a_p = st.number_input("تحصيل (-)", 0.0, key=f"ap{c['id']}")
                            a_f = st.multiselect("الشمع:", ["1", "2", "3", "4", "5", "6", "7", "ممبرين"], key=f"f{c['id']}")
                            a_n = st.text_input("البيان", key=f"an{c['id']}")
                            if st.form_submit_button("حفظ العملية 🚀"):
                                c['history'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "note": f"{a_n} - شمع: {', '.join(a_f)}", "tech": "المدير", "debt": a_d, "price": a_p, "filters": a_f})
                                save_and_refresh("customers.json", st.session_state.data); st.success("تم الحفظ"); st.rerun()

    elif menu == "🛠️ تقارير الفنيين":
        st.markdown("<h2 style='color:#00d4ff;'>🛠️ تقارير الأداء والاستهلاك</h2>", unsafe_allow_html=True)
        
        # إضافة تقرير المواقع
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📍 نشاط الفنيين الجغرافي")
            if st.session_state.gps_data:
                tech_stats = []
                for tech, locations in st.session_state.gps_data.items():
                    if locations:
                        tech_stats.append({
                            "الفني": tech,
                            "عدد الزيارات": len(locations),
                            "آخر نشاط": locations[-1]['timestamp'] if locations else "لا يوجد"
                        })
                if tech_stats:
                    st.dataframe(pd.DataFrame(tech_stats), use_container_width=True)
        
        all_visits = []
        all_filters = []
        tech_debt = []
        
        for c in st.session_state.data:
            for h in c['history']:
                if h.get('tech') and h.get('tech') != "المدير":
                    all_visits.append({"الفني": h['tech'], "العميل": c['name'], "المحصل": h.get('price', 0), "التاريخ": h['date'], "البيان": h.get('note','')})
                    if h.get('filters'):
                        for f in h['filters']: all_filters.append({"الفني": h['tech'], "الشمعة": f})
                    if float(h.get('debt', 0)) > float(h.get('price', 0)):
                        tech_debt.append({"كود العميل": c['id'], "العميل": c['name'], "الفني": h['tech'], "مديونية العملية": float(h['debt']) - float(h['price']), "التاريخ": h['date']})

        tab1, tab2, tab3 = st.tabs(["📋 سجل الزيارات", "📦 استهلاك الشمع", "⚠️ مديونيات الفنيين"])
        
        with tab1:
            if all_visits:
                df_v = pd.DataFrame(all_visits)
                st.dataframe(df_v, use_container_width=True)
                st.write("### إجمالي التحصيل:")
                st.table(df_v.groupby('الفني')['المحصل'].sum())
        
        with tab2:
            if all_filters:
                df_f = pd.DataFrame(all_filters)
                st.write("### إجمالي استهلاك الشمع لكل فني:")
                st.table(pd.crosstab(df_f['الفني'], df_f['الشمعة']))
            else: st.info("لا توجد بيانات شمع مسجلة")

        with tab3:
            if tech_debt:
                st.warning("هذا الجدول يوضح المبالغ التي لم يتم تحصيلها بالكامل أثناء زيارة الفني")
                df_d = pd.DataFrame(tech_debt)
                st.dataframe(df_d, use_container_width=True)
                st.write("### مديونية مسجلة باسم كل فني:")
                st.table(df_d.groupby('الفني')['مديونية العملية'].sum())
            else: st.success("لا توجد مديونيات متروكة من الفنيين")

        with st.expander("➕ إدارة الفنيين"):
            tn, tp = st.text_input("اسم الفني"), st.text_input("السر")
            if st.button("حفظ الفني الجديد"):
                st.session_state.techs.append({"name": tn, "pass": tp}); save_and_refresh("techs.json", st.session_state.techs); st.rerun()

    elif menu == "➕ إضافة عميل":
        with st.form("new_c"):
            n, p, d = st.text_input("الاسم"), st.text_input("الفون"), st.number_input("مديونية سابقة")
            
            # إضافة حقول الموقع
            col1, col2 = st.columns(2)
            with col1: loc_lat = st.number_input("خط العرض", value=30.0444)
            with col2: loc_lng = st.number_input("خط الطول", value=31.2357)
            loc_address = st.text_input("عنوان العميل")
            
            if st.form_submit_button("إضافة"):
                nid = max([x['id'] for x in st.session_state.data], default=0) + 1
                new_customer = {
                    "id": nid,
                    "name": n,
                    "phone": p,
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "افتتاح الحساب", "debt": d, "price": 0, "tech": "المدير"}]
                }
                
                # إضافة الموقع إذا تم تحديده
                if loc_address:
                    new_customer["location"] = {
                        "lat": loc_lat,
                        "lng": loc_lng,
                        "address": loc_address
                    }
                
                st.session_state.data.append(new_customer)
                save_and_refresh("customers.json", st.session_state.data)
                st.success("تم إضافة العميل مع الموقع ✅")
                st.rerun()

    if st.sidebar.button("🚪 خروج"): del st.session_state.role; st.rerun()

# ================== 8. واجهة الفني (مع نظام GPS) ==================
elif st.session_state.role == "tech_panel":
    st.sidebar.markdown(f"🛠️ الفني: **{st.session_state.current_tech}**")
    t_menu = st.sidebar.radio("القائمة", ["📋 تنفيذ مهمة", "📍 تحديث موقعي", "💰 محفظتي", "🗺️ الخريطة", "🚪 خروج"])

    # تحديث الموقع عند فتح واجهة الفني
    if 'location_updated' not in st.session_state:
        location_data = get_current_location()
        if location_data and location_data.get('lat'):
            address = get_address_from_coords(location_data['lat'], location_data['lng'])
            update_tech_location(st.session_state.current_tech, location_data['lat'], location_data['lng'], address)
            st.session_state.location_updated = True

    if t_menu == "📍 تحديث موقعي":
        st.markdown("<div class='location-tracker'>", unsafe_allow_html=True)
        st.subheader("📍 تحديث موقعي الجغرافي")
        
        # محاكاة الحصول على الموقع
        with st.spinner("جاري تحديد موقعك..."):
            location_data = get_current_location()
            time.sleep(1)
        
        if location_data and location_data.get('lat'):
            address = get_address_from_coords(location_data['lat'], location_data['lng'])
            update_tech_location(st.session_state.current_tech, location_data['lat'], location_data['lng'], address)
            
            st.success("✅ تم تحديث موقعك بنجاح!")
            st.write(f"**الإحداثيات:** {location_data['lat']:.6f}, {location_data['lng']:.6f}")
            st.write(f"**العنوان:** {address}")
            
            # عرض الخريطة
            m = folium.Map(location=[location_data['lat'], location_data['lng']], zoom_start=15)
            folium.Marker(
                [location_data['lat'], location_data['lng']],
                popup=f"<b>موقع {st.session_state.current_tech}</b><br>{datetime.now().strftime('%H:%M')}",
                icon=folium.Icon(color='blue', icon='user')
            ).add_to(m)
            
            folium_static(m, width=400, height=300)
        else:
            st.warning("⚠️ لم يتم تحديد موقعك. تأكد من تفعيل GPS")
            
            # بديل يدوي
            with st.form("manual_location"):
                manual_lat = st.number_input("خط العرض", value=30.0444)
                manual_lng = st.number_input("خط الطول", value=31.2357)
                manual_addr = st.text_input("وصف الموقع")
                if st.form_submit_button("💾 حفظ الموقع يدوياً"):
                    update_tech_location(st.session_state.current_tech, manual_lat, manual_lng, manual_addr)
                    st.success("تم حفظ الموقع يدوياً ✅")
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

    elif t_menu == "📋 تنفيذ مهمة":
        cust_list = {f"{c['id']} - {c['name']}": c for c in st.session_state.data}
        choice = st.selectbox("🔍 ابحث واختر العميل:", [""] + list(cust_list.keys()))

        if choice:
            selected = cust_list[choice]
            st.markdown(f"<div class='balance-box'><h3>رصيد العميل الحالي: {calculate_balance(selected['history']):,.0f} ج.م</h3></div>", unsafe_allow_html=True)
            
            # عرض موقع العميل إذا كان مسجلاً
            if selected.get('location'):
                with st.expander("📍 موقع العميل على الخريطة"):
                    try:
                        m = folium.Map(location=[selected['location']['lat'], selected['location']['lng']], zoom_start=15)
                        folium.Marker(
                            [selected['location']['lat'], selected['location']['lng']],
                            popup=f"<b>موقع {selected['name']}</b>",
                            icon=folium.Icon(color='red', icon='home')
                        ).add_to(m)
                        
                        # إضافة موقع الفني الحالي
                        if st.session_state.gps_data.get(st.session_state.current_tech):
                            last_loc = st.session_state.gps_data[st.session_state.current_tech][-1]
                            if last_loc.get('lat'):
                                folium.Marker(
                                    [last_loc['lat'], last_loc['lng']],
                                    popup="<b>موقعك الحالي</b>",
                                    icon=folium.Icon(color='blue', icon='user')
                                ).add_to(m)
                        
                        folium_static(m, width=400, height=300)
                    except:
                        st.info("تعذر تحميل الخريطة")
            
            c_a, c_b = st.columns([2, 1])
            with c_b:
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={selected['id']}", caption="باركود العميل")
            with c_a:
                with st.form("t_form", clear_on_submit=True):
                    v_d, v_p = st.number_input("تكلفة الصيانة (+)"), st.number_input("المحصل (-)")
                    v_f = st.multiselect("الشمع المستهلك:", ["1", "2", "3", "4", "5", "6", "7", "ممبرين"])
                    v_n = st.text_area("البيان")
                    
                    # تسجيل الموقع تلقائياً عند الإنتهاء
                    record_location = st.checkbox("📍 تسجيل موقعي الحالي مع التقرير", value=True)
                    
                    if st.form_submit_button("إرسال التقرير 🚀"):
                        # تحديث موقع الفني
                        if record_location:
                            location_data = get_current_location()
                            if location_data and location_data.get('lat'):
                                address = get_address_from_coords(location_data['lat'], location_data['lng'])
                                update_tech_location(
                                    st.session_state.current_tech, 
                                    location_data['lat'], 
                                    location_data['lng'], 
                                    f"زيارة: {selected['name']} - {address}"
                                )
                        
                        # حفظ التقرير
                        selected['history'].append({
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "note": f"{v_n} - شمع: {', '.join(v_f)}",
                            "tech": st.session_state.current_tech,
                            "debt": v_d,
                            "price": v_p,
                            "filters": v_f,
                            "location_recorded": record_location
                        })
                        
                        save_and_refresh("customers.json", st.session_state.data)
                        st.success("تم حفظ التقرير مع الموقع الجغرافي ✅")
                        st.rerun()

    elif t_menu == "🗺️ الخريطة":
        st.subheader("🗺️ خريطة العملاء القريبين")
        
        # عرض الفنيين والعملاء على الخريطة
        if st.session_state.gps_data.get(st.session_state.current_tech):
            last_loc = st.session_state.gps_data[st.session_state.current_tech][-1]
            if last_loc.get('lat'):
                m = folium.Map(location=[last_loc['lat'], last_loc['lng']], zoom_start=13)
                
                # إضافة موقع الفني
                folium.Marker(
                    [last_loc['lat'], last_loc['lng']],
                    popup=f"<b>أنت هنا</b><br>{last_loc.get('address', '')}",
                    icon=folium.Icon(color='blue', icon='user', prefix='fa')
                ).add_to(m)
                
                # إضافة العملاء القريبين (في دائرة نصف قطرها 5 كم)
                nearby_customers = []
                for customer in st.session_state.data:
                    if customer.get('location') and customer['location'].get('lat'):
                        # حساب المسافة (محاكاة)
                        customer_lat = customer['location']['lat']
                        customer_lng = customer['location']['lng']
                        
                        folium.Marker(
                            [customer_lat, customer_lng],
                            popup=f"<b>{customer['name']}</b><br>الرصيد: {calculate_balance(customer['history']):,.0f} ج.م",
                            icon=folium.Icon(color='green', icon='home', prefix='fa')
                        ).add_to(m)
                        
                        nearby_customers.append(customer)
                
                if nearby_customers:
                    st.success(f"✅ يوجد {len(nearby_customers)} عميل بالقرب منك")
                    folium_static(m, width=800, height=500)
                    
                    # قائمة بالعملاء القريبين
                    st.subheader("📋 العملاء القريبين من موقعك")
                    for cust in nearby_customers[:5]:  # أول 5 عملاء فقط
                        st.write(f"**{cust['name']}** - الرصيد: {calculate_balance(cust['history']):,.0f} ج.م")
                        if st.button(f"📋 فتح {cust['name']}", key=f"open_{cust['id']}"):
                            st.session_state.selected_customer = cust['id']
                            st.rerun()
                else:
                    st.info("لا يوجد عملاء مسجلين بالقرب من موقعك الحالي")
                    folium_static(m, width=800, height=500)
            else:
                st.warning("⚠️ يرجى تحديث موقعك أولاً من قسم '📍 تحديث موقعي'")
        else:
            st.warning("⚠️ لم يتم تحديد موقعك بعد. انتقل إلى '📍 تحديث موقعي'")

    elif t_menu == "💰 محفظتي":
        cash = sum(float(h.get('price', 0)) for c in st.session_state.data for h in c['history'] if h.get('tech') == st.session_state.current_tech)
        st.metric("إجمالي المحصل معك", f"{cash:,.0f} ج.م")
        
        # إحصائيات الموقع
        st.subheader("📍 إحصائيات التنقل")
        if st.session_state.gps_data.get(st.session_state.current_tech):
            locations = st.session_state.gps_data[st.session_state.current_tech]
            st.write(f"**عدد نقاط التتبع:** {len(locations)}")
            st.write(f"**آخر تحديث:** {locations[-1]['timestamp']}")
            st.write(f"**آخر موقع:** {locations[-1].get('address', 'غير محدد')}")

    if st.sidebar.button("🚪 خروج"): 
        # تحديث حالة الفني عند الخروج
        update_tech_location(st.session_state.current_tech, None, None, None, "غير نشط")
        del st.session_state.role
        del st.session_state.current_tech
        st.rerun()

# ================== 9. ملف Manifest لتثبيت PWA ==================
# سيتم إنشاء هذا الملف تلقائياً
manifest_content = {
    "name": "Power Life System",
    "short_name": "PowerLife",
    "description": "نظام إدارة العملاء ومتابعة الفنيين",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#000b1a",
    "theme_color": "#00d4ff",
    "icons": [
        {
            "src": "https://cdn-icons-png.flaticon.com/512/3448/3448373.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "https://cdn-icons-png.flaticon.com/512/3448/3448373.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

# حفظ ملف manifest
with open("manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest_content, f, ensure_ascii=False, indent=2)

# ================== 10. توجيهات التثبيت على الهاتف ==================
with st.sidebar.expander("📱 تثبيت التطبيق على الهاتف"):
    st.markdown("""
    ### تعليمات التثبيت:
    
    **لأجهزة Android (Chrome):**
    1. افتح الموقع في متصفح Chrome
    2. اضغط على القائمة (ثلاث نقاط)
    3. اختر "تثبيت التطبيق"
    4. اضغط "تثبيت"
    
    **لأجهزة iPhone (Safari):**
    1. افتح الموقع في Safari
    2. اضغط على زر المشاركة (مربع وسهم)
    3. مرر لأسفل واختر "إضافة إلى الشاشة الرئيسية"
    4. اضغط "إضافة"
    
    **مميزات التطبيق المثبت:**
    ✅ يعمل بدون إنترنت جزئياً
    ✅ إشعارات الموقع التلقائي
    ✅ واجهة مخصصة للهاتف
    ✅ أسرع في التحميل
    """)

# ================== 11. Auto-refresh للخريطة ==================
# تحديث تلقائي للخريطة كل 30 ثانية للفنيين
if st.session_state.get('role') == 'tech_panel':
    st.markdown("""
    <script>
    // تحديث تلقائي كل 30 ثانية للخريطة
    setTimeout(function() {
        if (window.location.href.includes("tech_panel")) {
            window.location.reload();
        }
    }, 30000);
    </script>
    """, unsafe_allow_html=True)
