import streamlit as st
import json
import os
import hashlib
from datetime import datetime, timedelta
import random
import base64
from io import BytesIO

# ===============================================
# 1. نظام الإعدادات والتنسيق
# ===============================================
st.set_page_config(
    page_title="FilterPro - نظام إدارة الفلاتر",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS مخصص
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .main-header {
        background: linear-gradient(90deg, #1a2980, #26d0ce);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 5px;
    }
    
    .feature-card {
        background: white;
        color: #333;
        padding: 20px;
        border-radius: 15px;
        margin: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    
    .btn-primary {
        background: linear-gradient(90deg, #00d4ff, #0099ff);
        color: white;
        border: none;
        padding: 12px 25px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
    }
    
    .btn-primary:hover {
        background: linear-gradient(90deg, #0099ff, #00d4ff);
        box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
    }
    
    .sidebar .sidebar-content {
        background: rgba(0, 20, 40, 0.9);
    }
    
    /* تحسين ألوان النصوص */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .stTextInput label,
    .stSelectbox label,
    .stTextArea label {
        color: #00d4ff !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# ===============================================
# 2. نظام الملفات والبيانات
# ===============================================
class DataManager:
    def __init__(self):
        self.data_dir = "filterpro_data"
        self.init_data_structure()
    
    def init_data_structure(self):
        """إنشاء هيكل الملفات"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(f"{self.data_dir}/companies", exist_ok=True)
        os.makedirs(f"{self.data_dir}/backups", exist_ok=True)
        
        # ملف النظام الرئيسي
        if not os.path.exists(f"{self.data_dir}/system.json"):
            system_data = {
                "total_companies": 0,
                "total_users": 0,
                "total_invoices": 0,
                "total_revenue": 0,
                "created_date": str(datetime.now()),
                "version": "2.0.0"
            }
            self.save_file("system.json", system_data)
    
    def save_file(self, filename, data):
        """حفظ بيانات في ملف"""
        filepath = f"{self.data_dir}/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_file(self, filename):
        """تحميل بيانات من ملف"""
        filepath = f"{self.data_dir}/{filename}"
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def save_company_file(self, company_id, filename, data):
        """حفظ ملف خاص بشركة"""
        company_path = f"{self.data_dir}/companies/{company_id}"
        os.makedirs(company_path, exist_ok=True)
        
        filepath = f"{company_path}/{filename}"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_company_file(self, company_id, filename):
        """تحميل ملف خاص بشركة"""
        filepath = f"{self.data_dir}/companies/{company_id}/{filename}"
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return [] if filename.endswith(".json") else {}

# ===============================================
# 3. نظام إدارة الشركات والمستخدمين
# ===============================================
class CompanyManager:
    def __init__(self):
        self.data_manager = DataManager()
    
    def create_company(self, company_data):
        """إنشاء شركة جديدة"""
        company_id = f"COMP_{random.randint(10000, 99999)}"
        
        # بيانات الشركة
        company_info = {
            "id": company_id,
            "name": company_data["name"],
            "email": company_data["email"],
            "phone": company_data["phone"],
            "address": company_data.get("address", ""),
            "subscription_plan": company_data.get("plan", "basic"),
            "subscription_date": str(datetime.now()),
            "status": "active",
            "balance": 0.0,
            "created_by": "system"
        }
        
        # إنشاء المستخدم الأول (المدير)
        admin_user = {
            "id": 1,
            "username": company_data["admin_username"],
            "password": self.hash_password(company_data["admin_password"]),
            "name": company_data["admin_name"],
            "email": company_data["email"],
            "phone": company_data["phone"],
            "role": "company_admin",
            "permissions": ["all"],
            "created_at": str(datetime.now()),
            "status": "active"
        }
        
        # الملفات الأساسية للشركة
        files_to_create = {
            "info.json": company_info,
            "users.json": [admin_user],
            "customers.json": [],
            "technicians.json": [],
            "inventory.json": [],
            "invoices.json": [],
            "warehouses.json": [{
                "id": 1,
                "name": "المخزن الرئيسي",
                "location": company_data.get("address", ""),
                "manager_id": 1,
                "items": []
            }],
            "settings.json": {
                "invoice_template": "professional",
                "currency": "ج.م",
                "tax_rate": 14.0,
                "auto_backup": True
            }
        }
        
        # حفظ الملفات
        for filename, data in files_to_create.items():
            self.data_manager.save_company_file(company_id, filename, data)
        
        # تحديث إحصائيات النظام
        system_data = self.data_manager.load_file("system.json")
        system_data["total_companies"] += 1
        self.data_manager.save_file("system.json", system_data)
        
        return company_id
    
    def create_user(self, company_id, user_data, created_by):
        """إنشاء مستخدم جديد"""
        users = self.data_manager.load_company_file(company_id, "users.json")
        
        new_user = {
            "id": len(users) + 1,
            "username": user_data["username"],
            "password": self.hash_password(user_data["password"]),
            "name": user_data["name"],
            "email": user_data.get("email", ""),
            "phone": user_data.get("phone", ""),
            "role": user_data["role"],
            "permissions": self.get_role_permissions(user_data["role"]),
            "created_at": str(datetime.now()),
            "created_by": created_by,
            "status": "active"
        }
        
        users.append(new_user)
        self.data_manager.save_company_file(company_id, "users.json", users)
        
        # تحديث إحصائيات النظام
        system_data = self.data_manager.load_file("system.json")
        system_data["total_users"] += 1
        self.data_manager.save_file("system.json", system_data)
        
        return new_user
    
    def authenticate_user(self, company_id, username, password):
        """مصادقة المستخدم"""
        users = self.data_manager.load_company_file(company_id, "users.json")
        hashed_password = self.hash_password(password)
        
        for user in users:
            if user["username"] == username and user["password"] == hashed_password:
                return user
        return None
    
    def hash_password(self, password):
        """تشفير كلمة المرور"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_role_permissions(self, role):
        """الحصول على صلاحيات الدور"""
        permissions = {
            "company_admin": ["all"],
            "accountant": ["view_customers", "create_invoices", "view_reports", "manage_payments"],
            "technician": ["view_assigned_tasks", "update_task_status", "view_customer_info"],
            "warehouse_manager": ["manage_inventory", "view_warehouses", "create_transfers"],
            "sales_manager": ["view_customers", "create_quotes", "view_sales_reports"]
        }
        return permissions.get(role, [])

# ===============================================
# 4. نظام الفواتير المتقدم
# ===============================================
class InvoiceSystem:
    def __init__(self, company_id):
        self.company_id = company_id
        self.data_manager = DataManager()
    
    def create_invoice(self, invoice_data):
        """إنشاء فاتورة جديدة"""
        invoices = self.data_manager.load_company_file(self.company_id, "invoices.json")
        company_info = self.data_manager.load_company_file(self.company_id, "info.json")
        
        invoice_id = f"INV-{len(invoices)+1:06d}"
        
        # حساب المجموع
        subtotal = sum(item["quantity"] * item["price"] for item in invoice_data["items"])
        tax_rate = invoice_data.get("tax_rate", 14.0)
        tax_amount = subtotal * (tax_rate / 100)
        discount = invoice_data.get("discount", 0)
        total_amount = subtotal + tax_amount - discount
        
        # إنشاء الفاتورة
        invoice = {
            "id": invoice_id,
            "invoice_number": invoice_id,
            "date": str(datetime.now()),
            "customer": invoice_data["customer"],
            "items": invoice_data["items"],
            "subtotal": subtotal,
            "tax_rate": tax_rate,
            "tax_amount": tax_amount,
            "discount": discount,
            "total": total_amount,
            "paid": 0.0,
            "due": total_amount,
            "status": "غير مدفوع",
            "payment_method": "",
            "notes": invoice_data.get("notes", ""),
            "created_by": invoice_data.get("created_by", ""),
            "company_name": company_info.get("name", "")
        }
        
        invoices.append(invoice)
        self.data_manager.save_company_file(self.company_id, "invoices.json", invoices)
        
        # تحديث إحصائيات النظام
        system_data = self.data_manager.load_file("system.json")
        system_data["total_invoices"] += 1
        system_data["total_revenue"] += total_amount
        self.data_manager.save_file("system.json", system_data)
        
        return invoice
    
    def get_invoice_html(self, invoice):
        """إنشاء HTML للفاتورة"""
        html = f"""
        <div style='font-family: Cairo, sans-serif; padding: 20px; background: white; color: #333;'>
            <div style='text-align: center; border-bottom: 2px solid #00d4ff; padding-bottom: 20px;'>
                <h1 style='color: #1a2980;'>فاتورة ضريبية</h1>
                <h2>{invoice['company_name']}</h2>
            </div>
            
            <div style='display: flex; justify-content: space-between; margin: 20px 0;'>
                <div>
                    <h3>معلومات الفاتورة</h3>
                    <p><strong>رقم الفاتورة:</strong> {invoice['invoice_number']}</p>
                    <p><strong>التاريخ:</strong> {invoice['date']}</p>
                    <p><strong>الحالة:</strong> {invoice['status']}</p>
                </div>
                
                <div>
                    <h3>معلومات العميل</h3>
                    <p><strong>الاسم:</strong> {invoice['customer']['name']}</p>
                    <p><strong>الهاتف:</strong> {invoice['customer'].get('phone', '')}</p>
                    <p><strong>العنوان:</strong> {invoice['customer'].get('address', '')}</p>
                </div>
            </div>
            
            <table style='width: 100%; border-collapse: collapse; margin: 20px 0;'>
                <tr style='background: #1a2980; color: white;'>
                    <th style='padding: 10px; border: 1px solid #ddd;'>الوصف</th>
                    <th style='padding: 10px; border: 1px solid #ddd;'>الكمية</th>
                    <th style='padding: 10px; border: 1px solid #ddd;'>السعر</th>
                    <th style='padding: 10px; border: 1px solid #ddd;'>المجموع</th>
                </tr>
        """
        
        for item in invoice["items"]:
            html += f"""
                <tr>
                    <td style='padding: 10px; border: 1px solid #ddd;'>{item['description']}</td>
                    <td style='padding: 10px; border: 1px solid #ddd; text-align: center;'>{item['quantity']}</td>
                    <td style='padding: 10px; border: 1px solid #ddd; text-align: center;'>{item['price']:,.2f}</td>
                    <td style='padding: 10px; border: 1px solid #ddd; text-align: center;'>{item['quantity'] * item['price']:,.2f}</td>
                </tr>
            """
        
        html += f"""
            </table>
            
            <div style='text-align: left; margin-top: 30px;'>
                <h3>الإجماليات</h3>
                <p><strong>المجموع الجزئي:</strong> {invoice['subtotal']:,.2f}</p>
                <p><strong>الضريبة ({invoice['tax_rate']}%):</strong> {invoice['tax_amount']:,.2f}</p>
                <p><strong>الخصم:</strong> {invoice['discount']:,.2f}</p>
                <h2 style='color: #1a2980;'>المبلغ الإجمالي: {invoice['total']:,.2f}</h2>
            </div>
            
            <div style='margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd;'>
                <p><strong>ملاحظات:</strong> {invoice.get('notes', 'لا توجد ملاحظات')}</p>
                <p style='text-align: center; color: #666;'>شكراً لتعاملكم معنا</p>
            </div>
        </div>
        """
        
        return html

# ===============================================
# 5. نظام المخازن
# ===============================================
class WarehouseSystem:
    def __init__(self, company_id):
        self.company_id = company_id
        self.data_manager = DataManager()
    
    def add_item(self, warehouse_id, item_data):
        """إضافة صنف للمخزن"""
        warehouses = self.data_manager.load_company_file(self.company_id, "warehouses.json")
        
        for warehouse in warehouses:
            if warehouse["id"] == warehouse_id:
                if "items" not in warehouse:
                    warehouse["items"] = []
                
                new_item = {
                    "id": len(warehouse["items"]) + 1,
                    "name": item_data["name"],
                    "description": item_data.get("description", ""),
                    "quantity": item_data["quantity"],
                    "min_quantity": item_data.get("min_quantity", 10),
                    "price": item_data.get("price", 0.0),
                    "category": item_data.get("category", "عام"),
                    "added_date": str(datetime.now()),
                    "added_by": item_data.get("added_by", "")
                }
                
                warehouse["items"].append(new_item)
                break
        
        self.data_manager.save_company_file(self.company_id, "warehouses.json", warehouses)
        return True
    
    def get_low_stock_items(self):
        """الحصول على الأصناف المنخفضة"""
        warehouses = self.data_manager.load_company_file(self.company_id, "warehouses.json")
        low_stock_items = []
        
        for warehouse in warehouses:
            for item in warehouse.get("items", []):
                if item["quantity"] < item.get("min_quantity", 10):
                    low_stock_items.append({
                        "warehouse": warehouse["name"],
                        "item": item["name"],
                        "quantity": item["quantity"],
                        "min_quantity": item.get("min_quantity", 10)
                    })
        
        return low_stock_items

# ===============================================
# 6. واجهة المستخدم - الصفحة الرئيسية
# ===============================================
def show_home_page():
    """عرض الصفحة الرئيسية"""
    st.markdown("""
    <div class='main-header'>
        <h1>🌍 نظام FilterPro لإدارة شركات الفلاتر</h1>
        <p>الحل المتكامل لإدارة أعمال الفلاتر بكفاءة واحترافية</p>
    </div>
    """, unsafe_allow_html=True)
    
    # إحصائيات النظام
    data_manager = DataManager()
    system_data = data_manager.load_file("system.json")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>🏢 الشركات</h3>
            <h2>{system_data.get('total_companies', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>👥 المستخدمين</h3>
            <h2>{system_data.get('total_users', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>🧾 الفواتير</h3>
            <h2>{system_data.get('total_invoices', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <h3>💰 الإيرادات</h3>
            <h2>{system_data.get('total_revenue', 0):,.0f} ج.م</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # المميزات
    st.markdown("## ✨ مميزات النظام")
    
    features_col1, features_col2 = st.columns(2)
    
    with features_col1:
        st.markdown("""
        <div class='feature-card'>
            <h3>🏢 نظام متعدد الشركات</h3>
            <p>إدارة آلاف الشركات من منصة واحدة</p>
            <ul>
                <li>كل شركة لها قاعدة بيانات خاصة</li>
                <li>صلاحيات متعددة المستويات</li>
                <li>فواتير وإعدادات مستقلة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-card'>
            <h3>🧾 نظام الفواتير المتقدم</h3>
            <p>فواتير احترافية عربية بالكامل</p>
            <ul>
                <li>تصميم عربي احترافي</li>
                <li>تخزين وتصدير PDF</li>
                <li>إدارة مدفوعات</li>
                <li>تقارير مالية شاملة</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with features_col2:
        st.markdown("""
        <div class='feature-card'>
            <h3>👥 إدارة العملاء والفنيين</h3>
            <p>تنظيم كامل لعلاقات العملاء</p>
            <ul>
                <li>سجل كامل لكل عميل</li>
                <li>جدولة صيانة دورية</li>
                <li>متابعة الفنيين</li>
                <li>تقييم الخدمات</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='feature-card'>
            <h3>📦 نظام المخازن الذكي</h3>
            <p>إدارة مخزون ذكية وفعالة</p>
            <ul>
                <li>مخازن متعددة وفروع</li>
                <li>تنبيهات نفاذ المخزون</li>
                <li>حركة المخزون اليومية</li>
                <li>تقارير الجرد</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # خطط الأسعار
    st.markdown("## 💰 خطط الاشتراك")
    
    plans_col1, plans_col2, plans_col3 = st.columns(3)
    
    with plans_col1:
        st.markdown("""
        <div class='feature-card'>
            <h3>🟢 الأساسية</h3>
            <h2>199 ج.م/شهر</h2>
            <ul>
                <li>✓ 100 عميل</li>
                <li>✓ 3 فنيين</li>
                <li>✓ فواتير أساسية</li>
                <li>✓ تقارير مالية</li>
                <li>✓ دعم فني</li>
                <br>
                <button class='btn-primary'>اشترك الآن</button>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with plans_col2:
        st.markdown("""
        <div class='feature-card'>
            <h3>🔵 المحترف</h3>
            <h2>499 ج.م/شهر</h2>
            <ul>
                <li>✓ 500 عميل</li>
                <li>✓ 10 فنيين</li>
                <li>✓ فواتير متقدمة</li>
                <li>✓ نظام المخازن</li>
                <li>✓ تقارير متقدمة</li>
                <li>✓ دعم فني مميز</li>
                <button class='btn-primary'>اشترك الآن</button>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with plans_col3:
        st.markdown("""
        <div class='feature-card'>
            <h3>🟣 المؤسسة</h3>
            <h2>999 ج.م/شهر</h2>
            <ul>
                <li>✓ عملاء غير محدود</li>
                <li>✓ فنيين غير محدود</li>
                <li>✓ كل المميزات</li>
                <li>✓ دعم فني 24/7</li>
                <li>✓ تدريب فريقك</li>
                <li>✓ ميزات مخصصة</li>
                <button class='btn-primary'>اشترك الآن</button>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ===============================================
# 7. واجهة تسجيل الشركات
# ===============================================
def show_company_registration():
    """صفحة تسجيل شركة جديدة"""
    st.markdown("""
    <div class='main-header'>
        <h1>🏢 تسجيل شركة جديدة</h1>
        <p>ابدأ رحلة نجاحك مع نظام إدارة الفلاتر المتكامل</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("register_company", clear_on_submit=True):
        st.markdown("### معلومات الشركة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("اسم الشركة *", placeholder="شركة فلاتر النقاء")
            company_email = st.text_input("البريد الإلكتروني *", placeholder="info@company.com")
            company_phone = st.text_input("الهاتف *", placeholder="01001234567")
        
        with col2:
            company_address = st.text_area("عنوان الشركة", placeholder="المدينة، الحي، الشارع")
            company_type = st.selectbox("نشاط الشركة", [
                "فلاتر مياه", "فلاتر هواء", "فلاتر زيت", 
                "فلاتر وقود", "صيانة فلاتر", "جميع الأنواع"
            ])
            subscription_plan = st.selectbox("خطة الاشتراك", [
                "الأساسية (199 ج.م/شهر)",
                "المحترف (499 ج.م/شهر)", 
                "المؤسسة (999 ج.م/شهر)"
            ])
        
        st.markdown("### بيانات المدير المسؤول")
        
        col3, col4 = st.columns(2)
        
        with col3:
            admin_name = st.text_input("اسم المدير *", placeholder="محمد أحمد")
            admin_username = st.text_input("اسم المستخدم *", placeholder="mohamed_admin")
        
        with col4:
            admin_password = st.text_input("كلمة المرور *", type="password", placeholder="********")
            confirm_password = st.text_input("تأكيد كلمة المرور *", type="password", placeholder="********")
        
        st.markdown("### الشروط والأحكام")
        agree = st.checkbox("أوافق على الشروط والأحكام *")
        
        submit_button = st.form_submit_button("🏢 تسجيل الشركة", use_container_width=True)
        
        if submit_button:
            if not all([company_name, company_email, company_phone, admin_name, admin_username, admin_password]):
                st.error("جميع الحقول المميزة ب * إلزامية")
            elif admin_password != confirm_password:
                st.error("كلمات المرور غير متطابقة")
            elif not agree:
                st.error("يجب الموافقة على الشروط والأحكام")
            else:
                # إنشاء الشركة
                company_manager = CompanyManager()
                
                company_data = {
                    "name": company_name,
                    "email": company_email,
                    "phone": company_phone,
                    "address": company_address,
                    "plan": subscription_plan.split(" ")[0],
                    "admin_name": admin_name,
                    "admin_username": admin_username,
                    "admin_password": admin_password
                }
                
                try:
                    company_id = company_manager.create_company(company_data)
                    
                    st.success(f"""
                    ## ✅ تم تسجيل شركتك بنجاح!
                    
                    **رقم الشركة:** `{company_id}`
                    **اسم المستخدم:** `{admin_username}`
                    **كلمة المرور:** `{admin_password}`
                    
                    ### 🎉 يمكنك الآن:
                    1. تسجيل الدخول باستخدام بياناتك
                    2. إضافة فريق العمل
                    3. إضافة عملائك
                    4. البدء في إصدار الفواتير
                    """)
                    
                    # أزرار التنقل
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("🚀 دخول مباشر", use_container_width=True):
                            st.session_state.company_id = company_id
                            st.session_state.username = admin_username
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("📋 نسخ بيانات الدخول", use_container_width=True):
                            st.info(f"تم نسخ بيانات الدخول")
                
                except Exception as e:
                    st.error(f"حدث خطأ: {str(e)}")

# ===============================================
# 8. صفحة تسجيل الدخول
# ===============================================
def show_login_page():
    """صفحة تسجيل الدخول"""
    st.markdown("""
    <div class='main-header'>
        <h1>🔐 تسجيل الدخول</h1>
        <p>أدخل بيانات الدخول للوصول إلى لوحة التحكم</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            company_id = st.text_input("رقم الشركة", placeholder="COMP_12345")
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                login_button = st.form_submit_button("🚪 تسجيل الدخول", use_container_width=True)
            
            with col_btn2:
                if st.form_submit_button("🆕 تسجيل شركة جديدة", use_container_width=True):
                    st.session_state.page = "register"
                    st.rerun()
            
            if login_button:
                if company_id and username and password:
                    company_manager = CompanyManager()
                    user = company_manager.authenticate_user(company_id, username, password)
                    
                    if user:
                        st.session_state.company_id = company_id
                        st.session_state.username = username
                        st.session_state.user_info = user
                        st.success(f"مرحباً بك {user['name']}!")
                        st.rerun()
                    else:
                        st.error("بيانات الدخول غير صحيحة")
                else:
                    st.error("جميع الحقول إلزامية")

# ===============================================
# 9. لوحة تحكم الشركة
# ===============================================
def show_company_dashboard():
    """لوحة تحكم الشركة"""
    company_id = st.session_state.company_id
    username = st.session_state.username
    user_info = st.session_state.user_info
    
    # تحميل بيانات الشركة
    data_manager = DataManager()
    company_info = data_manager.load_company_file(company_id, "info.json")
    
    # رأس لوحة التحكم
    st.markdown(f"""
    <div class='main-header' style='text-align: right; padding: 20px;'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h2 style='margin: 0;'>🏢 {company_info.get('name', '')}</h2>
                <p style='margin: 0; opacity: 0.8;'>👤 {user_info['name']} | {user_info['role']}</p>
            </div>
            <div>
                <p style='margin: 0;'>رقم الشركة: {company_id}</p>
                <p style='margin: 0;'>الخطة: {company_info.get('subscription_plan', '')}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # القائمة الجانبية
    with st.sidebar:
        st.markdown(f"### 👤 {user_info['name']}")
        st.markdown(f"**الدور:** {user_info['role']}")
        st.divider()
        
        menu_options = ["📊 لوحة التحكم", "👥 العملاء", "🛠️ الفنيين", "🧾 الفواتير", 
                       "📦 المخازن", "💰 المحاسبة", "⚙️ الإعدادات"]
        
        if user_info["role"] == "company_admin":
            menu_options.append("👥 إدارة المستخدمين")
        
        selected_menu = st.radio("القائمة", menu_options)
        
        st.divider()
        
        # إنشاء حسابات جديدة (للمدير فقط)
        if user_info["role"] == "company_admin":
            with st.expander("➕ إنشاء حساب جديد"):
                with st.form("create_user_form"):
                    new_user_name = st.text_input("اسم الموظف")
                    new_user_username = st.text_input("اسم المستخدم")
                    new_user_password = st.text_input("كلمة المرور", type="password")
                    new_user_role = st.selectbox("الدور", ["accountant", "technician", "warehouse_manager", "sales_manager"])
                    
                    if st.form_submit_button("إنشاء الحساب"):
                        company_manager = CompanyManager()
                        user_data = {
                            "username": new_user_username,
                            "password": new_user_password,
                            "name": new_user_name,
                            "role": new_user_role
                        }
                        
                        company_manager.create_user(company_id, user_data, username)
                        st.success(f"تم إنشاء حساب {new_user_role}")
        
        st.divider()
        if st.button("🚪 تسجيل الخروج", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # المحتوى الرئيسي حسب القائمة
    if selected_menu == "📊 لوحة التحكم":
        show_dashboard_content(company_id)
    elif selected_menu == "🧾 الفواتير":
        show_invoices_content(company_id, user_info)
    elif selected_menu == "📦 المخازن":
        show_warehouse_content(company_id, user_info)
    elif selected_menu == "👥 إدارة المستخدمين":
        show_users_management(company_id)

def show_dashboard_content(company_id):
    """عرض محتوى لوحة التحكم"""
    data_manager = DataManager()
    
    # تحميل البيانات
    customers = data_manager.load_company_file(company_id, "customers.json")
    invoices = data_manager.load_company_file(company_id, "invoices.json")
    technicians = data_manager.load_company_file(company_id, "technicians.json")
    
    # إحصائيات سريعة
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(customers)
        st.metric("👥 العملاء", total_customers)
    
    with col2:
        total_invoices = len(invoices)
        paid_invoices = len([i for i in invoices if i.get("status") == "مدفوع"])
        st.metric("🧾 الفواتير", total_invoices, f"{paid_invoices} مدفوعة")
    
    with col3:
        total_technicians = len(technicians)
        active_techs = len([t for t in technicians if t.get("status") == "active"])
        st.metric("🛠️ الفنيين", total_technicians, f"{active_techs} نشط")
    
    with col4:
        total_revenue = sum(i.get("total", 0) for i in invoices)
        pending_amount = sum(i.get("due", 0) for i in invoices)
        st.metric("💰 الإيرادات", f"{total_revenue:,.0f} ج.م", f"{pending_amount:,.0f} مستحق")
    
    # أحدث الفواتير
    st.subheader("🧾 آخر الفواتير")
    if invoices:
        recent_invoices = sorted(invoices, key=lambda x: x.get("date", ""), reverse=True)[:5]
        
        for inv in recent_invoices:
            with st.expander(f"فاتورة #{inv.get('invoice_number', '')} - {inv.get('customer', {}).get('name', '')}", expanded=False):
                col_a, col_b, col_c = st.columns([3, 2, 1])
                
                with col_a:
                    st.write(f"**العميل:** {inv.get('customer', {}).get('name', '')}")
                    st.write(f"**التاريخ:** {inv.get('date', '')}")
                
                with col_b:
                    st.write(f"**المبلغ:** {inv.get('total', 0):,.2f} ج.م")
                    st.write(f"**الحالة:** {inv.get('status', '')}")
                
                with col_c:
                    if st.button("عرض", key=f"view_{inv.get('id')}"):
                        invoice_system = InvoiceSystem(company_id)
                        invoice_html = invoice_system.get_invoice_html(inv)
                        st.components.v1.html(invoice_html, height=800, scrolling=True)
    
    # الأصناف المنخفضة في المخزون
    warehouse_system = WarehouseSystem(company_id)
    low_stock_items = warehouse_system.get_low_stock_items()
    
    if low_stock_items:
        st.subheader("⚠️ تنبيهات المخزون المنخفض")
        for item in low_stock_items[:3]:
            st.warning(f"{item['item']} في {item['warehouse']}: {item['quantity']} فقط (الحد الأدنى: {item['min_quantity']})")

def show_invoices_content(company_id, user_info):
    """عرض نظام الفواتير"""
    st.title("🧾 نظام الفواتير")
    
    tab1, tab2, tab3 = st.tabs(["إنشاء فاتورة", "قائمة الفواتير", "تقارير الفواتير"])
    
    with tab1:
        with st.form("create_invoice_form"):
            st.subheader("إنشاء فاتورة جديدة")
            
            # معلومات العميل
            col1, col2 = st.columns(2)
            with col1:
                customer_name = st.text_input("اسم العميل *")
                customer_phone = st.text_input("هاتف العميل")
            
            with col2:
                customer_address = st.text_input("عنوان العميل")
                invoice_date = st.date_input("تاريخ الفاتورة", datetime.now())
            
            # الأصناف
            st.subheader("الأصناف")
            
            items = []
            for i in range(3):
                col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
                with col_i1:
                    item_desc = st.text_input(f"وصف الصنف {i+1}", placeholder="فلتر مياه 3 مراحل")
                with col_i2:
                    item_qty = st.number_input(f"الكمية {i+1}", min_value=1, value=1)
                with col_i3:
                    item_price = st.number_input(f"السعر {i+1}", min_value=0.0, value=0.0)
                
                if item_desc:
                    items.append({
                        "description": item_desc,
                        "quantity": item_qty,
                        "price": item_price
                    })
            
            # الحسابات
            st.subheader("الحسابات")
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                tax_rate = st.number_input("نسبة الضريبة %", min_value=0.0, max_value=100.0, value=14.0)
                discount = st.number_input("الخصم", min_value=0.0, value=0.0)
            
            with col_c2:
                notes = st.text_area("ملاحظات")
            
            if st.form_submit_button("💾 إنشاء الفاتورة"):
                if customer_name and items:
                    invoice_system = InvoiceSystem(company_id)
                    
                    invoice_data = {
                        "customer": {
                            "name": customer_name,
                            "phone": customer_phone,
                            "address": customer_address
                        },
                        "items": items,
                        "tax_rate": tax_rate,
                        "discount": discount,
                        "notes": notes,
                        "created_by": user_info["name"]
                    }
                    
                    invoice = invoice_system.create_invoice(invoice_data)
                    
                    st.success("✅ تم إنشاء الفاتورة بنجاح!")
                    
                    # عرض الفاتورة
                    invoice_html = invoice_system.get_invoice_html(invoice)
                    st.components.v1.html(invoice_html, height=600, scrolling=True)
                    
                    # خيارات التحميل
                    st.download_button(
                        label="📥 تحميل الفاتورة",
                        data=invoice_html,
                        file_name=f"فاتورة_{invoice['invoice_number']}.html",
                        mime="text/html"
                    )
                else:
                    st.error("اسم العميل والأصناف إلزامية")
    
    with tab2:
        data_manager = DataManager()
        invoices = data_manager.load_company_file(company_id, "invoices.json")
        
        if invoices:
            for invoice in invoices:
                with st.expander(f"فاتورة #{invoice.get('invoice_number', '')} - {invoice.get('customer', {}).get('name', '')}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**العميل:** {invoice.get('customer', {}).get('name', '')}")
                        st.write(f"**التاريخ:** {invoice.get('date', '')}")
                    
                    with col2:
                        st.write(f"**المبلغ:** {invoice.get('total', 0):,.2f} ج.م")
                        st.write(f"**الحالة:** {invoice.get('status', '')}")
                    
                    with col3:
                        if st.button("عرض", key=f"show_{invoice.get('id')}"):
                            invoice_system = InvoiceSystem(company_id)
                            invoice_html = invoice_system.get_invoice_html(invoice)
                            st.components.v1.html(invoice_html, height=600, scrolling=True)
        
        else:
            st.info("لا توجد فواتير حتى الآن")

def show_warehouse_content(company_id, user_info):
    """عرض نظام المخازن"""
    st.title("📦 نظام المخازن")
    
    data_manager = DataManager()
    warehouses = data_manager.load_company_file(company_id, "warehouses.json")
    
    tab1, tab2, tab3 = st.tabs(["المخازن", "إضافة صنف", "تقارير المخزون"])
    
    with tab1:
        st.subheader("قائمة المخازن")
        
        for warehouse in warehouses:
            with st.expander(f"📦 {warehouse['name']} - {warehouse.get('location', '')}", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**المدير:** {warehouse.get('manager', 'غير محدد')}")
                    st.write(f"**عدد الأصناف:** {len(warehouse.get('items', []))}")
                    
                    # عرض الأصناف
                    if warehouse.get('items'):
                        for item in warehouse['items']:
                            st.write(f"- {item['name']}: {item['quantity']} وحدة")
                
                with col2:
                    # إضافة صنف سريع
                    with st.form(f"quick_add_{warehouse['id']}"):
                        item_name = st.text_input("اسم الصنف", key=f"item_{warehouse['id']}")
                        item_qty = st.number_input("الكمية", min_value=1, value=1, key=f"qty_{warehouse['id']}")
                        
                        if st.form_submit_button("➕ إضافة"):
                            warehouse_system = WarehouseSystem(company_id)
                            item_data = {
                                "name": item_name,
                                "quantity": item_qty,
                                "added_by": user_info["name"]
                            }
                            
                            warehouse_system.add_item(warehouse['id'], item_data)
                            st.success(f"تم إضافة {item_name}")
                            st.rerun()
    
    with tab2:
        st.subheader("إضافة صنف جديد")
        
        with st.form("add_item_form"):
            warehouse_id = st.selectbox(
                "المخزن",
                options=[w['id'] for w in warehouses],
                format_func=lambda x: next((w['name'] for w in warehouses if w['id'] == x), '')
            )
            
            col1, col2 = st.columns(2)
            with col1:
                item_name = st.text_input("اسم الصنف *")
                item_category = st.selectbox("الفئة", ["فلاتر مياه", "قطع غيار", "كيميكالات", "أخرى"])
            
            with col2:
                item_quantity = st.number_input("الكمية *", min_value=1, value=1)
                item_min_quantity = st.number_input("الحد الأدنى للتنبيه", min_value=1, value=10)
                item_price = st.number_input("سعر الوحدة", min_value=0.0, value=0.0)
            
            item_description = st.text_area("وصف الصنف")
            
            if st.form_submit_button("➕ إضافة الصنف"):
                if item_name and warehouse_id:
                    warehouse_system = WarehouseSystem(company_id)
                    
                    item_data = {
                        "name": item_name,
                        "description": item_description,
                        "quantity": item_quantity,
                        "min_quantity": item_min_quantity,
                        "price": item_price,
                        "category": item_category,
                        "added_by": user_info["name"]
                    }
                    
                    warehouse_system.add_item(warehouse_id, item_data)
                    st.success(f"تم إضافة {item_name} بنجاح!")
                    st.rerun()
                else:
                    st.error("اسم الصنف إلزامي")
    
    with tab3:
        st.subheader("تقارير المخزون")
        
        warehouse_system = WarehouseSystem(company_id)
        low_stock_items = warehouse_system.get_low_stock_items()
        
        if low_stock_items:
            st.warning("⚠️ الأصناف المنخفضة في المخزون")
            for item in low_stock_items:
                st.write(f"**{item['item']}** في {item['warehouse']}: {item['quantity']} فقط (الحد الأدنى: {item['min_quantity']})")
        else:
            st.success("🎉 جميع الأصناف في المستوى الآمن")
        
        # إحصائيات المخزون
        total_items = 0
        total_value = 0
        
        for warehouse in warehouses:
            for item in warehouse.get('items', []):
                total_items += item['quantity']
                total_value += item['quantity'] * item.get('price', 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("إجمالي الوحدات", total_items)
        with col2:
            st.metric("القيمة الإجمالية", f"{total_value:,.0f} ج.م")

def show_users_management(company_id):
    """إدارة المستخدمين"""
    st.title("👥 إدارة المستخدمين")
    
    data_manager = DataManager()
    users = data_manager.load_company_file(company_id, "users.json")
    
    if users:
        for user in users:
            with st.expander(f"👤 {user['name']} ({user['username']})", expanded=False):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**الدور:** {user['role']}")
                    st.write(f"**البريد:** {user.get('email', '')}")
                    st.write(f"**الهاتف:** {user.get('phone', '')}")
                    st.write(f"**تاريخ الإنشاء:** {user.get('created_at', '')}")
                
                with col2:
                    status = st.selectbox(
                        "الحالة",
                        ["active", "inactive", "suspended"],
                        index=["active", "inactive", "suspended"].index(user.get('status', 'active')),
                        key=f"status_{user['id']}"
                    )
                
                with col3:
                    if st.button("تحديث", key=f"update_{user['id']}"):
                        user['status'] = status
                        data_manager.save_company_file(company_id, "users.json", users)
                        st.success("تم التحديث")
                        st.rerun()

# ===============================================
# 10. التطبيق الرئيسي
# ===============================================
def main():
    """التطبيق الرئيسي"""
    
    # تهيئة حالة الجلسة
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    # القائمة الجانبية الرئيسية
    with st.sidebar:
        st.markdown("# 🌍 FilterPro")
        st.markdown("نظام إدارة شركات الفلاتر")
        st.divider()
        
        if "company_id" not in st.session_state:
            menu_choice = st.radio(
                "القائمة",
                ["🏠 الصفحة الرئيسية", "🏢 تسجيل شركة", "🔐 تسجيل الدخول"],
                key="main_menu"
            )
            
            if menu_choice == "🏠 الصفحة الرئيسية":
                st.session_state.page = "home"
            elif menu_choice == "🏢 تسجيل شركة":
                st.session_state.page = "register"
            elif menu_choice == "🔐 تسجيل الدخول":
                st.session_state.page = "login"
        
        st.divider()
        st.markdown("### الدعم الفني")
        st.markdown("📞 01012345678")
        st.markdown("✉️ support@filterpro.com")
        st.markdown("🕒 24/7")
    
    # عرض الصفحة المحددة
    if "company_id" in st.session_state:
        show_company_dashboard()
    else:
        if st.session_state.page == "home":
            show_home_page()
        elif st.session_state.page == "register":
            show_company_registration()
        elif st.session_state.page == "login":
            show_login_page()

# ===============================================
# 11. تشغيل التطبيق
# ===============================================
if __name__ == "__main__":
    main()
