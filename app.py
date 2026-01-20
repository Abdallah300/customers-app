import streamlit as st
import json
import os
import hashlib
from datetime import datetime, timedelta
import pandas as pd
import uuid
import qrcode
from io import BytesIO
import base64
import random

# ================== 1. نظام الشركات المتعددة ==================
class FilterProGlobalSystem:
    def __init__(self):
        self.init_system()
    
    def init_system(self):
        """تهيئة النظام"""
        os.makedirs("global_data/companies", exist_ok=True)
        os.makedirs("global_data/invoices", exist_ok=True)
        os.makedirs("global_data/backups", exist_ok=True)
        
        if not os.path.exists("global_data/master.json"):
            master_data = {
                "total_companies": 0,
                "total_invoices": 0,
                "total_revenue": 0,
                "subscription_plans": {
                    "basic": {"price": 199, "features": ["100 عميل", "3 فنيين", "تقارير أساسية"]},
                    "pro": {"price": 499, "features": ["500 عميل", "10 فنيين", "GPS تتبع", "فواتير متقدمة"]},
                    "enterprise": {"price": 999, "features": ["غير محدود", "كل المميزات", "دعم فني 24/7"]}
                },
                "monthly_features": {}  # المميزات الشهرية
            }
            self.save_master_data(master_data)
    
    def create_company(self, company_data):
        """إنشاء شركة جديدة"""
        company_id = f"FILTER_{random.randint(10000, 99999)}"
        company_path = f"global_data/companies/{company_id}"
        os.makedirs(company_path, exist_ok=True)
        
        # بيانات الشركة الأساسية
        company_info = {
            "id": company_id,
            "name": company_data["company_name"],
            "email": company_data["email"],
            "phone": company_data["phone"],
            "subscription_plan": company_data["plan"],
            "subscription_date": str(datetime.now()),
            "monthly_features": [],  # المميزات الشهرية المشتركة
            "status": "active",
            "balance": 0.0
        }
        
        # إنشاء الملفات الأساسية
        files_to_create = {
            "info.json": company_info,
            "users.json": [{
                "id": 1,
                "username": company_data["admin_username"],
                "password": self.hash_password(company_data["admin_password"]),
                "name": company_data["admin_name"],
                "role": "company_admin",
                "permissions": ["all"],
                "created_at": str(datetime.now())
            }],
            "customers.json": [],
            "technicians.json": [],
            "inventory.json": [],
            "invoices.json": [],
            "gps_tracking.json": [],
            "warehouses.json": [{
                "id": 1,
                "name": "المخزن الرئيسي",
                "location": company_data.get("address", ""),
                "manager_id": 1,
                "items": []
            }],
            "settings.json": {
                "invoice_template": "professional_arabic",
                "gps_tracking": True,
                "auto_backup": True,
                "monthly_features_enabled": True
            }
        }
        
        for filename, data in files_to_create.items():
            self.save_file(f"{company_path}/{filename}", data)
        
        # تحديث بيانات النظام الرئيسي
        master = self.load_master_data()
        master["total_companies"] += 1
        self.save_master_data(master)
        
        return company_id
    
    def create_invoice(self, company_id, invoice_data):
        """إنشاء فاتورة متقدمة"""
        invoices = self.load_company_file(company_id, "invoices.json")
        invoice_id = f"INV-{company_id}-{len(invoices)+1:06d}"
        
        professional_invoice = {
            "id": invoice_id,
            "invoice_number": invoice_id,
            "date": str(datetime.now()),
            "customer": invoice_data["customer"],
            "items": invoice_data["items"],
            "subtotal": invoice_data["subtotal"],
            "tax": invoice_data.get("tax", 0),
            "discount": invoice_data.get("discount", 0),
            "total": invoice_data["total"],
            "paid": 0,
            "due": invoice_data["total"],
            "status": "غير مدفوع",
            "payment_method": "",
            "notes": invoice_data.get("notes", ""),
            "qr_code": self.generate_invoice_qr(invoice_id, invoice_data["total"]),
            "template": "premium_arabic",
            "watermark": company_id
        }
        
        invoices.append(professional_invoice)
        self.save_company_file(company_id, "invoices.json", invoices)
        
        # تحديث الإحصائيات
        master = self.load_master_data()
        master["total_invoices"] += 1
        master["total_revenue"] += invoice_data["total"]
        self.save_master_data(master)
        
        return professional_invoice
    
    def gps_tracking(self, company_id, technician_id, location):
        """تحديث موقع الفني عبر GPS"""
        tracking_data = self.load_company_file(company_id, "gps_tracking.json")
        
        location_entry = {
            "technician_id": technician_id,
            "latitude": location["lat"],
            "longitude": location["lng"],
            "timestamp": str(datetime.now()),
            "speed": location.get("speed", 0),
            "accuracy": location.get("accuracy", 0),
            "address": location.get("address", "")
        }
        
        tracking_data.append(location_entry)
        self.save_company_file(company_id, "gps_tracking.json", tracking_data)
        
        # حفظ آخر موقع
        technicians = self.load_company_file(company_id, "technicians.json")
        for tech in technicians:
            if tech["id"] == technician_id:
                tech["last_location"] = location_entry
                tech["last_update"] = str(datetime.now())
                break
        
        self.save_company_file(company_id, "technicians.json", technicians)
    
    def warehouse_management(self, company_id, warehouse_data):
        """إدارة المخازن"""
        warehouses = self.load_company_file(company_id, "warehouses.json")
        
        if warehouse_data["action"] == "add_item":
            for wh in warehouses:
                if wh["id"] == warehouse_data["warehouse_id"]:
                    if "items" not in wh:
                        wh["items"] = []
                    
                    wh["items"].append({
                        "id": len(wh["items"]) + 1,
                        "name": warehouse_data["item_name"],
                        "quantity": warehouse_data["quantity"],
                        "min_stock": warehouse_data.get("min_stock", 10),
                        "last_updated": str(datetime.now()),
                        "updated_by": warehouse_data["user_id"]
                    })
                    break
        
        elif warehouse_data["action"] == "transfer":
            # نقل بين المخازن
            pass
        
        self.save_company_file(company_id, "warehouses.json", warehouses)
    
    def add_monthly_feature(self, company_id, feature_name):
        """إضافة ميزة شهرية للشركة"""
        company_info = self.load_company_file(company_id, "info.json")
        
        if "monthly_features" not in company_info:
            company_info["monthly_features"] = []
        
        if feature_name not in company_info["monthly_features"]:
            company_info["monthly_features"].append(feature_name)
            self.save_company_file(company_id, "info.json", company_info)
            
            # إضافة للتاريخ
            feature_log = {
                "company_id": company_id,
                "feature": feature_name,
                "added_date": str(datetime.now()),
                "active_until": str(datetime.now() + timedelta(days=30))
            }
            
            master = self.load_master_data()
            if "monthly_features" not in master:
                master["monthly_features"] = []
            master["monthly_features"].append(feature_log)
            self.save_master_data(master)
    
    # ========== دوال مساعدة ==========
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_master_data(self):
        with open("global_data/master.json", "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_master_data(self, data):
        with open("global_data/master.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_company_file(self, company_id, filename):
        path = f"global_data/companies/{company_id}/{filename}"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def save_company_file(self, company_id, filename, data):
        path = f"global_data/companies/{company_id}/{filename}"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_file(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_invoice_qr(self, invoice_id, amount):
        """إنشاء QR Code للفاتورة"""
        qr_data = f"INVOICE:{invoice_id}:AMOUNT:{amount}:DATE:{datetime.now()}"
        qr = qrcode.make(qr_data)
        
        buffered = BytesIO()
        qr.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

# ================== 2. واجهة النظام العالمية ==================
def global_dashboard():
    """لوحة التحكم العالمية"""
    st.set_page_config(page_title="FilterPro Global", layout="wide")
    
    st.markdown("""
    <style>
    .global-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
        color: white;
        text-align: center;
    }
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        margin: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: transform 0.3s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .stat-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # رأس الصفحة
    st.markdown("""
    <div class='global-header'>
        <h1>🌍 FilterPro Global System</h1>
        <p>النظام العالمي المتكامل لإدارة شركات الفلاتر</p>
    </div>
    """, unsafe_allow_html=True)
    
    # إحصائيات سريعة
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class='stat-card'>
            <h3>🏢 الشركات</h3>
            <h2>1,247</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='stat-card'>
            <h3>💰 الإيرادات</h3>
            <h2>4.2M ج.م</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class='stat-card'>
            <h3>📊 الفواتير</h3>
            <h2>45,821</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class='stat-card'>
            <h3>👥 الفنيين</h3>
            <h2>8,542</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # عرض المميزات
    st.subheader("🚀 المميزات العالمية المتوفرة")
    
    features_col1, features_col2 = st.columns(2)
    
    with features_col1:
        # نظام الفواتير العالمي
        st.markdown("""
        <div class='feature-card'>
            <h3>🧾 نظام الفواتير المتقدم</h3>
            <ul>
                <li>تصميم فواتير عربية احترافية</li>
                <li>QR Code لكل فاتورة</li>
                <li>توقيع إلكتروني</li>
                <li>شعار الشركة تلقائي</li>
                <li>نسخ PDF وطباعة</li>
                <li>فواتير ضريبية متوافقة</li>
                <li>إشعارات الدفع الآلي</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # نظام GPS
        st.markdown("""
        <div class='feature-card'>
            <h3>📍 نظام تتبع الفنيين GPS</h3>
            <ul>
                <li>تتبع حي مباشر للفنيين</li>
                <li>خرائط تفاعلية</li>
                <li>تقرير المسارات اليومية</li>
                <li>تنبيهات تأخير</li>
                <li>تحديد أقرب فني للعميل</li>
                <li>متابعة وقت الخدمة</li>
                <li>تقرير كفاءة الفنيين</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with features_col2:
        # نظام المخازن
        st.markdown("""
        <div class='feature-card'>
            <h3>📦 نظام المخازن الذكي</h3>
            <ul>
                <li>مخازن متعددة وفروع</li>
                <li>باركود للمنتجات</li>
                <li>تنبيهات نفاذ المخزون</li>
                <li>مراقبة أمين المخزن</li>
                <li>تحويل بين المخازن</li>
                <li>جرد دوري آلي</li>
                <li>تقارير حركة المخزون</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # المميزات الشهرية
        st.markdown("""
        <div class='feature-card'>
            <h3>🎁 مميزات شهرية جديدة</h3>
            <ul>
                <li><strong>يناير:</strong> تقارير ذكاء اصطناعي</li>
                <li><strong>فبراير:</strong> محفظة دفع إلكتروني</li>
                <li><strong>مارس:</strong> تطبيق جوال للعملاء</li>
                <li><strong>أبريل:</strong> تكامل مع منصات التسويق</li>
                <li><strong>مايو:</strong> نظام الولاء والعروض</li>
                <li><strong>يونيو:</strong> محادثات روبوت ذكي</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # خطة الأسعار
    st.subheader("💳 خطط الاشتراك الشهرية")
    
    plans_col1, plans_col2, plans_col3 = st.columns(3)
    
    with plans_col1:
        st.markdown("""
        <div style='padding:20px; border:2px solid #4CAF50; border-radius:15px;'>
            <h3>🟢 الأساسية</h3>
            <h2>199 ج.م/شهر</h2>
            <ul>
                <li>✓ 100 عميل</li>
                <li>✓ 3 فنيين</li>
                <li>✓ فواتير أساسية</li>
                <li>✓ تقارير مالية</li>
                <li>✗ GPS تتبع</li>
                <li>✗ مميزات شهرية</li>
            </ul>
            <button style='width:100%; padding:10px; background:#4CAF50; color:white; border:none; border-radius:5px;'>
                اشترك الآن
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    with plans_col2:
        st.markdown("""
        <div style='padding:20px; border:2px solid #2196F3; border-radius:15px; background:#f0f8ff;'>
            <h3>🔵 المحترف</h3>
            <h2>499 ج.م/شهر</h2>
            <ul>
                <li>✓ 500 عميل</li>
                <li>✓ 10 فنيين</li>
                <li>✓ فواتير متقدمة</li>
                <li>✓ GPS تتبع كامل</li>
                <li>✓ نظام المخازن</li>
                <li>✓ 3 مميزات شهرية</li>
            </ul>
            <button style='width:100%; padding:10px; background:#2196F3; color:white; border:none; border-radius:5px;'>
                اشترك الآن
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    with plans_col3:
        st.markdown("""
        <div style='padding:20px; border:2px solid #FF9800; border-radius:15px; background:#fff3e0;'>
            <h3>🟣 المؤسسة</h3>
            <h2>999 ج.م/شهر</h2>
            <ul>
                <li>✓ عملاء غير محدود</li>
                <li>✓ فنيين غير محدود</li>
                <li>✓ كل المميزات</li>
                <li>✓ مميزات شهرية كاملة</li>
                <li>✓ دعم فني 24/7</li>
                <li>✓ تدريب فريقك</li>
            </ul>
            <button style='width:100%; padding:10px; background:#FF9800; color:white; border:none; border-radius:5px;'>
                اشترك الآن
            </button>
        </div>
        """, unsafe_allow_html=True)

# ================== 3. صفحة تسجيل شركة جديدة ==================
def company_registration_page():
    st.title("🏢 سجل شركتك الآن")
    
    with st.form("new_company_form"):
        # معلومات الشركة
        st.header("معلومات الشركة")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input("اسم الشركة *", placeholder="شركة فلاتر النقاء")
            company_email = st.text_input("البريد الإلكتروني *", placeholder="info@company.com")
            company_phone = st.text_input("الهاتف *", placeholder="01001234567")
        
        with col2:
            company_address = st.text_area("عنوان الشركة", placeholder="المدينة، الحي، الشارع")
            company_type = st.selectbox("نشاط الشركة", 
                ["فلاتر مياه", "فلاتر هواء", "فلاتر زيت", "فلاتر وقود", "جميع الأنواع"])
            num_technicians = st.number_input("عدد الفنيين الحالي", min_value=1, max_value=100, value=3)
        
        # خطة الاشتراك
        st.header("خطة الاشتراك")
        
        plan = st.radio("اختر خطتك:", 
            ["الأساسية (199 ج.م/شهر)", "المحترف (499 ج.م/شهر)", "المؤسسة (999 ج.م/شهر)"],
            horizontal=True)
        
        # بيانات المدير
        st.header("بيانات المدير المسؤول")
        
        col3, col4 = st.columns(2)
        with col3:
            admin_name = st.text_input("اسم المدير *", placeholder="محمد أحمد")
            admin_username = st.text_input("اسم المستخدم *", placeholder="mohamed_admin")
        
        with col4:
            admin_password = st.text_input("كلمة المرور *", type="password")
            confirm_password = st.text_input("تأكيد كلمة المرور *", type="password")
        
        # الموافقة
        agree = st.checkbox("أوافق على شروط الاستخدام *")
        
        if st.form_submit_button("🏢 إنشاء شركتي", use_container_width=True):
            if admin_password == confirm_password and agree:
                # إنشاء الشركة
                system = FilterProGlobalSystem()
                
                company_data = {
                    "company_name": company_name,
                    "email": company_email,
                    "phone": company_phone,
                    "address": company_address,
                    "type": company_type,
                    "plan": plan.split(" ")[0],
                    "admin_name": admin_name,
                    "admin_username": admin_username,
                    "admin_password": admin_password
                }
                
                company_id = system.create_company(company_data)
                
                st.success(f"""
                ## ✅ تم إنشاء شركتك بنجاح!
                
                **رقم الشركة:** `{company_id}`
                **اسم المستخدم:** `{admin_username}`
                **كلمة المرور:** `{admin_password}`
                
                ### 🎁 المميزات المتاحة الآن:
                1. نظام الفواتير المتقدم
                2. إدارة الفنيين
                3. النظام المالي
                4. لوحة تحكم متكاملة
                
                ### 📋 الخطوات التالية:
                1. سجل الدخول الآن
                2. أضف فنييك
                3. أضف عملائك
                4. ابدأ بإصدار الفواتير
                """)
                
                # زر الدخول المباشر
                if st.button("🚀 دخول مباشر إلى لوحة تحكم شركتي", type="primary"):
                    st.session_state.company_id = company_id
                    st.session_state.username = admin_username
                    st.rerun()

# ================== 4. لوحة تحكم الشركة ==================
def company_dashboard(company_id, username):
    """لوحة تحكم الشركة"""
    
    # تحميل بيانات الشركة
    system = FilterProGlobalSystem()
    company_info = system.load_company_file(company_id, "info.json")
    user_info = None
    
    users = system.load_company_file(company_id, "users.json")
    for user in users:
        if user["username"] == username:
            user_info = user
            break
    
    if not user_info:
        st.error("خطأ في المصادقة")
        return
    
    # رأس لوحة التحكم
    st.markdown(f"""
    <div style='background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding:30px; border-radius:20px; color:white;'>
        <h1>🏢 {company_info['name']}</h1>
        <p>👤 {user_info['name']} | {user_info['role']} | الخطة: {company_info['subscription_plan']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # القائمة الجانبية
    with st.sidebar:
        st.title("📋 القائمة")
        
        menu = st.radio("الخيارات:", [
            "📊 لوحة التحكم",
            "👥 العملاء", 
            "🛠️ الفنيين",
            "🧾 الفواتير",
            "📍 تتبع GPS",
            "📦 المخازن",
            "💰 المحاسبة",
            "⚙️ الإعدادات"
        ])
        
        st.divider()
        
        # إنشاء حسابات جديدة (للمدير فقط)
        if user_info["role"] == "company_admin":
            st.subheader("➕ إنشاء حسابات")
            
            new_user_type = st.selectbox("نوع الحساب:", ["فني", "محاسب", "مدير مخزن", "مدير مبيعات"])
            new_username = st.text_input("اسم المستخدم")
            new_password = st.text_input("كلمة المرور", type="password")
            
            if st.button("إنشاء حساب"):
                new_user = {
                    "username": new_username,
                    "password": system.hash_password(new_password),
                    "name": f"موظف جديد",
                    "role": new_user_type,
                    "permissions": [],
                    "created_at": str(datetime.now()),
                    "created_by": username
                }
                system.create_user_in_company(company_id, new_user)
                st.success(f"تم إنشاء حساب {new_user_type}")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج"):
            del st.session_state.company_id
            st.rerun()
    
    # المحتوى الرئيسي
    if menu == "📊 لوحة التحكم":
        show_company_overview(company_id, system)
    elif menu == "🧾 الفواتير":
        show_invoices_system(company_id, system)
    elif menu == "📍 تتبع GPS":
        show_gps_tracking(company_id, system)
    elif menu == "📦 المخازن":
        show_warehouse_system(company_id, system)

def show_invoices_system(company_id, system):
    """نظام الفواتير المتقدم"""
    st.title("🧾 نظام الفواتير العالمي")
    
    # إنشاء فاتورة جديدة
    with st.expander("➕ إنشاء فاتورة جديدة", expanded=True):
        with st.form("create_invoice_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_name = st.text_input("اسم العميل")
                customer_phone = st.text_input("هاتف العميل")
                customer_address = st.text_input("عنوان العميل")
            
            with col2:
                invoice_date = st.date_input("تاريخ الفاتورة", datetime.now())
                due_date = st.date_input("تاريخ الاستحقاق", datetime.now() + timedelta(days=30))
                payment_method = st.selectbox("طريقة الدفع", ["نقدي", "تحويل بنكي", "بطاقة ائتمان", "أقساط"])
            
            # إضافة الأصناف
            st.subheader("🛒 الأصناف")
            
            items = []
            for i in range(3):
                col_i1, col_i2, col_i3, col_i4 = st.columns([3, 1, 1, 1])
                with col_i1:
                    item_name = st.text_input(f"اسم الصنف {i+1}", placeholder="فلتر مياه 3 مراحل")
                with col_i2:
                    quantity = st.number_input(f"الكمية {i+1}", min_value=1, value=1)
                with col_i3:
                    price = st.number_input(f"السعر {i+1}", min_value=0.0, value=0.0)
                with col_i4:
                    total = quantity * price
                    st.text(f"الإجمالي: {total:,.2f}")
                
                if item_name:
                    items.append({
                        "name": item_name,
                        "quantity": quantity,
                        "price": price,
                        "total": total
                    })
            
            # الحسابات النهائية
            subtotal = sum(item["total"] for item in items)
            tax = st.number_input("الضريبة (%)", min_value=0.0, max_value=100.0, value=14.0)
            discount = st.number_input("الخصم", min_value=0.0, value=0.0)
            
            tax_amount = subtotal * (tax / 100)
            total_amount = subtotal + tax_amount - discount
            
            st.markdown(f"""
            <div style='background:#f0f8ff; padding:20px; border-radius:10px;'>
                <h4>🧮 الإجماليات:</h4>
                <p>المجموع الجزئي: {subtotal:,.2f} ج.م</p>
                <p>الضريبة ({tax}%): {tax_amount:,.2f} ج.م</p>
                <p>الخصم: {discount:,.2f} ج.م</p>
                <h3>المبلغ الإجمالي: {total_amount:,.2f} ج.م</h3>
            </div>
            """, unsafe_allow_html=True)
            
            notes = st.text_area("ملاحظات الفاتورة")
            
            if st.form_submit_button("💾 إنشاء الفاتورة"):
                invoice_data = {
                    "customer": {
                        "name": customer_name,
                        "phone": customer_phone,
                        "address": customer_address
                    },
                    "items": items,
                    "subtotal": subtotal,
                    "tax": tax_amount,
                    "discount": discount,
                    "total": total_amount,
                    "notes": notes
                }
                
                invoice = system.create_invoice(company_id, invoice_data)
                
                # عرض الفاتورة المنشأة
                st.success("✅ تم إنشاء الفاتورة بنجاح!")
                
                col_preview1, col_preview2 = st.columns(2)
                with col_preview1:
                    st.markdown("### معاينة الفاتورة")
                    st.json(invoice)
                
                with col_preview2:
                    st.markdown("### QR Code الفاتورة")
                    st.image(f"data:image/png;base64,{invoice['qr_code']}", width=200)
                    
                    # خيارات التصدير
                    st.download_button("📥 تحميل كـ PDF", data="PDF_CONTENT", file_name=f"{invoice['id']}.pdf")
                    st.button("🖨️ طباعة الفاتورة")
                    st.button("📧 إرسال للعميل")

def show_gps_tracking(company_id, system):
    """نظام تتبع الفنيين GPS"""
    st.title("📍 نظام تتبع الفنيين GPS")
    
    # خريطة افتراضية
    st.markdown("""
    <div style='background:#e8f4f8; padding:20px; border-radius:10px; text-align:center;'>
        <h3>🌍 خريطة تتبع الفنيين</h3>
        <p>🚗 عرض مباشر لمواقع الفنيين على الخريطة</p>
        <div style='background:white; height:400px; border:2px solid #ddd; border-radius:10px; display:flex; align-items:center; justify-content:center;'>
            <h4 style='color:#666;'>خريطة تفاعلية - تتطلب تكامل مع Google Maps API</h4>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # قائمة الفنيين وأماكنهم
    technicians = system.load_company_file(company_id, "technicians.json")
    
    if technicians:
        st.subheader("👨‍🔧 مواقع الفنيين الحالية")
        
        for tech in technicians:
            if "last_location" in tech:
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.write(f"**{tech['name']}**")
                    st.write(f"📱 {tech.get('phone', '')}")
                with col2:
                    loc = tech["last_location"]
                    st.write(f"📍 {loc.get('address', 'موقع غير معروف')}")
                    st.write(f"🕐 {loc['timestamp']}")
                with col3:
                    status_color = {"active": "🟢", "busy": "🟡", "offline": "🔴"}.get(tech.get("status", "active"), "⚪")
                    st.write(f"{status_color} {tech.get('status', 'نشط')}")
                    
                    if st.button("📞 اتصل", key=f"call_{tech['id']}"):
                        st.info(f"الاتصال بـ {tech['name']}: {tech.get('phone', '')}")
    
    # إضافة فني جديد
    with st.expander("➕ إضافة فني جديد للتتبع"):
        with st.form("add_technician_form"):
            col1, col2 = st.columns(2)
            with col1:
                tech_name = st.text_input("اسم الفني")
                tech_phone = st.text_input("هاتف الفني")
            with col2:
                tech_car = st.text_input("رقم السيارة", placeholder="أ ب ج 1234")
                tech_area = st.selectbox("المنطقة", ["القاهرة", "الجيزة", "الإسكندرية", "الدقهلية"])
            
            if st.form_submit_button("➕ إضافة فني"):
                new_tech = {
                    "id": len(technicians) + 1,
                    "name": tech_name,
                    "phone": tech_phone,
                    "car_number": tech_car,
                    "area": tech_area,
                    "status": "active",
                    "created_at": str(datetime.now())
                }
                technicians.append(new_tech)
                system.save_company_file(company_id, "technicians.json", technicians)
                st.success(f"تم إضافة الفني {tech_name}")

def show_warehouse_system(company_id, system):
    """نظام إدارة المخازن"""
    st.title("📦 نظام إدارة المخازن الذكي")
    
    warehouses = system.load_company_file(company_id, "warehouses.json")
    
    # إنشاء مخزن جديد
    with st.expander("🏗️ إنشاء مخزن جديد"):
        with st.form("new_warehouse_form"):
            wh_name = st.text_input("اسم المخزن")
            wh_location = st.text_input("موقع المخزن")
            wh_manager = st.text_input("اسم أمين المخزن")
            
            if st.form_submit_button("➕ إنشاء مخزن"):
                new_warehouse = {
                    "id": len(warehouses) + 1,
                    "name": wh_name,
                    "location": wh_location,
                    "manager": wh_manager,
                    "items": [],
                    "created_at": str(datetime.now())
                }
                warehouses.append(new_warehouse)
                system.save_company_file(company_id, "warehouses.json", warehouses)
                st.success(f"تم إنشاء مخزن {wh_name}")
    
    # عرض المخازن
    st.subheader("📊 المخازن المتاحة")
    
    for wh in warehouses:
        with st.expander(f"📦 {wh['name']} - {wh['location']}", expanded=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**أمين المخزن:** {wh.get('manager', 'غير محدد')}")
                st.write(f"**عدد الأصناف:** {len(wh.get('items', []))}")
                
                # إضافة صنف جديد
                with st.form(f"add_item_{wh['id']}"):
                    item_name = st.text_input("اسم الصنف", key=f"item_name_{wh['id']}")
                    item_qty = st.number_input("الكمية", min_value=1, value=1, key=f"item_qty_{wh['id']}")
                    min_stock = st.number_input("الحد الأدنى", min_value=1, value=10, key=f"min_stock_{wh['id']}")
                    
                    if st.form_submit_button("➕ إضافة صنف"):
                        warehouse_data = {
                            "action": "add_item",
                            "warehouse_id": wh["id"],
                            "item_name": item_name,
                            "quantity": item_qty,
                            "min_stock": min_stock,
                            "user_id": "current_user"
                        }
                        system.warehouse_management(company_id, warehouse_data)
                        st.rerun()
            
            with col2:
                # تقرير المخزون
                if wh.get("items"):
                    df = pd.DataFrame(wh["items"])
                    st.dataframe(df[["name", "quantity", "min_stock"]], use_container_width=True)
                else:
                    st.info("لا توجد أصناف في هذا المخزن")
    
    # تنبيهات المخزون المنخفض
    st.subheader("⚠️ تنبيهات المخزون المنخفض")
    
    low_stock_items = []
    for wh in warehouses:
        for item in wh.get("items", []):
            if item.get("quantity", 0) < item.get("min_stock", 10):
                low_stock_items.append({
                    "المخزن": wh["name"],
                    "الصنف": item["name"],
                    "الكمية": item["quantity"],
                    "الحد الأدنى": item.get("min_stock", 10)
                })
    
    if low_stock_items:
        st.dataframe(pd.DataFrame(low_stock_items), use_container_width=True)
    else:
        st.success("🎉 جميع الأصناف في المستوى الآمن")

def show_company_overview(company_id, system):
    """نظرة عامة على الشركة"""
    
    # تحميل البيانات
    invoices = system.load_company_file(company_id, "invoices.json")
    customers = system.load_company_file(company_id, "customers.json")
    technicians = system.load_company_file(company_id, "technicians.json")
    
    # الإحصائيات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_invoices = len(invoices)
        paid_invoices = len([i for i in invoices if i.get("status") == "مدفوع"])
        st.metric("الفواتير", f"{total_invoices}", f"{paid_invoices} مدفوعة")
    
    with col2:
        total_customers = len(customers)
        active_customers = len([c for c in customers if c.get("status") == "نشط"])
        st.metric("العملاء", f"{total_customers}", f"{active_customers} نشط")
    
    with col3:
        total_technicians = len(technicians)
        active_techs = len([t for t in technicians if t.get("status") == "active"])
        st.metric("الفنيين", f"{total_technicians}", f"{active_techs} نشط")
    
    with col4:
        total_revenue = sum(inv.get("total", 0) for inv in invoices)
        pending_amount = sum(inv.get("due", 0) for inv in invoices)
        st.metric("الإيرادات", f"{total_revenue:,.0f} ج.م", f"{pending_amount:,.0f} مستحق")
    
    # الفواتير الحديثة
    st.subheader("🧾 آخر الفواتير")
    if invoices:
        recent_invoices = sorted(invoices, key=lambda x: x.get("date", ""), reverse=True)[:5]
        for inv in recent_invoices:
            col_a, col_b, col_c = st.columns([3, 2, 1])
            with col_a:
                st.write(f"**{inv.get('customer', {}).get('name', 'عميل')}**")
                st.write(f"رقم: {inv.get('id', '')}")
            with col_b:
                st.write(f"المبلغ: {inv.get('total', 0):,.2f} ج.م")
                st.write(f"الحالة: {inv.get('status', '')}")
            with col_c:
                if st.button("عرض", key=f"view_{inv.get('id')}"):
                    st.json(inv)
    
    # المميزات الشهرية
    company_info = system.load_company_file(company_id, "info.json")
    if "monthly_features" in company_info and company_info["monthly_features"]:
        st.subheader("🎁 المميزات الشهرية المشتركة")
        for feature in company_info["monthly_features"]:
            st.info(f"✓ {feature}")

# ================== 5. التطبيق الرئيسي ==================
def main():
    # إعدادات الصفحة
    st.set_page_config(
        page_title="FilterPro Global",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS مخصص
    st.markdown("""
    <style>
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # التحقق من حالة الدخول
    if "company_id" not in st.session_state:
        # صفحة الاختيار
        st.sidebar.title("🌍 FilterPro Global")
        
        choice = st.sidebar.radio("اختر:", [
            "🏠 الصفحة الرئيسية",
            "🏢 تسجيل شركة جديدة", 
            "🔐 دخول شركة"
        ])
        
        if choice == "🏠 الصفحة الرئيسية":
            global_dashboard()
        elif choice == "🏢 تسجيل شركة جديدة":
            company_registration_page()
        elif choice == "🔐 دخول شركة":
            with st.form("login_form"):
                company_id = st.text_input("رقم الشركة")
                username = st.text_input("اسم المستخدم")
                password = st.text_input("كلمة المرور", type="password")
                
                if st.form_submit_button("دخول"):
                    # التحقق من صحة الدخول
                    system = FilterProGlobalSystem()
                    users = system.load_company_file(company_id, "users.json")
                    
                    for user in users:
                        if (user["username"] == username and 
                            user["password"] == system.hash_password(password)):
                            st.session_state.company_id = company_id
                            st.session_state.username = username
                            st.rerun()
                            break
                    else:
                        st.error("بيانات الدخول غير صحيحة")
    else:
        # دخول لوحة تحكم الشركة
        company_dashboard(st.session_state.company_id, st.session_state.username)

# ================== 6. تشغيل التطبيق ==================
if __name__ == "__main__":
    main()
