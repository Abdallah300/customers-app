import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import base64
from io import BytesIO
import qrcode
import hashlib

# ================== 1. إعدادات النظام وتنسيق الواجهة ==================

st.set_page_config(
    page_title="Power Life CRM Ultra",
    page_icon="💧", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص مع دعم كامل للعربية والأيقونات
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* تحسينات للشريط الجانبي */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #f8f9fa !important;
    }
    
    /* تحسين الأزرار */
    .stButton > button {
        width: 100%;
        background-color: #28a745 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: #218838 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3) !important;
    }
    
    /* تحسين حقول الإدخال */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        text-align: right !important;
        border-radius: 8px !important;
        border: 2px solid #e9ecef !important;
        padding: 10px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #28a745 !important;
        box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important;
    }
    
    /* تحسين الجداول */
    .report-table {
        width: 100%;
        border-collapse: collapse;
        background-color: white;
        color: black;
        margin-bottom: 20px;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .report-table th {
        background-color: #28a745 !important;
        color: white !important;
        padding: 12px 15px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    
    .report-table td {
        padding: 10px 15px !important;
        border-top: 1px solid #dee2e6 !important;
    }
    
    .report-table tr:hover {
        background-color: #f8f9fa !important;
    }
    
    /* تحسين البطاقات */
    .customer-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border-right: 5px solid #28a745;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #28a745, #20c997);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
    }
    
    .qr-card {
        border: 2px dashed #28a745;
        padding: 25px;
        text-align: center;
        background: #f8fff8;
        border-radius: 12px;
        max-width: 350px;
        margin: 20px auto;
        box-shadow: 0 4px 15px rgba(40, 167, 69, 0.1);
    }
    
    /* تحسينات الشريط العلوي */
    .st-emotion-cache-1avcm0n {
        background: linear-gradient(90deg, #28a745, #20c997) !important;
    }
    
    /* تحسينات للهواتف */
    @media (max-width: 768px) {
        .customer-card, .stats-card, .qr-card {
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .stButton > button {
            padding: 8px 15px !important;
            font-size: 14px !important;
        }
        
        h1 { font-size: 24px !important; }
        h2 { font-size: 20px !important; }
        h3 { font-size: 18px !important; }
    }
    
    /* تحسينات القوائم */
    .stRadio > div {
        flex-direction: column !important;
        gap: 8px !important;
    }
    
    .stRadio > div > label {
        background: white !important;
        border: 2px solid #e9ecef !important;
        border-radius: 10px !important;
        padding: 12px 15px !important;
        margin: 5px 0 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    .stRadio > div > label:hover {
        border-color: #28a745 !important;
        background: #f8fff8 !important;
    }
    
    .stRadio > div > label[data-testid="stRadio"] {
        background: #f8fff8 !important;
        border-color: #28a745 !important;
    }
    
    /* إصلاح الأيقونات */
    .menu-icon {
        font-size: 18px !important;
        margin-left: 8px !important;
        vertical-align: middle !important;
    }
    
    /* تحسينات النماذج */
    .stForm {
        border: 2px solid #e9ecef;
        border-radius: 12px;
        padding: 25px;
        background: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* تحسينات التنبيهات */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
    }
    
    /* تحسينات علامات التبويب */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0 !important;
        padding: 10px 20px !important;
        background-color: #f8f9fa !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #28a745 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. إدارة ملفات البيانات ==================

USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"

def load_data(file):
    """تحميل البيانات من ملف JSON"""
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"خطأ في تحميل الملف {file}: {str(e)}")
            return []
    return []

def save_data(file, data):
    """حفظ البيانات إلى ملف JSON"""
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"خطأ في حفظ الملف {file}: {str(e)}")
        return False

# تحميل البيانات
users = load_data(USERS_FILE)
customers = load_data(CUSTOMERS_FILE)

# تأمين حساب المدير
if not any(u.get('username') == "admin" for u in users):
    users.append({
        "username": "admin",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "full_name": "مدير النظام",
        "phone": "01000000000",
        "created_at": str(datetime.now().date())
    })
    save_data(USERS_FILE, users)

# ================== 3. وظائف مساعدة ==================

def hash_password(password):
    """تشفير كلمة المرور"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """التحقق من كلمة المرور"""
    return hash_password(password) == hashed

def generate_qr_code(data, size=200):
    """إنشاء رمز QR"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#28a745", back_color="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_bytes = buffered.getvalue()
        
        encoded = base64.b64encode(img_bytes).decode()
        return encoded, img_bytes
    except Exception as e:
        st.error(f"خطأ في إنشاء الباركود: {str(e)}")
        return None, None

def create_qr_download_link(img_bytes, filename="باركود_عميل.png"):
    """إنشاء رابط تحميل للباركود"""
    try:
        b64 = base64.b64encode(img_bytes).decode()
        href = f'''
        <a href="data:image/png;base64,{b64}" 
           download="{filename}" 
           style="
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 8px;
                display: inline-block;
                margin: 10px 5px;
                font-weight: bold;
                text-align: center;
                min-width: 150px;
           ">
           📥 {filename}
        </a>
        '''
        return href
    except:
        return ""

def get_customer_url(customer_id):
    """إنشاء رابط العميل"""
    # عند النشر على Streamlit Cloud، استبدل هذا بالرابط الحقيقي
    base_url = st.secrets.get("APP_URL", "https://powerlife.streamlit.app")
    return f"{base_url}/?id={customer_id}"

def get_customer_stats(customer):
    """حساب إحصائيات العميل"""
    history = customer.get('history', [])
    
    if not history:
        return {
            "total_paid": 0,
            "total_visits": 0,
            "technicians": [],
            "last_visit": None,
            "monthly_stats": []
        }
    
    total_paid = sum(h.get('التكلفة', 0) for h in history)
    total_visits = len(history)
    technicians = list(set(h.get('الفني', 'غير معروف') for h in history))
    
    # الإحصائيات الشهرية
    monthly_data = {}
    for h in history:
        try:
            date_str = h.get('التاريخ', '')
            if date_str:
                date = datetime.strptime(date_str, "%Y-%m-%d")
                month_year = f"{date.year}-{date.month:02d}"
                
                if month_year not in monthly_data:
                    monthly_data[month_year] = {
                        "amount": 0,
                        "visits": 0,
                        "technicians": set()
                    }
                
                monthly_data[month_year]["amount"] += h.get('التكلفة', 0)
                monthly_data[month_year]["visits"] += 1
                monthly_data[month_year]["technicians"].add(h.get('الفني', 'غير معروف'))
        except:
            continue
    
    # تحويل إلى قائمة
    monthly_stats = []
    for month in sorted(monthly_data.keys(), reverse=True):
        monthly_stats.append({
            "الشهر": month,
            "المبلغ": monthly_data[month]["amount"],
            "الزيارات": monthly_data[month]["visits"],
            "الفنيين": ", ".join(monthly_data[month]["technicians"])
        })
    
    # آخر زيارة
    last_visit = max(history, key=lambda x: x.get('التاريخ', ''), default=None)
    
    return {
        "total_paid": total_paid,
        "total_visits": total_visits,
        "technicians": technicians,
        "last_visit": last_visit,
        "monthly_stats": monthly_stats
    }

# ================== 4. صفحة العميل العامة (من خلال الباركود) ==================

# التحقق من وجود معامل id في الرابط
if "id" in st.query_params:
    try:
        cust_id = int(st.query_params["id"])
        target_cust = next((c for c in customers if c.get('id') == cust_id), None)
        
        if target_cust:
            # ========== تصميم صفحة العميل ==========
            st.markdown(f"<h1 style='text-align: center; color: #28a745;'>💧 مرحباً بك: {target_cust.get('name', '')}</h1>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; color: #666;'>سجل الصيانة والمدفوعات الخاص بك</h3>", unsafe_allow_html=True)
            
            # حساب الإحصائيات
            stats = get_customer_stats(target_cust)
            
            # عرض الإحصائيات في صف واحد
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stats-card">
                    <h4>👤 رقم العميل</h4>
                    <h3>PL-{target_cust.get('id', 0):04d}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stats-card">
                    <h4>💰 إجمالي المدفوعات</h4>
                    <h3>{stats['total_paid']:,} ج.م</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stats-card">
                    <h4>🛠️ عدد الزيارات</h4>
                    <h3>{stats['total_visits']}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="stats-card">
                    <h4>👷 عدد الفنيين</h4>
                    <h3>{len(stats['technicians'])}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            # ========== معلومات العميل ==========
            st.markdown("---")
            st.subheader("📋 معلومات العميل")
            
            info_col1, info_col2 = st.columns(2)
            
            with info_col1:
                st.markdown(f"""
                <div class="customer-card">
                    <h4>📱 معلومات الاتصال</h4>
                    <p><strong>الاسم:</strong> {target_cust.get('name', '')}</p>
                    <p><strong>الهاتف:</strong> {target_cust.get('phone', '')}</p>
                    <p><strong>المحافظة:</strong> {target_cust.get('gov', '')}</p>
                    <p><strong>القرية:</strong> {target_cust.get('village', '')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with info_col2:
                st.markdown(f"""
                <div class="customer-card">
                    <h4>⚙️ معلومات الجهاز</h4>
                    <p><strong>نوع الجهاز:</strong> {target_cust.get('type', '')}</p>
                    <p><strong>تاريخ التسجيل:</strong> {target_cust.get('created_at', '')}</p>
                    <p><strong>آخر زيارة:</strong> {stats['last_visit'].get('التاريخ', 'لا توجد') if stats['last_visit'] else 'لا توجد'}</p>
                    <p><strong>ملاحظات:</strong> {target_cust.get('notes', 'لا توجد')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # ========== الفنيون الذين قاموا بالخدمة ==========
            if stats['technicians']:
                st.subheader("👷 الفنيون الذين قاموا بخدمتك")
                tech_cols = st.columns(4)
                for i, tech in enumerate(stats['technicians']):
                    with tech_cols[i % 4]:
                        st.markdown(f"""
                        <div style="
                            background: #fff3cd;
                            padding: 15px;
                            border-radius: 10px;
                            text-align: center;
                            margin: 5px;
                            border-right: 4px solid #ffc107;
                        ">
                            <h4 style='margin: 0; color: #856404;'>{tech}</h4>
                        </div>
                        """, unsafe_allow_html=True)
            
            # ========== الإحصائيات الشهرية ==========
            if stats['monthly_stats']:
                st.markdown("---")
                st.subheader("📊 الإحصائيات الشهرية")
                
                monthly_df = pd.DataFrame(stats['monthly_stats'])
                st.dataframe(monthly_df, use_container_width=True, hide_index=True)
                
                # رسم بياني
                if not monthly_df.empty:
                    monthly_df['الشهر'] = pd.to_datetime(monthly_df['الشهر'] + '-01')
                    chart_data = monthly_df.set_index('الشهر')[['المبلغ']]
                    st.line_chart(chart_data, height=300)
            
            # ========== سجل الصيانة الكامل ==========
            st.markdown("---")
            st.subheader("🛠️ سجل الصيانة الكامل")
            
            history = target_cust.get('history', [])
            if history:
                # فرز التاريخ من الأحدث
                sorted_history = sorted(history, key=lambda x: x.get('التاريخ', ''), reverse=True)
                
                for i, entry in enumerate(sorted_history, 1):
                    with st.expander(f"📅 زيارة {i} - {entry.get('التاريخ', '')} - {entry.get('التكلفة', 0):,} ج.م", expanded=(i == 1)):
                        cols = st.columns([1, 2, 1, 1])
                        
                        with cols[0]:
                            st.markdown(f"**📅 التاريخ:**\n{entry.get('التاريخ', '')}")
                        
                        with cols[1]:
                            st.markdown(f"**🔧 الأعمال:**\n{entry.get('العمل', '')}")
                        
                        with cols[2]:
                            st.markdown(f"**💰 المبلغ:**\n{entry.get('التكلفة', 0):,} ج.م")
                        
                        with cols[3]:
                            st.markdown(f"**👷 الفني:**\n{entry.get('الفني', '')}")
                        
                        if entry.get('ملاحظات'):
                            st.info(f"**ملاحظات:** {entry.get('ملاحظات')}")
                        
                        if entry.get('طريقة الدفع'):
                            st.info(f"**طريقة الدفع:** {entry.get('طريقة الدفع')}")
            else:
                st.info("📭 لا توجد سجلات صيانة حتى الآن")
            
            # ========== معلومات التواصل ==========
            st.markdown("---")
            st.markdown("""
            <div style="
                background: #e9f7ef;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin-top: 20px;
                border-right: 5px solid #28a745;
            ">
                <h4 style='color: #28a745; margin-bottom: 10px;'>📞 للاستفسار أو طلب خدمة</h4>
                <p style='margin: 5px 0;'><strong>خدمة العملاء:</strong> 01234567890</p>
                <p style='margin: 5px 0;'><strong>البريد الإلكتروني:</strong> support@powerlife.com</p>
                <p style='margin: 5px 0; color: #666;'>⏰ ساعات العمل: من 9 صباحاً إلى 5 مساءً</p>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.error("⚠️ كود العميل غير صحيح أو غير موجود")
            st.info("يرجى التأكد من صحة الباركود أو التواصل مع إدارة الشركة")
    
    except ValueError:
        st.error("❌ خطأ في كود العميل")
    except Exception as e:
        st.error(f"حدث خطأ: {str(e)}")
    
    st.stop()

# ================== 5. نظام تسجيل الدخول ==================

# تهيئة حالة الجلسة
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "menu_choice" not in st.session_state:
    st.session_state.menu_choice = "📋 قائمة العملاء"

# صفحة تسجيل الدخول
if not st.session_state.logged_in:
    # تصميم صفحة الدخول
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #28a745, #20c997);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            color: white;
            margin-bottom: 30px;
        ">
            <h1 style='margin-bottom: 10px;'>💧</h1>
            <h2 style='margin: 0;'>Power Life CRM Ultra</h2>
            <p style='margin-top: 5px; opacity: 0.9;'>نظام إدارة عملاء متكامل</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<h3 style='text-align: center;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
            
            username = st.text_input("👤 اسم المستخدم", placeholder="أدخل اسم المستخدم")
            password = st.text_input("🔒 كلمة المرور", type="password", placeholder="أدخل كلمة المرور")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_btn = st.button("🚀 دخول", use_container_width=True, type="primary")
            
            with col_btn2:
                if st.button("🔄 إعادة تحميل", use_container_width=True):
                    st.rerun()
            
            if login_btn:
                if not username or not password:
                    st.error("⚠️ يرجى إدخال اسم المستخدم وكلمة المرور")
                else:
                    user_found = False
                    for user in users:
                        if user.get('username') == username:
                            if verify_password(password, user.get('password', '')):
                                st.session_state.logged_in = True
                                st.session_state.current_user = user
                                st.success(f"✅ تم تسجيل الدخول بنجاح! مرحباً {user.get('full_name', username)}")
                                st.rerun()
                            else:
                                st.error("❌ كلمة المرور غير صحيحة")
                            user_found = True
                            break
                    
                    if not user_found:
                        st.error("❌ اسم المستخدم غير موجود")
            
            # معلومات الدخول الافتراضية
            with st.expander("🔑 بيانات الدخول الافتراضية (للمدير)"):
                st.code("اسم المستخدم: admin\nكلمة المرور: admin123")
                st.info("يمكن للمدير إضافة مستخدمين جدد من قائمة إدارة الفنيين")
    
    with col1:
        st.empty()
    
    with col3:
        st.empty()
    
    st.stop()

# ================== 6. القائمة الرئيسية (بعد تسجيل الدخول) ==================

user_now = st.session_state.current_user

# القائمة الرئيسية في الشريط الجانبي
st.sidebar.markdown(f"""
<div style="
    background: linear-gradient(135deg, #28a745, #20c997);
    padding: 20px;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
">
    <h3 style='margin: 0;'>💧 Power Life</h3>
    <p style='margin: 5px 0 0 0; opacity: 0.9; font-size: 14px;'>{user_now.get('full_name', user_now.get('username'))}</p>
    <p style='margin: 2px 0; font-size: 12px; background: rgba(255,255,255,0.2); padding: 3px 8px; border-radius: 10px; display: inline-block;'>
        {user_now.get('role', 'مستخدم')}
    </p>
</div>
""", unsafe_allow_html=True)

# تعريف القائمة بناءً على صلاحيات المستخدم
menu_items = [
    {"icon": "📋", "title": "قائمة العملاء", "key": "customers_list"},
    {"icon": "➕", "title": "إضافة عميل", "key": "add_customer"},
    {"icon": "🛠️", "title": "إضافة صيانة", "key": "add_maintenance"},
    {"icon": "🔍", "title": "بحث وتعديل", "key": "search_edit"},
    {"icon": "💰", "title": "أرباح الشركة", "key": "profits"}
]

if user_now.get('role') == 'admin':
    menu_items.extend([
        {"icon": "👤", "title": "إدارة الفنيين", "key": "manage_tech"},
        {"icon": "📊", "title": "التقارير", "key": "reports"},
        {"icon": "⚙️", "title": "الإعدادات", "key": "settings"}
    ])

menu_items.append({"icon": "🚪", "title": "تسجيل الخروج", "key": "logout"})

# عرض القائمة في الشريط الجانبي
st.sidebar.markdown("### 📂 القائمة الرئيسية")
selected_key = st.session_state.menu_choice

# إنشاء أزرار القائمة
for item in menu_items:
    if st.sidebar.button(
        f"{item['icon']} {item['title']}",
        key=item['key'],
        use_container_width=True,
        type="primary" if selected_key == item['key'] else "secondary"
    ):
        st.session_state.menu_choice = item['key']
        st.rerun()

# ================== 7. معالجة اختيار القائمة ==================

# --- 1. قائمة العملاء ---
if st.session_state.menu_choice == "customers_list":
    st.title("📋 قائمة العملاء")
    
    if not customers:
        st.info("📭 لا يوجد عملاء مسجلين حتى الآن")
    else:
        # شريط البحث والتحكم
        search_col1, search_col2, search_col3 = st.columns([3, 1, 1])
        
        with search_col1:
            search_term = st.text_input("🔍 بحث عن عميل", placeholder="ابحث بالاسم، الهاتف، المحافظة...")
        
        with search_col2:
            show_qr = st.checkbox("عرض الباركود", value=False)
        
        with search_col3:
            if st.button("📥 تصدير Excel"):
                df = pd.DataFrame(customers)
                
                # إزالة الحقول الكبيرة للتصدير
                df_export = df.copy()
                if 'history' in df_export.columns:
                    df_export['عدد_الزيارات'] = df_export['history'].apply(lambda x: len(x) if isinstance(x, list) else 0)
                    df_export = df_export.drop('history', axis=1, errors='ignore')
                
                # تحويل إلى Excel
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_export.to_excel(writer, index=False, sheet_name='العملاء')
                
                excel_data = output.getvalue()
                st.download_button(
                    label="📥 تحميل ملف Excel",
                    data=excel_data,
                    file_name="عملاء_powerlife.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        # فلترة العملاء
        filtered_customers = customers
        if search_term:
            filtered_customers = [
                c for c in customers
                if (search_term.lower() in c.get('name', '').lower() or
                    search_term in c.get('phone', '') or
                    search_term.lower() in c.get('gov', '').lower() or
                    search_term.lower() in c.get('village', '').lower())
            ]
        
        if not filtered_customers:
            st.warning("⚠️ لا توجد نتائج للبحث")
        else:
            st.success(f"✅ تم العثور على {len(filtered_customers)} عميل")
            
            # عرض العملاء
            for customer in filtered_customers:
                stats = get_customer_stats(customer)
                
                with st.expander(f"👤 {customer.get('name', '')} - 📱 {customer.get('phone', '')} - 📍 {customer.get('gov', '')}", expanded=False):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        st.markdown(f"""
                        <div style="padding: 10px;">
                            <p><strong>رقم العميل:</strong> PL-{customer.get('id', 0):04d}</p>
                            <p><strong>القرية:</strong> {customer.get('village', '')}</p>
                            <p><strong>نوع الجهاز:</strong> {customer.get('type', '')}</p>
                            <p><strong>تاريخ التسجيل:</strong> {customer.get('created_at', '')}</p>
                            <p><strong>عدد الزيارات:</strong> {stats['total_visits']}</p>
                            <p><strong>إجمالي المدفوعات:</strong> {stats['total_paid']:,} ج.م</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_b:
                        if show_qr:
                            cust_url = get_customer_url(customer.get('id', 0))
                            qr_encoded, qr_bytes = generate_qr_code(cust_url)
                            if qr_encoded:
                                st.markdown(f"""
                                <div style="text-align: center;">
                                    <img src="data:image/png;base64,{qr_encoded}" width="120">
                                    <p style="font-size: 12px; margin: 5px 0;">PL-{customer.get('id', 0):04d}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # زر تحميل الباركود
                                st.download_button(
                                    label="📥 تحميل",
                                    data=qr_bytes,
                                    file_name=f"باركود_PL-{customer.get('id', 0):04d}.png",
                                    mime="image/png",
                                    key=f"download_qr_{customer.get('id', 0)}"
                                )

# --- 2. إضافة عميل جديد ---
elif st.session_state.menu_choice == "add_customer":
    st.title("➕ تسجيل عميل جديد")
    
    with st.form("add_customer_form", clear_on_submit=True):
        st.markdown("### 📝 معلومات العميل الأساسية")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("👤 اسم العميل *", placeholder="الاسم الكامل للعميل")
            phone = st.text_input("📱 رقم الهاتف *", placeholder="مثال: 01012345678")
            gov = st.selectbox("📍 المحافظة *", ["القاهرة", "الجيزة", "المنوفية", "الغربية", "القليوبية", "الشرقية", "الدقهلية", "أخرى"])
        
        with col2:
            village = st.text_input("🏘️ القرية/المركز *", placeholder="اسم القرية أو المركز")
            ctype = st.selectbox("⚙️ نوع الجهاز *", ["7 مراحل", "5 مراحل", "جامبو", "فلتر عادي", "رو اوسموسيس"])
            notes = st.text_area("📝 ملاحظات إضافية", placeholder="أي ملاحظات إضافية...")
        
        st.markdown("---")
        submitted = st.form_submit_button("💾 حفظ العميل وإنشاء الباركود", type="primary")
        
        if submitted:
            if not name or not phone or not village:
                st.error("⚠️ يرجى ملء جميع الحقول الإلزامية (*)")
            else:
                # توليد ID جديد
                new_id = max([c.get('id', 0) for c in customers], default=0) + 1
                
                # إنشاء عميل جديد
                new_customer = {
                    "id": new_id,
                    "name": name,
                    "phone": phone,
                    "gov": gov,
                    "village": village,
                    "type": ctype,
                    "notes": notes,
                    "history": [],
                    "created_by": user_now.get('username'),
                    "created_at": str(datetime.now().date())
                }
                
                # إضافة العميل
                customers.append(new_customer)
                if save_data(CUSTOMERS_FILE, customers):
                    st.success(f"✅ تم تسجيل العميل {name} بنجاح!")
                    
                    # عرض الباركود والمعلومات
                    st.markdown("---")
                    st.subheader("🎫 كارت متابعة العميل")
                    
                    # إنشاء QR Code
                    cust_url = get_customer_url(new_id)
                    qr_encoded, qr_bytes = generate_qr_code(cust_url)
                    
                    if qr_encoded:
                        col_a, col_b = st.columns([1, 1])
                        
                        with col_a:
                            st.markdown(f"""
                            <div class="customer-card">
                                <h3 style='color: #28a745;'>معلومات العميل</h3>
                                <p><strong>👤 الاسم:</strong> {name}</p>
                                <p><strong>🆔 رقم العميل:</strong> PL-{new_id:04d}</p>
                                <p><strong>📱 الهاتف:</strong> {phone}</p>
                                <p><strong>📍 العنوان:</strong> {gov} - {village}</p>
                                <p><strong>⚙️ نوع الجهاز:</strong> {ctype}</p>
                                <p><strong>📅 تاريخ التسجيل:</strong> {new_customer['created_at']}</p>
                                <p><strong>👨‍💼 المسجل:</strong> {user_now.get('username')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col_b:
                            st.markdown(f"""
                            <div class="qr-card">
                                <h4 style='color: #28a745;'>باركود المتابعة</h4>
                                <img src="data:image/png;base64,{qr_encoded}" style="width: 200px; height: 200px;">
                                <p style='color: #666; font-size: 14px; margin: 10px 0;'>
                                    🔍 مسح الباركود لمتابعة الصيانة
                                </p>
                                <p style='background: #28a745; color: white; padding: 8px; border-radius: 5px; font-weight: bold;'>
                                    كود العميل: PL-{new_id:04d}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # أزرار التحميل والمشاركة
                        st.markdown("### 📤 خيارات التحميل والمشاركة")
                        col_dl1, col_dl2, col_dl3 = st.columns(3)
                        
                        with col_dl1:
                            # رابط تحميل الباركود
                            st.markdown(create_qr_download_link(qr_bytes, f"باركود_PL-{new_id:04d}.png"), unsafe_allow_html=True)
                        
                        with col_dl2:
                            # نسخ الرابط
                            st.code(cust_url, language="text")
                        
                        with col_dl3:
                            if st.button("📋 نسخ الرابط", use_container_width=True):
                                st.success("✅ تم نسخ الرابط!")
                        
                        # تعليمات الاستخدام
                        with st.expander("📖 تعليمات استخدام الباركود"):
                            st.markdown("""
                            ### 🎯 كيفية استخدام الباركود:
                            
                            1. **قم بتحميل الباركود** واحفظه على جهازك
                            2. **أرسل الباركود للعميل** عبر:
                               - 📱 الواتساب
                               - ✉️ البريد الإلكتروني
                               - 📲 أي تطبيق مراسلة
                            
                            3. **يمكن للعميل**:
                               - 📸 مسح الباركود بكاميرا الهاتف
                               - 💾 حفظ الصورة وعرضها عند الحاجة
                               - 🔗 مشاركة الرابط مباشرة
                            
                            4. **عند مسح الباركود** سيظهر للعميل:
                               - 📋 جميع زيارات الصيانة
                               - 💰 المبالغ المدفوعة
                               - 👷 الفنيين الذين قاموا بالخدمة
                               - 📊 الإحصائيات الشهرية
                               - 📞 معلومات التواصل
                            
                            5. **نصائح مهمة**:
                               - احفظ نسخة من الباركود في ملف العميل
                               - تأكد من وضوح الباركود عند الطباعة
                               - يمكن إعادة إنشاء الباركود من قائمة العملاء
                            """)
                else:
                    st.error("❌ حدث خطأ أثناء حفظ البيانات")

# --- 3. إضافة صيانة ---
elif st.session_state.menu_choice == "add_maintenance":
    st.title("🛠️ تسجيل صيانة جديدة")
    
    if not customers:
        st.warning("⚠️ لا يوجد عملاء مسجلين. الرجاء إضافة عميل أولاً.")
    else:
        # البحث عن العميل
        search_col1, search_col2 = st.columns([3, 1])
        
        with search_col1:
            maintenance_search = st.text_input("🔍 بحث عن عميل", placeholder="ابحث بالاسم أو الهاتف...")
        
        with search_col2:
            show_all = st.checkbox("عرض الكل", value=True)
        
        # فلترة العملاء
        if maintenance_search:
            filtered_for_maintenance = [
                c for c in customers
                if (maintenance_search.lower() in c.get('name', '').lower() or
                    maintenance_search in c.get('phone', ''))
            ]
        else:
            filtered_for_maintenance = customers if show_all else []
        
        if not filtered_for_maintenance:
            st.warning("⚠️ لا توجد نتائج للبحث")
        else:
            # اختيار العميل
            customer_options = {f"{c.get('name')} - {c.get('phone')} - {c.get('gov')}": c for c in filtered_for_maintenance}
            selected_customer_name = st.selectbox("👤 اختر العميل", list(customer_options.keys()))
            selected_customer = customer_options[selected_customer_name]
            
            st.info(f"تم اختيار: **{selected_customer.get('name')}** - نوع الجهاز: **{selected_customer.get('type')}**")
            
            # نموذج إضافة الصيانة
            with st.form("add_maintenance_form"):
                st.markdown("### 📝 تفاصيل الصيانة")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    work_options = [
                        "تنظيف عام", "تغيير شمعة 1", "تغيير شمعة 2", "تغيير شمعة 3",
                        "تغيير ممبرين", "تغيير كربون", "صيانة موتور", "تغيير خزان",
                        "فحص ضغط", "تعقيم", "أخرى"
                    ]
                    work_done = st.multiselect("🔧 الأعمال المنجزة", work_options)
                    custom_work = st.text_input("🔨 أعمال أخرى (اكتبها)")
                
                with col2:
                    amount = st.number_input("💰 المبلغ المدفوع (ج.م)", min_value=0, value=0, step=50)
                    payment_method = st.selectbox("💳 طريقة الدفع", ["نقدي", "تحويل بنكي", "شيك", "آخرى"])
                    maintenance_notes = st.text_area("📝 ملاحظات الصيانة", placeholder="تفاصيل إضافية عن الصيانة...")
                
                # جمع الأعمال
                all_work = work_done.copy()
                if custom_work.strip():
                    all_work.append(custom_work.strip())
                
                st.markdown("---")
                submit_maintenance = st.form_submit_button("💾 حفظ الصيانة", type="primary")
                
                if submit_maintenance:
                    if not all_work:
                        st.error("⚠️ يرجى تحديد الأعمال المنجزة")
                    else:
                        # إنشاء سجل الصيانة
                        maintenance_record = {
                            "التاريخ": str(datetime.now().date()),
                            "الفني": user_now.get('username'),
                            "العمل": ", ".join(all_work),
                            "التكلفة": amount,
                            "طريقة الدفع": payment_method,
                            "ملاحظات": maintenance_notes
                        }
                        
                        # إضافة السجل للعميل
                        for i, c in enumerate(customers):
                            if c.get('id') == selected_customer.get('id'):
                                if 'history' not in customers[i]:
                                    customers[i]['history'] = []
                                customers[i]['history'].append(maintenance_record)
                                break
                        
                        if save_data(CUSTOMERS_FILE, customers):
                            st.success("✅ تم حفظ بيانات الصيانة بنجاح!")
                            
                            # عرض الباركود للعميل
                            st.info("يمكنك إرسال الباركود للعميل لمتابعة الصيانة:")
                            cust_url = get_customer_url(selected_customer.get('id'))
                            qr_encoded, _ = generate_qr_code(cust_url)
                            
                            if qr_encoded:
                                st.markdown(f"""
                                <div style="text-align: center; padding: 20px;">
                                    <img src="data:image/png;base64,{qr_encoded}" style="width: 180px; height: 180px;">
                                    <p style="margin: 10px 0; font-weight: bold; color: #28a745;">
                                        كود العميل: PL-{selected_customer.get('id'):04d}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error("❌ حدث خطأ أثناء حفظ البيانات")

# --- 4. أرباح الشركة ---
elif st.session_state.menu_choice == "profits":
    st.title("💰 أرباح وإيرادات الشركة")
    
    if not customers:
        st.info("📭 لا توجد بيانات مالية حتى الآن")
    else:
        # حساب الإحصائيات
        all_transactions = []
        total_income = 0
        technician_stats = {}
        monthly_income = {}
        
        for customer in customers:
            for transaction in customer.get('history', []):
                all_transactions.append({
                    "التاريخ": transaction.get('التاريخ', ''),
                    "العميل": customer.get('name', ''),
                    "الهاتف": customer.get('phone', ''),
                    "الفني": transaction.get('الفني', 'غير معروف'),
                    "الأعمال": transaction.get('العمل', ''),
                    "المبلغ": transaction.get('التكلفة', 0),
                    "طريقة الدفع": transaction.get('طريقة الدفع', 'نقدي')
                })
                
                total_income += transaction.get('التكلفة', 0)
                
                # إحصائيات الفنيين
                tech_name = transaction.get('الفني', 'غير معروف')
                if tech_name not in technician_stats:
                    technician_stats[tech_name] = {"income": 0, "transactions": 0}
                technician_stats[tech_name]["income"] += transaction.get('التكلفة', 0)
                technician_stats[tech_name]["transactions"] += 1
                
                # إحصائيات شهرية
                try:
                    date_str = transaction.get('التاريخ', '')
                    if date_str:
                        date = datetime.strptime(date_str, "%Y-%m-%d")
                        month_year = f"{date.year}-{date.month:02d}"
                        if month_year not in monthly_income:
                            monthly_income[month_year] = 0
                        monthly_income[month_year] += transaction.get('التكلفة', 0)
                except:
                    pass
        
        # عرض الإحصائيات الرئيسية
        st.subheader("📊 الإحصائيات العامة")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="stats-card">
                <h4>💰 إجمالي الدخل</h4>
                <h3>{total_income:,} ج.م</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stats-card">
                <h4>📋 عدد المعاملات</h4>
                <h3>{len(all_transactions)}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stats-card">
                <h4>👤 عدد العملاء</h4>
                <h3>{len(customers)}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="stats-card">
                <h4>👷 عدد الفنيين</h4>
                <h3>{len(technician_stats)}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # أرباح الفنيين
        if technician_stats:
            st.subheader("🎯 أرباح الفنيين")
            
            tech_df = pd.DataFrame([
                {"الفني": tech, "الدخل": stats["income"], "المعاملات": stats["transactions"]}
                for tech, stats in technician_stats.items()
            ]).sort_values("الدخل", ascending=False)
            
            col_chart, col_table = st.columns([2, 1])
            
            with col_chart:
                st.bar_chart(tech_df.set_index("الفني")["الدخل"], height=300)
            
            with col_table:
                st.dataframe(tech_df, use_container_width=True, hide_index=True)
        
        # الإيرادات الشهرية
        if monthly_income:
            st.subheader("📈 الإيرادات الشهرية")
            
            monthly_df = pd.DataFrame([
                {"الشهر": month, "الإيرادات": income}
                for month, income in sorted(monthly_income.items())
            ])
            
            if not monthly_df.empty:
                st.line_chart(monthly_df.set_index("الشهر")["الإيرادات"], height=300)
        
        # تفاصيل المعاملات
        if all_transactions:
            st.subheader("📋 تفاصيل جميع المعاملات")
            
            # فلترة حسب التاريخ
            date_filter = st.date_input("📅 فلترة حسب التاريخ", [])
            
            filtered_transactions = all_transactions
            if date_filter:
                if len(date_filter) == 2:
                    start_date, end_date = date_filter
                    filtered_transactions = [
                        t for t in all_transactions
                        if start_date <= datetime.strptime(t["التاريخ"], "%Y-%m-%d").date() <= end_date
                    ]
            
            if filtered_transactions:
                transactions_df = pd.DataFrame(filtered_transactions)
                
                # تصدير البيانات
                csv_data = transactions_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 تحميل كافة المعاملات (CSV)",
                    data=csv_data,
                    file_name="معاملات_powerlife.csv",
                    mime="text/csv"
                )
                
                st.dataframe(transactions_df.sort_values("التاريخ", ascending=False), use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد معاملات في الفترة المحددة")

# --- 5. إدارة الفنيين (للمدير فقط) ---
elif st.session_state.menu_choice == "manage_tech" and user_now.get('role') == 'admin':
    st.title("👤 إدارة الفنيين والمستخدمين")
    
    tab1, tab2, tab3 = st.tabs(["➕ إضافة فني جديد", "📋 قائمة الفنيين", "✏️ تعديل بيانات"])
    
    with tab1:
        st.subheader("إضافة فني أو مستخدم جديد")
        
        with st.form("add_technician_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("👤 الاسم الكامل *", placeholder="الاسم الثلاثي")
                username = st.text_input("📝 اسم المستخدم *", placeholder="اسم الدخول")
                phone = st.text_input("📱 رقم الهاتف", placeholder="رقم التواصل")
            
            with col2:
                password = st.text_input("🔒 كلمة المرور *", type="password", placeholder="أدخل كلمة مرور قوية")
                confirm_password = st.text_input("✅ تأكيد كلمة المرور *", type="password", placeholder="أعد إدخال كلمة المرور")
                role = st.selectbox("🎭 الدور الوظيفي", ["technician", "admin", "supervisor"])
            
            submit_tech = st.form_submit_button("💾 حفظ المستخدم الجديد", type="primary")
            
            if submit_tech:
                if not all([full_name, username, password, confirm_password]):
                    st.error("⚠️ يرجى ملء جميع الحقول الإلزامية (*)")
                elif password != confirm_password:
                    st.error("❌ كلمتا المرور غير متطابقتين")
                elif any(u.get('username') == username for u in users):
                    st.error("❌ اسم المستخدم موجود مسبقاً")
                else:
                    new_user = {
                        "username": username,
                        "password": hash_password(password),
                        "full_name": full_name,
                        "phone": phone,
                        "role": role,
                        "created_at": str(datetime.now().date()),
                        "created_by": user_now.get('username')
                    }
                    
                    users.append(new_user)
                    if save_data(USERS_FILE, users):
                        st.success(f"✅ تم إضافة {full_name} بنجاح!")
                    else:
                        st.error("❌ حدث خطأ أثناء حفظ البيانات")
    
    with tab2:
        st.subheader("قائمة الفنيين والمستخدمين")
        
        if users:
            # إنشاء DataFrame
            users_df = pd.DataFrame([
                {
                    "اسم المستخدم": u.get('username'),
                    "الاسم الكامل": u.get('full_name', ''),
                    "الدور": u.get('role'),
                    "الهاتف": u.get('phone', ''),
                    "تاريخ الإضافة": u.get('created_at', '')
                }
                for u in users
                if u.get('username') != 'admin'  # إخفاء المدير الرئيسي
            ])
            
            if not users_df.empty:
                st.dataframe(users_df, use_container_width=True, hide_index=True)
                
                # تصدير البيانات
                csv_users = users_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 تحميل قائمة المستخدمين",
                    data=csv_users,
                    file_name="مستخدمين_powerlife.csv",
                    mime="text/csv"
                )
            else:
                st.info("📭 لا يوجد مستخدمين مسجلين")
        else:
            st.info("📭 لا يوجد مستخدمين مسجلين")
    
    with tab3:
        st.subheader("تعديل بيانات المستخدمين")
        st.info("هذه الميزة قيد التطوير...")

# --- 6. التقارير (للمدير فقط) ---
elif st.session_state.menu_choice == "reports" and user_now.get('role') == 'admin':
    st.title("📊 التقارير والإحصائيات المتقدمة")
    
    if not customers:
        st.info("📭 لا توجد بيانات كافية للتحليل")
    else:
        # تحويل البيانات إلى DataFrame
        customers_df = pd.DataFrame(customers)
        
        tab1, tab2, tab3 = st.tabs(["📍 التوزيع الجغرافي", "⚙️ أنواع الأجهزة", "📈 العملاء الجدد"])
        
        with tab1:
            st.subheader("توزيع العملاء حسب المحافظة")
            
            if 'gov' in customers_df.columns:
                gov_dist = customers_df['gov'].value_counts()
                if not gov_dist.empty:
                    col_chart, col_table = st.columns([2, 1])
                    
                    with col_chart:
                        st.bar_chart(gov_dist, height=400)
                    
                    with col_table:
                        st.dataframe(gov_dist, use_container_width=True)
                else:
                    st.info("لا توجد بيانات جغرافية")
        
        with tab2:
            st.subheader("توزيع أنواع الأجهزة")
            
            if 'type' in customers_df.columns:
                type_dist = customers_df['type'].value_counts()
                if not type_dist.empty:
                    st.plotly_chart({
                        "data": [{
                            "values": type_dist.values.tolist(),
                            "labels": type_dist.index.tolist(),
                            "type": "pie",
                            "hole": 0.4,
                            "marker": {"colors": ["#28a745", "#20c997", "#17a2b8", "#ffc107"]}
                        }],
                        "layout": {
                            "title": "نسبة أنواع الأجهزة",
                            "height": 400
                        }
                    }, use_container_width=True)
                else:
                    st.info("لا توجد بيانات عن أنواع الأجهزة")
        
        with tab3:
            st.subheader("العملاء الجدد حسب الشهر")
            
            if 'created_at' in customers_df.columns:
                try:
                    customers_df['created_at'] = pd.to_datetime(customers_df['created_at'])
                    monthly_new = customers_df.set_index('created_at').resample('M').size()
                    
                    if not monthly_new.empty:
                        st.line_chart(monthly_new, height=400)
                        
                        # عرض البيانات
                        st.dataframe(pd.DataFrame({
                            "الشهر": monthly_new.index.strftime('%Y-%m'),
                            "عدد العملاء الجدد": monthly_new.values
                        }), use_container_width=True, hide_index=True)
                    else:
                        st.info("لا توجد بيانات زمنية كافية")
                except:
                    st.info("تنسيق التاريخ غير صحيح")

# --- 7. الإعدادات (للمدير فقط) ---
elif st.session_state.menu_choice == "settings" and user_now.get('role') == 'admin':
    st.title("⚙️ إعدادات النظام")
    
    st.subheader("معلومات النظام")
    st.info(f"""
    **إحصائيات النظام:**
    - عدد العملاء: {len(customers)}
    - عدد المستخدمين: {len(users)}
    - تاريخ التحديث الأخير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """)
    
    st.subheader("نسخ احتياطي للبيانات")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 نسخ احتياطي للعملاء", use_container_width=True):
            customers_json = json.dumps(customers, ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 تحميل ملف العملاء",
                data=customers_json,
                file_name=f"backup_customers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📥 نسخ احتياطي للمستخدمين", use_container_width=True):
            users_json = json.dumps(users, ensure_ascii=False, indent=2)
            st.download_button(
                label="💾 تحميل ملف المستخدمين",
                data=users_json,
                file_name=f"backup_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    st.subheader("استعادة البيانات")
    st.warning("⚠️ هذه العملية ستستبدل جميع البيانات الحالية. تأكد من وجود نسخة احتياطية.")
    
    backup_file = st.file_uploader("اختر ملف النسخ الاحتياطي", type=['json'])
    
    if backup_file and st.button("🔄 استعادة البيانات", type="primary"):
        try:
            data = json.load(backup_file)
            if 'customers' in str(backup_file.name):
                customers.clear()
                customers.extend(data)
                save_data(CUSTOMERS_FILE, customers)
                st.success("✅ تم استعادة بيانات العملاء بنجاح!")
            elif 'users' in str(backup_file.name):
                users.clear()
                users.extend(data)
                save_data(USERS_FILE, users)
                st.success("✅ تم استعادة بيانات المستخدمين بنجاح!")
        except Exception as e:
            st.error(f"❌ خطأ في استعادة البيانات: {str(e)}")

# --- 8. تسجيل الخروج ---
elif st.session_state.menu_choice == "logout":
    st.title("🚪 تسجيل الخروج")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.warning("هل أنت متأكد من تسجيل الخروج؟")
        
        col_yes, col_no = st.columns(2)
        
        with col_yes:
            if st.button("✅ نعم، سجل خروج", use_container_width=True, type="primary"):
                st.session_state.logged_in = False
                st.session_state.current_user = None
                st.session_state.menu_choice = "📋 قائمة العملاء"
                st.success("✅ تم تسجيل الخروج بنجاح!")
                st.rerun()
        
        with col_no:
            if st.button("❌ لا، إلغاء", use_container_width=True):
                st.session_state.menu_choice = "customers_list"
                st.rerun()

# --- 9. البحث والتعديل ---
elif st.session_state.menu_choice == "search_edit":
    st.title("🔍 بحث وتعديل بيانات العملاء")
    
    if not customers:
        st.info("📭 لا يوجد عملاء مسجلين")
    else:
        # شريط البحث المتقدم
        search_col1, search_col2 = st.columns([3, 1])
        
        with search_col1:
            search_query = st.text_input("أدخل كلمة البحث", placeholder="ابحث بالاسم، الهاتف، العنوان، نوع الجهاز...")
        
        with search_col2:
            search_type = st.selectbox("نوع البحث", ["جميع الحقول", "الاسم فقط", "الهاتف فقط", "العنوان فقط"])
        
        # تطبيق البحث
        if search_query:
            if search_type == "الاسم فقط":
                filtered = [c for c in customers if search_query.lower() in c.get('name', '').lower()]
            elif search_type == "الهاتف فقط":
                filtered = [c for c in customers if search_query in c.get('phone', '')]
            elif search_type == "العنوان فقط":
                filtered = [c for c in customers if (
                    search_query.lower() in c.get('gov', '').lower() or
                    search_query.lower() in c.get('village', '').lower()
                )]
            else:  # جميع الحقول
                filtered = [c for c in customers if (
                    search_query.lower() in c.get('name', '').lower() or
                    search_query in c.get('phone', '') or
                    search_query.lower() in c.get('gov', '').lower() or
                    search_query.lower() in c.get('village', '').lower() or
                    search_query.lower() in c.get('type', '').lower()
                )]
        else:
            filtered = customers
        
        if not filtered:
            st.warning("⚠️ لا توجد نتائج للبحث")
        else:
            st.success(f"✅ تم العثور على {len(filtered)} عميل")
            
            # عرض النتائج
            for customer in filtered:
                with st.expander(f"👤 {customer.get('name', '')} - 📱 {customer.get('phone', '')}", expanded=False):
                    # عرض معلومات العميل
                    col_info, col_actions = st.columns([3, 1])
                    
                    with col_info:
                        st.markdown(f"""
                        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px;">
                            <p><strong>🆔 رقم العميل:</strong> PL-{customer.get('id', 0):04d}</p>
                            <p><strong>📍 العنوان:</strong> {customer.get('gov', '')} - {customer.get('village', '')}</p>
                            <p><strong>⚙️ نوع الجهاز:</strong> {customer.get('type', '')}</p>
                            <p><strong>📅 تاريخ التسجيل:</strong> {customer.get('created_at', '')}</p>
                            <p><strong>📝 ملاحظات:</strong> {customer.get('notes', 'لا توجد')}</p>
                            <p><strong>🛠️ عدد زيارات الصيانة:</strong> {len(customer.get('history', []))}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_actions:
                        # أزرار الإجراءات
                        if st.button("✏️ تعديل", key=f"edit_{customer.get('id')}", use_container_width=True):
                            st.session_state.editing_customer = customer.get('id')
                            st.rerun()
                        
                        if st.button("🗑️ حذف", key=f"delete_{customer.get('id')}", use_container_width=True, type="secondary"):
                            st.warning("⚠️ هذه العملية لا يمكن التراجع عنها!")
                            confirm = st.checkbox(f"تأكيد حذف {customer.get('name')}", key=f"confirm_{customer.get('id')}")
                            if confirm:
                                customers[:] = [c for c in customers if c.get('id') != customer.get('id')]
                                if save_data(CUSTOMERS_FILE, customers):
                                    st.success("✅ تم حذف العميل بنجاح!")
                                    st.rerun()
                        
                        # عرض الباركود
                        if st.button("🎫 باركود", key=f"qrcode_{customer.get('id')}", use_container_width=True):
                            cust_url = get_customer_url(customer.get('id'))
                            qr_encoded, _ = generate_qr_code(cust_url)
                            if qr_encoded:
                                st.markdown(f"""
                                <div style="text-align: center; margin: 15px 0;">
                                    <img src="data:image/png;base64,{qr_encoded}" style="width: 150px; height: 150px;">
                                    <p style="font-size: 12px; margin: 5px 0;">PL-{customer.get('id'):04d}</p>
                                </div>
                                """, unsafe_allow_html=True)
            
            # التعديل (إذا تم اختيار عميل للتعديل)
            if 'editing_customer' in st.session_state:
                customer_to_edit = next((c for c in customers if c.get('id') == st.session_state.editing_customer), None)
                
                if customer_to_edit:
                    st.markdown("---")
                    st.subheader(f"✏️ تعديل بيانات العميل: {customer_to_edit.get('name')}")
                    
                    with st.form("edit_customer_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edited_name = st.text_input("👤 اسم العميل", value=customer_to_edit.get('name', ''))
                            edited_phone = st.text_input("📱 رقم الهاتف", value=customer_to_edit.get('phone', ''))
                            edited_gov = st.selectbox(
                                "📍 المحافظة",
                                ["القاهرة", "الجيزة", "المنوفية", "الغربية", "القليوبية", "الشرقية", "الدقهلية", "أخرى"],
                                index=["القاهرة", "الجيزة", "المنوفية", "الغربية", "القليوبية", "الشرقية", "الدقهلية", "أخرى"].index(customer_to_edit.get('gov', 'القاهرة'))
                            )
                        
                        with col2:
                            edited_village = st.text_input("🏘️ القرية/المركز", value=customer_to_edit.get('village', ''))
                            edited_type = st.selectbox(
                                "⚙️ نوع الجهاز",
                                ["7 مراحل", "5 مراحل", "جامبو", "فلتر عادي", "رو اوسموسيس"],
                                index=["7 مراحل", "5 مراحل", "جامبو", "فلتر عادي", "رو اوسموسيس"].index(customer_to_edit.get('type', '7 مراحل'))
                            )
                            edited_notes = st.text_area("📝 ملاحظات", value=customer_to_edit.get('notes', ''))
                        
                        col_save, col_cancel = st.columns(2)
                        
                        with col_save:
                            save_edit = st.form_submit_button("💾 حفظ التعديلات", type="primary")
                        
                        with col_cancel:
                            cancel_edit = st.form_submit_button("❌ إلغاء", type="secondary")
                        
                        if save_edit:
                            if not edited_name or not edited_phone:
                                st.error("⚠️ يرجى ملء الحقول الإلزامية")
                            else:
                                # تحديث بيانات العميل
                                for i, c in enumerate(customers):
                                    if c.get('id') == customer_to_edit.get('id'):
                                        customers[i].update({
                                            "name": edited_name,
                                            "phone": edited_phone,
                                            "gov": edited_gov,
                                            "village": edited_village,
                                            "type": edited_type,
                                            "notes": edited_notes
                                        })
                                        break
                                
                                if save_data(CUSTOMERS_FILE, customers):
                                    st.success("✅ تم تحديث بيانات العميل بنجاح!")
                                    del st.session_state.editing_customer
                                    st.rerun()
                        
                        if cancel_edit:
                            del st.session_state.editing_customer
                            st.rerun()

# ================== 10. تذييل الصفحة ==================

st.markdown("---")
st.markdown("""
<div style="
    text-align: center;
    color: #666;
    font-size: 14px;
    padding: 20px;
">
    <p>💧 <strong>Power Life CRM Ultra</strong> - نظام إدارة عملاء متكامل</p>
    <p>📞 للدعم الفني: 01234567890 | ✉️ البريد الإلكتروني: support@powerlife.com</p>
    <p>© 2024 جميع الحقوق محفوظة</p>
</div>
""", unsafe_allow_html=True)
