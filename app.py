<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<title>نظام إدارة شركة فلاتر المياه | Dr.Filter</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root {
  --primary: #1a73e8;
  --primary-dark: #0d47a1;
  --secondary: #00acc1;
  --accent: #00bcd4;
  --success: #4caf50;
  --warning: #ff9800;
  --danger: #f44336;
  --dark: #001529;
  --light: #f5f7fa;
  --gray: #e0e0e0;
  --text: #333;
  --text-light: #666;
  --bg: #f0f2f5;
  --panel: #ffffff;
  --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  --radius: 10px;
  --transition: all 0.3s ease;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
}

.hidden { display: none !important; }

/* صفحة تسجيل الدخول */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
  padding: 20px;
}

.login-box {
  background: var(--panel);
  width: 100%;
  max-width: 400px;
  padding: 40px 30px;
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  text-align: center;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  color: var(--primary);
}

.logo i {
  font-size: 40px;
  margin-left: 15px;
}

.logo h1 {
  font-size: 28px;
  font-weight: 700;
}

.login-box h2 {
  margin-bottom: 25px;
  color: var(--dark);
  font-weight: 600;
}

.input-group {
  margin-bottom: 20px;
  text-align: right;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-light);
}

.input-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid var(--gray);
  border-radius: var(--radius);
  font-size: 16px;
  transition: var(--transition);
}

.input-group input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.2);
}

.btn {
  display: inline-block;
  background: var(--primary);
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: var(--radius);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  text-align: center;
  width: 100%;
}

.btn:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.btn-secondary {
  background: var(--secondary);
}

.btn-success {
  background: var(--success);
}

.btn-warning {
  background: var(--warning);
}

.btn-danger {
  background: var(--danger);
}

.btn-outline {
  background: transparent;
  border: 2px solid var(--primary);
  color: var(--primary);
}

.btn-outline:hover {
  background: var(--primary);
  color: white;
}

.btn-small {
  padding: 6px 15px;
  font-size: 14px;
}

.alert {
  padding: 12px 15px;
  border-radius: var(--radius);
  margin-bottom: 20px;
  font-weight: 500;
}

.alert-danger {
  background: rgba(244, 67, 54, 0.1);
  color: var(--danger);
  border: 1px solid rgba(244, 67, 54, 0.2);
}

.alert-success {
  background: rgba(76, 175, 80, 0.1);
  color: var(--success);
  border: 1px solid rgba(76, 175, 80, 0.2);
}

/* تخطيط التطبيق */
#app {
  display: flex;
  min-height: 100vh;
}

/* الشريط الجانبي */
#sidebar {
  width: 260px;
  background: var(--dark);
  color: white;
  transition: var(--transition);
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

#sidebar.collapsed {
  width: 70px;
}

#sidebar.collapsed .sidebar-header h2,
#sidebar.collapsed .nav-item span {
  display: none;
}

#sidebar.collapsed .nav-item {
  justify-content: center;
}

.sidebar-header {
  padding: 25px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
}

.sidebar-header h2 i {
  margin-left: 10px;
  color: var(--accent);
}

.toggle-btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.toggle-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-menu {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: var(--transition);
  cursor: pointer;
  border-right: 3px solid transparent;
}

.nav-item:hover, .nav-item.active {
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border-right-color: var(--accent);
}

.nav-item i {
  font-size: 18px;
  margin-left: 10px;
  width: 24px;
  text-align: center;
}

.nav-item span {
  font-size: 15px;
  font-weight: 500;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 10px;
  font-weight: 700;
}

.user-details h4 {
  font-size: 14px;
  margin-bottom: 2px;
}

.user-details p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* المحتوى الرئيسي */
#main {
  flex: 1;
  overflow: auto;
  background: var(--bg);
}

.topbar {
  background: white;
  padding: 15px 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 99;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--dark);
}

.search-box {
  position: relative;
  width: 300px;
}

.search-box input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border: 1px solid var(--gray);
  border-radius: var(--radius);
  font-size: 14px;
}

.search-box i {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
}

.content {
  padding: 25px;
}

/* البطاقات */
.card {
  background: var(--panel);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 20px;
  margin-bottom: 25px;
  transition: var(--transition);
}

.card:hover {
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--gray);
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--dark);
  display: flex;
  align-items: center;
}

.card-title i {
  margin-left: 10px;
  color: var(--primary);
}

/* الشبكات */
.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -10px;
}

.col {
  flex: 1;
  min-width: 300px;
  padding: 0 10px;
  margin-bottom: 20px;
}

.col-3 { flex: 0 0 25%; max-width: 25%; }
.col-4 { flex: 0 0 33.333%; max-width: 33.333%; }
.col-6 { flex: 0 0 50%; max-width: 50%; }
.col-8 { flex: 0 0 66.666%; max-width: 66.666%; }
.col-12 { flex: 0 0 100%; max-width: 100%; }

/* الجداول */
.table-container {
  overflow-x: auto;
  border-radius: var(--radius);
  border: 1px solid var(--gray);
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

thead {
  background: var(--dark);
  color: white;
}

th, td {
  padding: 15px;
  text-align: right;
  border-bottom: 1px solid var(--gray);
}

tbody tr:hover {
  background: rgba(0, 0, 0, 0.02);
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.badge-success { background: rgba(76, 175, 80, 0.1); color: var(--success); }
.badge-warning { background: rgba(255, 152, 0, 0.1); color: var(--warning); }
.badge-danger { background: rgba(244, 67, 54, 0.1); color: var(--danger); }
.badge-info { background: rgba(0, 188, 212, 0.1); color: var(--secondary); }

.action-btns {
  display: flex;
  gap: 8px;
}

/* الفورم */
.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -10px;
}

.form-col {
  flex: 1;
  min-width: 250px;
  padding: 0 10px;
}

/* الاحصائيات */
.stats-container {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -10px;
}

.stat-card {
  flex: 1;
  min-width: 200px;
  padding: 0 10px;
  margin-bottom: 20px;
}

.stat-box {
  background: white;
  border-radius: var(--radius);
  padding: 20px;
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  transition: var(--transition);
}

.stat-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 15px;
  font-size: 24px;
  color: white;
}

.stat-icon.clients { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.stat-icon.techs { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.stat-icon.appointments { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.stat-icon.products { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }

.stat-info h3 {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 5px;
}

.stat-info p {
  font-size: 14px;
  color: var(--text-light);
}

/* الصفحات */
.page {
  display: none;
}

.page.active {
  display: block;
  animation: fadeIn 0.5s ease-out;
}

/* متجاوب */
@media (max-width: 992px) {
  #sidebar {
    position: fixed;
    height: 100vh;
    left: -260px;
  }
  
  #sidebar.active {
    left: 0;
  }
  
  #sidebar.collapsed {
    width: 260px;
    left: -260px;
  }
  
  #sidebar.collapsed.active {
    left: 0;
  }
  
  #sidebar.collapsed .sidebar-header h2,
  #sidebar.collapsed .nav-item span {
    display: block;
  }
  
  #sidebar.collapsed .nav-item {
    justify-content: flex-start;
  }
  
  .mobile-toggle {
    display: block !important;
  }
  
  .col, .col-3, .col-4, .col-6, .col-8 {
    flex: 0 0 100%;
    max-width: 100%;
  }
}

@media (max-width: 768px) {
  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .search-box {
    width: 100%;
    margin-top: 15px;
  }
  
  .action-btns {
    flex-wrap: wrap;
  }
}

.mobile-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 24px;
  color: var(--dark);
  cursor: pointer;
}

/* الأيقونات المتحركة */
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.pulse {
  animation: pulse 2s infinite;
}
</style>
</head>

<body>
<!-- تسجيل الدخول -->
<div id="login" class="login-container">
  <div class="login-box">
    <div class="logo">
      <i class="fas fa-tint"></i>
      <h1>Dr.Filter</h1>
    </div>
    <h2>نظام إدارة شركة فلاتر المياه</h2>
    <div id="loginAlert" class="alert hidden"></div>
    <div class="input-group">
      <label for="username">اسم المستخدم</label>
      <input type="text" id="username" placeholder="أدخل اسم المستخدم">
    </div>
    <div class="input-group">
      <label for="password">كلمة المرور</label>
      <input type="password" id="password" placeholder="أدخل كلمة المرور">
    </div>
    <button class="btn" onclick="login()">تسجيل الدخول</button>
    <div style="margin-top: 20px; color: var(--text-light); font-size: 14px;">
      <p>بيانات الدخول الافتراضية: admin / 1010</p>
    </div>
  </div>
</div>

<!-- التطبيق الرئيسي -->
<div id="app" class="hidden">
  <!-- الشريط الجانبي -->
  <div id="sidebar">
    <div class="sidebar-header">
      <h2><i class="fas fa-tint"></i> Dr.Filter</h2>
      <button class="toggle-btn" onclick="toggleSidebar()">
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
    
    <div class="nav-menu">
      <a class="nav-item active" data-page="dashboard">
        <i class="fas fa-home"></i>
        <span>لوحة التحكم</span>
      </a>
      <a class="nav-item" data-page="clients">
        <i class="fas fa-users"></i>
        <span>العملاء</span>
      </a>
      <a class="nav-item" data-page="techs">
        <i class="fas fa-user-cog"></i>
        <span>الفنيين</span>
      </a>
      <a class="nav-item" data-page="appointments">
        <i class="fas fa-calendar-alt"></i>
        <span>المواعيد</span>
      </a>
      <a class="nav-item" data-page="products">
        <i class="fas fa-filter"></i>
        <span>المنتجات</span>
      </a>
      <a class="nav-item" data-page="orders">
        <i class="fas fa-shopping-cart"></i>
        <span>الطلبات</span>
      </a>
      <a class="nav-item" data-page="reports">
        <i class="fas fa-chart-bar"></i>
        <span>التقارير</span>
      </a>
      <a class="nav-item" data-page="backup">
        <i class="fas fa-database"></i>
        <span>النسخ الاحتياطي</span>
      </a>
    </div>
    
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="user-avatar">A</div>
        <div class="user-details">
          <h4 id="loggedUser">المسؤول</h4>
          <p>مدير النظام</p>
        </div>
      </div>
      <button class="btn btn-danger btn-small" onclick="logout()">
        <i class="fas fa-sign-out-alt"></i>
        <span>تسجيل الخروج</span>
      </button>
    </div>
  </div>

  <!-- المحتوى الرئيسي -->
  <div id="main">
    <!-- شريط القمة -->
    <div class="topbar">
      <button class="mobile-toggle" onclick="toggleMobileSidebar()">
        <i class="fas fa-bars"></i>
      </button>
      <div class="page-title">لوحة التحكم</div>
      <div class="search-box">
        <input type="text" placeholder="بحث في النظام...">
        <i class="fas fa-search"></i>
      </div>
    </div>
    
    <!-- المحتوى -->
    <div class="content">
      <!-- صفحة لوحة التحكم -->
      <div id="dashboard" class="page active">
        <div class="row">
          <div class="col-12">
            <div class="card">
              <div class="card-header">
                <div class="card-title">
                  <i class="fas fa-chart-line"></i>
                  نظرة عامة
                </div>
                <div>التاريخ: <span id="currentDate"></span></div>
              </div>
              <div class="stats-container">
                <div class="stat-card">
                  <div class="stat-box">
                    <div class="stat-icon clients">
                      <i class="fas fa-users"></i>
                    </div>
                    <div class="stat-info">
                      <h3 id="clientsCount">0</h3>
                      <p>إجمالي العملاء</p>
                    </div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-box">
                    <div class="stat-icon techs">
                      <i class="fas fa-user-cog"></i>
                    </div>
                    <div class="stat-info">
                      <h3 id="techsCount">0</h3>
                      <p>إجمالي الفنيين</p>
                    </div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-box">
                    <div class="stat-icon appointments">
                      <i class="fas fa-calendar-alt"></i>
                    </div>
                    <div class="stat-info">
                      <h3 id="appointmentsCount">0</h3>
                      <p>موعد اليوم</p>
                    </div>
                  </div>
                </div>
                <div class="stat-card">
                  <div class="stat-box">
                    <div class="stat-icon products">
                      <i class="fas fa-filter"></i>
                    </div>
                    <div class="stat-info">
                      <h3 id="productsCount">0</h3>
                      <p>المنتجات المتاحة</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-6">
            <div class="card">
              <div class="card-header">
                <div class="card-title">
                  <i class="fas fa-calendar-check"></i>
                  مواعيد اليوم
                </div>
                <button class="btn btn-secondary btn-small" onclick="showPage('appointments')">
                  <i class="fas fa-plus"></i> إضافة موعد
                </button>
              </div>
              <div class="table-container">
                <table id="todayAppointments">
                  <thead>
                    <tr>
                      <th>العميل</th>
                      <th>الوقت</th>
                      <th>الفني</th>
                      <th>الحالة</th>
                    </tr>
                  </thead>
                  <tbody>
                    <!-- سيتم تعبئتها ديناميكياً -->
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          
          <div class="col-6">
            <div class="card">
              <div class="card-header">
                <div class="card-title">
                  <i class="fas fa-exclamation-circle"></i>
                  طلبات تحتاج متابعة
                </div>
              </div>
              <div class="table-container">
                <table id="pendingOrders">
                  <thead>
                    <tr>
                      <th>رقم الطلب</th>
                      <th>العميل</th>
                      <th>التاريخ</th>
                      <th>الحالة</th>
                    </tr>
                  </thead>
                  <tbody>
                    <!-- سيتم تعبئتها ديناميكياً -->
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- صفحة العملاء -->
      <div id="clients" class="page">
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <i class="fas fa-users"></i>
              إدارة العملاء
            </div>
            <button class="btn btn-success" onclick="openClientModal()">
              <i class="fas fa-plus"></i> إضافة عميل جديد
            </button>
          </div>
          
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>اسم العميل</th>
                  <th>الهاتف</th>
                  <th>العنوان</th>
                  <th>نوع الفلتر</th>
                  <th>تاريخ الصيانة</th>
                  <th>الحالة</th>
                  <th>الإجراءات</th>
                </tr>
              </thead>
              <tbody id="clientsTable">
                <!-- سيتم تعبئتها ديناميكياً -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- صفحة الفنيين -->
      <div id="techs" class="page">
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <i class="fas fa-user-cog"></i>
              إدارة الفنيين
            </div>
            <button class="btn btn-success" onclick="openTechModal()">
              <i class="fas fa-plus"></i> إضافة فني جديد
            </button>
          </div>
          
          <div class="row">
            <div class="col-12">
              <div class="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>اسم الفني</th>
                      <th>الهاتف</th>
                      <th>البريد الإلكتروني</th>
                      <th>التخصص</th>
                      <th>عدد المهام</th>
                      <th>الحالة</th>
                      <th>الإجراءات</th>
                    </tr>
                  </thead>
                  <tbody id="techsTable">
                    <!-- سيتم تعبئتها ديناميكياً -->
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- صفحة المواعيد -->
      <div id="appointments" class="page">
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <i class="fas fa-calendar-alt"></i>
              إدارة المواعيد
            </div>
            <button class="btn btn-success" onclick="openAppointmentModal()">
              <i class="fas fa-plus"></i> إضافة موعد جديد
            </button>
          </div>
          
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>العميل</th>
                  <th>الفني</th>
                  <th>نوع الخدمة</th>
                  <th>التاريخ</th>
                  <th>الوقت</th>
                  <th>الحالة</th>
                  <th>الإجراءات</th>
                </tr>
              </thead>
              <tbody id="appointmentsTable">
                <!-- سيتم تعبئتها ديناميكياً -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- صفحة المنتجات -->
      <div id="products" class="page">
        <div class="row">
          <div class="col-12">
            <div class="card">
              <div class="card-header">
                <div class="card-title">
                  <i class="fas fa-filter"></i>
                  إدارة المنتجات
                </div>
                <button class="btn btn-success" onclick="openProductModal()">
                  <i class="fas fa-plus"></i> إضافة منتج جديد
                </button>
              </div>
              
              <div class="row" id="productsGrid">
                <!-- سيتم تعبئتها ديناميكياً -->
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- صفحة الطلبات -->
      <div id="orders" class="page">
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <i class="fas fa-shopping-cart"></i>
              إدارة الطلبات
            </div>
            <button class="btn btn-success" onclick="openOrderModal()">
              <i class="fas fa-plus"></i> إضافة طلب جديد
            </button>
          </div>
          
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>رقم الطلب</th>
                  <th>العميل</th>
                  <th>المنتجات</th>
                  <th>المجموع</th>
                  <th>تاريخ الطلب</th>
                  <th>الحالة</th>
                  <th>الإجراءات</th>
                </tr>
              </thead>
              <tbody id="ordersTable">
                <!-- سيتم تعبئتها ديناميكياً -->
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <!-- صفحة التقارير -->
      <div id="reports" class="page">
        <div class="card">
          <div class="card-header">
            <div class="card-title">
              <i class="fas fa-chart-bar"></i>
              التقارير والإحصائيات
            </div>
            <div>
              <button class="btn btn-secondary btn-small" onclick="generateReport('monthly')">
                <i class="fas fa-file-pdf"></i> تقرير شهري
              </button>
              <button class="btn btn-secondary btn-small" onclick="generateReport('yearly')">
                <i class="fas fa-file-excel"></i> تقرير سنوي
              </button>
            </div>
          </div>
          
          <div class="row">
            <div class="col-6">
              <div class="card">
                <div class="card-title">
                  <i class="fas fa-chart-pie"></i>
                  توزيع المبيعات
                </div>
                <div id="salesChart" style="height: 300px; display: flex; align-items: center; justify-content: center; color: var(--text-light);">
                  <p>رسم بياني سيظهر هنا</p>
                </div>
              </div>
            </div>
            <div class="col-6">
              <div class="card">
                <div class="card-title">
                  <i class="fas fa-chart-line"></i>
                  المبيعات الشهرية
                </div>
                <div id="monthlyChart" style="height: 300px; display: flex; align-items: center; justify-content: center; color: var(--text-light);">
                  <p>رسم بياني سيظهر هنا</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card" style="margin-top: 20px;">
            <div class="card-title">
              <i class="fas fa-list"></i>
              تقرير تفصيلي
            </div>
            <div class="table-container">
              <table>
                <thead>
                  <tr>
                    <th>الشهر</th>
                    <th>عدد العملاء الجدد</th>
                    <th>عدد المواعيد</th>
                    <th>إجمالي المبيعات</th>
                    <th>صافي الربح</th>
                  </tr>
                </thead>
                <tbody id="reportsTable">
                  <!-- سيتم تعبئتها ديناميكياً -->
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <!-- صفحة النسخ الاحتياطي -->
      <div id="backup" class="page">
        <div class="row">
          <div class="col-6">
            <div class="card">
              <div class="card-header">
                <div class="card-title">
                  <i class="fas fa-database"></i>
                  النسخ الاحتياطي
                </div>
              </div>
              <div style="padding: 20px 0;">
                <p style="margin-bottom: 20px;">النسخ الاحتياطي يحفظ جميع بيانات النظام.</p>
                <button class="btn btn-success" onclick="createBackup()">
                  <i class="fas fa-save"></i> إنشاء نسخة احتياطية
                </button>
                <button class="btn btn-secondary" onclick="restoreBackup()" style="margin-right: 10px;">
                  <i class="fas fa-undo"></i> استعادة نسخة
                </button>
              </div>
              <div id="backupList">
                <!-- قائمة النسخ الاحتياطية -->
              </div>
            </div>
          </div>
          
          <div class="col-6">
            <div class="card">
              <div class="card-header">
                <div class="card-title">
                  <i class="fas fa-info-circle"></i>
                  معلومات النظام
                </div>
              </div>
              <div style="padding: 20px 0;">
                <div class="info-item" style="margin-bottom: 15px;">
                  <strong>إصدار النظام:</strong> 2.1.0
                </div>
                <div class="info-item" style="margin-bottom: 15px;">
                  <strong>آخر تحديث:</strong> 15 أكتوبر 2023
                </div>
                <div class="info-item" style="margin-bottom: 15px;">
                  <strong>إجمالي البيانات المخزنة:</strong> <span id="totalData">0</span> كيلوبايت
                </div>
                <div class="info-item" style="margin-bottom: 15px;">
                  <strong>آخر نسخة احتياطية:</strong> <span id="lastBackup">لم يتم بعد</span>
                </div>
                <div class="info-item">
                  <strong>حالة النظام:</strong> <span class="badge badge-success">جيد</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- نموذج إضافة/تعديل عميل -->
<div id="clientModal" class="modal hidden">
  <div class="modal-content">
    <div class="modal-header">
      <h3><i class="fas fa-user-plus"></i> عميل جديد</h3>
      <span class="close" onclick="closeModal('clientModal')">&times;</span>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label>اسم العميل الكامل</label>
        <input type="text" id="clientName" placeholder="أدخل اسم العميل">
      </div>
      <div class="form-row">
        <div class="form-col">
          <label>رقم الهاتف</label>
          <input type="tel" id="clientPhone" placeholder="05XXXXXXXX">
        </div>
        <div class="form-col">
          <label>البريد الإلكتروني</label>
          <input type="email" id="clientEmail" placeholder="example@email.com">
        </div>
      </div>
      <div class="form-group">
        <label>العنوان</label>
        <textarea id="clientAddress" rows="2" placeholder="أدخل العنوان التفصيلي"></textarea>
      </div>
      <div class="form-row">
        <div class="form-col">
          <label>نوع الفلتر</label>
          <select id="clientFilterType">
            <option value="">اختر نوع الفلتر</option>
            <option value="تحت الحوض">تحت الحوض</option>
            <option value="فوق الحوض">فوق الحوض</option>
            <option value="محطة تنقية">محطة تنقية</option>
            <option value="فلتر 7 مراحل">فلتر 7 مراحل</option>
            <option value="فلتر 5 مراحل">فلتر 5 مراحل</option>
          </select>
        </div>
        <div class="form-col">
          <label>تاريخ التركيب</label>
          <input type="date" id="clientInstallDate">
        </div>
      </div>
      <div class="form-group">
        <label>ملاحظات</label>
        <textarea id="clientNotes" rows="3" placeholder="أي ملاحظات إضافية"></textarea>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal('clientModal')">إلغاء</button>
      <button class="btn btn-success" onclick="saveClient()">حفظ العميل</button>
    </div>
  </div>
</div>

<!-- نموذج إضافة/تعديل فني -->
<div id="techModal" class="modal hidden">
  <div class="modal-content">
    <div class="modal-header">
      <h3><i class="fas fa-user-cog"></i> فني جديد</h3>
      <span class="close" onclick="closeModal('techModal')">&times;</span>
    </div>
    <div class="modal-body">
      <div class="form-group">
        <label>اسم الفني الكامل</label>
        <input type="text" id="techName" placeholder="أدخل اسم الفني">
      </div>
      <div class="form-row">
        <div class="form-col">
          <label>رقم الهاتف</label>
          <input type="tel" id="techPhone" placeholder="05XXXXXXXX">
        </div>
        <div class="form-col">
          <label>البريد الإلكتروني</label>
          <input type="email" id="techEmail" placeholder="example@email.com">
        </div>
      </div>
      <div class="form-row">
        <div class="form-col">
          <label>التخصص</label>
          <select id="techSpecialty">
            <option value="">اختر التخصص</option>
            <option value="تركيب فلاتر">تركيب فلاتر</option>
            <option value="صيانة فلاتر">صيانة فلاتر</option>
            <option value="تركيب وصيانة">تركيب وصيانة</option>
            <option value="خدمة عملاء">خدمة عملاء</option>
          </select>
        </div>
        <div class="form-col">
          <label>الحالة</label>
          <select id="techStatus">
            <option value="نشط">نشط</option>
            <option value="غير نشط">غير نشط</option>
            <option value="إجازة">إجازة</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label>ملاحظات</label>
        <textarea id="techNotes" rows="3" placeholder="أي ملاحظات إضافية"></textarea>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal('techModal')">إلغاء</button>
      <button class="btn btn-success" onclick="saveTech()">حفظ الفني</button>
    </div>
  </div>
</div>

<!-- نماذج أخرى (سيتم إنشاؤها ديناميكياً حسب الحاجة) -->

<script>
// البيانات الأولية
let currentUser = null;
let clients = JSON.parse(localStorage.getItem("drfilter_clients") || "[]");
let techs = JSON.parse(localStorage.getItem("drfilter_techs") || "[]");
let appointments = JSON.parse(localStorage.getItem("drfilter_appointments") || "[]");
let products = JSON.parse(localStorage.getItem("drfilter_products") || "[]");
let orders = JSON.parse(localStorage.getItem("drfilter_orders") || "[]");
let currentEditId = null;

// بيانات افتراضية للمنتجات إذا كانت فارغة
if (products.length === 0) {
  products = [
    { id: 1, name: "فلتر 7 مراحل", category: "فلاتر", price: 850, stock: 15, status: "متوفر" },
    { id: 2, name: "فلتر 5 مراحل", category: "فلاتر", price: 650, stock: 10, status: "متوفر" },
    { id: 3, name: "فلتر تحت الحوض", category: "فلاتر", price: 450, stock: 8, status: "متوفر" },
    { id: 4, name: "شمعات فلتر", category: "قطع غيار", price: 120, stock: 50, status: "متوفر" },
    { id: 5, name: "محمض مياه", category: "كيماويات", price: 35, stock: 30, status: "متوفر" },
    { id: 6, name: "فلتر معادن", category: "قطع غيار", price: 95, stock: 25, status: "متوفر" }
  ];
  saveData('products', products);
}

// بيانات افتراضية للفنيين إذا كانت فارغة
if (techs.length === 0) {
  techs = [
    { id: 1, name: "أحمد محمد", phone: "0551234567", email: "ahmed@drfilter.com", specialty: "تركيب وصيانة", status: "نشط", tasks: 3 },
    { id: 2, name: "خالد العتيبي", phone: "0557654321", email: "khaled@drfilter.com", specialty: "صيانة فلاتر", status: "نشط", tasks: 2 },
    { id: 3, name: "علي السعيد", phone: "0509876543", email: "ali@drfilter.com", specialty: "تركيب فلاتر", status: "إجازة", tasks: 0 }
  ];
  saveData('techs', techs);
}

// تسجيل الدخول
function login() {
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  const loginAlert = document.getElementById('loginAlert');
  
  if (username === "admin" && password === "1010") {
    currentUser = { name: "المسؤول", role: "مدير" };
    document.getElementById('login').classList.add('hidden');
    document.getElementById('app').classList.remove('hidden');
    document.getElementById('loggedUser').textContent = currentUser.name;
    
    // تحديث التاريخ الحالي
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('currentDate').textContent = now.toLocaleDateString('ar-SA', options);
    
    // تحميل البيانات وعرض لوحة التحكم
    loadDashboard();
    updateStats();
    
    loginAlert.classList.remove('alert-danger');
    loginAlert.classList.add('hidden');
  } else {
    loginAlert.textContent = "بيانات الدخول غير صحيحة. يرجى المحاولة مرة أخرى.";
    loginAlert.classList.remove('hidden');
    loginAlert.classList.add('alert-danger');
  }
}

// تسجيل الخروج
function logout() {
  if (confirm("هل أنت متأكد من تسجيل الخروج؟")) {
    location.reload();
  }
}

// تبديل الشريط الجانبي
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const toggleIcon = document.querySelector('.toggle-btn i');
  
  sidebar.classList.toggle('collapsed');
  
  if (sidebar.classList.contains('collapsed')) {
    toggleIcon.classList.remove('fa-chevron-right');
    toggleIcon.classList.add('fa-chevron-left');
  } else {
    toggleIcon.classList.remove('fa-chevron-left');
    toggleIcon.classList.add('fa-chevron-right');
  }
}

// تبديل الشريط الجانبي على الجوال
function toggleMobileSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('active');
}

// عرض صفحة محددة
function showPage(pageId) {
  // تحديث القائمة النشطة
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
  });
  
  document.querySelector(`[data-page="${pageId}"]`).classList.add('active');
  
  // إخفاء جميع الصفحات وعرض الصفحة المطلوبة
  document.querySelectorAll('.page').forEach(page => {
    page.classList.remove('active');
  });
  
  document.getElementById(pageId).classList.add('active');
  
  // تحديث عنوان الصفحة
  const pageTitles = {
    dashboard: 'لوحة التحكم',
    clients: 'إدارة العملاء',
    techs: 'إدارة الفنيين',
    appointments: 'إدارة المواعيد',
    products: 'إدارة المنتجات',
    orders: 'إدارة الطلبات',
    reports: 'التقارير والإحصائيات',
    backup: 'النسخ الاحتياطي'
  };
  
  document.querySelector('.page-title').textContent = pageTitles[pageId];
  
  // تحميل محتوى الصفحة
  switch(pageId) {
    case 'dashboard':
      loadDashboard();
      updateStats();
      break;
    case 'clients':
      loadClients();
      break;
    case 'techs':
      loadTechs();
      break;
    case 'appointments':
      loadAppointments();
      break;
    case 'products':
      loadProducts();
      break;
    case 'orders':
      loadOrders();
      break;
    case 'reports':
      loadReports();
      break;
    case 'backup':
      loadBackupInfo();
      break;
  }
  
  // إغلاق الشريط الجانبي على الجوال
  if (window.innerWidth <= 992) {
    document.getElementById('sidebar').classList.remove('active');
  }
}

// ربط أحداث القائمة
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', function() {
    const pageId = this.getAttribute('data-page');
    showPage(pageId);
  });
});

// حفظ البيانات في localStorage
function saveData(key, data) {
  localStorage.setItem(`drfilter_${key}`, JSON.stringify(data));
}

// تحميل لوحة التحكم
function loadDashboard() {
  // تحديث الإحصائيات
  updateStats();
  
  // تحميل مواعيد اليوم
  const today = new Date().toISOString().split('T')[0];
  const todayAppointments = appointments.filter(apt => apt.date === today);
  const tbody = document.querySelector('#todayAppointments tbody');
  tbody.innerHTML = '';
  
  if (todayAppointments.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 20px;">لا توجد مواعيد لليوم</td></tr>`;
  } else {
    todayAppointments.forEach(apt => {
      const client = clients.find(c => c.id === apt.clientId) || { name: 'غير معروف' };
      const tech = techs.find(t => t.id === apt.techId) || { name: 'غير معين' };
      
      const statusBadge = apt.status === 'مكتمل' ? 'badge-success' : 
                         apt.status === 'ملغى' ? 'badge-danger' : 'badge-warning';
      
      tbody.innerHTML += `
        <tr>
          <td>${client.name}</td>
          <td>${apt.time}</td>
          <td>${tech.name}</td>
          <td><span class="badge ${statusBadge}">${apt.status}</span></td>
        </tr>
      `;
    });
  }
  
  // تحميل الطلبات التي تحتاج متابعة
  const pendingOrders = orders.filter(order => order.status === 'قيد المعالجة');
  const ordersTbody = document.querySelector('#pendingOrders tbody');
  ordersTbody.innerHTML = '';
  
  if (pendingOrders.length === 0) {
    ordersTbody.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 20px;">لا توجد طلبات تحتاج متابعة</td></tr>`;
  } else {
    pendingOrders.slice(0, 5).forEach(order => {
      const client = clients.find(c => c.id === order.clientId) || { name: 'غير معروف' };
      const statusBadge = order.status === 'مكتمل' ? 'badge-success' : 
                         order.status === 'ملغى' ? 'badge-danger' : 'badge-warning';
      
      ordersTbody.innerHTML += `
        <tr>
          <td>#${order.id}</td>
          <td>${client.name}</td>
          <td>${order.date}</td>
          <td><span class="badge ${statusBadge}">${order.status}</span></td>
        </tr>
      `;
    });
  }
}

// تحديث الإحصائيات
function updateStats() {
  document.getElementById('clientsCount').textContent = clients.length;
  document.getElementById('techsCount').textContent = techs.length;
  
  const today = new Date().toISOString().split('T')[0];
  const todayAppointments = appointments.filter(apt => apt.date === today);
  document.getElementById('appointmentsCount').textContent = todayAppointments.length;
  
  document.getElementById('productsCount').textContent = products.length;
}

// تحميل العملاء
function loadClients() {
  const tbody = document.getElementById('clientsTable');
  tbody.innerHTML = '';
  
  if (clients.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 20px;">لا يوجد عملاء مسجلين بعد</td></tr>`;
  } else {
    clients.forEach((client, index) => {
      // حساب موعد الصيانة القادم (بعد 3 أشهر من التركيب)
      let nextMaintenance = 'غير محدد';
      if (client.installDate) {
        const installDate = new Date(client.installDate);
        installDate.setMonth(installDate.getMonth() + 3);
        nextMaintenance = installDate.toLocaleDateString('ar-SA');
      }
      
      tbody.innerHTML += `
        <tr>
          <td>${index + 1}</td>
          <td>${client.name || 'غير معروف'}</td>
          <td>${client.phone || 'غير محدد'}</td>
          <td>${client.address ? client.address.substring(0, 20) + '...' : 'غير محدد'}</td>
          <td>${client.filterType || 'غير محدد'}</td>
          <td>${nextMaintenance}</td>
          <td><span class="badge badge-success">نشط</span></td>
          <td>
            <div class="action-btns">
              <button class="btn btn-secondary btn-small" onclick="editClient(${client.id})">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-danger btn-small" onclick="deleteClient(${client.id})">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    });
  }
}

// فتح نموذج إضافة عميل
function openClientModal(editId = null) {
  currentEditId = editId;
  const modal = document.getElementById('clientModal');
  const title = modal.querySelector('h3');
  
  if (editId) {
    title.innerHTML = '<i class="fas fa-user-edit"></i> تعديل العميل';
    const client = clients.find(c => c.id === editId);
    
    if (client) {
      document.getElementById('clientName').value = client.name || '';
      document.getElementById('clientPhone').value = client.phone || '';
      document.getElementById('clientEmail').value = client.email || '';
      document.getElementById('clientAddress').value = client.address || '';
      document.getElementById('clientFilterType').value = client.filterType || '';
      document.getElementById('clientInstallDate').value = client.installDate || '';
      document.getElementById('clientNotes').value = client.notes || '';
    }
  } else {
    title.innerHTML = '<i class="fas fa-user-plus"></i> عميل جديد';
    // تفريغ الحقول
    document.getElementById('clientName').value = '';
    document.getElementById('clientPhone').value = '';
    document.getElementById('clientEmail').value = '';
    document.getElementById('clientAddress').value = '';
    document.getElementById('clientFilterType').value = '';
    document.getElementById('clientInstallDate').value = '';
    document.getElementById('clientNotes').value = '';
  }
  
  modal.classList.remove('hidden');
}

// حفظ العميل
function saveClient() {
  const client = {
    id: currentEditId || Date.now(),
    name: document.getElementById('clientName').value,
    phone: document.getElementById('clientPhone').value,
    email: document.getElementById('clientEmail').value,
    address: document.getElementById('clientAddress').value,
    filterType: document.getElementById('clientFilterType').value,
    installDate: document.getElementById('clientInstallDate').value,
    notes: document.getElementById('clientNotes').value,
    createdAt: new Date().toISOString()
  };
  
  if (!client.name) {
    alert('يرجى إدخال اسم العميل');
    return;
  }
  
  if (currentEditId) {
    // تحديث العميل الموجود
    const index = clients.findIndex(c => c.id === currentEditId);
    if (index !== -1) {
      clients[index] = client;
    }
  } else {
    // إضافة عميل جديد
    clients.push(client);
  }
  
  saveData('clients', clients);
  closeModal('clientModal');
  loadClients();
  updateStats();
  
  // إظهار رسالة نجاح
  showAlert('تم حفظ بيانات العميل بنجاح', 'success');
}

// تحميل الفنيين
function loadTechs() {
  const tbody = document.getElementById('techsTable');
  tbody.innerHTML = '';
  
  if (techs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 20px;">لا يوجد فنيين مسجلين بعد</td></tr>`;
  } else {
    techs.forEach((tech, index) => {
      const statusBadge = tech.status === 'نشط' ? 'badge-success' : 
                         tech.status === 'إجازة' ? 'badge-warning' : 'badge-danger';
      
      tbody.innerHTML += `
        <tr>
          <td>${index + 1}</td>
          <td>${tech.name}</td>
          <td>${tech.phone}</td>
          <td>${tech.email}</td>
          <td>${tech.specialty}</td>
          <td>${tech.tasks || 0}</td>
          <td><span class="badge ${statusBadge}">${tech.status}</span></td>
          <td>
            <div class="action-btns">
              <button class="btn btn-secondary btn-small" onclick="editTech(${tech.id})">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-danger btn-small" onclick="deleteTech(${tech.id})">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    });
  }
}

// فتح نموذج إضافة فني
function openTechModal(editId = null) {
  currentEditId = editId;
  const modal = document.getElementById('techModal');
  const title = modal.querySelector('h3');
  
  if (editId) {
    title.innerHTML = '<i class="fas fa-user-edit"></i> تعديل الفني';
    const tech = techs.find(t => t.id === editId);
    
    if (tech) {
      document.getElementById('techName').value = tech.name || '';
      document.getElementById('techPhone').value = tech.phone || '';
      document.getElementById('techEmail').value = tech.email || '';
      document.getElementById('techSpecialty').value = tech.specialty || '';
      document.getElementById('techStatus').value = tech.status || 'نشط';
      document.getElementById('techNotes').value = tech.notes || '';
    }
  } else {
    title.innerHTML = '<i class="fas fa-user-cog"></i> فني جديد';
    // تفريغ الحقول
    document.getElementById('techName').value = '';
    document.getElementById('techPhone').value = '';
    document.getElementById('techEmail').value = '';
    document.getElementById('techSpecialty').value = '';
    document.getElementById('techStatus').value = 'نشط';
    document.getElementById('techNotes').value = '';
  }
  
  modal.classList.remove('hidden');
}

// حفظ الفني
function saveTech() {
  const tech = {
    id: currentEditId || Date.now(),
    name: document.getElementById('techName').value,
    phone: document.getElementById('techPhone').value,
    email: document.getElementById('techEmail').value,
    specialty: document.getElementById('techSpecialty').value,
    status: document.getElementById('techStatus').value,
    notes: document.getElementById('techNotes').value,
    tasks: 0
  };
  
  if (!tech.name) {
    alert('يرجى إدخال اسم الفني');
    return;
  }
  
  if (currentEditId) {
    // تحديث الفني الموجود
    const index = techs.findIndex(t => t.id === currentEditId);
    if (index !== -1) {
      // الحفاظ على عدد المهام
      tech.tasks = techs[index].tasks;
      techs[index] = tech;
    }
  } else {
    // إضافة فني جديد
    techs.push(tech);
  }
  
  saveData('techs', techs);
  closeModal('techModal');
  loadTechs();
  updateStats();
  
  // إظهار رسالة نجاح
  showAlert('تم حفظ بيانات الفني بنجاح', 'success');
}

// تحميل المنتجات
function loadProducts() {
  const container = document.getElementById('productsGrid');
  container.innerHTML = '';
  
  if (products.length === 0) {
    container.innerHTML = `<div class="col-12" style="text-align: center; padding: 40px; color: var(--text-light);">
      <i class="fas fa-filter" style="font-size: 48px; margin-bottom: 20px; display: block;"></i>
      <p>لا توجد منتجات مسجلة بعد</p>
    </div>`;
  } else {
    products.forEach(product => {
      const statusClass = product.status === 'متوفر' ? 'badge-success' : 
                         product.status === 'قليل' ? 'badge-warning' : 'badge-danger';
      
      container.innerHTML += `
        <div class="col-4">
          <div class="card" style="height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <h4 style="margin-bottom: 10px;">${product.name}</h4>
              <span class="badge ${statusClass}">${product.status}</span>
            </div>
            <p style="color: var(--text-light); margin-bottom: 15px;">${product.category}</p>
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
              <div>
                <strong>السعر:</strong> ${product.price} ريال
              </div>
              <div>
                <strong>المخزون:</strong> ${product.stock}
              </div>
            </div>
            <div class="action-btns">
              <button class="btn btn-secondary btn-small" onclick="editProduct(${product.id})">
                <i class="fas fa-edit"></i> تعديل
              </button>
              <button class="btn btn-danger btn-small" onclick="deleteProduct(${product.id})">
                <i class="fas fa-trash"></i> حذف
              </button>
            </div>
          </div>
        </div>
      `;
    });
  }
}

// تحميل الطلبات
function loadOrders() {
  const tbody = document.getElementById('ordersTable');
  tbody.innerHTML = '';
  
  if (orders.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 20px;">لا توجد طلبات مسجلة بعد</td></tr>`;
  } else {
    orders.forEach(order => {
      const client = clients.find(c => c.id === order.clientId) || { name: 'غير معروف' };
      const statusBadge = order.status === 'مكتمل' ? 'badge-success' : 
                         order.status === 'ملغى' ? 'badge-danger' : 'badge-warning';
      
      tbody.innerHTML += `
        <tr>
          <td>#${order.id}</td>
          <td>${client.name}</td>
          <td>${order.products ? order.products.length : 0} منتج</td>
          <td>${order.total || 0} ريال</td>
          <td>${order.date || 'غير محدد'}</td>
          <td><span class="badge ${statusBadge}">${order.status}</span></td>
          <td>
            <div class="action-btns">
              <button class="btn btn-secondary btn-small" onclick="viewOrder(${order.id})">
                <i class="fas fa-eye"></i>
              </button>
              <button class="btn btn-danger btn-small" onclick="deleteOrder(${order.id})">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    });
  }
}

// تحميل التقارير
function loadReports() {
  const tbody = document.getElementById('reportsTable');
  tbody.innerHTML = '';
  
  // بيانات افتراضية للتقرير
  const months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'];
  const reportsData = [];
  
  for (let i = 0; i < 6; i++) {
    reportsData.push({
      month: months[i],
      newClients: Math.floor(Math.random() * 20) + 5,
      appointments: Math.floor(Math.random() * 30) + 10,
      totalSales: Math.floor(Math.random() * 50000) + 10000,
      netProfit: Math.floor(Math.random() * 20000) + 5000
    });
  }
  
  reportsData.forEach(report => {
    tbody.innerHTML += `
      <tr>
        <td>${report.month} 2023</td>
        <td>${report.newClients}</td>
        <td>${report.appointments}</td>
        <td>${report.totalSales.toLocaleString()} ريال</td>
        <td>${report.netProfit.toLocaleString()} ريال</td>
      </tr>
    `;
  });
}

// تحميل معلومات النسخ الاحتياطي
function loadBackupInfo() {
  // حساب حجم البيانات
  let totalSize = 0;
  const keys = ['clients', 'techs', 'appointments', 'products', 'orders'];
  
  keys.forEach(key => {
    const data = localStorage.getItem(`drfilter_${key}`);
    if (data) {
      totalSize += data.length;
    }
  });
  
  document.getElementById('totalData').textContent = Math.round(totalSize / 1024);
  
  // عرض قائمة النسخ الاحتياطية
  const backupList = document.getElementById('backupList');
  const backups = JSON.parse(localStorage.getItem('drfilter_backups') || '[]');
  
  if (backups.length === 0) {
    backupList.innerHTML = `<div style="padding: 20px 0; text-align: center; color: var(--text-light);">
      <p>لا توجد نسخ احتياطية</p>
    </div>`;
    document.getElementById('lastBackup').textContent = 'لم يتم بعد';
  } else {
    const lastBackup = backups[backups.length - 1];
    document.getElementById('lastBackup').textContent = new Date(lastBackup.date).toLocaleDateString('ar-SA');
    
    backupList.innerHTML = '<h4 style="margin-bottom: 15px;">النسخ الاحتياطية السابقة</h4>';
    
    backups.slice(-5).reverse().forEach((backup, index) => {
      backupList.innerHTML += `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid var(--gray);">
          <div>
            <strong>نسخة ${backups.length - index}</strong>
            <p style="font-size: 12px; color: var(--text-light); margin-top: 5px;">
              ${new Date(backup.date).toLocaleString('ar-SA')}
            </p>
          </div>
          <button class="btn btn-secondary btn-small" onclick="restoreSpecificBackup(${backup.id})">
            استعادة
          </button>
        </div>
      `;
    });
  }
}

// إنشاء نسخة احتياطية
function createBackup() {
  const backup = {
    id: Date.now(),
    date: new Date().toISOString(),
    clients: JSON.parse(localStorage.getItem('drfilter_clients') || '[]'),
    techs: JSON.parse(localStorage.getItem('drfilter_techs') || '[]'),
    appointments: JSON.parse(localStorage.getItem('drfilter_appointments') || '[]'),
    products: JSON.parse(localStorage.getItem('drfilter_products') || '[]'),
    orders: JSON.parse(localStorage.getItem('drfilter_orders') || '[]')
  };
  
  let backups = JSON.parse(localStorage.getItem('drfilter_backups') || '[]');
  backups.push(backup);
  
  // الاحتفاظ فقط بـ 10 نسخ احتياطية
  if (backups.length > 10) {
    backups = backups.slice(-10);
  }
  
  localStorage.setItem('drfilter_backups', JSON.stringify(backups));
  
  // تحديث العرض
  loadBackupInfo();
  
  // إظهار رسالة نجاح
  showAlert('تم إنشاء نسخة احتياطية بنجاح', 'success');
}

// استعادة نسخة احتياطية
function restoreBackup() {
  if (confirm('هل أنت متأكد من استعادة النسخة الاحتياطية؟ سيتم استبدال جميع البيانات الحالية.')) {
    const backups = JSON.parse(localStorage.getItem('drfilter_backups') || '[]');
    
    if (backups.length === 0) {
      alert('لا توجد نسخ احتياطية للاستعادة');
      return;
    }
    
    const lastBackup = backups[backups.length - 1];
    
    // استعادة البيانات
    localStorage.setItem('drfilter_clients', JSON.stringify(lastBackup.clients));
    localStorage.setItem('drfilter_techs', JSON.stringify(lastBackup.techs));
    localStorage.setItem('drfilter_appointments', JSON.stringify(lastBackup.appointments));
    localStorage.setItem('drfilter_products', JSON.stringify(lastBackup.products));
    localStorage.setItem('drfilter_orders', JSON.stringify(lastBackup.orders));
    
    // تحديث المتغيرات
    clients = lastBackup.clients;
    techs = lastBackup.techs;
    appointments = lastBackup.appointments;
    products = lastBackup.products;
    orders = lastBackup.orders;
    
    // تحديث العرض
    loadDashboard();
    loadClients();
    loadTechs();
    loadProducts();
    loadOrders();
    
    showAlert('تم استعادة النسخة الاحتياطية بنجاح', 'success');
  }
}

// إغلاق النموذج
function closeModal(modalId) {
  document.getElementById(modalId).classList.add('hidden');
  currentEditId = null;
}

// عرض رسالة تنبيه
function showAlert(message, type = 'info') {
  // إزالة أي رسائل سابقة
  const existingAlert = document.querySelector('.global-alert');
  if (existingAlert) {
    existingAlert.remove();
  }
  
  // إنشاء رسالة جديدة
  const alert = document.createElement('div');
  alert.className = `global-alert alert alert-${type}`;
  alert.innerHTML = `
    <span>${message}</span>
    <button onclick="this.parentElement.remove()" style="background: none; border: none; color: inherit; margin-right: 10px;">×</button>
  `;
  
  // إضافة الأنماط
  alert.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 1000;
    min-width: 300px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: fadeIn 0.5s ease-out;
  `;
  
  document.body.appendChild(alert);
  
  // إزالة الرسالة بعد 5 ثواني
  setTimeout(() => {
    if (alert.parentElement) {
      alert.remove();
    }
  }, 5000);
}

// الوظائف المساعدة
function deleteClient(id) {
  if (confirm('هل أنت متأكد من حذف هذا العميل؟')) {
    clients = clients.filter(c => c.id !== id);
    saveData('clients', clients);
    loadClients();
    updateStats();
    showAlert('تم حذف العميل بنجاح', 'success');
  }
}

function deleteTech(id) {
  if (confirm('هل أنت متأكد من حذف هذا الفني؟')) {
    techs = techs.filter(t => t.id !== id);
    saveData('techs', techs);
    loadTechs();
    updateStats();
    showAlert('تم حذف الفني بنجاح', 'success');
  }
}

function deleteProduct(id) {
  if (confirm('هل أنت متأكد من حذف هذا المنتج؟')) {
    products = products.filter(p => p.id !== id);
    saveData('products', products);
    loadProducts();
    updateStats();
    showAlert('تم حذف المنتج بنجاح', 'success');
  }
}

function deleteOrder(id) {
  if (confirm('هل أنت متأكد من حذف هذا الطلب؟')) {
    orders = orders.filter(o => o.id !== id);
    saveData('orders', orders);
    loadOrders();
    showAlert('تم حذف الطلب بنجاح', 'success');
  }
}

function editClient(id) {
  openClientModal(id);
}

function editTech(id) {
  openTechModal(id);
}

function editProduct(id) {
  // يمكن تنفيذ هذه الوظيفة لاحقاً
  alert('ستتم إضافة هذه الوظيفة قريباً');
}

function viewOrder(id) {
  // يمكن تنفيذ هذه الوظيفة لاحقاً
  alert('ستتم إضافة هذه الوظيفة قريباً');
}

function openAppointmentModal() {
  alert('ستتم إضافة هذه الوظيفة قريباً');
}

function openProductModal() {
  alert('ستتم إضافة هذه الوظيفة قريباً');
}

function openOrderModal() {
  alert('ستتم إضافة هذه الوظيفة قريباً');
}

function generateReport(type) {
  alert(`سيتم إنشاء تقرير ${type === 'monthly' ? 'شهري' : 'سنوي'}`);
}

function restoreSpecificBackup(id) {
  if (confirm('هل أنت متأكد من استعادة هذه النسخة الاحتياطية؟')) {
    const backups = JSON.parse(localStorage.getItem('drfilter_backups') || '[]');
    const backup = backups.find(b => b.id === id);
    
    if (backup) {
      // استعادة البيانات
      localStorage.setItem('drfilter_clients', JSON.stringify(backup.clients));
      localStorage.setItem('drfilter_techs', JSON.stringify(backup.techs));
      localStorage.setItem('drfilter_appointments', JSON.stringify(backup.appointments));
      localStorage.setItem('drfilter_products', JSON.stringify(backup.products));
      localStorage.setItem('drfilter_orders', JSON.stringify(backup.orders));
      
      // تحديث المتغيرات
      clients = backup.clients;
      techs = backup.techs;
      appointments = backup.appointments;
      products = backup.products;
      orders = backup.orders;
      
      // تحديث العرض
      loadDashboard();
      loadClients();
      loadTechs();
      loadProducts();
      loadOrders();
      
      showAlert('تم استعادة النسخة الاحتياطية بنجاح', 'success');
    }
  }
}

// تحميل المواعيد (وظيفة مساعدة)
function loadAppointments() {
  const tbody = document.getElementById('appointmentsTable');
  tbody.innerHTML = '';
  
  if (appointments.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align: center; padding: 20px;">لا توجد مواعيد مسجلة بعد</td></tr>`;
  } else {
    appointments.forEach((apt, index) => {
      const client = clients.find(c => c.id === apt.clientId) || { name: 'غير معروف' };
      const tech = techs.find(t => t.id === apt.techId) || { name: 'غير معين' };
      
      const statusBadge = apt.status === 'مكتمل' ? 'badge-success' : 
                         apt.status === 'ملغى' ? 'badge-danger' : 'badge-warning';
      
      tbody.innerHTML += `
        <tr>
          <td>${index + 1}</td>
          <td>${client.name}</td>
          <td>${tech.name}</td>
          <td>${apt.serviceType || 'صيانة'}</td>
          <td>${apt.date || 'غير محدد'}</td>
          <td>${apt.time || 'غير محدد'}</td>
          <td><span class="badge ${statusBadge}">${apt.status}</span></td>
          <td>
            <div class="action-btns">
              <button class="btn btn-secondary btn-small" onclick="editAppointment(${apt.id})">
                <i class="fas fa-edit"></i>
              </button>
              <button class="btn btn-danger btn-small" onclick="deleteAppointment(${apt.id})">
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </td>
        </tr>
      `;
    });
  }
}

// تهيئة النظام عند التحميل
document.addEventListener('DOMContentLoaded', function() {
  // إضافة أنماط النماذج المنبثقة
  const style = document.createElement('style');
  style.textContent = `
    .modal {
      position: fixed;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      background: rgba(0, 0, 0, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      padding: 20px;
    }
    
    .modal-content {
      background: white;
      border-radius: var(--radius);
      width: 100%;
      max-width: 600px;
      max-height: 90vh;
      overflow: auto;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .modal-header {
      padding: 20px;
      border-bottom: 1px solid var(--gray);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    
    .modal-header h3 {
      margin: 0;
      color: var(--dark);
    }
    
    .close {
      font-size: 28px;
      cursor: pointer;
      color: var(--text-light);
    }
    
    .modal-body {
      padding: 20px;
    }
    
    .modal-footer {
      padding: 20px;
      border-top: 1px solid var(--gray);
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
    
    textarea, select {
      width: 100%;
      padding: 12px 15px;
      border: 1px solid var(--gray);
      border-radius: var(--radius);
      font-size: 16px;
      transition: var(--transition);
    }
    
    textarea:focus, select:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(26, 115, 232, 0.2);
    }
  `;
  document.head.appendChild(style);
  
  // ضبط تاريخ اليوم في نموذج العميل
  const today = new Date().toISOString().split('T')[0];
  document.getElementById('clientInstallDate').value = today;
});
</script>
</body>
</html>
