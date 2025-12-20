import streamlit as st
import json
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from dateutil.relativedelta import relativedelta

# ================== إعداد الصفحة ==================
st.set_page_config(
    page_title="Power Life | إدارة العملاء المتقدمة",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== الملفات ==================
USERS_FILE = "users.json"
CUSTOMERS_FILE = "customers.json"
TICKETS_FILE = "tickets.json"
PRODUCTS_FILE = "products.json"

# ================== دوال مساعدة ==================
def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ================== تحميل البيانات ==================
@st.cache_data(ttl=60)
def load_all_data():
    return {
        "users": load_json(USERS_FILE, []),
        "customers": load_json(CUSTOMERS_FILE, []),
        "tickets": load_json(TICKETS_FILE, []),
        "products": load_json(PRODUCTS_FILE, [])
    }

data = load_all_data()
users = data["users"]
customers = data["customers"]
tickets = data["tickets"]
products = data["products"]

# ================== إنشاء المدير ==================
if not any(u.get("username") == "Abdallah" for u in users):
    users.append({
        "username": "Abdallah",
        "password": "772001",
        "role": "admin",
        "created_at": datetime.now().strftime("%Y-%m-%d")
    })
    save_json(USERS_FILE, users)

# ================== الجلسة ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ================== تسجيل الخروج ==================
def logout():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

# ================== تسجيل الدخول ==================
def login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("💧 Power Life")
        st.markdown("---")
        
        with st.container(border=True):
            st.subheader("تسجيل الدخول")
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("تسجيل الدخول", use_container_width=True):
                    user = next(
                        (u for u in users if u["username"] == username and u["password"] == password),
                        None
                    )
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.current_user = user
                        st.success("تم تسجيل الدخول بنجاح")
                        st.rerun()
                    else:
                        st.error("بيانات الدخول غير صحيحة")
            
            with col_btn2:
                if st.button("إعادة التحميل", use_container_width=True):
                    st.rerun()

# ================== الميزة 1: نظام نقاط الولاء ==================
def loyalty_points_system():
    st.subheader("🎯 نظام نقاط الولاء")
    
    tab1, tab2, tab3 = st.tabs(["زيادة النقاط", "خصم النقاط", "تصنيف العملاء"])
    
    with tab1:
        with st.form("add_points"):
            customer_id = st.selectbox(
                "اختر العميل",
                options=[c["id"] for c in customers],
                format_func=lambda x: f"{next(c['name'] for c in customers if c['id'] == x)} (ID: {x})"
            )
            points = st.number_input("عدد النقاط", min_value=1, max_value=1000, value=10)
            reason = st.selectbox("السبب", ["زيارة دورية", "شراء منتج", "إحالة عميل", "أخرى"])
            
            if st.form_submit_button("إضافة النقاط"):
                customer = next(c for c in customers if c["id"] == customer_id)
                if "loyalty_points" not in customer:
                    customer["loyalty_points"] = 0
                customer["loyalty_points"] += points
                customer["last_points_update"] = datetime.now().strftime("%Y-%m-%d")
                save_json(CUSTOMERS_FILE, customers)
                st.success(f"تمت إضافة {points} نقطة للعميل {customer['name']}")
    
    with tab2:
        with st.form("redeem_points"):
            customer_id = st.selectbox(
                "اختر العميل",
                options=[c["id"] for c in customers if c.get("loyalty_points", 0) > 0],
                format_func=lambda x: f"{next(c['name'] for c in customers if c['id'] == x)} - النقاط: {next(c.get('loyalty_points', 0) for c in customers if c['id'] == x)}",
                key="redeem_customer"
            )
            redeem_points = st.number_input(
                "النقاط للخصم",
                min_value=1,
                max_value=next(c.get("loyalty_points", 0) for c in customers if c["id"] == customer_id)
            )
            
            if st.form_submit_button("خصم النقاط"):
                customer = next(c for c in customers if c["id"] == customer_id)
                customer["loyalty_points"] -= redeem_points
                save_json(CUSTOMERS_FILE, customers)
                st.success(f"تم خصم {redeem_points} نقطة من رصيد العميل")
    
    with tab3:
        loyal_customers = sorted(
            [c for c in customers if c.get("loyalty_points", 0) > 0],
            key=lambda x: x.get("loyalty_points", 0),
            reverse=True
        )[:10]
        
        if loyal_customers:
            df = pd.DataFrame(loyal_customers)[["name", "phone", "loyalty_points", "category"]]
            st.dataframe(df, use_container_width=True)
            
            # رسم بياني للنقاط
            fig = px.bar(df, x="name", y="loyalty_points", color="category",
                         title="أفضل 10 عملاء حسب نقاط الولاء")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد نقاط ولاء مسجلة")

# ================== الميزة 2: لوحة التقارير ==================
def analytics_dashboard():
    st.subheader("📊 لوحة التقارير والإحصاءات")
    
    # الإحصائيات الرئيسية
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_customers = len(customers)
        st.metric("إجمالي العملاء", total_customers)
    
    with col2:
        overdue_customers = len([c for c in customers 
                                if (datetime.now() - datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")).days > 30])
        st.metric("عملاء متأخرين", overdue_customers, delta=f"-{overdue_customers/total_customers*100:.1f}%" if total_customers else 0)
    
    with col3:
        total_points = sum(c.get("loyalty_points", 0) for c in customers)
        st.metric("إجمالي النقاط", total_points)
    
    with col4:
        tickets_open = len([t for t in tickets if t.get("status") == "مفتوحة"])
        st.metric("تذاكر مفتوحة", tickets_open)
    
    # المخططات
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # توزيع العملاء حسب التصنيف
        if customers:
            categories = pd.DataFrame(customers)["category"].value_counts()
            fig1 = px.pie(values=categories.values, names=categories.index,
                         title="توزيع العملاء حسب التصنيف")
            st.plotly_chart(fig1, use_container_width=True)
    
    with col_chart2:
        # عملاء جدد خلال الشهر
        one_month_ago = datetime.now() - timedelta(days=30)
        new_customers = [c for c in customers 
                        if datetime.strptime(c.get("created_at", "2000-01-01"), "%Y-%m-%d") >= one_month_ago]
        
        if new_customers:
            dates = [datetime.strptime(c.get("created_at"), "%Y-%m-%d").date() for c in new_customers]
            date_counts = pd.Series(dates).value_counts().sort_index()
            
            fig2 = px.line(x=date_counts.index, y=date_counts.values,
                          title="العملاء الجدد خلال 30 يوم",
                          labels={"x": "التاريخ", "y": "عدد العملاء"})
            st.plotly_chart(fig2, use_container_width=True)
    
    # جدول الزيارات المتأخرة
    st.subheader("📋 تفاصيل الزيارات المتأخرة")
    overdue_list = []
    for c in customers:
        try:
            last_visit = datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")
            days_overdue = (datetime.now() - last_visit).days - 30
            if days_overdue > 0:
                overdue_list.append({
                    "اسم العميل": c["name"],
                    "الهاتف": c["phone"],
                    "آخر زيارة": c["last_visit"],
                    "أيام التأخير": days_overdue,
                    "التصنيف": c.get("category", "غير محدد")
                })
        except:
            continue
    
    if overdue_list:
        df_overdue = pd.DataFrame(overdue_list)
        st.dataframe(df_overdue.sort_values("أيام التأخير", ascending=False), use_container_width=True)
    else:
        st.success("🎉 لا توجد زيارات متأخرة")

# ================== الميزة 3: نظام التذاكر ==================
def ticket_system():
    st.subheader("🎫 نظام تذاكر الدعم")
    
    tab1, tab2, tab3 = st.tabs(["تذكرة جديدة", "التذاكر النشطة", "سجل التذاكر"])
    
    with tab1:
        with st.form("new_ticket"):
            col1, col2 = st.columns(2)
            with col1:
                customer_id = st.selectbox(
                    "العميل",
                    options=[c["id"] for c in customers],
                    format_func=lambda x: f"{next(c['name'] for c in customers if c['id'] == x)}"
                )
                priority = st.selectbox("الأولوية", ["منخفضة", "متوسطة", "عاجلة"])
            
            with col2:
                assigned_to = st.selectbox(
                    "الفني المسؤول",
                    options=[u["username"] for u in users if u.get("role") == "technician"]
                )
                ticket_type = st.selectbox("نوع الطلب", ["صيانة", "تركيب", "شكوى", "استفسار"])
            
            description = st.text_area("وصف المشكلة", height=100)
            
            if st.form_submit_button("إنشاء التذكرة"):
                new_ticket = {
                    "id": len(tickets) + 1,
                    "customer_id": customer_id,
                    "customer_name": next(c["name"] for c in customers if c["id"] == customer_id),
                    "description": description,
                    "priority": priority,
                    "type": ticket_type,
                    "assigned_to": assigned_to,
                    "status": "مفتوحة",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                tickets.append(new_ticket)
                save_json(TICKETS_FILE, tickets)
                st.success("تم إنشاء التذكرة بنجاح")
    
    with tab2:
        active_tickets = [t for t in tickets if t["status"] == "مفتوحة"]
        if active_tickets:
            for ticket in active_tickets:
                with st.container(border=True):
                    cols = st.columns([3,1,1,1])
                    with cols[0]:
                        st.markdown(f"**{ticket['customer_name']}** - {ticket['description'][:50]}...")
                    with cols[1]:
                        priority_color = {"عاجلة": "red", "متوسطة": "orange", "منخفضة": "green"}[ticket["priority"]]
                        st.markdown(f"<span style='color:{priority_color}'>{ticket['priority']}</span>", unsafe_allow_html=True)
                    with cols[2]:
                        st.text(ticket["assigned_to"])
                    with cols[3]:
                        if st.button("إغلاق", key=f"close_{ticket['id']}"):
                            ticket["status"] = "مغلقة"
                            save_json(TICKETS_FILE, tickets)
                            st.rerun()
        else:
            st.info("لا توجد تذاكر نشطة")
    
    with tab3:
        if tickets:
            df_tickets = pd.DataFrame(tickets)
            st.dataframe(df_tickets, use_container_width=True)

# ================== الميزة 4: إدارة المنتجات ==================
def products_management():
    st.subheader("🛍️ إدارة المنتجات والخدمات")
    
    tab1, tab2 = st.tabs(["إضافة منتج", "قائمة المنتجات"])
    
    with tab1:
        with st.form("add_product"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("اسم المنتج")
                category = st.selectbox("التصنيف", ["فلتر مياه", "قطع غيار", "مواد تنظيف", "خدمة صيانة"])
                price = st.number_input("السعر (ريال)", min_value=0.0, value=0.0)
            
            with col2:
                stock = st.number_input("الكمية المتاحة", min_value=0, value=0)
                points_cost = st.number_input("تكلفة النقاط", min_value=0, value=0)
            
            description = st.text_area("الوصف")
            
            if st.form_submit_button("إضافة المنتج"):
                products.append({
                    "id": len(products) + 1,
                    "name": name,
                    "category": category,
                    "price": price,
                    "stock": stock,
                    "points_cost": points_cost,
                    "description": description,
                    "created_at": datetime.now().strftime("%Y-%m-%d")
                })
                save_json(PRODUCTS_FILE, products)
                st.success("تم إضافة المنتج بنجاح")
    
    with tab2:
        if products:
            # فلترة المنتجات
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                filter_category = st.multiselect(
                    "التصنيف",
                    options=list(set(p["category"] for p in products)),
                    default=[]
                )
            
            df_products = pd.DataFrame(products)
            if filter_category:
                df_products = df_products[df_products["category"].isin(filter_category)]
            
            st.dataframe(df_products, use_container_width=True)
            
            # مخطط توزيع الأسعار
            if not df_products.empty:
                fig = px.histogram(df_products, x="price", nbins=10,
                                  title="توزيع أسعار المنتجات")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("لا توجد منتجات مسجلة")

# ================== الميزة 5: التقارير الشهرية ==================
def monthly_reports():
    st.subheader("📈 التقارير الشهرية")
    
    # اختيار الشهر
    current_date = datetime.now()
    months = [(current_date - relativedelta(months=i)).strftime("%Y-%m") 
              for i in range(6)]
    
    selected_month = st.selectbox("اختر الشهر", months)
    
    # تحليل البيانات
    st.markdown(f"### تقرير شهر {selected_month}")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    
    with col_r1:
        # العملاء الجدد
        new_customers_count = len([c for c in customers 
                                  if c.get("created_at", "").startswith(selected_month)])
        st.metric("عملاء جدد", new_customers_count)
    
    with col_r2:
        # الزيارات المسجلة
        visits_count = len([c for c in customers 
                           if c.get("last_visit", "").startswith(selected_month)])
        st.metric("زيارات مسجلة", visits_count)
    
    with col_r3:
        # التذاكر المغلقة
        closed_tickets = len([t for t in tickets 
                             if t.get("status") == "مغلقة" 
                             and t.get("updated_at", "").startswith(selected_month)])
        st.metric("تذاكر مغلقة", closed_tickets)
    
    # مخطط الزيارات
    if customers:
        visits_data = []
        for day in range(1, 32):
            date_str = f"{selected_month}-{day:02d}"
            day_visits = len([c for c in customers if c.get("last_visit") == date_str])
            visits_data.append({"تاريخ": date_str, "زيارات": day_visits})
        
        df_visits = pd.DataFrame(visits_data)
        fig = px.line(df_visits, x="تاريخ", y="زيارات", 
                      title="الزيارات اليومية")
        st.plotly_chart(fig, use_container_width=True)

# ================== الميزات الأساسية المحسنة ==================
def add_customer():
    st.subheader("➕ إضافة عميل جديد")
    
    with st.form("add_customer", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("اسم العميل *", placeholder="أدخل الاسم الكامل")
            phone = st.text_input("رقم الهاتف *", placeholder="05xxxxxxxx")
            email = st.text_input("البريد الإلكتروني", placeholder="example@email.com")
        
        with col2:
            location = st.text_input("الإحداثيات (lat,lon)", placeholder="24.7136,46.6753")
            category = st.selectbox("التصنيف *", ["منزل", "شركة", "مدرسة", "مستشفى", "فندق"])
            source = st.selectbox("مصدر العميل", ["إحالة", "إعلان", "موقع إلكتروني", "أخرى"])
        
        notes = st.text_area("ملاحظات", placeholder="أي معلومات إضافية...")
        
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            last_visit = st.date_input("تاريخ آخر زيارة", datetime.today())
        with col_date2:
            next_visit = st.date_input("الزيارة القادمة المتوقعة", 
                                      datetime.today() + timedelta(days=30))
        
        if st.form_submit_button("حفظ العميل"):
            if not name or not phone:
                st.error("الرجاء ملء الحقول الإلزامية (*)")
            else:
                new_customer = {
                    "id": max([c["id"] for c in customers], default=0) + 1,
                    "name": name,
                    "phone": phone,
                    "email": email if email else "",
                    "location": location,
                    "category": category,
                    "source": source,
                    "notes": notes,
                    "last_visit": str(last_visit),
                    "next_visit": str(next_visit),
                    "loyalty_points": 0,
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "status": "نشط"
                }
                customers.append(new_customer)
                save_json(CUSTOMERS_FILE, customers)
                st.success("✅ تم إضافة العميل بنجاح")
                st.balloons()

def show_customers():
    st.subheader("📋 قائمة العملاء")
    
    # أدوات الفلترة
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        filter_category = st.multiselect(
            "التصنيف",
            options=list(set(c.get("category", "غير محدد") for c in customers)),
            default=[]
        )
    
    with col_filter2:
        filter_status = st.multiselect(
            "الحالة",
            options=["نشط", "متأخر", "غير نشط"],
            default=["نشط"]
        )
    
    with col_filter3:
        search_term = st.text_input("بحث سريع")
    
    # تطبيق الفلترة
    filtered_customers = customers.copy()
    
    if filter_category:
        filtered_customers = [c for c in filtered_customers if c.get("category") in filter_category]
    
    if search_term:
        filtered_customers = [c for c in filtered_customers 
                             if search_term.lower() in c["name"].lower() 
                             or search_term in c["phone"]]
    
    # عرض البيانات
    if filtered_customers:
        # تحويل للعرض
        display_data = []
        for c in filtered_customers:
            try:
                days_since_visit = (datetime.now() - datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")).days
                status = "متأخر" if days_since_visit > 30 else "نشط"
            except:
                status = "غير محدد"
            
            if status in filter_status or not filter_status:
                display_data.append({
                    "ID": c["id"],
                    "الاسم": c["name"],
                    "الهاتف": c["phone"],
                    "التصنيف": c.get("category", ""),
                    "آخر زيارة": c.get("last_visit", ""),
                    "النقاط": c.get("loyalty_points", 0),
                    "الحالة": status
                })
        
        if display_data:
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True, height=400)
            
            # خيار التصدير
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 تصدير إلى Excel",
                data=csv,
                file_name=f"customers_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("لا توجد نتائج تطابق معايير البحث")
    else:
        st.info("لا يوجد عملاء مسجلين")

def search_customer():
    st.subheader("🔍 بحث متقدم عن عميل")
    
    tab_search1, tab_search2 = st.tabs(["بحث عام", "بحث متقدم"])
    
    with tab_search1:
        keyword = st.text_input("اكتب للبحث (الاسم، الهاتف، البريد)")
        if keyword:
            results = [
                c for c in customers
                if (keyword.lower() in c["name"].lower() or 
                    keyword in c["phone"] or 
                    keyword.lower() in c.get("email", "").lower() or
                    keyword.lower() in c.get("notes", "").lower())
            ]
            if results:
                df_results = pd.DataFrame(results)[["id", "name", "phone", "category", "last_visit"]]
                st.dataframe(df_results, use_container_width=True)
            else:
                st.warning("لا توجد نتائج")
    
    with tab_search2:
        with st.form("advanced_search"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                name_part = st.text_input("جزء من الاسم")
                category_filter = st.selectbox(
                    "التصنيف",
                    ["الكل"] + list(set(c.get("category", "") for c in customers))
                )
            
            with col_s2:
                date_from = st.date_input("من تاريخ", datetime.now() - timedelta(days=365))
                date_to = st.date_input("إلى تاريخ", datetime.now())
            
            if st.form_submit_button("بحث متقدم"):
                results = customers.copy()
                
                if name_part:
                    results = [c for c in results if name_part.lower() in c["name"].lower()]
                
                if category_filter != "الكل":
                    results = [c for c in results if c.get("category") == category_filter]
                
                try:
                    results = [
                        c for c in results
                        if date_from <= datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d") <= date_to
                    ]
                except:
                    pass
                
                if results:
                    df_advanced = pd.DataFrame(results)
                    st.dataframe(df_advanced, use_container_width=True)
                else:
                    st.warning("لا توجد نتائج")

def visit_reminder():
    st.subheader("⏰ تذكير الزيارات")
    
    # إعداد الفلاتر
    days_threshold = st.slider("عدد أيام التأخير", 1, 90, 30)
    
    # حساب العملاء المتأخرين
    today = datetime.today()
    due = []
    
    for c in customers:
        try:
            last = datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")
            days_overdue = (today - last).days
            
            if days_overdue >= days_threshold:
                # حساب أولوية التأخير
                priority = "عالي" if days_overdue > 60 else "متوسط" if days_overdue > 45 else "منخفض"
                
                due.append({
                    "العميل": c["name"],
                    "الهاتف": c["phone"],
                    "آخر زيارة": c["last_visit"],
                    "أيام التأخير": days_overdue,
                    "الأولوية": priority,
                    "التصنيف": c.get("category", "")
                })
        except Exception as e:
            continue
    
    if due:
        # تحويل ل DataFrame
        df_due = pd.DataFrame(due)
        
        # فرز حسب الأولوية
        df_due = df_due.sort_values("أيام التأخير", ascending=False)
        
        # عرض مع ألوان
        st.dataframe(df_due, use_container_width=True)
        
        # إجراءات سريعة
        st.markdown("### إجراءات سريعة")
        col_act1, col_act2, col_act3 = st.columns(3)
        
        with col_act1:
            if st.button("إرسال رسالة نصية جماعية", use_container_width=True):
                st.info("سيتم إرسال رسائل تذكير للعملاء المحددين")
        
        with col_act2:
            if st.button("طباعة قائمة الزيارات", use_container_width=True):
                st.info("جاهز للطباعة")
        
        with col_act3:
            if st.button("تحديث جميع الزيارات", use_container_width=True):
                st.warning("هذا الإجراء سيحدد تاريخ اليوم كتاريخ زيارة للجميع")
        
        # إحصاءات
        st.markdown("### 📊 إحصاءات التأخير")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        
        with col_stat1:
            high_priority = len([d for d in due if d["الأولوية"] == "عالي"])
            st.metric("أولوية عالية", high_priority)
        
        with col_stat2:
            total_due = len(due)
            st.metric("إجمالي المتأخرين", total_due)
        
        with col_stat3:
            avg_delay = df_due["أيام التأخير"].mean() if not df_due.empty else 0
            st.metric("متوسط التأخير", f"{avg_delay:.1f} يوم")
    
    else:
        st.success(f"🎉 لا يوجد عملاء متأخرين عن {days_threshold} يوم")

def add_technician():
    st.subheader("👷 إضافة فني جديد")
    
    with st.form("add_tech", clear_on_submit=True):
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            username = st.text_input("اسم المستخدم *")
            full_name = st.text_input("الاسم الكامل")
        
        with col_t2:
            password = st.text_input("كلمة المرور *", type="password")
            confirm_password = st.text_input("تأكيد كلمة المرور *", type="password")
        
        phone = st.text_input("رقم الهاتف")
        email = st.text_input("البريد الإلكتروني")
        specialization = st.multiselect(
            "التخصص",
            ["تركيب فلاتر", "صيانة دورية", "إصلاح أعطال", "خدمة عملاء"]
        )
        
        if st.form_submit_button("إضافة الفني"):
            if not username or not password:
                st.error("الحقول الإلزامية (*) مطلوبة")
            elif password != confirm_password:
                st.error("كلمتا المرور غير متطابقتين")
            elif any(u["username"] == username for u in users):
                st.error("اسم المستخدم موجود مسبقاً")
            else:
                users.append({
                    "username": username,
                    "password": password,
                    "full_name": full_name,
                    "phone": phone,
                    "email": email,
                    "specialization": specialization,
                    "role": "technician",
                    "created_at": datetime.now().strftime("%Y-%m-%d"),
                    "status": "نشط"
                })
                save_json(USERS_FILE, users)
                st.success("✅ تم إضافة الفني بنجاح")

def show_map():
    st.subheader("🗺️ خريطة العملاء التفاعلية")
    
    if not customers:
        st.info("لا توجد بيانات للعرض على الخريطة")
        return
    
    # تحضير بيانات الخريطة
    map_data = []
    for c in customers:
        try:
            if c.get("location"):
                lat, lon = map(float, c["location"].split(","))
                
                # تحديد لون حسب التصنيف
                color_map = {
                    "منزل": "#FF6B6B",
                    "شركة": "#4ECDC4",
                    "مدرسة": "#FFD166",
                    "مستشفى": "#06D6A0",
                    "فندق": "#118AB2"
                }
                
                map_data.append({
                    "lat": lat,
                    "lon": lon,
                    "name": c["name"],
                    "category": c.get("category", "غير محدد"),
                    "color": color_map.get(c.get("category"), "#999999"),
                    "last_visit": c.get("last_visit", ""),
                    "size": min(c.get("loyalty_points", 0) / 10 + 5, 20)  # حجم النقطة حسب النقاط
                })
        except:
            continue
    
    if map_data:
        df_map = pd.DataFrame(map_data)
        
        # إنشاء خريطة تفاعلية
        fig = px.scatter_mapbox(
            df_map,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data=["category", "last_visit"],
            color="category",
            size="size",
            zoom=10,
            height=500
        )
        
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
        st.plotly_chart(fig, use_container_width=True)
        
        # إحصائيات الخريطة
        st.markdown("##### 📍 إحصائيات المواقع")
        col_map1, col_map2, col_map3 = st.columns(3)
        
        with col_map1:
            st.metric("مواقع ظاهرة", len(map_data))
        
        with col_map2:
            categories_shown = len(set(df_map["category"]))
            st.metric("أنواع ظاهرة", categories_shown)
        
        with col_map3:
            if not df_map.empty:
                avg_lat = df_map["lat"].mean()
                avg_lon = df_map["lon"].mean()
                st.metric("المركز الجغرافي", f"{avg_lat:.3f}, {avg_lon:.3f}")
    else:
        st.warning("لا توجد إحداثيات صالحة للعرض")

# ================== الواجهة الرئيسية ==================
def dashboard():
    user = st.session_state.current_user
    role = user.get("role")
    
    # الشريط الجانبي
    with st.sidebar:
        st.title("💧 Power Life")
        st.markdown(f"**المستخدم:** {user.get('username')}")
        st.markdown(f"**الدور:** {role}")
        st.markdown("---")
        
        # القائمة الرئيسية
        menu_options = ["🏠 لوحة التحكم", "📋 قائمة العملاء", "🔍 بحث متقدم", 
                       "⏰ تذكير الزيارات", "🗺️ الخريطة التفاعلية"]
        
        if role == "admin":
            menu_options.extend([
                "➕ إضافة عميل جديد",
                "👷 إدارة الفنيين",
                "🎯 نظام نقاط الولاء",
                "🎫 نظام التذاكر",
                "🛍️ إدارة المنتجات",
                "📊 التقارير والإحصاءات",
                "📈 التقارير الشهرية"
            ])
        
        menu_options.append("🚪 تسجيل الخروج")
        
        choice = st.selectbox("القائمة الرئيسية", menu_options)
        st.markdown("---")
        
        # معلومات سريعة
        st.markdown("##### 📈 معلومات سريعة")
        st.metric("إجمالي العملاء", len(customers))
        
        overdue_count = len([c for c in customers 
                           if (datetime.now() - datetime.strptime(c.get("last_visit", "2000-01-01"), "%Y-%m-%d")).days > 30])
        st.metric("زيارات متأخرة", overdue_count)
        
        # تذييل
        st.markdown("---")
        st.markdown(f"<small>الإصدار 2.0 | {datetime.now().strftime('%Y-%m-%d')}</small>", 
                   unsafe_allow_html=True)
    
    # المحتوى الرئيسي
    if choice == "🏠 لوحة التحكم":
        analytics_dashboard()
    
    elif choice == "📋 قائمة العملاء":
        show_customers()
    
    elif choice == "🔍 بحث متقدم":
        search_customer()
    
    elif choice == "⏰ تذكير الزيارات":
        visit_reminder()
    
    elif choice == "🗺️ الخريطة التفاعلية":
        show_map()
    
    elif choice == "➕ إضافة عميل جديد":
        add_customer()
    
    elif choice == "👷 إدارة الفنيين":
        add_technician()
    
    elif choice == "🎯 نظام نقاط الولاء":
        loyalty_points_system()
    
    elif choice == "🎫 نظام التذاكر":
        ticket_system()
    
    elif choice == "🛍️ إدارة المنتجات":
        products_management()
    
    elif choice == "📊 التقارير والإحصاءات":
        analytics_dashboard()
    
    elif choice == "📈 التقارير الشهرية":
        monthly_reports()
    
    elif choice == "🚪 تسجيل الخروج":
        logout()

# ================== تشغيل التطبيق ==================
if not st.session_state.logged_in:
    login_page()
else:
    dashboard()
