import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import base64
from io import BytesIO
import qrcode
import hashlib
import plotly.graph_objects as go
import plotly.express as px
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import folium_static
import time

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================

st.set_page_config(
    page_title="Power Life CRM Pro",
    page_icon="💧", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://powerlife.com/support',
        'Report a bug': 'https://powerlife.com/bug',
        'About': '# Power Life CRM System v3.0'
    }
)

# CSS مخصص مع دعم التمرير الكامل
st.markdown("""
<style>
    /* إعادة ضبط CSS */
    * {
        font-family: 'Cairo', 'Arial', sans-serif !important;
        text-align: right !important;
        direction: rtl !important;
        box-sizing: border-box !important;
    }
    
    /* إصلاح التمرير الرئيسي */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
        overflow: visible !important;
    }
    
    /* إصلاح التمرير في المحتوى */
    .stApp {
        overflow: auto !important;
        height: 100vh !important;
    }
    
    /* تحسين الشريط الجانبي */
    [data-testid="stSidebar"] {
        overflow-y: auto !important;
        height: 100vh !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 2rem !important;
    }
    
    /* تحسين التبويبات */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
        white-space: nowrap !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px !important;
        padding: 0 24px !important;
        white-space: nowrap !important;
    }
    
    /* تحسين الجداول */
    .dataframe {
        width: 100% !important;
        overflow-x: auto !important;
        display: block !important;
    }
    
    /* تحسين البطاقات */
    .custom-card {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        border-right: 5px solid #28a745;
        transition: transform 0.3s ease;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .custom-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.12);
    }
    
    /* إحصائيات بطاقة */
    .stat-card {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.25);
    }
    
    /* بطاقة الباركود */
    .qr-card-custom {
        border: 3px dashed #28a745;
        padding: 25px;
        text-align: center;
        background: linear-gradient(135deg, #f8fff8, #e8f5e9);
        border-radius: 20px;
        margin: 20px auto;
        max-width: 400px;
        box-shadow: 0 8px 25px rgba(40, 167, 69, 0.15);
    }
    
    /* شارة الفني */
    .tech-badge {
        background: linear-gradient(135deg, #ffc107, #ff9800);
        color: #000;
        padding: 8px 15px;
        border-radius: 25px;
        display: inline-block;
        margin: 5px;
        font-weight: bold;
        box-shadow: 0 3px 10px rgba(255, 193, 7, 0.3);
    }
    
    /* شارة الحالة */
    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin: 2px;
    }
    
    .status-active { background: #d4edda; color: #155724; }
    .status-pending { background: #fff3cd; color: #856404; }
    .status-completed { background: #d1ecf1; color: #0c5460; }
    
    /* تذييل الصفحة */
    .footer {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-top: 40px;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.1);
    }
    
    /* زر مخصص */
    .custom-btn {
        background: linear-gradient(135deg, #28a745, #20c997) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 25px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin: 5px 0 !important;
    }
    
    .custom-btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 15px rgba(40, 167, 69, 0.4) !important;
    }
    
    /* إصلاح الهواتف */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1rem !important;
        }
        
        .custom-card, .stat-card {
            padding: 15px !important;
            margin: 10px 0 !important;
        }
        
        .stButton > button {
            padding: 10px !important;
            font-size: 14px !important;
        }
        
        h1 { font-size: 24px !important; }
        h2 { font-size: 20px !important; }
        h3 { font-size: 18px !important; }
        
        [data-testid="stVerticalBlock"] {
            gap: 1rem !important;
        }
    }
    
    /* تحسينات الإدخال */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 10px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 12px !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 3px rgba(40, 167, 69, 0.1) !important;
    }
    
    /* إصلاح القوائم */
    .stRadio > div {
        flex-direction: column !important;
        gap: 10px !important;
    }
    
    .stRadio > div > label {
        border: 2px solid #e0e0e0 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin: 5px 0 !important;
        background: white !important;
        transition: all 0.3s ease !important;
    }
    
    .stRadio > div > label:hover {
        border-color: #28a745 !important;
        background: #f8fff8 !important;
    }
    
    /* إصلاح الأعمدة */
    .stColumn {
        padding: 10px !important;
    }
    
    /* إصلاح التوسيع */
    .streamlit-expanderHeader {
        background: #f8f9fa !important;
        border-radius: 10px !important;
        border: 2px solid #e9ecef !important;
        font-weight: bold !important;
    }
    
    /* خلفية الصفحة */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# إضافة خط Cairo
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ================== 2. إدارة ملفات البيانات ==================

USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"
TECHNICIANS_FILE = "technicians.json"
LOCATIONS_FILE = "locations.json"

def load_data(file, default=[]):
    """تحميل البيانات من ملف JSON"""
    try:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"خطأ في تحميل {file}: {str(e)}")
    return default.copy()

def save_data(file, data):
    """حفظ البيانات إلى ملف JSON"""
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"خطأ في حفظ {file}: {str(e)}")
        return False

# تحميل جميع البيانات
users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)
technicians = load_data(TECHNICIANS_FILE, [
    {
        "id": 1,
        "name": "فني رئيسي",
        "phone": "01000000001",
        "specialty": "جميع الأعمال",
        "status": "نشط",
        "location": {"lat": 30.0444, "lng": 31.2357},
        "rating": 5.0,
        "completed_jobs": 0,
        "current_location": "المقر الرئيسي"
    }
])
locations = load_data(LOCATIONS_FILE)

# تهيئة حساب المدير
if not any(u.get('username') == 'admin' for u in users):
    users.append({
        "id": 1,
        "username": "admin",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "full_name": "مدير النظام",
        "role": "admin",
        "phone": "01000000000",
        "email": "admin@powerlife.com",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    save_data(USERS_FILE, users)

# ================== 3. وظائف مساعدة ==================

def hash_password(password):
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """التحقق من كلمة المرور"""
    return hash_password(password) == hashed

def generate_qr_code(data, size=250):
    """إنشاء رمز QR عالي الجودة"""
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#28a745", back_color="white")
        img = img.resize((size, size))
        
        buffered = BytesIO()
        img.save(buffered, format="PNG", optimize=True)
        img_bytes = buffered.getvalue()
        
        encoded = base64.b64encode(img_bytes).decode()
        return encoded, img_bytes
    except Exception as e:
        st.error(f"خطأ في إنشاء الباركود: {str(e)}")
        return None, None

def create_qr_download_button(img_bytes, filename, text="📥 تحميل الباركود"):
    """إنشاء زر تحميل للباركود"""
    b64 = base64.b64encode(img_bytes).decode()
    
    button_html = f'''
    <div style="text-align: center; margin: 20px 0;">
        <a href="data:image/png;base64,{b64}" download="{filename}" 
           style="
                background: linear-gradient(135deg, #28a745, #20c997);
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 25px;
                display: inline-block;
                font-weight: bold;
                font-size: 16px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
                border: none;
                cursor: pointer;
                min-width: 200px;
           "
           onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(40, 167, 69, 0.4)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(40, 167, 69, 0.3)';">
           {text}
        </a>
    </div>
    '''
    return button_html

def get_current_url():
    """الحصول على رابط التطبيق الحالي"""
    try:
        # على Streamlit Cloud
        import streamlit as st
        from streamlit import runtime
        
        if runtime.exists():
            import os
            if 'STREAMLIT_SERVER_BASE_URL_PATH' in os.environ:
                base_url = os.environ['STREAMLIT_SERVER_BASE_URL_PATH']
                return f"https://{base_url}"
    except:
        pass
    
    # رابط محلي للاختبار
    return "http://localhost:8501"

def calculate_customer_summary(customer):
    """حساب ملخص شامل للعميل"""
    history = customer.get('history', [])
    
    if not history:
        return {
            "total_paid": 0,
            "total_visits": 0,
            "last_visit": None,
            "last_technician": None,
            "last_amount": 0,
            "monthly_payments": {},
            "technicians_list": [],
            "device_balance": 0,
            "installments": [],
            "status": "جديد"
        }
    
    # الحسابات الأساسية
    total_paid = sum(h.get('amount', h.get('التكلفة', 0)) for h in history)
    total_visits = len(history)
    
    # آخر زيارة
    last_visit = max(history, key=lambda x: x.get('date', x.get('التاريخ', '')))
    
    # المدفوعات الشهرية
    monthly_payments = {}
    for h in history:
        date_str = h.get('date', h.get('التاريخ', ''))
        if date_str:
            try:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                month_key = date.strftime("%Y-%m")
                amount = h.get('amount', h.get('التكلفة', 0))
                monthly_payments[month_key] = monthly_payments.get(month_key, 0) + amount
            except:
                continue
    
    # قائمة الفنيين
    technicians_list = list(set(h.get('technician', h.get('الفني', '')) for h in history))
    
    # حساب رصيد الجهاز (مثال: إذا كان هناك أقساط)
    device_price = customer.get('device_price', 10000)
    device_balance = device_price - total_paid
    
    # الأقساط
    installments = []
    for i, h in enumerate(history[-5:], 1):  # آخر 5 دفعات
        installments.append({
            "number": i,
            "date": h.get('date', h.get('التاريخ', '')),
            "amount": h.get('amount', h.get('التكلفة', 0)),
            "technician": h.get('technician', h.get('الفني', ''))
        })
    
    return {
        "total_paid": total_paid,
        "total_visits": total_visits,
        "last_visit": last_visit.get('date', last_visit.get('التاريخ', '')),
        "last_technician": last_visit.get('technician', last_visit.get('الفني', '')),
        "last_amount": last_visit.get('amount', last_visit.get('التكلفة', 0)),
        "monthly_payments": monthly_payments,
        "technicians_list": technicians_list,
        "device_balance": max(0, device_balance),
        "installments": installments,
        "status": "نشط" if device_balance <= 0 else "مدين"
    }

def get_technician_location(tech_id):
    """الحصول على موقع الفني"""
    tech = next((t for t in technicians if t.get('id') == tech_id), None)
    if tech and 'location' in tech:
        return tech['location']
    return {"lat": 30.0444, "lng": 31.2357}  # موقع افتراضي

def create_customer_map(customer, technicians_list):
    """إنشاء خريطة للعميل والفنيين"""
    try:
        # إنشاء خريطة مركزة على موقع العميل
        customer_location = customer.get('location', {"lat": 30.0444, "lng": 31.2357})
        m = folium.Map(
            location=[customer_location['lat'], customer_location['lng']],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # إضافة علامة للعميل
        folium.Marker(
            [customer_location['lat'], customer_location['lng']],
            popup=f"<b>العميل:</b> {customer.get('name')}<br><b>الهاتف:</b> {customer.get('phone')}",
            icon=folium.Icon(color='red', icon='user', prefix='fa')
        ).add_to(m)
        
        # إضافة علامات للفنيين
        for tech_name in technicians_list:
            tech = next((t for t in technicians if t.get('name') == tech_name), None)
            if tech and 'location' in tech:
                folium.Marker(
                    [tech['location']['lat'], tech['location']['lng']],
                    popup=f"<b>الفني:</b> {tech.get('name')}<br><b>التخصص:</b> {tech.get('specialty')}",
                    icon=folium.Icon(color='green', icon='wrench', prefix='fa')
                ).add_to(m)
                
                # إضافة خط بين العميل والفني
                folium.PolyLine(
                    [[customer_location['lat'], customer_location['lng']],
                     [tech['location']['lat'], tech['location']['lng']]],
                    color='blue',
                    weight=2,
                    opacity=0.5
                ).add_to(m)
        
        return m
    except Exception as e:
        st.error(f"خطأ في إنشاء الخريطة: {str(e)}")
        return None

# ================== 4. صفحة العميل العامة (من خلال الباركود) ==================

# التحقق من وجود معامل id في الرابط
query_params = st.query_params
if "id" in query_params:
    try:
        cust_id = int(query_params["id"])
        target_customer = next((c for c in customers if c.get('id') == cust_id), None)
        
        if target_customer:
            # ========== رأس الصفحة ==========
            col_logo, col_title = st.columns([1, 4])
            with col_logo:
                st.markdown("<h1 style='color: #28a745; text-align: center;'>💧</h1>", unsafe_allow_html=True)
            with col_title:
                st.markdown(f"""
                <div style="text-align: center; padding: 10px;">
                    <h1 style='color: #28a745; margin-bottom: 5px;'>Power Life</h1>
                    <h3 style='color: #666; margin-top: 0;'>نظام متابعة العملاء</h3>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ========== معلومات العميل الأساسية ==========
            st.markdown(f"<h2 style='text-align: center; color: #333;'>👤 {target_customer.get('name', '')}</h2>", unsafe_allow_html=True)
            
            # بطاقة المعلومات الرئيسية
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                st.markdown(f"""
                <div class="custom-card">
                    <h4 style='color: #28a745;'>📱 معلومات الاتصال</h4>
                    <p><strong>رقم الهاتف:</strong> {target_customer.get('phone', '')}</p>
                    <p><strong>العنوان:</strong> {target_customer.get('gov', '')} - {target_customer.get('village', '')}</p>
                    <p><strong>نوع الجهاز:</strong> {target_customer.get('type', '')}</p>
                    <p><strong>سعة الجهاز:</strong> {target_customer.get('capacity', 'غير محدد')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_info2:
                st.markdown(f"""
                <div class="custom-card">
                    <h4 style='color: #28a745;'>📅 معلومات العضوية</h4>
                    <p><strong>رقم العضوية:</strong> PL-{target_customer.get('id', 0):04d}</p>
                    <p><strong>تاريخ التسجيل:</strong> {target_customer.get('created_at', '')}</p>
                    <p><strong>آخر تحديث:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
                    <p><strong>حالة العضوية:</strong> <span class='status-active'>نشط</span></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_info3:
                # صورة العميل أو أيقونة
                st.markdown(f"""
                <div class="custom-card" style="text-align: center;">
                    <h4 style='color: #28a745;'>🆔 بطاقة العميل</h4>
                    <div style="
                        background: linear-gradient(135deg, #28a745, #20c997);
                        color: white;
                        padding: 20px;
                        border-radius: 15px;
                        margin: 10px 0;
                    ">
                        <h3 style='margin: 0;'>Power Life</h3>
                        <h2 style='margin: 10px 0;'>PL-{target_customer.get('id', 0):04d}</h2>
                        <p style='margin: 0; font-size: 14px;'>{target_customer.get('name', '')}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ========== الإحصائيات المالية ==========
            st.subheader("💰 الإحصائيات المالية")
            
            summary = calculate_customer_summary(target_customer)
            
            # إحصائيات سريعة
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            with col_stat1:
                st.markdown(f"""
                <div class="stat-card">
                    <h4>إجمالي المدفوعات</h4>
                    <h2>{summary['total_paid']:,} ج.م</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat2:
                st.markdown(f"""
                <div class="stat-card">
                    <h4>رصيد الجهاز</h4>
                    <h2>{summary['device_balance']:,} ج.م</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat3:
                st.markdown(f"""
                <div class="stat-card">
                    <h4>عدد الزيارات</h4>
                    <h2>{summary['total_visits']}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col_stat4:
                status_color = "#28a745" if summary['status'] == "نشط" else "#dc3545"
                st.markdown(f"""
                <div class="stat-card">
                    <h4>الحالة المالية</h4>
                    <h2 style='color: {status_color};'>{summary['status']}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # ========== آخر الأقساط ==========
            if summary['installments']:
                st.subheader("📋 آخر الدفعات")
                
                installments_df = pd.DataFrame(summary['installments'])
                st.dataframe(
                    installments_df,
                    column_config={
                        "number": "رقم الدفعة",
                        "date": "التاريخ",
                        "amount": "المبلغ",
                        "technician": "الفني"
                    },
                    use_container_width=True,
                    hide_index=True
                )
            
            # ========== المدفوعات الشهرية ==========
            if summary['monthly_payments']:
                st.subheader("📊 المدفوعات الشهرية")
                
                monthly_df = pd.DataFrame([
                    {"الشهر": month, "المبلغ": amount}
                    for month, amount in sorted(summary['monthly_payments'].items(), reverse=True)
                ])
                
                # رسم بياني
                fig = px.bar(
                    monthly_df,
                    x='الشهر',
                    y='المبلغ',
                    title='المدفوعات الشهرية',
                    color_discrete_sequence=['#28a745']
                )
                fig.update_layout(
                    plot_bgcolor='white',
                    xaxis_title='الشهر',
                    yaxis_title='المبلغ (ج.م)',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # ========== الفنيون الذين خدموا العميل ==========
            if summary['technicians_list']:
                st.subheader("👷 الفنيون الذين قاموا بالخدمة")
                
                tech_cols = st.columns(4)
                for i, tech_name in enumerate(summary['technicians_list']):
                    with tech_cols[i % 4]:
                        tech_info = next((t for t in technicians if t.get('name') == tech_name), {})
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #fff3cd, #ffeaa7);
                            padding: 15px;
                            border-radius: 12px;
                            text-align: center;
                            margin: 5px;
                            border-right: 4px solid #ffc107;
                        ">
                            <h4 style='margin: 0 0 10px 0; color: #856404;'>{tech_name}</h4>
                            <p style='margin: 5px 0; font-size: 12px;'>
                                📞 {tech_info.get('phone', 'غير متوفر')}
                            </p>
                            <p style='margin: 5px 0; font-size: 12px;'>
                                ⭐ {tech_info.get('rating', '5.0')}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # ========== سجل الصيانة الكامل ==========
            st.subheader("🛠️ سجل الصيانة الكامل")
            
            history = target_customer.get('history', [])
            if history:
                # فرز من الأحدث
                sorted_history = sorted(
                    history,
                    key=lambda x: x.get('date', x.get('التاريخ', '')),
                    reverse=True
                )
                
                for i, visit in enumerate(sorted_history, 1):
                    with st.expander(
                        f"📅 زيارة {i} - {visit.get('date', visit.get('التاريخ', ''))} - {visit.get('amount', visit.get('التكلفة', 0)):,} ج.م",
                        expanded=(i == 1)
                    ):
                        cols = st.columns([1, 2, 1, 1])
                        
                        with cols[0]:
                            st.markdown(f"**📅 التاريخ:**\n{visit.get('date', visit.get('التاريخ', ''))}")
                        
                        with cols[1]:
                            st.markdown(f"**🔧 الأعمال:**\n{visit.get('work', visit.get('العمل', 'لا توجد تفاصيل'))}")
                        
                        with cols[2]:
                            st.markdown(f"**💰 المبلغ:**\n{visit.get('amount', visit.get('التكلفة', 0)):,} ج.م")
                        
                        with cols[3]:
                            st.markdown(f"**👷 الفني:**\n{visit.get('technician', visit.get('الفني', 'غير معروف'))}")
                        
                        if visit.get('notes'):
                            st.info(f"**📝 ملاحظات:** {visit.get('notes')}")
                        
                        if visit.get('payment_method'):
                            st.success(f"**💳 طريقة الدفع:** {visit.get('payment_method')}")
            else:
                st.info("📭 لا توجد سجلات صيانة حتى الآن")
            
            # ========== خريطة تتبع ==========
            st.subheader("📍 خريطة التتبع")
            
            try:
                # إنشاء خريطة مبسطة (بدون folium)
                map_data = pd.DataFrame({
                    'lat': [30.0444, 30.0131, 30.1276],
                    'lon': [31.2357, 31.2089, 31.3135],
                    'name': ['العميل', 'الفني 1', 'الفني 2']
                })
                
                st.map(map_data, zoom=10)
                
                col_map1, col_map2 = st.columns(2)
                with col_map1:
                    st.info("**📍 موقع العميل:** " + target_customer.get('gov', '') + " - " + target_customer.get('village', ''))
                with col_map2:
                    st.info("**👷 أقرب فني:** " + (summary['technicians_list'][0] if summary['technicians_list'] else "لا يوجد"))
            
            except:
                st.info("📍 ميزة الخرائط تحت التطوير")
            
            # ========== معلومات التواصل ==========
            st.markdown("---")
            st.markdown("""
            <div class="footer">
                <h3 style='margin-bottom: 15px;'>💧 Power Life - خدمة العملاء</h3>
                <div style="display: flex; justify-content: center; gap: 30px; flex-wrap: wrap;">
                    <div>
                        <h4 style='margin: 0 0 10px 0;'>📞 الاتصال</h4>
                        <p style='margin: 5px 0;'><strong>خدمة العملاء:</strong> 01234567890</p>
                        <p style='margin: 5px 0;'><strong>الطوارئ:</strong> 01112223333</p>
                    </div>
                    <div>
                        <h4 style='margin: 0 0 10px 0;'>✉️ البريد</h4>
                        <p style='margin: 5px 0;'>support@powerlife.com</p>
                        <p style='margin: 5px 0;'>info@powerlife.com</p>
                    </div>
                    <div>
                        <h4 style='margin: 0 0 10px 0;'>⏰ ساعات العمل</h4>
                        <p style='margin: 5px 0;'>من 9 صباحاً إلى 10 مساءً</p>
                        <p style='margin: 5px 0;'>طوال أيام الأسبوع</p>
                    </div>
                </div>
                <p style='margin-top: 20px; opacity: 0.8; font-size: 14px;'>
                    © 2024 Power Life. جميع الحقوق محفوظة.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # صفحة خطأ
            st.error("## ❌ كود العميل غير صحيح")
            st.info("""
            **السبب المحتمل:**
            1. كود الباركود غير صحيح
            2. العميل غير مسجل في النظام
            3. خطأ في مسح الباركود
            
            **الحلول:**
            - تأكد من مسح الباركود بشكل صحيح
            - تواصل مع خدمة العملاء: 01234567890
            - أعد تحميل الصفحة وحاول مرة أخرى
            """)
            
            # زر العودة
            if st.button("🔄 إعادة تحميل الصفحة", use_container_width=True):
                st.rerun()
    
    except ValueError:
        st.error("## ⚠️ خطأ في كود العميل")
        st.info("يجب أن يكون كود العميل رقماً صحيحاً")
    
    except Exception as e:
        st.error(f"## 🚨 خطأ غير متوقع: {str(e)}")
    
    st.stop()

# ================== 5. نظام تسجيل الدخول ==================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.page = "dashboard"

if not st.session_state.logged_in:
    # صفحة تسجيل الدخول
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # شعار وتصميم صفحة الدخول
        st.markdown("""
        <div style="
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #28a745, #20c997);
            border-radius: 25px;
            color: white;
            margin-bottom: 40px;
            box-shadow: 0 15px 35px rgba(40, 167, 69, 0.3);
        ">
            <h1 style='font-size: 48px; margin-bottom: 10px;'>💧</h1>
            <h1 style='margin: 0; font-size: 36px;'>Power Life CRM</h1>
            <p style='margin-top: 10px; opacity: 0.9; font-size: 18px;'>
                نظام إدارة وتتبع العملاء المتكامل
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # نموذج الدخول
        with st.container():
            st.markdown("<h3 style='text-align: center;'>تسجيل الدخول إلى النظام</h3>", unsafe_allow_html=True)
            
            username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم...")
            password = st.text_input("🔒 كلمة المرور", type="password", placeholder="أدخل كلمة المرور...")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_clicked = st.button("🚀 تسجيل الدخول", use_container_width=True, type="primary")
            
            with col_btn2:
                if st.button("🔄 تحديث الصفحة", use_container_width=True):
                    st.rerun()
            
            if login_clicked:
                if not username or not password:
                    st.error("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
                else:
                    user_found = False
                    for user in users:
                        if user.get('username') == username and verify_password(password, user.get('password', '')):
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.session_state.page = "dashboard"
                            st.success(f"✅ تم الدخول بنجاح! مرحباً {user.get('full_name', username)}")
                            time.sleep(1)
                            st.rerun()
                            user_found = True
                            break
                    
                    if not user_found:
                        st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")
        
        # معلومات الدخول
        with st.expander("🔑 معلومات الدخول الافتراضية", expanded=False):
            st.code("""
            للمدير:
            اسم المستخدم: admin
            كلمة المرور: admin123
            
            يمكن للمدير إضافة مستخدمين جدد
            """)
            st.info("⚠️ يرجى تغيير كلمة المرور بعد أول دخول")
    
    st.stop()

# ================== 6. القائمة الرئيسية ==================

user = st.session_state.user

# الشريط الجانبي
with st.sidebar:
    # معلومات المستخدم
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #28a745, #20c997);
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(40, 167, 69, 0.25);
    ">
        <div style="
            background: rgba(255,255,255,0.2);
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin: 0 auto 15px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
        ">
            👤
        </div>
        <h3 style='margin: 0 0 5px 0;'>{user.get('full_name', user.get('username'))}</h3>
        <p style='margin: 0; opacity: 0.9; font-size: 14px;'>{user.get('role', 'مستخدم')}</p>
        <div style="
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
            font-size: 12px;
        ">
            💧 Power Life
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # القائمة
    st.markdown("### 📂 القائمة الرئيسية")
    
    menu_options = [
        {"icon": "📊", "label": "لوحة التحكم", "page": "dashboard"},
        {"icon": "👥", "label": "العملاء", "page": "customers"},
        {"icon": "➕", "label": "إضافة عميل", "page": "add_customer"},
        {"icon": "🛠️", "label": "الصيانة", "page": "maintenance"},
        {"icon": "👷", "label": "الفنيون", "page": "technicians"},
        {"icon": "📍", "label": "التتبع على الخريطة", "page": "tracking"},
        {"icon": "📈", "label": "التقارير", "page": "reports"},
        {"icon": "💰", "label": "المالية", "page": "finance"}
    ]
    
    if user.get('role') == 'admin':
        menu_options.extend([
            {"icon": "⚙️", "label": "الإعدادات", "page": "settings"},
            {"icon": "👤", "label": "المستخدمين", "page": "users"}
        ])
    
    menu_options.append({"icon": "🚪", "label": "تسجيل الخروج", "page": "logout"})
    
    # عرض القائمة
    for option in menu_options:
        if st.button(
            f"{option['icon']} {option['label']}",
            key=f"menu_{option['page']}",
            use_container_width=True,
            type="primary" if st.session_state.page == option['page'] else "secondary"
        ):
            st.session_state.page = option['page']
            st.rerun()

# ================== 7. معالجة الصفحات ==================

# --- لوحة التحكم ---
if st.session_state.page == "dashboard":
    st.title("📊 لوحة تحكم Power Life")
    
    # إحصائيات سريعة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(customers)
        st.markdown(f"""
        <div class="stat-card">
            <h4>👥 العملاء</h4>
            <h2>{total_customers}</h2>
            <p style='font-size: 12px; opacity: 0.9;'>إجمالي العملاء</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_technicians = len(technicians)
        st.markdown(f"""
        <div class="stat-card">
            <h4>👷 الفنيون</h4>
            <h2>{total_technicians}</h2>
            <p style='font-size: 12px; opacity: 0.9;'>فني نشط</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_income = sum(
            h.get('amount', h.get('التكلفة', 0))
            for c in customers
            for h in c.get('history', [])
        )
        st.markdown(f"""
        <div class="stat-card">
            <h4>💰 الإيرادات</h4>
            <h2>{total_income:,} ج.م</h2>
            <p style='font-size: 12px; opacity: 0.9;'>إجمالي الدخل</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        active_maintenance = sum(
            1 for c in customers
            if c.get('history') and len(c.get('history', [])) > 0
        )
        st.markdown(f"""
        <div class="stat-card">
            <h4>🛠️ الصيانة</h4>
            <h2>{active_maintenance}</h2>
            <p style='font-size: 12px; opacity: 0.9;'>عملاء لديهم صيانة</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # العملاء الجدد
    st.subheader("🆕 العملاء المضافون حديثاً")
    
    if customers:
        recent_customers = sorted(customers, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
        
        for customer in recent_customers:
            col_info, col_action = st.columns([3, 1])
            
            with col_info:
                summary = calculate_customer_summary(customer)
                st.markdown(f"""
                <div style="
                    background: white;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 5px 0;
                    border-right: 4px solid #28a745;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{customer.get('name')}</strong>
                            <p style='margin: 5px 0; color: #666; font-size: 14px;'>
                                📱 {customer.get('phone')} | 📍 {customer.get('gov')}
                            </p>
                        </div>
                        <div style="text-align: left;">
                            <span class="status-{'active' if summary['status'] == 'نشط' else 'pending'}">
                                {summary['status']}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_action:
                if st.button("عرض", key=f"view_{customer.get('id')}", use_container_width=True):
                    st.session_state.page = "customer_detail"
                    st.session_state.selected_customer = customer.get('id')
                    st.rerun()
    
    # الصيانة القادمة
    st.subheader("📅 الصيانة القادمة")
    
    upcoming_maintenance = []
    for customer in customers:
        history = customer.get('history', [])
        if history:
            last_visit = max(history, key=lambda x: x.get('date', x.get('التاريخ', '')))
            last_date = last_visit.get('date', last_visit.get('التاريخ', ''))
            try:
                last_date_obj = datetime.strptime(last_date, "%Y-%m-%d")
                days_since = (datetime.now() - last_date_obj).days
                if days_since >= 30:  # صيانة كل شهر
                    upcoming_maintenance.append({
                        "customer": customer.get('name'),
                        "last_visit": last_date,
                        "days_since": days_since
                    })
            except:
                pass
    
    if upcoming_maintenance[:3]:
        for maintenance in upcoming_maintenance[:3]:
            st.info(f"**{maintenance['customer']}** - آخر صيانة: {maintenance['last_visit']} (قبل {maintenance['days_since']} يوم)")
    else:
        st.success("✅ لا توجد صيانة متأخرة")

# --- إدارة العملاء ---
elif st.session_state.page == "customers":
    st.title("👥 إدارة العملاء")
    
    # شريط البحث
    search_col1, search_col2, search_col3 = st.columns([3, 1, 1])
    
    with search_col1:
        search_query = st.text_input("🔍 بحث عن عميل", placeholder="ابحث بالاسم، الهاتف، العنوان...")
    
    with search_col2:
        filter_status = st.selectbox("الحالة", ["الكل", "نشط", "مدين", "جديد"])
    
    with search_col3:
        if st.button("🔄 تحديث", use_container_width=True):
            st.rerun()
    
    # فلترة العملاء
    filtered_customers = customers
    if search_query:
        filtered_customers = [
            c for c in customers
            if (search_query.lower() in c.get('name', '').lower() or
                search_query in c.get('phone', '') or
                search_query.lower() in c.get('gov', '').lower() or
                search_query.lower() in c.get('village', '').lower())
        ]
    
    if filter_status != "الكل":
        filtered_customers = [
            c for c in filtered_customers
            if calculate_customer_summary(c)['status'] == filter_status
        ]
    
    if not filtered_customers:
        st.warning("⚠️ لا توجد نتائج للبحث")
    else:
        st.success(f"✅ تم العثور على {len(filtered_customers)} عميل")
        
        # عرض العملاء
        for customer in filtered_customers:
            with st.expander(f"👤 {customer.get('name')} - 📱 {customer.get('phone')}", expanded=False):
                summary = calculate_customer_summary(customer)
                
                # عرض المعلومات
                col_left, col_center, col_right = st.columns([2, 2, 1])
                
                with col_left:
                    st.markdown(f"""
                    **معلومات العميل:**
                    - رقم العميل: PL-{customer.get('id'):04d}
                    - العنوان: {customer.get('gov')} - {customer.get('village')}
                    - نوع الجهاز: {customer.get('type')}
                    - تاريخ التسجيل: {customer.get('created_at')}
                    """)
                
                with col_center:
                    st.markdown(f"""
                    **الإحصائيات:**
                    - إجمالي المدفوعات: {summary['total_paid']:,} ج.م
                    - رصيد الجهاز: {summary['device_balance']:,} ج.م
                    - عدد الزيارات: {summary['total_visits']}
                    - الحالة: {summary['status']}
                    """)
                
                with col_right:
                    # إنشاء باركود
                    cust_url = f"{get_current_url()}/?id={customer.get('id')}"
                    qr_encoded, qr_bytes = generate_qr_code(cust_url)
                    
                    if qr_encoded:
                        st.markdown(f"""
                        <div style="text-align: center;">
                            <img src="data:image/png;base64,{qr_encoded}" style="width: 120px; height: 120px;">
                            <p style="font-size: 12px; margin: 5px 0;">PL-{customer.get('id'):04d}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # زر تحميل الباركود
                        st.download_button(
                            label="📥 تحميل الباركود",
                            data=qr_bytes,
                            file_name=f"باركود_PL-{customer.get('id'):04d}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                
                # أزرار الإجراءات
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                
                with col_btn1:
                    if st.button("🛠️ إضافة صيانة", key=f"add_maint_{customer.get('id')}", use_container_width=True):
                        st.session_state.page = "maintenance"
                        st.session_state.selected_customer = customer.get('id')
                        st.rerun()
                
                with col_btn2:
                    if st.button("✏️ تعديل", key=f"edit_{customer.get('id')}", use_container_width=True):
                        st.session_state.page = "edit_customer"
                        st.session_state.selected_customer = customer.get('id')
                        st.rerun()
                
                with col_btn3:
                    if st.button("🗑️ حذف", key=f"delete_{customer.get('id')}", use_container_width=True, type="secondary"):
                        if st.checkbox(f"تأكيد حذف {customer.get('name')}", key=f"confirm_del_{customer.get('id')}"):
                            customers[:] = [c for c in customers if c.get('id') != customer.get('id')]
                            save_data(CUSTOMERS_FILE, customers)
                            st.success("✅ تم حذف العميل بنجاح")
                            st.rerun()

# --- إضافة عميل جديد ---
elif st.session_state.page == "add_customer":
    st.title("➕ إضافة عميل جديد")
    
    with st.form("new_customer_form", clear_on_submit=True):
        st.subheader("📝 المعلومات الأساسية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 اسم العميل *", placeholder="الاسم الكامل للعميل")
            phone = st.text_input("📱 رقم الهاتف *", placeholder="مثال: 01012345678")
            email = st.text_input("✉️ البريد الإلكتروني", placeholder="email@example.com")
            gov = st.selectbox("📍 المحافظة *", [
                "القاهرة", "الجيزة", "المنوفية", "الغربية", 
                "القليوبية", "الشرقية", "الدقهلية", "الأسكندرية", "أخرى"
            ])
        
        with col2:
            village = st.text_input("🏘️ القرية/المركز *", placeholder="اسم القرية أو المركز")
            street = st.text_input("🏠 الشارع", placeholder="اسم الشارع والمبنى")
            ctype = st.selectbox("⚙️ نوع الجهاز *", [
                "7 مراحل", "5 مراحل", "جامبو", "فلتر عادي", 
                "رو اوسموسيس", "تحلية بحر", "أخرى"
            ])
            capacity = st.selectbox("💧 سعة الجهاز", ["غير محدد", "50 جالون", "100 جالون", "200 جالون", "500 جالون"])
        
        st.subheader("💰 المعلومات المالية")
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            device_price = st.number_input("سعر الجهاز (ج.م)", min_value=0, value=10000, step=500)
            down_payment = st.number_input("المقدم (ج.م)", min_value=0, value=2000, step=500)
        
        with col_f2:
            installment_months = st.slider("عدد أشهر الأقساط", 1, 36, 12)
            monthly_payment = (device_price - down_payment) / installment_months
            st.info(f"**القسط الشهري:** {monthly_payment:,.0f} ج.م")
        
        st.subheader("📋 معلومات إضافية")
        notes = st.text_area("ملاحظات", placeholder="أي ملاحظات إضافية عن العميل...")
        
        st.markdown("---")
        
        col_submit, col_cancel = st.columns([1, 1])
        
        with col_submit:
            submitted = st.form_submit_button("💾 حفظ وإنشاء الباركود", type="primary", use_container_width=True)
        
        with col_cancel:
            if st.form_submit_button("❌ إلغاء", type="secondary", use_container_width=True):
                st.session_state.page = "customers"
                st.rerun()
        
        if submitted:
            if not name or not phone or not gov or not village:
                st.error("⚠️ يرجى ملء جميع الحقول الإلزامية (*)")
            else:
                # توليد ID جديد
                new_id = max([c.get('id', 0) for c in customers], default=0) + 1
                
                # إنشاء العميل
                new_customer = {
                    "id": new_id,
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "gov": gov,
                    "village": village,
                    "street": street,
                    "type": ctype,
                    "capacity": capacity,
                    "device_price": device_price,
                    "down_payment": down_payment,
                    "installment_months": installment_months,
                    "monthly_payment": monthly_payment,
                    "notes": notes,
                    "history": [],
                    "created_by": user.get('username'),
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "location": {
                        "lat": 30.0444 + (new_id * 0.001),
                        "lng": 31.2357 + (new_id * 0.001)
                    }
                }
                
                customers.append(new_customer)
                if save_data(CUSTOMERS_FILE, customers):
                    st.success(f"✅ تم تسجيل العميل {name} بنجاح!")
                    
                    # عرض الباركود
                    st.markdown("---")
                    st.subheader("🎫 بطاقة العميل الجديد")
                    
                    cust_url = f"{get_current_url()}/?id={new_id}"
                    qr_encoded, qr_bytes = generate_qr_code(cust_url, 300)
                    
                    if qr_encoded:
                        col_qr, col_info = st.columns([1, 2])
                        
                        with col_qr:
                            st.markdown(f"""
                            <div class="qr-card-custom">
                                <img src="data:image/png;base64,{qr_encoded}" 
                                     style="width: 100%; max-width: 300px; margin: 0 auto;">
                                <h4 style='color: #28a745; margin: 15px 0 5px 0;'>باركود المتابعة</h4>
                                <p style='color: #666; font-size: 14px;'>
                                    مسح الباركود لعرض بيانات العميل
                                </p>
                                <div style="
                                    background: #28a745;
                                    color: white;
                                    padding: 8px 15px;
                                    border-radius: 20px;
                                    font-weight: bold;
                                    display: inline-block;
                                    margin-top: 10px;
                                ">
                                    PL-{new_id:04d}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # زر تحميل الباركود
                            st.markdown(
                                create_qr_download_button(
                                    qr_bytes, 
                                    f"PowerLife_PL-{new_id:04d}.png",
                                    "📥 تحميل الباركود"
                                ),
                                unsafe_allow_html=True
                            )
                        
                        with col_info:
                            st.markdown(f"""
                            <div class="custom-card">
                                <h3 style='color: #28a745;'>معلومات العميل</h3>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                                    <div>
                                        <p><strong>👤 الاسم:</strong> {name}</p>
                                        <p><strong>📱 الهاتف:</strong> {phone}</p>
                                        <p><strong>✉️ البريد:</strong> {email if email else 'غير محدد'}</p>
                                        <p><strong>📍 العنوان:</strong> {gov} - {village}</p>
                                    </div>
                                    <div>
                                        <p><strong>⚙️ نوع الجهاز:</strong> {ctype}</p>
                                        <p><strong>💧 السعة:</strong> {capacity}</p>
                                        <p><strong>💰 سعر الجهاز:</strong> {device_price:,} ج.م</p>
                                        <p><strong>📅 تاريخ التسجيل:</strong> {new_customer['created_at']}</p>
                                    </div>
                                </div>
                                <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                                    <h4 style='color: #28a745; margin-bottom: 10px;'>💳 خطة السداد</h4>
                                    <p><strong>المقدم:</strong> {down_payment:,} ج.م</p>
                                    <p><strong>المتبقي:</strong> {device_price - down_payment:,} ج.م</p>
                                    <p><strong>القسط الشهري:</strong> {monthly_payment:,.0f} ج.م</p>
                                    <p><strong>المدة:</strong> {installment_months} شهر</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    # عرض الرابط
                    st.markdown("### 🔗 رابط المتابعة")
                    st.code(cust_url, language="text")
                    
                    if st.button("📋 نسخ الرابط", use_container_width=True):
                        st.success("✅ تم نسخ الرابط!")
                else:
                    st.error("❌ حدث خطأ أثناء حفظ البيانات")

# --- إدارة الصيانة ---
elif st.session_state.page == "maintenance":
    st.title("🛠️ إدارة الصيانة")
    
    tab1, tab2, tab3 = st.tabs(["إضافة صيانة", "سجل الصيانة", "الصيانة المجدولة"])
    
    with tab1:
        if not customers:
            st.warning("⚠️ لا يوجد عملاء لإضافة صيانة")
        else:
            # اختيار العميل
            customer_options = {f"{c.get('name')} - {c.get('phone')}": c for c in customers}
            selected_customer_key = st.selectbox("👤 اختر العميل", list(customer_options.keys()))
            selected_customer = customer_options[selected_customer_key]
            
            st.info(f"**العميل:** {selected_customer.get('name')} | **نوع الجهاز:** {selected_customer.get('type')}")
            
            # نموذج الصيانة
            with st.form("maintenance_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    work_types = [
                        "تنظيف عام", "تغيير شمعة 1", "تغيير شمعة 2", "تغيير شمعة 3",
                        "تغيير ممبرين", "تغيير كربون", "صيانة موتور", "تغيير خزان",
                        "فحص ضغط", "تعقيم", "تغيير فلاتر", "أخرى"
                    ]
                    work_done = st.multiselect("🔧 الأعمال المنجزة", work_types)
                    custom_work = st.text_input("🔨 أعمال أخرى")
                    
                    # اختيار الفني
                    tech_options = [t.get('name') for t in technicians]
                    technician = st.selectbox("👷 الفني المسؤول", tech_options)
                
                with col2:
                    amount = st.number_input("💰 المبلغ (ج.م)", min_value=0, value=0, step=50)
                    payment_method = st.selectbox("💳 طريقة الدفع", ["نقدي", "تحويل بنكي", "شيك", "آخرى"])
                    maintenance_date = st.date_input("📅 تاريخ الصيانة", datetime.now())
                    next_maintenance = st.date_input("📅 موعد الصيانة القادمة", datetime.now() + timedelta(days=30))
                    notes = st.text_area("📝 ملاحظات الصيانة")
                
                # جمع الأعمال
                all_work = work_done.copy()
                if custom_work.strip():
                    all_work.append(custom_work.strip())
                
                submitted = st.form_submit_button("💾 حفظ الصيانة", type="primary")
                
                if submitted:
                    if not all_work:
                        st.error("⚠️ يرجى تحديد الأعمال المنجزة")
                    else:
                        # إنشاء سجل الصيانة
                        maintenance_record = {
                            "id": int(time.time()),
                            "date": maintenance_date.strftime("%Y-%m-%d"),
                            "technician": technician,
                            "work": ", ".join(all_work),
                            "amount": amount,
                            "payment_method": payment_method,
                            "notes": notes,
                            "next_maintenance": next_maintenance.strftime("%Y-%m-%d"),
                            "added_by": user.get('username'),
                            "added_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        # إضافة للعميل
                        for i, c in enumerate(customers):
                            if c.get('id') == selected_customer.get('id'):
                                if 'history' not in customers[i]:
                                    customers[i]['history'] = []
                                customers[i]['history'].append(maintenance_record)
                                break
                        
                        if save_data(CUSTOMERS_FILE, customers):
                            st.success("✅ تم حفظ بيانات الصيانة بنجاح!")
                            
                            # تحديث بيانات الفني
                            for i, t in enumerate(technicians):
                                if t.get('name') == technician:
                                    technicians[i]['completed_jobs'] = technicians[i].get('completed_jobs', 0) + 1
                                    save_data(TECHNICIANS_FILE, technicians)
                                    break
    
    with tab2:
        st.subheader("📋 سجل الصيانة الكامل")
        
        all_maintenance = []
        for customer in customers:
            for record in customer.get('history', []):
                all_maintenance.append({
                    "العميل": customer.get('name'),
                    "التاريخ": record.get('date', record.get('التاريخ', '')),
                    "الفني": record.get('technician', record.get('الفني', '')),
                    "الأعمال": record.get('work', record.get('العمل', '')),
                    "المبلغ": record.get('amount', record.get('التكلفة', 0)),
                    "طريقة الدفع": record.get('payment_method', 'نقدي')
                })
        
        if all_maintenance:
            df = pd.DataFrame(all_maintenance)
            df = df.sort_values("التاريخ", ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 لا توجد سجلات صيانة")

# --- إدارة الفنيين ---
elif st.session_state.page == "technicians":
    st.title("👷 إدارة الفنيين")
    
    tab1, tab2, tab3 = st.tabs(["قائمة الفنيين", "تتبع الفنيين", "أداء الفنيين"])
    
    with tab1:
        col_add, col_refresh = st.columns([3, 1])
        
        with col_add:
            if st.button("➕ إضافة فني جديد", use_container_width=True):
                st.session_state.page = "add_technician"
                st.rerun()
        
        with col_refresh:
            if st.button("🔄 تحديث", use_container_width=True):
                st.rerun()
        
        if technicians:
            for tech in technicians:
                with st.expander(f"👷 {tech.get('name')} - 📱 {tech.get('phone')}", expanded=False):
                    col_info, col_stats, col_actions = st.columns([2, 2, 1])
                    
                    with col_info:
                        st.markdown(f"""
                        **معلومات الفني:**
                        - التخصص: {tech.get('specialty', 'جميع الأعمال')}
                        - الحالة: {tech.get('status', 'نشط')}
                        - الموقع: {tech.get('current_location', 'غير محدد')}
                        - تاريخ الإضافة: {tech.get('created_at', 'غير محدد')}
                        """)
                    
                    with col_stats:
                        rating = tech.get('rating', 5.0)
                        completed = tech.get('completed_jobs', 0)
                        
                        st.markdown(f"""
                        **الإحصائيات:**
                        - التقييم: {'⭐' * int(rating)}{'½' if rating % 1 else ''} ({rating})
                        - المهام المكتملة: {completed}
                        - المعدل اليومي: {completed//30 if completed>30 else 1}
                        """)
                    
                    with col_actions:
                        if st.button("📍 تحديث الموقع", key=f"loc_{tech.get('id')}", use_container_width=True):
                            # في الواقع، سيتم الحصول من GPS
                            st.success("✅ تم تحديث الموقع")
                        
                        if st.button("📞 اتصال", key=f"call_{tech.get('id')}", use_container_width=True):
                            st.info(f"اتصال بـ {tech.get('phone')}")
    
    with tab2:
        st.subheader("📍 تتبع الفنيين على الخريطة")
        
        try:
            # خريطة الفنيين
            map_data = []
            for tech in technicians:
                if 'location' in tech:
                    map_data.append({
                        'lat': tech['location']['lat'],
                        'lon': tech['location']['lng'],
                        'name': tech.get('name')
                    })
            
            if map_data:
                df_map = pd.DataFrame(map_data)
                st.map(df_map, zoom=10)
                
                # معلومات الفنيين
                for tech in technicians:
                    if 'location' in tech:
                        st.info(f"**{tech.get('name')}** - {tech.get('current_location', 'غير محدد')}")
            else:
                st.info("📍 لا توجد بيانات موقع للفنيين")
        except:
            st.info("📍 ميزة الخرائط تحت التطوير")
    
    with tab3:
        st.subheader("📊 أداء الفنيين")
        
        performance_data = []
        for tech in technicians:
            completed = tech.get('completed_jobs', 0)
            rating = tech.get('rating', 5.0)
            
            performance_data.append({
                "الفني": tech.get('name'),
                "المهام المكتملة": completed,
                "التقييم": rating,
                "الكفاءة": min(100, (completed / 10) * 100) if completed > 0 else 0
            })
        
        if performance_data:
            df_perf = pd.DataFrame(performance_data)
            df_perf = df_perf.sort_values("المهام المكتملة", ascending=False)
            
            # رسم بياني
            fig = px.bar(
                df_perf,
                x='الفني',
                y='المهام المكتملة',
                color='التقييم',
                title='أداء الفنيين',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_perf, use_container_width=True, hide_index=True)

# --- التتبع على الخريطة ---
elif st.session_state.page == "tracking":
    st.title("📍 تتبع العملاء والفنيين")
    
    # خريطة تفاعلية
    try:
        # بيانات الموقع
        locations_data = []
        
        # إضافة العملاء
        for customer in customers[:10]:  # أول 10 عملاء فقط
            if 'location' in customer:
                locations_data.append({
                    'lat': customer['location']['lat'],
                    'lon': customer['location']['lng'],
                    'name': customer.get('name'),
                    'type': 'customer',
                    'color': 'red'
                })
        
        # إضافة الفنيين
        for tech in technicians:
            if 'location' in tech:
                locations_data.append({
                    'lat': tech['location']['lat'],
                    'lon': tech['location']['lng'],
                    'name': tech.get('name'),
                    'type': 'technician',
                    'color': 'green'
                })
        
        if locations_data:
            df_locations = pd.DataFrame(locations_data)
            
            # عرض الخريطة
            st.map(df_locations, zoom=10)
            
            # مفتاح الخريطة
            st.markdown("""
            <div style="
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin: 15px 0;
                display: flex;
                gap: 20px;
                flex-wrap: wrap;
            ">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 15px; height: 15px; background: red; border-radius: 50%;"></div>
                    <span>عملاء</span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 15px; height: 15px; background: green; border-radius: 50%;"></div>
                    <span>فنيون</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # قائمة النقاط
            st.subheader("📍 النقاط على الخريطة")
            
            col_list1, col_list2 = st.columns(2)
            
            with col_list1:
                st.markdown("**👥 العملاء:**")
                for loc in locations_data:
                    if loc['type'] == 'customer':
                        st.write(f"- {loc['name']}")
            
            with col_list2:
                st.markdown("**👷 الفنيون:**")
                for loc in locations_data:
                    if loc['type'] == 'technician':
                        st.write(f"- {loc['name']}")
        else:
            st.info("📍 لا توجد بيانات موقع متاحة")
            
    except Exception as e:
        st.error(f"خطأ في عرض الخريطة: {str(e)}")
        st.info("جاري تطوير ميزة الخرائط...")

# --- التقارير ---
elif st.session_state.page == "reports":
    st.title("📈 التقارير والإحصائيات")
    
    tab1, tab2, tab3 = st.tabs(["التقارير المالية", "تقارير الصيانة", "تقارير العملاء"])
    
    with tab1:
        st.subheader("💰 التقارير المالية")
        
        # إحصائيات مالية
        total_income = 0
        monthly_income = {}
        payment_methods = {}
        
        for customer in customers:
            for record in customer.get('history', []):
                amount = record.get('amount', record.get('التكلفة', 0))
                total_income += amount
                
                # حسب الشهر
                date_str = record.get('date', record.get('التاريخ', ''))
                if date_str:
                    try:
                        month = date_str[:7]  # YYYY-MM
                        monthly_income[month] = monthly_income.get(month, 0) + amount
                    except:
                        pass
                
                # حسب طريقة الدفع
                method = record.get('payment_method', 'نقدي')
                payment_methods[method] = payment_methods.get(method, 0) + amount
        
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            st.metric("إجمالي الدخل", f"{total_income:,} ج.م")
            
            if monthly_income:
                months = list(monthly_income.keys())[-6:]  # آخر 6 أشهر
                values = [monthly_income[m] for m in months]
                
                fig = px.line(
                    x=months,
                    y=values,
                    title="الدخل الشهري",
                    labels={'x': 'الشهر', 'y': 'المبلغ (ج.م)'}
                )
                fig.update_traces(line_color='#28a745')
                st.plotly_chart(fig, use_container_width=True)
        
        with col_f2:
            if payment_methods:
                methods = list(payment_methods.keys())
                values = list(payment_methods.values())
                
                fig = px.pie(
                    names=methods,
                    values=values,
                    title="طرق الدفع",
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("🛠️ تقارير الصيانة")
        
        # إحصائيات الصيانة
        maintenance_by_month = {}
        maintenance_by_tech = {}
        
        for customer in customers:
            for record in customer.get('history', []):
                date_str = record.get('date', record.get('التاريخ', ''))
                tech = record.get('technician', record.get('الفني', ''))
                
                if date_str:
                    try:
                        month = date_str[:7]
                        maintenance_by_month[month] = maintenance_by_month.get(month, 0) + 1
                    except:
                        pass
                
                if tech:
                    maintenance_by_tech[tech] = maintenance_by_tech.get(tech, 0) + 1
        
        if maintenance_by_month:
            months = list(maintenance_by_month.keys())[-6:]
            counts = [maintenance_by_month[m] for m in months]
            
            fig = px.bar(
                x=months,
                y=counts,
                title="عدد عمليات الصيانة الشهرية",
                labels={'x': 'الشهر', 'y': 'عدد العمليات'},
                color_discrete_sequence=['#20c997']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("👥 تقارير العملاء")
        
        # توزيع العملاء
        customer_by_gov = {}
        customer_by_type = {}
        
        for customer in customers:
            gov = customer.get('gov', 'غير محدد')
            device_type = customer.get('type', 'غير محدد')
            
            customer_by_gov[gov] = customer_by_gov.get(gov, 0) + 1
            customer_by_type[device_type] = customer_by_type.get(device_type, 0) + 1
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            if customer_by_gov:
                fig = px.pie(
                    names=list(customer_by_gov.keys()),
                    values=list(customer_by_gov.values()),
                    title="توزيع العملاء حسب المحافظة"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col_c2:
            if customer_by_type:
                fig = px.bar(
                    x=list(customer_by_type.keys()),
                    y=list(customer_by_type.values()),
                    title="توزيع أنواع الأجهزة"
                )
                st.plotly_chart(fig, use_container_width=True)

# --- إدارة المستخدمين (للمدير فقط) ---
elif st.session_state.page == "users" and user.get('role') == 'admin':
    st.title("👤 إدارة المستخدمين")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("الاسم الكامل *")
            username = st.text_input("اسم المستخدم *")
            password = st.text_input("كلمة المرور *", type="password")
        
        with col2:
            phone = st.text_input("رقم الهاتف")
            email = st.text_input("البريد الإلكتروني")
            role = st.selectbox("الدور *", ["technician", "admin", "supervisor", "accountant"])
        
        if st.form_submit_button("➕ إضافة مستخدم", type="primary"):
            if all([full_name, username, password]):
                new_user = {
                    "id": max([u.get('id', 0) for u in users], default=0) + 1,
                    "full_name": full_name,
                    "username": username,
                    "password": hash_password(password),
                    "phone": phone,
                    "email": email,
                    "role": role,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "created_by": user.get('username')
                }
                
                users.append(new_user)
                save_data(USERS_FILE, users)
                st.success(f"✅ تم إضافة المستخدم {full_name}")
            else:
                st.error("⚠️ يرجى ملء الحقول الإلزامية")
    
    # قائمة المستخدمين
    st.subheader("📋 قائمة المستخدمين")
    
    if users:
        users_df = pd.DataFrame([
            {
                "الاسم": u.get('full_name'),
                "اسم المستخدم": u.get('username'),
                "الدور": u.get('role'),
                "الهاتف": u.get('phone', ''),
                "تاريخ الإضافة": u.get('created_at', '')
            }
            for u in users
            if u.get('username') != 'admin'  # إخفاء المدير الرئيسي
        ])
        
        st.dataframe(users_df, use_container_width=True, hide_index=True)

# --- تسجيل الخروج ---
elif st.session_state.page == "logout":
    st.title("🚪 تسجيل الخروج")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.warning("### هل أنت متأكد من تسجيل الخروج؟")
        
        col_yes, col_no = st.columns(2)
        
        with col_yes:
            if st.button("✅ نعم، سجل خروج", use_container_width=True, type="primary"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.page = "dashboard"
                st.success("✅ تم تسجيل الخروج بنجاح!")
                time.sleep(1)
                st.rerun()
        
        with col_no:
            if st.button("❌ لا، إلغاء", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()

# ================== 8. تذييل الصفحة ==================

st.markdown("---")

# معلومات الشركة
st.markdown("""
<div style="
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    margin-top: 50px;
    box-shadow: 0 -5px 25px rgba(0,0,0,0.1);
">
    <h2 style='margin-bottom: 20px;'>💧 Power Life</h2>
    
    <div style="display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; margin-bottom: 25px;">
        <div style="text-align: center;">
            <h4 style='margin-bottom: 10px;'>📞 اتصل بنا</h4>
            <p style='margin: 5px 0;'>خدمة العملاء: 01234567890</p>
            <p style='margin: 5px 0;'>الدعم الفني: 01112223333</p>
        </div>
        
        <div style="text-align: center;">
            <h4 style='margin-bottom: 10px;'>✉️ البريد</h4>
            <p style='margin: 5px 0;'>info@powerlife.com</p>
            <p style='margin: 5px 0;'>support@powerlife.com</p>
        </div>
        
        <div style="text-align: center;">
            <h4 style='margin-bottom: 10px;'>⏰ ساعات العمل</h4>
            <p style='margin: 5px 0;'>من 9 صباحاً إلى 10 مساءً</p>
            <p style='margin: 5px 0;'>طوال أيام الأسبوع</p>
        </div>
    </div>
    
    <div style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 20px;">
        <p style='margin: 0; font-size: 14px; opacity: 0.8;'>
            © 2024 Power Life Company. جميع الحقوق محفوظة.
        </p>
        <p style='margin: 5px 0 0 0; font-size: 12px; opacity: 0.6;'>
            نظام إدارة العملاء المتكامل - الإصدار 3.0
        </p>
    </div>
</div>
""", unsafe_allow_html=True)
