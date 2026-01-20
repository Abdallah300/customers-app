import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

# ================== 1. الإعدادات الأساسية ==================
st.set_page_config(
    page_title="نظام إدارة شركات الفلاتر | FilterPro",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تحميل الخط العربي وتحسين التنسيق
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl !important;
        text-align: right !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0c2461 0%, #1e3799 50%, #4a69bd 100%);
    }
    
    .main-header {
        background: linear-gradient(90deg, #1a2980, #26d0ce);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s;
    }
    
    .card:hover {
        transform: translateY(-5px);
        border-color: #00d4ff;
    }
    
    .btn-primary {
        background: linear-gradient(90deg, #00d4ff, #0099ff);
        color: white;
        border: none;
        padding: 10px 25px;
        border-radius: 8px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .btn-primary:hover {
        background: linear-gradient(90deg, #0099ff, #00d4ff);
        box-shadow: 0 5px 15px rgba(0, 212, 255, 0.4);
    }
    
    .status-active { color: #00ff88; font-weight: bold; }
    .status-pending { color: #ffaa00; font-weight: bold; }
    .status-completed { color: #00d4ff; font-weight: bold; }
    .status-cancelled { color: #ff4444; font-weight: bold; }
    
    .metric-box {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        border-left: 5px solid #00d4ff;
    }
    
    .filter-item {
        background: rgba(255,255,255,0.03);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .emergency-card {
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 65, 108, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 65, 108, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 65, 108, 0); }
    }
    
    .sidebar .sidebar-content {
        background: rgba(0, 20, 40, 0.9);
    }
</style>
""", unsafe_allow_html=True)

# ================== 2. نظام إدارة الملفات والبيانات ==================
DATA_FILES = {
    "customers": "customers.json",
    "technicians": "technicians.json",
    "inventory": "inventory.json",
    "tasks": "tasks.json",
    "contracts": "contracts.json",
    "invoices": "invoices.json",
    "maintenance_schedule": "maintenance_schedule.json"
}

def init_data_files():
    """تهيئة جميع ملفات البيانات إذا لم تكن موجودة"""
    for key, filename in DATA_FILES.items():
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

def load_data(filename):
    """تحميل البيانات من ملف JSON"""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return data
    except:
        return []

def save_data(filename, data):
    """حفظ البيانات إلى ملف JSON"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================== 3. نماذج البيانات الأساسية ==================
class Customer:
    def __init__(self, data=None):
        self.id = data.get("id", 0)
        self.name = data.get("name", "")
        self.phone = data.get("phone", "")
        self.email = data.get("email", "")
        self.address = data.get("address", "")
        self.company = data.get("company", "")
        self.customer_type = data.get("customer_type", "فرد")  # فرد/شركة/مؤسسة
        self.registration_date = data.get("registration_date", datetime.now().strftime("%Y-%m-%d"))
        self.status = data.get("status", "نشط")  # نشط/موقوف/محذوف
        self.notes = data.get("notes", "")
        self.filters = data.get("filters", [])  # قائمة الفلاتر المثبتة
        self.maintenance_history = data.get("maintenance_history", [])
        self.payment_history = data.get("payment_history", [])
        self.total_spent = data.get("total_spent", 0.0)
        self.current_balance = data.get("current_balance", 0.0)
        self.next_maintenance = data.get("next_maintenance", "")
        self.contract_id = data.get("contract_id", "")
        
    def to_dict(self):
        return self.__dict__
    
    def calculate_balance(self):
        """حساب الرصيد الحالي للعميل"""
        total_debt = sum(item.get("amount", 0) for item in self.payment_history if item.get("type") == "debt")
        total_paid = sum(item.get("amount", 0) for item in self.payment_history if item.get("type") == "payment")
        self.current_balance = total_debt - total_paid
        return self.current_balance

class FilterItem:
    def __init__(self, data=None):
        self.id = data.get("id", 0)
        self.name = data.get("name", "")
        self.model = data.get("model", "")
        self.type = data.get("type", "منزلي")  # منزلي/تجاري/صناعي
        self.category = data.get("category", "فلتر مياه")  # فلتر مياه/هواء/زيت/وقود
        self.manufacturer = data.get("manufacturer", "")
        self.price = data.get("price", 0.0)
        self.cost = data.get("cost", 0.0)
        self.quantity = data.get("quantity", 0)
        self.min_quantity = data.get("min_quantity", 5)
        self.location = data.get("location", "المستودع الرئيسي")
        self.supplier = data.get("supplier", "")
        self.last_restock = data.get("last_restock", "")
        self.next_restock = data.get("next_restock", "")
        self.serial_numbers = data.get("serial_numbers", [])
        
    def to_dict(self):
        return self.__dict__

class MaintenanceTask:
    def __init__(self, data=None):
        self.id = data.get("id", 0)
        self.customer_id = data.get("customer_id", 0)
        self.customer_name = data.get("customer_name", "")
        self.task_type = data.get("task_type", "صيانة دورية")  # صيانة دورية/طارئة/تركيب/إصلاح
        self.priority = data.get("priority", "عادي")  # عادي/عاجل/طارئ
        self.status = data.get("status", "معلقة")  # معلقة/قيد التنفيذ/مكتملة/ملغاة
        self.assigned_to = data.get("assigned_to", "")
        self.assigned_date = data.get("assigned_date", "")
        self.scheduled_date = data.get("scheduled_date", "")
        self.completed_date = data.get("completed_date", "")
        self.description = data.get("description", "")
        self.notes = data.get("notes", "")
        self.used_items = data.get("used_items", [])  # القطع المستخدمة
        self.total_cost = data.get("total_cost", 0.0)
        self.total_price = data.get("total_price", 0.0)
        self.payment_status = data.get("payment_status", "غير مدفوع")  # مدفوع/جزئي/غير مدفوع
        self.invoice_id = data.get("invoice_id", "")
        
    def to_dict(self):
        return self.__dict__

class ServiceContract:
    def __init__(self, data=None):
        self.id = data.get("id", 0)
        self.customer_id = data.get("customer_id", 0)
        self.customer_name = data.get("customer_name", "")
        self.contract_type = data.get("contract_type", "صيانة سنوية")  # سنوية/نصف سنوية/ربع سنوية
        self.start_date = data.get("start_date", "")
        self.end_date = data.get("end_date", "")
        self.total_amount = data.get("total_amount", 0.0)
        self.paid_amount = data.get("paid_amount", 0.0)
        self.remaining_amount = data.get("remaining_amount", 0.0)
        self.installments = data.get("installments", [])
        self.visit_count = data.get("visit_count", 4)  # عدد الزيارات في العقد
        self.used_visits = data.get("used_visits", 0)
        self.remaining_visits = data.get("remaining_visits", 0)
        self.includes_parts = data.get("includes_parts", True)
        self.includes_labor = data.get("includes_labor", True)
        self.status = data.get("status", "نشط")  # نشط/منتهي/ملغى
        
    def to_dict(self):
        return self.__dict__

# ================== 4. نظام إدارة الجلسات والحالة ==================
def init_session_state():
    """تهيئة حالة الجلسة"""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.user = None
        st.session_state.role = None
        st.session_state.page = "dashboard"
        st.session_state.selected_customer = None
        st.session_state.selected_task = None
        st.session_state.selected_filter = None
        st.session_state.editing_id = None
        
        # تحميل البيانات
        for key in DATA_FILES:
            st.session_state[key] = load_data(DATA_FILES[key])

# ================== 5. نظام المصادقة والصلاحيات ==================
def login_system():
    """نظام تسجيل الدخول"""
    st.markdown("<div class='main-header'><h1 style='text-align:center; margin:0;'>💧 نظام إدارة شركات الفلاتر | FilterPro</h1></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;'>تسجيل الدخول</h3>", unsafe_allow_html=True)
        
        role = st.selectbox("الدور", ["مدير النظام", "مدير المبيعات", "مدير العمليات", "فني", "محاسب"])
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🚪 دخول", use_container_width=True):
                if username and password:
                    st.session_state.user = username
                    st.session_state.role = role
                    st.success(f"مرحباً {username}!")
                    st.rerun()
                else:
                    st.error("يرجى إدخال اسم المستخدم وكلمة المرور")
        
        with col_btn2:
            if st.button("🆕 حساب جديد", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def register_system():
    """نظام التسجيل"""
    st.markdown("<div class='main-header'><h1 style='text-align:center; margin:0;'>إنشاء حساب جديد</h1></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("register_form"):
            st.write("### معلومات الحساب")
            
            full_name = st.text_input("الاسم الكامل")
            email = st.text_input("البريد الإلكتروني")
            phone = st.text_input("رقم الهاتف")
            company = st.text_input("اسم الشركة (إن وجد)")
            user_type = st.selectbox("نوع الحساب", ["مدير شركة", "موظف إدارة", "فني", "عميل"])
            
            st.write("### بيانات الدخول")
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            confirm_password = st.text_input("تأكيد كلمة المرور", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("إنشاء الحساب", use_container_width=True)
            with col2:
                back = st.form_submit_button("رجوع لتسجيل الدخول", use_container_width=True)
            
            if submit:
                if password == confirm_password:
                    st.success("تم إنشاء الحساب بنجاح!")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.error("كلمات المرور غير متطابقة")
            
            if back:
                st.session_state.page = "login"
                st.rerun()

# ================== 6. لوحة التحكم الرئيسية ==================
def dashboard():
    """لوحة التحكم الرئيسية"""
    st.markdown(f"<div class='main-header'><h1 style='margin:0;'>مرحباً {st.session_state.user} 👋</h1><p style='margin:0; opacity:0.8;'>لوحة تحكم نظام إدارة الفلاتر</p></div>", unsafe_allow_html=True)
    
    # عرض الإحصائيات الرئيسية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(st.session_state.customers)
        st.markdown(f"""
        <div class='metric-box'>
            <h3 style='margin:0;'>👥 العملاء</h3>
            <h2 style='margin:0; color:#00d4ff;'>{total_customers}</h2>
            <p style='margin:0; font-size:12px; opacity:0.7;'>إجمالي العملاء المسجلين</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        active_tasks = len([t for t in st.session_state.tasks if t.get("status") in ["معلقة", "قيد التنفيذ"]])
        st.markdown(f"""
        <div class='metric-box'>
            <h3 style='margin:0;'>📋 المهام النشطة</h3>
            <h2 style='margin:0; color:#00ff88;'>{active_tasks}</h2>
            <p style='margin:0; font-size:12px; opacity:0.7;'>مهام تحت التنفيذ</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        low_stock = len([i for i in st.session_state.inventory if i.get("quantity", 0) < i.get("min_quantity", 5)])
        st.markdown(f"""
        <div class='metric-box'>
            <h3 style='margin:0;'>⚠️ قطع منخفضة</h3>
            <h2 style='margin:0; color:#ffaa00;'>{low_stock}</h2>
            <p style='margin:0; font-size:12px; opacity:0.7;'>تحت الحد الأدنى</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_balance = sum(c.get("current_balance", 0) for c in st.session_state.customers)
        st.markdown(f"""
        <div class='metric-box'>
            <h3 style='margin:0;'>💰 إجمالي المستحقات</h3>
            <h2 style='margin:0; color:#ff4444;'>{total_balance:,.0f} ج.م</h2>
            <p style='margin:0; font-size:12px; opacity:0.7;'>مديونيات العملاء</p>
        </div>
        """, unsafe_allow_html=True)
    
    # قسم المهام العاجلة
    st.markdown("### 📌 المهام العاجلة اليوم")
    urgent_tasks = [t for t in st.session_state.tasks if t.get("priority") == "طارئ" and t.get("status") != "مكتملة"]
    
    if urgent_tasks:
        for task in urgent_tasks[:3]:
            with st.container():
                st.markdown(f"""
                <div class='emergency-card'>
                    <strong>🚨 {task.get('customer_name', '')}</strong><br>
                    {task.get('description', '')}<br>
                    <small>الفني: {task.get('assigned_to', 'غير معين')} | التاريخ: {task.get('scheduled_date', '')}</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("🎉 لا توجد مهام عاجلة اليوم")
    
    # قسم العملاء القريبين من الصيانة
    st.markdown("### 📅 عملاء بحاجة لصيانة قريباً")
    upcoming_maintenance = []
    today = datetime.now()
    
    for customer in st.session_state.customers:
        next_maintenance = customer.get("next_maintenance")
        if next_maintenance:
            try:
                maintenance_date = datetime.strptime(next_maintenance, "%Y-%m-%d")
                days_diff = (maintenance_date - today).days
                if 0 <= days_diff <= 7:  # خلال الأسبوع القادم
                    upcoming_maintenance.append({
                        "name": customer.get("name"),
                        "date": next_maintenance,
                        "days_left": days_diff,
                        "phone": customer.get("phone", "")
                    })
            except:
                pass
    
    if upcoming_maintenance:
        for client in sorted(upcoming_maintenance, key=lambda x: x["days_left"])[:5]:
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.write(f"👤 **{client['name']}**")
            with col2:
                st.write(f"📅 {client['date']}")
            with col3:
                st.write(f"⏳ {client['days_left']} يوم")
    else:
        st.info("🎉 لا توجد صيانة مجدولة خلال الأسبوع القادم")
    
    # مخطط إحصائي
    st.markdown("### 📊 الإحصائيات الشهرية")
    
    if st.session_state.tasks:
        tasks_df = pd.DataFrame(st.session_state.tasks)
        if "completed_date" in tasks_df.columns:
            tasks_df["month"] = tasks_df["completed_date"].apply(lambda x: str(x)[:7] if x else None)
            monthly_stats = tasks_df[tasks_df["month"].notna()].groupby("month").size().reset_index(name="count")
            
            if not monthly_stats.empty:
                fig = px.line(monthly_stats, x="month", y="count", 
                            title="المهام المكتملة شهرياً",
                            markers=True)
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

# ================== 7. نظام إدارة العملاء ==================
def manage_customers():
    """إدارة العملاء"""
    st.markdown("<div class='main-header'><h1 style='margin:0;'>👥 إدارة العملاء</h1></div>", unsafe_allow_html=True)
    
    # أزرار سريعة
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ إضافة عميل جديد", use_container_width=True):
            st.session_state.editing_id = "new"
            st.rerun()
    with col2:
        if st.button("📋 تصدير البيانات", use_container_width=True):
            export_customers_data()
    with col3:
        search_term = st.text_input("🔍 بحث", placeholder="اسم/هاتف/بريد")
    with col4:
        filter_type = st.selectbox("فلترة", ["جميع العملاء", "نشط فقط", "متأخر في السداد"])
    
    # عرض قائمة العملاء
    st.markdown("### قائمة العملاء")
    
    # فلترة العملاء
    filtered_customers = st.session_state.customers
    
    if search_term:
        filtered_customers = [c for c in filtered_customers if 
                             search_term.lower() in c.get("name", "").lower() or 
                             search_term in c.get("phone", "") or 
                             search_term.lower() in c.get("email", "").lower()]
    
    if filter_type == "نشط فقط":
        filtered_customers = [c for c in filtered_customers if c.get("status") == "نشط"]
    elif filter_type == "متأخر في السداد":
        filtered_customers = [c for c in filtered_customers if c.get("current_balance", 0) > 0]
    
    # عرض العملاء في شكل بطاقات
    for customer in filtered_customers:
        with st.expander(f"👤 {customer.get('name', '')} - 💰 {customer.get('current_balance', 0):,.0f} ج.م - 📞 {customer.get('phone', '')}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**البريد:** {customer.get('email', 'لا يوجد')}")
                st.write(f"**العنوان:** {customer.get('address', 'لا يوجد')}")
                st.write(f"**نوع العميل:** {customer.get('customer_type', 'فرد')}")
                st.write(f"**تاريخ التسجيل:** {customer.get('registration_date', '')}")
                
                # عرض الفلاتر المثبتة
                if customer.get("filters"):
                    st.write("**الفلاتر المثبتة:**")
                    for filt in customer.get("filters", []):
                        st.write(f"- {filt.get('type', '')} ({filt.get('model', '')}) - تركيب: {filt.get('install_date', '')}")
            
            with col2:
                balance = customer.get("current_balance", 0)
                if balance > 0:
                    st.error(f"مدين: {balance:,.0f} ج.م")
                elif balance < 0:
                    st.success(f"لديه رصيد: {abs(balance):,.0f} ج.م")
                else:
                    st.info("مستوى")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("تعديل", key=f"edit_{customer.get('id')}"):
                        st.session_state.editing_id = customer.get('id')
                        st.rerun()
                with col_btn2:
                    if st.button("حذف", key=f"delete_{customer.get('id')}"):
                        delete_customer(customer.get('id'))
    
    # نموذج إضافة/تعديل عميل
    if st.session_state.editing_id:
        edit_customer_form()

def edit_customer_form():
    """نموذج إضافة/تعديل عميل"""
    if st.session_state.editing_id == "new":
        customer_data = {}
        title = "إضافة عميل جديد"
    else:
        customer_data = next((c for c in st.session_state.customers if c.get("id") == st.session_state.editing_id), {})
        title = f"تعديل عميل: {customer_data.get('name', '')}"
    
    st.markdown(f"### {title}")
    
    with st.form("customer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("اسم العميل*", value=customer_data.get("name", ""))
            phone = st.text_input("رقم الهاتف*", value=customer_data.get("phone", ""))
            email = st.text_input("البريد الإلكتروني", value=customer_data.get("email", ""))
            address = st.text_area("العنوان", value=customer_data.get("address", ""))
        
        with col2:
            company = st.text_input("اسم الشركة", value=customer_data.get("company", ""))
            customer_type = st.selectbox("نوع العميل", ["فرد", "شركة", "مؤسسة حكومية", "مؤسسة خاصة"], 
                                        index=["فرد", "شركة", "مؤسسة حكومية", "مؤسسة خاصة"].index(customer_data.get("customer_type", "فرد")) if customer_data.get("customer_type") in ["فرد", "شركة", "مؤسسة حكومية", "مؤسسة خاصة"] else 0)
            status = st.selectbox("الحالة", ["نشط", "موقوف", "محذوف"], 
                                 index=["نشط", "موقوف", "محذوف"].index(customer_data.get("status", "نشط")) if customer_data.get("status") in ["نشط", "موقوف", "محذوف"] else 0)
            next_maintenance = st.date_input("موعد الصيانة القادم", 
                                           value=datetime.strptime(customer_data.get("next_maintenance", str(datetime.now().date())), "%Y-%m-%d") if customer_data.get("next_maintenance") else datetime.now())
        
        notes = st.text_area("ملاحظات", value=customer_data.get("notes", ""))
        
        # قسم الفلاتر المثبتة
        st.markdown("#### الفلاتر المثبتة")
        if "filters" not in customer_data:
            customer_data["filters"] = []
        
        for i, filt in enumerate(customer_data.get("filters", [])):
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                st.text_input(f"نوع الفلتر {i+1}", value=filt.get("type", ""), key=f"filter_type_{i}")
            with col_f2:
                st.text_input(f"الموديل {i+1}", value=filt.get("model", ""), key=f"filter_model_{i}")
            with col_f3:
                st.date_input(f"تاريخ التركيب {i+1}", 
                            value=datetime.strptime(filt.get("install_date", str(datetime.now().date())), "%Y-%m-%d") if filt.get("install_date") else datetime.now(),
                            key=f"filter_date_{i}")
        
        if st.button("إضافة فلتر جديد"):
            customer_data["filters"].append({"type": "", "model": "", "install_date": str(datetime.now().date())})
            st.rerun()
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            submit = st.form_submit_button("💾 حفظ", use_container_width=True)
        with col_btn2:
            cancel = st.form_submit_button("❌ إلغاء", use_container_width=True)
        with col_btn3:
            if st.session_state.editing_id != "new":
                delete_btn = st.form_submit_button("🗑️ حذف", use_container_width=True)
        
        if submit:
            if name and phone:
                save_customer_data({
                    "id": st.session_state.editing_id if st.session_state.editing_id != "new" else (max([c.get("id", 0) for c in st.session_state.customers], default=0) + 1),
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "address": address,
                    "company": company,
                    "customer_type": customer_type,
                    "status": status,
                    "notes": notes,
                    "next_maintenance": str(next_maintenance),
                    "registration_date": customer_data.get("registration_date", str(datetime.now().date())),
                    "current_balance": customer_data.get("current_balance", 0.0),
                    "filters": customer_data.get("filters", [])
                })
                st.success("تم حفظ بيانات العميل بنجاح!")
                st.session_state.editing_id = None
                st.rerun()
            else:
                st.error("الاسم ورقم الهاتف حقول إلزامية")
        
        if cancel:
            st.session_state.editing_id = None
            st.rerun()

def save_customer_data(customer_data):
    """حفظ بيانات العميل"""
    if st.session_state.editing_id == "new":
        st.session_state.customers.append(customer_data)
    else:
        for i, customer in enumerate(st.session_state.customers):
            if customer.get("id") == st.session_state.editing_id:
                st.session_state.customers[i] = customer_data
                break
    
    save_data("customers.json", st.session_state.customers)

def delete_customer(customer_id):
    """حذف عميل"""
    st.session_state.customers = [c for c in st.session_state.customers if c.get("id") != customer_id]
    save_data("customers.json", st.session_state.customers)
    st.success("تم حذف العميل بنجاح!")
    st.rerun()

def export_customers_data():
    """تصدير بيانات العملاء"""
    import csv
    from io import StringIO
    
    if st.session_state.customers:
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=["ID", "Name", "Phone", "Email", "Address", "Balance"])
        writer.writeheader()
        
        for customer in st.session_state.customers:
            writer.writerow({
                "ID": customer.get("id", ""),
                "Name": customer.get("name", ""),
                "Phone": customer.get("phone", ""),
                "Email": customer.get("email", ""),
                "Address": customer.get("address", ""),
                "Balance": customer.get("current_balance", 0)
            })
        
        st.download_button(
            label="📥 تحميل البيانات كملف CSV",
            data=output.getvalue(),
            file_name="customers_export.csv",
            mime="text/csv"
        )

# ================== 8. نظام إدارة المخزون ==================
def manage_inventory():
    """إدارة المخزون"""
    st.markdown("<div class='main-header'><h1 style='margin:0;'>📦 إدارة المخزون والمستودع</h1></div>", unsafe_allow_html=True)
    
    # أزرار سريعة
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ إضافة صنف جديد", use_container_width=True):
            st.session_state.selected_filter = "new"
            st.rerun()
    with col2:
        category_filter = st.selectbox("فلترة حسب النوع", ["جميع الأصناف", "فلتر مياه", "قطع غيار", "كيميكالات", "أخرى"])
    with col3:
        location_filter = st.selectbox("فلترة حسب الموقع", ["جميع المواقع", "المستودع الرئيسي", "فرع 1", "فرع 2", "عربة الفني"])
    
    # عرض التحذيرات
    low_stock_items = [item for item in st.session_state.inventory if item.get("quantity", 0) < item.get("min_quantity", 5)]
    if low_stock_items:
        st.warning(f"⚠️ هناك {len(low_stock_items)} أصناف تحت الحد الأدنى للمخزون!")
        
        for item in low_stock_items[:3]:
            st.markdown(f"""
            <div class='filter-item' style='border-right: 5px solid #ffaa00;'>
                <strong>{item.get('name', '')} ({item.get('model', '')})</strong><br>
                الكمية الحالية: <strong style='color:#ff4444;'>{item.get('quantity', 0)}</strong> | الحد الأدنى: {item.get('min_quantity', 5)}<br>
                الموقع: {item.get('location', '')}
            </div>
            """, unsafe_allow_html=True)
    
    # عرض قائمة المخزون
    st.markdown("### قائمة المخزون")
    
    filtered_items = st.session_state.inventory
    
    if category_filter != "جميع الأصناف":
        filtered_items = [item for item in filtered_items if item.get("category") == category_filter]
    
    if location_filter != "جميع المواقع":
        filtered_items = [item for item in filtered_items if item.get("location") == location_filter]
    
    # عرض المخزون في شكل جدول
    if filtered_items:
        inventory_df = pd.DataFrame(filtered_items)
        
        # تحديد الألوان للكميات المنخفضة
        def highlight_low_stock(row):
            if row['quantity'] < row['min_quantity']:
                return ['background-color: #ffcccc'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            inventory_df[["name", "model", "type", "quantity", "min_quantity", "price", "location"]].style.apply(highlight_low_stock, axis=1),
            use_container_width=True,
            height=400
        )
    else:
        st.info("لا توجد أصناف في المخزون")
    
    # نموذج إدارة الصنف
    if st.session_state.selected_filter:
        manage_filter_item_form()

def manage_filter_item_form():
    """نموذج إدارة صنف المخزون"""
    if st.session_state.selected_filter == "new":
        item_data = {}
        title = "إضافة صنف جديد للمخزون"
    else:
        item_data = next((item for item in st.session_state.inventory if item.get("id") == st.session_state.selected_filter), {})
        title = f"إدارة: {item_data.get('name', '')}"
    
    st.markdown(f"### {title}")
    
    with st.form("inventory_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("اسم الصنف*", value=item_data.get("name", ""))
            model = st.text_input("الموديل/الرقم التسلسلي", value=item_data.get("model", ""))
            category = st.selectbox("الفئة*", ["فلتر مياه", "قطع غيار", "كيميكالات", "أخرى"], 
                                  index=["فلتر مياه", "قطع غيار", "كيميكالات", "أخرى"].index(item_data.get("category", "فلتر مياه")) if item_data.get("category") in ["فلتر مياه", "قطع غيار", "كيميكالات", "أخرى"] else 0)
            item_type = st.selectbox("النوع*", ["منزلي", "تجاري", "صناعي", "متعدد الأغراض"], 
                                   index=["منزلي", "تجاري", "صناعي", "متعدد الأغراض"].index(item_data.get("type", "منزلي")) if item_data.get("type") in ["منزلي", "تجاري", "صناعي", "متعدد الأغراض"] else 0)
        
        with col2:
            quantity = st.number_input("الكمية الحالية*", min_value=0, value=item_data.get("quantity", 0))
            min_quantity = st.number_input("الحد الأدنى للتنبيه*", min_value=1, value=item_data.get("min_quantity", 5))
            price = st.number_input("سعر البيع*", min_value=0.0, value=float(item_data.get("price", 0.0)))
            cost = st.number_input("سعر التكلفة", min_value=0.0, value=float(item_data.get("cost", 0.0)))
        
        col3, col4 = st.columns(2)
        with col3:
            manufacturer = st.text_input("الشركة المصنعة", value=item_data.get("manufacturer", ""))
            supplier = st.text_input("المورد", value=item_data.get("supplier", ""))
        with col4:
            location = st.selectbox("موقع التخزين", ["المستودع الرئيسي", "فرع 1", "فرع 2", "عربة الفني", "مخزن المؤقت"], 
                                  index=["المستودع الرئيسي", "فرع 1", "فرع 2", "عربة الفني", "مخزن المؤقت"].index(item_data.get("location", "المستودع الرئيسي")) if item_data.get("location") in ["المستودع الرئيسي", "فرع 1", "فرع 2", "عربة الفني", "مخزن المؤقت"] else 0)
            last_restock = st.date_input("تاريخ آخر إعادة تخزين", 
                                       value=datetime.strptime(item_data.get("last_restock", str(datetime.now().date())), "%Y-%m-%d") if item_data.get("last_restock") else datetime.now())
        
        notes = st.text_area("ملاحظات", value=item_data.get("notes", ""))
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            submit = st.form_submit_button("💾 حفظ الصنف", use_container_width=True)
        with col_btn2:
            cancel = st.form_submit_button("❌ إلغاء", use_container_width=True)
        with col_btn3:
            if st.session_state.selected_filter != "new":
                delete_btn = st.form_submit_button("🗑️ حذف الصنف", use_container_width=True)
        
        if submit:
            if name and category:
                save_inventory_item({
                    "id": st.session_state.selected_filter if st.session_state.selected_filter != "new" else (max([i.get("id", 0) for i in st.session_state.inventory], default=0) + 1),
                    "name": name,
                    "model": model,
                    "category": category,
                    "type": item_type,
                    "manufacturer": manufacturer,
                    "quantity": quantity,
                    "min_quantity": min_quantity,
                    "price": price,
                    "cost": cost,
                    "location": location,
                    "supplier": supplier,
                    "last_restock": str(last_restock),
                    "notes": notes
                })
                st.success("تم حفظ الصنف بنجاح!")
                st.session_state.selected_filter = None
                st.rerun()
            else:
                st.error("اسم الصنف والفئة حقول إلزامية")
        
        if cancel:
            st.session_state.selected_filter = None
            st.rerun()

def save_inventory_item(item_data):
    """حفظ صنف المخزون"""
    if st.session_state.selected_filter == "new":
        st.session_state.inventory.append(item_data)
    else:
        for i, item in enumerate(st.session_state.inventory):
            if item.get("id") == st.session_state.selected_filter:
                st.session_state.inventory[i] = item_data
                break
    
    save_data("inventory.json", st.session_state.inventory)

# ================== 9. نظام إدارة المهام ==================
def manage_tasks():
    """إدارة المهام والجدولة"""
    st.markdown("<div class='main-header'><h1 style='margin:0;'>📋 إدارة المهام والجدولة</h1></div>", unsafe_allow_html=True)
    
    # أزرار سريعة
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ مهمة جديدة", use_container_width=True):
            st.session_state.selected_task = "new"
            st.rerun()
    with col2:
        status_filter = st.selectbox("حالة المهمة", ["جميع المهام", "معلقة", "قيد التنفيذ", "مكتملة", "ملغاة"])
    with col3:
        priority_filter = st.selectbox("أولويات", ["جميع الأولويات", "طارئ", "عاجل", "عادي"])
    with col4:
        technician_filter = st.selectbox("الفني", ["جميع الفنيين", "غير معين"] + list(set([t.get("assigned_to", "") for t in st.session_state.tasks if t.get("assigned_to")])))
    
    # عرض تقويم المهام
    st.markdown("### 📅 تقويم المهام لهذا الأسبوع")
    
    today = datetime.now()
    week_tasks = []
    
    for task in st.session_state.tasks:
        scheduled_date = task.get("scheduled_date")
        if scheduled_date:
            try:
                task_date = datetime.strptime(scheduled_date, "%Y-%m-%d")
                days_diff = (task_date - today).days
                if 0 <= days_diff <= 7:  # خلال الأسبوع القادم
                    week_tasks.append({
                        "date": scheduled_date,
                        "customer": task.get("customer_name", ""),
                        "task": task.get("description", ""),
                        "technician": task.get("assigned_to", "غير معين"),
                        "priority": task.get("priority", "عادي")
                    })
            except:
                pass
    
    if week_tasks:
        for day_num in range(8):
            day_date = today + timedelta(days=day_num)
            day_str = day_date.strftime("%Y-%m-%d")
            day_tasks = [t for t in week_tasks if t["date"] == day_str]
            
            if day_tasks:
                st.markdown(f"**{day_date.strftime('%A %Y-%m-%d')}**")
                for task in day_tasks:
                    priority_color = {"طارئ": "#ff4444", "عاجل": "#ffaa00", "عادي": "#00d4ff"}.get(task["priority"], "#00d4ff")
                    st.markdown(f"""
                    <div style='padding: 10px; margin: 5px 0; border-right: 5px solid {priority_color}; border-radius: 5px; background: rgba(255,255,255,0.05);'>
                        <strong>{task['customer']}</strong><br>
                        {task['task']}<br>
                        <small>الفني: {task['technician']}</small>
                    </div>
                    """, unsafe_allow_html=True)
    
    # قائمة المهام المفصلة
    st.markdown("### 📋 قائمة المهام التفصيلية")
    
    filtered_tasks = st.session_state.tasks
    
    if status_filter != "جميع المهام":
        filtered_tasks = [t for t in filtered_tasks if t.get("status") == status_filter]
    
    if priority_filter != "جميع الأولويات":
        filtered_tasks = [t for t in filtered_tasks if t.get("priority") == priority_filter]
    
    if technician_filter not in ["جميع الفنيين", "غير معين"]:
        filtered_tasks = [t for t in filtered_tasks if t.get("assigned_to") == technician_filter]
    elif technician_filter == "غير معين":
        filtered_tasks = [t for t in filtered_tasks if not t.get("assigned_to")]
    
    # عرض المهام
    for task in filtered_tasks:
        with st.expander(f"{task.get('customer_name', '')} - {task.get('description', '')[:50]}... - {task.get('status', '')}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**نوع المهمة:** {task.get('task_type', '')}")
                st.write(f"**الأولوية:** <span class='status-{task.get('priority', '')}'>{task.get('priority', '')}</span>", unsafe_allow_html=True)
                st.write(f"**الحالة:** <span class='status-{task.get('status', '')}'>{task.get('status', '')}</span>", unsafe_allow_html=True)
                st.write(f"**الفني المكلف:** {task.get('assigned_to', 'غير معين')}")
                st.write(f"**التاريخ المجدول:** {task.get('scheduled_date', '')}")
                st.write(f"**ملاحظات:** {task.get('notes', '')}")
            
            with col2:
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("تعديل", key=f"edit_task_{task.get('id')}"):
                        st.session_state.selected_task = task.get('id')
                        st.rerun()
                with col_btn2:
                    if st.button("حذف", key=f"delete_task_{task.get('id')}"):
                        delete_task(task.get('id'))
    
    # نموذج إدارة المهمة
    if st.session_state.selected_task:
        manage_task_form()

def manage_task_form():
    """نموذج إدارة المهمة"""
    if st.session_state.selected_task == "new":
        task_data = {}
        title = "إنشاء مهمة جديدة"
    else:
        task_data = next((t for t in st.session_state.tasks if t.get("id") == st.session_state.selected_task), {})
        title = f"تعديل مهمة: {task_data.get('customer_name', '')}"
    
    st.markdown(f"### {title}")
    
    with st.form("task_form"):
        # اختيار العميل
        customer_options = {c["id"]: c["name"] for c in st.session_state.customers}
        selected_customer = st.selectbox("العميل*", 
                                        options=list(customer_options.keys()), 
                                        format_func=lambda x: customer_options.get(x, ""),
                                        index=list(customer_options.keys()).index(task_data.get("customer_id")) if task_data.get("customer_id") in customer_options else 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            task_type = st.selectbox("نوع المهمة*", ["صيانة دورية", "صيانة طارئة", "تركيب جديد", "إصلاح عطل", "فحص دوري", "تغيير فلاتر"], 
                                   index=["صيانة دورية", "صيانة طارئة", "تركيب جديد", "إصلاح عطل", "فحص دوري", "تغيير فلاتر"].index(task_data.get("task_type", "صيانة دورية")) if task_data.get("task_type") in ["صيانة دورية", "صيانة طارئة", "تركيب جديد", "إصلاح عطل", "فحص دوري", "تغيير فلاتر"] else 0)
            priority = st.selectbox("الأولوية*", ["عادي", "عاجل", "طارئ"], 
                                  index=["عادي", "عاجل", "طارئ"].index(task_data.get("priority", "عادي")) if task_data.get("priority") in ["عادي", "عاجل", "طارئ"] else 0)
        
        with col2:
            status = st.selectbox("الحالة*", ["معلقة", "قيد التنفيذ", "مكتملة", "ملغاة"], 
                                index=["معلقة", "قيد التنفيذ", "مكتملة", "ملغاة"].index(task_data.get("status", "معلقة")) if task_data.get("status") in ["معلقة", "قيد التنفيذ", "مكتملة", "ملغاة"] else 0)
            
            # قائمة الفنيين
            technicians = load_data("technicians.json")
            tech_names = [t.get("name", "") for t in technicians if t.get("name")]
            assigned_to = st.selectbox("الفني المكلف", ["غير معين"] + tech_names, 
                                      index=(["غير معين"] + tech_names).index(task_data.get("assigned_to", "غير معين")) if task_data.get("assigned_to") in ["غير معين"] + tech_names else 0)
        
        description = st.text_area("وصف المهمة*", value=task_data.get("description", ""), height=100)
        scheduled_date = st.date_input("التاريخ المجدول*", 
                                      value=datetime.strptime(task_data.get("scheduled_date", str(datetime.now().date())), "%Y-%m-%d") if task_data.get("scheduled_date") else datetime.now())
        
        # قسم القطع المستخدمة
        st.markdown("#### القطع المستخدمة")
        
        if "used_items" not in task_data:
            task_data["used_items"] = []
        
        inventory_items = {item["id"]: f"{item['name']} ({item['model']}) - متاح: {item['quantity']}" for item in st.session_state.inventory}
        
        for i, used_item in enumerate(task_data.get("used_items", [])):
            col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
            with col_i1:
                item_id = st.selectbox(f"القطعة {i+1}", 
                                      options=list(inventory_items.keys()),
                                      format_func=lambda x: inventory_items.get(x, ""),
                                      index=list(inventory_items.keys()).index(used_item.get("item_id")) if used_item.get("item_id") in inventory_items else 0,
                                      key=f"item_{i}")
            with col_i2:
                quantity = st.number_input(f"الكمية {i+1}", min_value=1, value=used_item.get("quantity", 1), key=f"qty_{i}")
            with col_i3:
                if st.button("🗑️", key=f"remove_item_{i}"):
                    task_data["used_items"].pop(i)
                    st.rerun()
        
        if st.button("➕ إضافة قطعة"):
            task_data["used_items"].append({"item_id": 0, "quantity": 1})
            st.rerun()
        
        notes = st.text_area("ملاحظات إضافية", value=task_data.get("notes", ""))
        
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            submit = st.form_submit_button("💾 حفظ المهمة", use_container_width=True)
        with col_btn2:
            cancel = st.form_submit_button("❌ إلغاء", use_container_width=True)
        with col_btn3:
            if st.session_state.selected_task != "new":
                delete_btn = st.form_submit_button("🗑️ حذف المهمة", use_container_width=True)
        
        if submit:
            if selected_customer and description:
                save_task_data({
                    "id": st.session_state.selected_task if st.session_state.selected_task != "new" else (max([t.get("id", 0) for t in st.session_state.tasks], default=0) + 1),
                    "customer_id": selected_customer,
                    "customer_name": customer_options.get(selected_customer, ""),
                    "task_type": task_type,
                    "priority": priority,
                    "status": status,
                    "assigned_to": assigned_to if assigned_to != "غير معين" else "",
                    "scheduled_date": str(scheduled_date),
                    "description": description,
                    "notes": notes,
                    "used_items": task_data.get("used_items", []),
                    "assigned_date": task_data.get("assigned_date", str(datetime.now().date())),
                    "total_cost": task_data.get("total_cost", 0.0),
                    "total_price": task_data.get("total_price", 0.0)
                })
                st.success("تم حفظ المهمة بنجاح!")
                st.session_state.selected_task = None
                st.rerun()
            else:
                st.error("العميل ووصف المهمة حقول إلزامية")
        
        if cancel:
            st.session_state.selected_task = None
            st.rerun()

def save_task_data(task_data):
    """حفظ بيانات المهمة"""
    if st.session_state.selected_task == "new":
        st.session_state.tasks.append(task_data)
    else:
        for i, task in enumerate(st.session_state.tasks):
            if task.get("id") == st.session_state.selected_task:
                st.session_state.tasks[i] = task_data
                break
    
    save_data("tasks.json", st.session_state.tasks)

def delete_task(task_id):
    """حذف مهمة"""
    st.session_state.tasks = [t for t in st.session_state.tasks if t.get("id") != task_id]
    save_data("tasks.json", st.session_state.tasks)
    st.success("تم حذف المهمة بنجاح!")
    st.rerun()

# ================== 10. نظام التقارير والتحليلات ==================
def reports_and_analytics():
    """التقارير والتحليلات"""
    st.markdown("<div class='main-header'><h1 style='margin:0;'>📊 التقارير والتحليلات</h1></div>", unsafe_allow_html=True)
    
    # اختيار نوع التقرير
    report_type = st.selectbox("اختر نوع التقرير", [
        "التقرير المالي الشامل",
        "تقرير أداء الفنيين",
        "تقرير المبيعات",
        "تقرير المخزون",
        "تقرير رضا العملاء",
        "تقرير الصيانة الدورية"
    ])
    
    # اختيار الفترة
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("من تاريخ", value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("إلى تاريخ", value=datetime.now())
    
    if st.button("توليد التقرير", use_container_width=True):
        generate_report(report_type, start_date, end_date)

def generate_report(report_type, start_date, end_date):
    """توليد التقرير"""
    st.markdown(f"### 📄 {report_type}")
    st.markdown(f"**الفترة:** {start_date} إلى {end_date}")
    
    if report_type == "التقرير المالي الشامل":
        financial_report(start_date, end_date)
    elif report_type == "تقرير أداء الفنيين":
        technicians_performance_report(start_date, end_date)
    elif report_type == "تقرير المبيعات":
        sales_report(start_date, end_date)
    elif report_type == "تقرير المخزون":
        inventory_report()
    elif report_type == "تقرير الصيانة الدورية":
        maintenance_report(start_date, end_date)

def financial_report(start_date, end_date):
    """التقرير المالي"""
    # حساب الإيرادات
    total_revenue = sum(c.get("total_spent", 0) for c in st.session_state.customers)
    
    # حساب المستحقات
    total_receivables = sum(c.get("current_balance", 0) for c in st.session_state.customers if c.get("current_balance", 0) > 0)
    
    # حساب المهام المكتملة
    completed_tasks = [t for t in st.session_state.tasks if t.get("status") == "مكتملة"]
    completed_tasks_count = len(completed_tasks)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("إجمالي الإيرادات", f"{total_revenue:,.0f} ج.م")
    with col2:
        st.metric("إجمالي المستحقات", f"{total_receivables:,.0f} ج.م")
    with col3:
        st.metric("المهام المكتملة", f"{completed_tasks_count}")
    
    # مخطط الإيرادات
    if st.session_state.customers:
        customers_df = pd.DataFrame(st.session_state.customers)
        if "registration_date" in customers_df.columns:
            customers_df["month"] = customers_df["registration_date"].apply(lambda x: str(x)[:7] if x else None)
            monthly_revenue = customers_df.groupby("month")["total_spent"].sum().reset_index()
            
            if not monthly_revenue.empty:
                fig = px.bar(monthly_revenue, x="month", y="total_spent", 
                           title="الإيرادات الشهرية")
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

def technicians_performance_report(start_date, end_date):
    """تقرير أداء الفنيين"""
    technicians = load_data("technicians.json")
    
    if not technicians:
        st.info("لا توجد بيانات للفنيين")
        return
    
    performance_data = []
    
    for tech in technicians:
        tech_name = tech.get("name", "")
        tech_tasks = [t for t in st.session_state.tasks if t.get("assigned_to") == tech_name]
        completed_tasks = [t for t in tech_tasks if t.get("status") == "مكتملة"]
        
        performance_data.append({
            "الفني": tech_name,
            "إجمالي المهام": len(tech_tasks),
            "المهام المكتملة": len(completed_tasks),
            "نسبة الإنجاز": f"{(len(completed_tasks) / len(tech_tasks) * 100 if tech_tasks else 0):.1f}%"
        })
    
    if performance_data:
        df = pd.DataFrame(performance_data)
        st.dataframe(df, use_container_width=True)
        
        # مخطط أداء الفنيين
        fig = px.bar(df, x="الفني", y="المهام المكتملة", 
                    title="أداء الفنيين (المهام المكتملة)")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def inventory_report():
    """تقرير المخزون"""
    low_stock_items = [item for item in st.session_state.inventory if item.get("quantity", 0) < item.get("min_quantity", 5)]
    
    st.markdown("### 📦 تقرير المخزون")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_items = len(st.session_state.inventory)
        st.metric("إجمالي الأصناف", total_items)
    
    with col2:
        total_value = sum(item.get("quantity", 0) * item.get("price", 0) for item in st.session_state.inventory)
        st.metric("القيمة الإجمالية", f"{total_value:,.0f} ج.م")
    
    with col3:
        st.metric("الأصناف المنخفضة", len(low_stock_items))
    
    if low_stock_items:
        st.markdown("### ⚠️ الأصناف تحت الحد الأدنى")
        low_stock_df = pd.DataFrame(low_stock_items)[["name", "model", "quantity", "min_quantity", "location"]]
        st.dataframe(low_stock_df, use_container_width=True)

def maintenance_report(start_date, end_date):
    """تقرير الصيانة الدورية"""
    # المهام المجدولة للصيانة
    maintenance_tasks = [t for t in st.session_state.tasks if t.get("task_type") in ["صيانة دورية", "تغيير فلاتر"]]
    
    st.markdown("### 🔧 تقرير الصيانة الدورية")
    
    col1, col2 = st.columns(2)
    
    with col1:
        scheduled = len([t for t in maintenance_tasks if t.get("status") in ["معلقة", "قيد التنفيذ"]])
        st.metric("المهام المجدولة", scheduled)
    
    with col2:
        completed = len([t for t in maintenance_tasks if t.get("status") == "مكتملة"])
        st.metric("المهام المكتملة", completed)
    
    # العملاء القريبين من موعد الصيانة
    upcoming_clients = []
    today = datetime.now()
    
    for customer in st.session_state.customers:
        next_maintenance = customer.get("next_maintenance")
        if next_maintenance:
            try:
                maintenance_date = datetime.strptime(next_maintenance, "%Y-%m-%d")
                days_diff = (maintenance_date - today).days
                if 0 <= days_diff <= 30:
                    upcoming_clients.append({
                        "العميل": customer.get("name"),
                        "موعد الصيانة": next_maintenance,
                        "الأيام المتبقية": days_diff,
                        "الهاتف": customer.get("phone", "")
                    })
            except:
                pass
    
    if upcoming_clients:
        st.markdown("### 📅 العملاء القريبين من موعد الصيانة (خلال 30 يوم)")
        upcoming_df = pd.DataFrame(upcoming_clients)
        st.dataframe(upcoming_df.sort_values("الأيام المتبقية"), use_container_width=True)

# ================== 11. القائمة الجانبية الرئيسية ==================
def main_sidebar():
    """القائمة الجانبية الرئيسية"""
    with st.sidebar:
        st.markdown("<h2 style='text-align:center; color:#00d4ff;'>💧 FilterPro</h2>", unsafe_allow_html=True)
        
        if st.session_state.user:
            st.markdown(f"<p style='text-align:center;'>👤 {st.session_state.user}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; font-size:12px; opacity:0.7;'>{st.session_state.role}</p>", unsafe_allow_html=True)
            st.divider()
        
        # القائمة الرئيسية
        menu_items = [
            {"icon": "📊", "name": "لوحة التحكم", "page": "dashboard"},
            {"icon": "👥", "name": "إدارة العملاء", "page": "customers"},
            {"icon": "📋", "name": "المهام والجدولة", "page": "tasks"},
            {"icon": "📦", "name": "إدارة المخزون", "page": "inventory"},
            {"icon": "📊", "name": "التقارير والتحليلات", "page": "reports"},
            {"icon": "🛠️", "name": "إدارة الفنيين", "page": "technicians"},
            {"icon": "📝", "name": "العقود والاشتراكات", "page": "contracts"},
            {"icon": "💰", "name": "الفواتير والمبيعات", "page": "invoices"},
            {"icon": "⚙️", "name": "الإعدادات", "page": "settings"}
        ]
        
        for item in menu_items:
            if st.button(f"{item['icon']} {item['name']}", use_container_width=True, key=f"menu_{item['page']}"):
                st.session_state.page = item["page"]
                st.rerun()
        
        st.divider()
        
        if st.session_state.user:
            if st.button("🚪 تسجيل الخروج", use_container_width=True):
                st.session_state.user = None
                st.session_state.role = None
                st.session_state.page = "login"
                st.rerun()

# ================== 12. الوظائف الإضافية ==================
def manage_technicians():
    """إدارة الفنيين"""
    st.markdown("<div class='main-header'><h1 style='margin:0;'>🛠️ إدارة الفنيين والموظفين</h1></div>", unsafe_allow_html=True)
    
    # عرض قائمة الفنيين
    technicians = load_data("technicians.json")
    
    if technicians:
        for tech in technicians:
            with st.expander(f"🛠️ {tech.get('name', '')} - {tech.get('title', 'فني')}", expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**الهاتف:** {tech.get('phone', '')}")
                    st.write(f"**البريد:** {tech.get('email', '')}")
                    st.write(f"**التخصص:** {tech.get('specialty', 'عام')}")
                    st.write(f"**تاريخ التعيين:** {tech.get('hire_date', '')}")
                    
                    # حساب أداء الفني
                    tech_tasks = [t for t in st.session_state.tasks if t.get("assigned_to") == tech.get("name")]
                    completed_tasks = [t for t in tech_tasks if t.get("status") == "مكتملة"]
                    
                    st.write(f"**المهام المكتملة:** {len(completed_tasks)} من {len(tech_tasks)}")
                
                with col2:
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("تعديل", key=f"edit_tech_{tech.get('id')}"):
                            pass
                    with col_btn2:
                        if st.button("حذف", key=f"delete_tech_{tech.get('id')}"):
                            pass
    
    # نموذج إضافة فني
    with st.form("add_technician"):
        st.markdown("### إضافة فني جديد")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("اسم الفني")
            phone = st.text_input("رقم الهاتف")
            email = st.text_input("البريد الإلكتروني")
        
        with col2:
            title = st.selectbox("المسمى الوظيفي", ["فني", "فني أول", "مشرف", "مدير عمليات"])
            specialty = st.selectbox("التخصص", ["فلاتر مياه", "فلاتر هواء", "صيانة عامة", "تركيب"])
            hire_date = st.date_input("تاريخ التعيين", value=datetime.now())
        
        if st.form_submit_button("إضافة الفني"):
            new_tech = {
                "id": max([t.get("id", 0) for t in technicians], default=0) + 1,
                "name": name,
                "phone": phone,
                "email": email,
                "title": title,
                "specialty": specialty,
                "hire_date": str(hire_date),
                "status": "نشط"
            }
            technicians.append(new_tech)
            save_data("technicians.json", technicians)
            st.success("تم إضافة الفني بنجاح!")
            st.rerun()

def manage_contracts():
    """إدارة العقود والاشتراكات"""
    st.markdown("<div class='main-header'><h1 style='margin:0;'>📝 إدارة العقود والاشتراكات</h1></div>", unsafe_allow_html=True)
    
    # عرض العقود النشطة
    contracts = load_data("contracts.json")
    
    if contracts:
        active_contracts = [c for c in contracts if c.get("status") == "نشط"]
        expired_contracts = [c for c in contracts if c.get("status") == "منتهي"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("العقود النشطة", len(active_contracts))
        
        with col2:
            st.metric("العقود المنتهية", len(expired_contracts))
        
        # عرض العقود النشطة
        st.markdown("### 📄 العقود النشطة")
        for contract in active_contracts:
            with st.expander(f"{contract.get('customer_name', '')} - {contract.get('contract_type', '')}", expanded=False):
                st.write(f"**رقم العقد:** {contract.get('id', '')}")
                st.write(f"**تاريخ البدء:** {contract.get('start_date', '')}")
                st.write(f"**تاريخ الانتهاء:** {contract.get('end_date', '')}")
                st.write(f"**القيمة الإجمالية:** {contract.get('total_amount', 0):,.0f} ج.م")
                st.write(f"**المبلغ المدفوع:** {contract.get('paid_amount', 0):,.0f} ج.م")
                st.write(f"**المتبقي:** {contract.get('remaining_amount', 0):,.0f} ج.م")
                
                # حساب الأيام المتبقية
                try:
                    end_date = datetime.strptime(contract.get("end_date", ""), "%Y-%m-%d")
                    days_left = (end_date - datetime.now()).days
                    
                    if days_left < 0:
                        st.error("منتهي")
                    elif days_left <= 30:
                        st.warning(f"ينتهي خلال {days_left} يوم")
                    else:
                        st.success(f"متبقي {days_left} يوم")
                except:
                    pass
    
    # نموذج إنشاء عقد جديد
    with st.form("add_contract"):
        st.markdown("### إنشاء عقد جديد")
        
        # اختيار العميل
        customer_options = {c["id"]: c["name"] for c in st.session_state.customers}
        customer_id = st.selectbox("العميل", options=list(customer_options.keys()), 
                                  format_func=lambda x: customer_options.get(x, ""))
        
        col1, col2 = st.columns(2)
        
        with col1:
            contract_type = st.selectbox("نوع العقد", ["صيانة سنوية", "صيانة نصف سنوية", "صيانة ربع سنوية", "عقد تركيب", "عقد صيانة شامل"])
            start_date = st.date_input("تاريخ البدء", value=datetime.now())
            end_date = st.date_input("تاريخ الانتهاء", value=datetime.now() + timedelta(days=365))
        
        with col2:
            total_amount = st.number_input("القيمة الإجمالية", min_value=0.0, value=0.0)
            payment_method = st.selectbox("طريقة الدفع", ["كاش", "تحويل بنكي", "أقساط", "بطاقة ائتمان"])
            installments = st.number_input("عدد الأقساط", min_value=1, max_value=24, value=1)
        
        contract_details = st.text_area("تفاصيل العقد")
        
        if st.form_submit_button("إنشاء العقد"):
            new_contract = {
                "id": max([c.get("id", 0) for c in contracts], default=0) + 1,
                "customer_id": customer_id,
                "customer_name": customer_options.get(customer_id, ""),
                "contract_type": contract_type,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "total_amount": total_amount,
                "paid_amount": 0.0,
                "remaining_amount": total_amount,
                "payment_method": payment_method,
                "installments": installments,
                "details": contract_details,
                "status": "نشط"
            }
            contracts.append(new_contract)
            save_data("contracts.json", contracts)
            st.success("تم إنشاء العقد بنجاح!")
            st.rerun()

def manage_invoices():
    """إدارة الفواتير والمبيعات"""
    st.markdown("<div class='main-header'><h1 style='margin:0;'>💰 إدارة الفواتير والمبيعات</h1></div>", unsafe_allow_html=True)
    
    # إحصائيات سريعة
    invoices = load_data("invoices.json")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_invoices = len(invoices)
        st.metric("إجمالي الفواتير", total_invoices)
    
    with col2:
        paid_invoices = len([i for i in invoices if i.get("status") == "مدفوع"])
        st.metric("الفواتير المدفوعة", paid_invoices)
    
    with col3:
        pending_invoices = len([i for i in invoices if i.get("status") == "غير مدفوع"])
        st.metric("الفواتير المعلقة", pending_invoices)
    
    with col4:
        total_amount = sum(i.get("total_amount", 0) for i in invoices)
        st.metric("القيمة الإجمالية", f"{total_amount:,.0f} ج.م")
    
    # إنشاء فاتورة جديدة
    with st.form("create_invoice"):
        st.markdown("### إنشاء فاتورة جديدة")
        
        # اختيار العميل
        customer_options = {c["id"]: c["name"] for c in st.session_state.customers}
        customer_id = st.selectbox("العميل", options=list(customer_options.keys()), 
                                  format_func=lambda x: customer_options.get(x, ""), key="invoice_customer")
        
        invoice_date = st.date_input("تاريخ الفاتورة", value=datetime.now())
        due_date = st.date_input("تاريخ الاستحقاق", value=datetime.now() + timedelta(days=30))
        
        # إضافة الأصناف
        st.markdown("#### أصناف الفاتورة")
        
        items = []
        for i in range(3):
            col_i1, col_i2, col_i3 = st.columns([3, 1, 1])
            with col_i1:
                item_name = st.text_input(f"وصف الصنف {i+1}", key=f"inv_item_{i}")
            with col_i2:
                quantity = st.number_input(f"الكمية {i+1}", min_value=1, value=1, key=f"inv_qty_{i}")
            with col_i3:
                price = st.number_input(f"السعر {i+1}", min_value=0.0, value=0.0, key=f"inv_price_{i}")
            
            if item_name:
                items.append({
                    "description": item_name,
                    "quantity": quantity,
                    "price": price,
                    "total": quantity * price
                })
        
        if st.button("➕ إضافة صنف آخر"):
            st.rerun()
        
        notes = st.text_area("ملاحظات الفاتورة")
        
        if st.form_submit_button("إنشاء الفاتورة"):
            total_amount = sum(item["total"] for item in items)
            
            new_invoice = {
                "id": max([i.get("id", 0) for i in invoices], default=0) + 1,
                "customer_id": customer_id,
                "customer_name": customer_options.get(customer_id, ""),
                "invoice_date": str(invoice_date),
                "due_date": str(due_date),
                "items": items,
                "total_amount": total_amount,
                "paid_amount": 0.0,
                "remaining_amount": total_amount,
                "notes": notes,
                "status": "غير مدفوع"
            }
            invoices.append(new_invoice)
            save_data("invoices.json", invoices)
            st.success("تم إنشاء الفاتورة بنجاح!")
            st.rerun()

def settings_page():
    """صفحة الإعدادات"""
    st.markdown("<div class='main-header'><h1 style='margin:0;'>⚙️ إعدادات النظام</h1></div>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["عام", "المستخدمين", "الاشعارات", "النسخ الاحتياطي"])
    
    with tab1:
        st.markdown("### الإعدادات العامة")
        
        company_name = st.text_input("اسم الشركة", value="شركة فلاتر المياه")
        company_logo = st.file_uploader("شعار الشركة", type=["png", "jpg", "jpeg"])
        currency = st.selectbox("العملة", ["جنيه مصري (ج.م)", "ريال سعودي (ر.س)", "دينار كويتي (د.ك)", "دولار أمريكي ($)"])
        timezone = st.selectbox("المنطقة الزمنية", ["Africa/Cairo", "Asia/Riyadh", "Asia/Dubai", "Europe/London"])
        
        if st.button("حفظ الإعدادات العامة", use_container_width=True):
            st.success("تم حفظ الإعدادات!")
    
    with tab2:
        st.markdown("### إدارة المستخدمين والصلاحيات")
        
        users = [
            {"name": "محمد أحمد", "role": "مدير النظام", "status": "نشط"},
            {"name": "أحمد محمود", "role": "مدير المبيعات", "status": "نشط"},
            {"name": "خالد سعيد", "role": "فني", "status": "نشط"},
        ]
        
        for user in users:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"👤 {user['name']}")
            with col2:
                st.write(user['role'])
            with col3:
                st.selectbox("الحالة", ["نشط", "موقوف"], key=f"user_status_{user['name']}", index=0 if user['status'] == "نشط" else 1)
    
    with tab3:
        st.markdown("### إعدادات الإشعارات")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.checkbox("إشعارات البريد الإلكتروني", value=True)
            st.checkbox("إشعارات الصيانة الدورية", value=True)
            st.checkbox("إشعارات المهام الجديدة", value=True)
        
        with col2:
            st.checkbox("إشعارات الدفع", value=True)
            st.checkbox("إشعارات المخزون المنخفض", value=True)
            st.checkbox("إشعارات العقود المنتهية", value=True)
        
        notification_email = st.text_input("البريد الإلكتروني للإشعارات")
        
        if st.button("حفظ إعدادات الإشعارات", use_container_width=True):
            st.success("تم حفظ الإعدادات!")
    
    with tab4:
        st.markdown("### النسخ الاحتياطي والاستعادة")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("إنشاء نسخة احتياطية", use_container_width=True):
                create_backup()
        
        with col2:
            backup_file = st.file_uploader("استعادة نسخة احتياطية", type=["json", "zip"])
            if backup_file and st.button("استعادة النسخة", use_container_width=True):
                st.success("تم استعادة النسخة الاحتياطية!")

def create_backup():
    """إنشاء نسخة احتياطية"""
    import zipfile
    import io
    
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w') as zip_file:
        for key, filename in DATA_FILES.items():
            if os.path.exists(filename):
                zip_file.write(filename)
    
    buffer.seek(0)
    
    st.download_button(
        label="📥 تحميل النسخة الاحتياطية",
        data=buffer,
        file_name=f"backup_filterpro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
        mime="application/zip"
    )

# ================== 13. الدالة الرئيسية للتشغيل ==================
def main():
    """الدالة الرئيسية للتشغيل"""
    # تهيئة النظام
    init_data_files()
    init_session_state()
    
    # تحديد الصفحة الحالية
    if not st.session_state.user:
        if st.session_state.page == "register":
            register_system()
        else:
            login_system()
    else:
        # عرض القائمة الجانبية
        main_sidebar()
        
        # عرض الصفحة المحددة
        if st.session_state.page == "dashboard":
            dashboard()
        elif st.session_state.page == "customers":
            manage_customers()
        elif st.session_state.page == "tasks":
            manage_tasks()
        elif st.session_state.page == "inventory":
            manage_inventory()
        elif st.session_state.page == "reports":
            reports_and_analytics()
        elif st.session_state.page == "technicians":
            manage_technicians()
        elif st.session_state.page == "contracts":
            manage_contracts()
        elif st.session_state.page == "invoices":
            manage_invoices()
        elif st.session_state.page == "settings":
            settings_page()
        else:
            dashboard()

# ================== 14. تشغيل التطبيق ==================
if __name__ == "__main__":
    main()
