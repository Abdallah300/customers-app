import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# ================== 1. إعدادات المظهر (الأزرق الاحترافي) ==================

st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>  
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');  
    .stApp { background: #000b1a; color: #ffffff; }  
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }  
    .client-header {   
        background: #001f3f; border-radius: 15px;   
        padding: 20px; border: 2px solid #007bff; margin-bottom: 25px;   
    }  
    header {visibility: hidden;}  
    footer {visibility: hidden;}  
    .stButton > button {
        width: 100%;
        background: linear-gradient(45deg, #007bff, #0056b3);
        color: white;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #0056b3, #003d82);
        transform: translateY(-2px);
    }
    .highlight-number {
        font-size: 1.5em;
        color: #00ffcc;
        font-weight: bold;
    }
</style>  
""", unsafe_allow_html=True)

# ================== 2. إدارة البيانات ==================

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: 
                return json.load(f)
            except: 
                return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: 
    st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: 
    st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    total_debt = sum(float(h.get('debt', 0)) for h in history)
    total_paid = sum(float(h.get('price', 0)) for h in history)
    return total_debt - total_paid

# إضافة جديدة: دالة لحفظ نسخة احتياطية
def create_backup():
    try:
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"customers_backup_{timestamp}.json")
        
        with open(backup_file, "w", encoding="utf-8") as f:
            json.dump(st.session_state.data, f, ensure_ascii=False, indent=2)
        
        # حذف الملفات القديمة (احتفظ بآخر 10 نسخ)
        if os.path.exists(backup_dir):
            backup_files = sorted([f for f in os.listdir(backup_dir) if f.endswith('.json')])
            if len(backup_files) > 10:
                for old_file in backup_files[:-10]:
                    try:
                        os.remove(os.path.join(backup_dir, old_file))
                    except:
                        pass
        return True
    except Exception as e:
        st.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
        return False

# إضافة جديدة: دالة لتصدير البيانات
def export_to_excel():
    try:
        data = []
        for customer in st.session_state.data:
            balance = calculate_balance(customer.get('history', []))
            data.append({
                'ID': customer.get('id', 0),
                'الاسم': customer.get('name', ''),
                'المحافظة': customer.get('gov', ''),
                'الفرع': customer.get('branch', ''),
                'الرصيد الحالي': balance,
                'عدد العمليات': len(customer.get('history', []))
            })
        
        df = pd.DataFrame(data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"customers_export_{timestamp}.xlsx"
        df.to_excel(filename, index=False)
        return filename
    except Exception as e:
        st.error(f"خطأ في تصدير البيانات: {e}")
        return None

# ================== 3. واجهة الباركود ==================

params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h1 style='text-align:center; color:#00d4ff;'>Power Life 💧</h1>", unsafe_allow_html=True)

            # حساب الرصيد الإجمالي الحالي  
            current_bal = calculate_balance(c.get('history', []))  
            
            st.markdown(f"""  
            <div class='client-header'>  
                <div style='font-size:18px;'>👤 <b>العميل:</b> {c.get('name', '')}</div>  
                <div style='font-size:15px; color:#00d4ff;'>📍 {c.get('gov', '---')} | 🏛️ {c.get('branch', '---')}</div>  
                <hr style='border: 0.5px solid #007bff; opacity: 0.3;'>  
                <div style='text-align:center;'>  
                    <p style='margin:0;'>إجمالي المديونية الحالية</p>  
                    <p style='font-size:35px; color:#00ffcc; font-weight:bold; margin:0;'>{current_bal:,.0f} ج.م</p>  
                </div>  
            </div>  
            """, unsafe_allow_html=True)  
            
            # إحصائيات سريعة
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("عدد العمليات", len(c.get('history', [])))
            with col2:
                total_debt = sum(float(h.get('debt', 0)) for h in c.get('history', []))
                st.metric("إجمالي المديونيات", f"{total_debt:,.0f} ج.م")
            with col3:
                total_paid = sum(float(h.get('price', 0)) for h in c.get('history', []))
                st.metric("إجمالي المدفوعات", f"{total_paid:,.0f} ج.م")
            
            st.subheader("📋 سجل الحركات المالي التفصيلي")  
            
            if c.get('history'):  
                # حساب الرصيد التراكمي لكل خطوة  
                running_balance = 0  
                history_with_balance = []  
                for h in c['history']:  
                    running_balance += (float(h.get('debt', 0)) - float(h.get('price', 0)))  
                    h_copy = h.copy()  
                    h_copy['after_bal'] = running_balance  
                    history_with_balance.append(h_copy)  
                
                # فلترة حسب النوع
                date_filter = st.selectbox(
                    "🔍 تصفية حسب النوع",
                    ["جميع العمليات", "المديونيات فقط", "المدفوعات فقط", "آخر 10 عمليات"]
                )
                
                filtered_history = []
                if date_filter == "المديونيات فقط":
                    filtered_history = [h for h in reversed(history_with_balance) if float(h.get('debt', 0)) > 0]
                elif date_filter == "المدفوعات فقط":
                    filtered_history = [h for h in reversed(history_with_balance) if float(h.get('price', 0)) > 0]
                elif date_filter == "آخر 10 عمليات":
                    filtered_history = list(reversed(history_with_balance))[:10]
                else:
                    filtered_history = list(reversed(history_with_balance))
                
                # عرض التاريخ  
                for h in filtered_history:  
                    with st.container():  
                        st.markdown("---")  
                        col1, col2 = st.columns([2, 1])  
                        with col1:  
                            st.markdown(f"**📝 {h.get('note', 'عملية مالية')}**")  
                            if float(h.get('debt', 0)) > 0: 
                                st.markdown(f"<span style='color:#ff4444'>🔴 مضاف للحساب: `{float(h.get('debt', 0)):,.0f} ج.م`</span>", unsafe_allow_html=True)  
                            if float(h.get('price', 0)) > 0: 
                                st.markdown(f"<span style='color:#44ff44'>🟢 مبلغ محصل: `{float(h.get('price', 0)):,.0f} ج.م`</span>", unsafe_allow_html=True)  
                        with col2:  
                            st.markdown(f"📅 `{h.get('date', '---')}`")  
                            st.markdown(f"👤 `{h.get('tech', 'الإدارة')}`")  
                          
                        # ميزة الرصيد المتبقي بعد كل زيارة  
                        st.info(f"💰 المديونية المتبقية بعد هذه العملية: {float(h['after_bal']):,.0f} ج.م")  
                
                # ملخص بياني
                if len(c.get('history', [])) > 1:
                    try:
                        st.subheader("📈 ملخص بياني")
                        df_history = pd.DataFrame(c['history'])
                        # تحويل التاريخ
                        df_history['date'] = pd.to_datetime(df_history['date'], errors='coerce')
                        df_history = df_history.dropna(subset=['date'])
                        df_history = df_history.sort_values('date')
                        
                        # تحويل الأعمدة إلى أرقام
                        df_history['debt'] = pd.to_numeric(df_history['debt'], errors='coerce').fillna(0)
                        df_history['price'] = pd.to_numeric(df_history['price'], errors='coerce').fillna(0)
                        
                        # حساب الرصيد التراكمي
                        df_history['debt_cum'] = df_history['debt'].cumsum()
                        df_history['price_cum'] = df_history['price'].cumsum()
                        df_history['balance_cum'] = df_history['debt_cum'] - df_history['price_cum']
                        
                        fig, ax = plt.subplots(figsize=(10, 4))
                        ax.plot(df_history['date'], df_history['balance_cum'], marker='o', linewidth=2)
                        ax.fill_between(df_history['date'], 0, df_history['balance_cum'], alpha=0.3)
                        ax.set_xlabel('التاريخ')
                        ax.set_ylabel('الرصيد (ج.م)')
                        ax.grid(True, alpha=0.3)
                        ax.set_facecolor('#0e1117')
                        fig.patch.set_facecolor('#0e1117')
                        ax.tick_params(colors='white')
                        ax.xaxis.label.set_color('white')
                        ax.yaxis.label.set_color('white')
                        
                        st.pyplot(fig)
                    except Exception as e:
                        st.warning(f"لا يمكن عرض الرسم البياني: {e}")
                    
            else:  
                st.info("لا توجد عمليات مسجلة.")  
        
        # زر للطباعة والتقرير
        st.markdown("---")
        col_print1, col_print2 = st.columns(2)
        with col_print1:
            if st.button("🖨️ طباعة تقرير العميل", use_container_width=True):
                st.success("تم إنشاء تقرير العميل للطباعة (يمكنك استخدام Ctrl+P)")
        with col_print2:
            if st.button("📱 مشاركة الباركود", use_container_width=True):
                st.info("انسخ الرابط أدناه:")
                st.code(f"https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={cust_id}")
        
        st.stop()  
    except Exception as e:  
        st.error(f"خطأ في تحميل بيانات العميل: {e}")
        st.stop()

# ================== 4. لوحة التحكم (الدخول) ==================

if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>Power Life Control 🔒</h2>", unsafe_allow_html=True)
    
    # إحصائيات سريعة على شاشة الدخول
    total_customers = len(st.session_state.data)
    total_techs = len(st.session_state.techs)
    total_balance = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
    
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("👥 عدد العملاء", total_customers)
    with col_stats2:
        st.metric("🛠️ عدد الفنيين", total_techs)
    with col_stats3:
        st.metric("💰 إجمالي المديونيات", f"{total_balance:,.0f} ج.م")
    
    c1, c2 = st.columns(2)
    if c1.button("🔑 لوحة الإدارة", use_container_width=True): 
        st.session_state.role = "admin_login"
        st.rerun()
    if c2.button("🛠️ لوحة الفني", use_container_width=True): 
        st.session_state.role = "tech_login"
        st.rerun()
    
    # نبذة عن النظام
    with st.expander("ℹ️ معلومات عن النظام"):
        st.write("""
        **Power Life System** - نظام إدارة العملاء والفنيين
        
        المميزات:
        - إدارة كاملة لسجلات العملاء
        - متابعة المديونيات والمدفوعات
        - باركود فريد لكل عميل
        - واجهة منفصلة للإدارة والفنيين
        - تقارير وإحصائيات مفصلة
        """)
    
    st.stop()

# منطق تسجيل الدخول
if st.session_state.role == "admin_login":
    u = st.text_input("اسم المستخدم")
    p = st.text_input("كلمة السر", type="password")
    col_login1, col_login2 = st.columns(2)
    with col_login1:
        if st.button("دخول", use_container_width=True):
            if u == "admin" and p == "admin123": 
                st.session_state.role = "admin"
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة السر غير صحيحة")
    with col_login2:
        if st.button("رجوع", use_container_width=True): 
            del st.session_state.role
            st.rerun()
    st.stop()

if st.session_state.role == "tech_login":
    t_list = [t.get('name', '') for t in st.session_state.techs if t.get('name')]
    if t_list:
        t_user = st.selectbox("اختر الفني", t_list)
        p = st.text_input("السر", type="password")
        col_login1, col_login2 = st.columns(2)
        with col_login1:
            if st.button("دخول", use_container_width=True):
                tech = next((t for t in st.session_state.techs if t.get('name') == t_user), None)
                if tech and p == tech.get('pass', ''): 
                    st.session_state.role = "tech"
                    st.session_state.tech_name = t_user
                    st.rerun()
                else:
                    st.error("اسم الفني أو كلمة السر غير صحيحة")
        with col_login2:
            if st.button("رجوع", use_container_width=True): 
                del st.session_state.role
                st.rerun()
    else:
        st.error("لا يوجد فنيين مسجلين في النظام")
        if st.button("رجوع"):
            del st.session_state.role
            st.rerun()
    st.stop()

# ================== 5. واجهة الإدارة الكاملة ==================

if st.session_state.role == "admin":
    st.sidebar.title("💎 لوحة الإدارة")
    menu = st.sidebar.radio("القائمة", ["👥 إدارة العملاء", "➕ إضافة عميل", "📊 الحسابات", "🛠️ الفنيين", "📁 النسخ الاحتياطية", "🚪 خروج"])
    
    # إحصائيات في الشريط الجانبي
    st.sidebar.markdown("---")
    total_balance = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
    st.sidebar.metric("💰 إجمالي المديونيات", f"{total_balance:,.0f} ج.م")
    st.sidebar.metric("👥 عدد العملاء", len(st.session_state.data))
    
    if menu == "👥 إدارة العملاء":  
        # حقل بحث متقدم
        col_search1, col_search2 = st.columns(2)
        with col_search1:
            search_name = st.text_input("بحث بالاسم...", key="search_name")
        with col_search2:
            gov_list = list(set(c.get('gov', '') for c in st.session_state.data if c.get('gov')))
            gov_list = ["جميع المحافظات"] + sorted([g for g in gov_list if g])
            search_gov = st.selectbox("فلترة بالمحافظة", gov_list, key="search_gov")
        
        filtered_data = st.session_state.data
        if search_name:
            filtered_data = [c for c in filtered_data if search_name.lower() in c.get('name', '').lower()]
        if search_gov != "جميع المحافظات":
            filtered_data = [c for c in filtered_data if c.get('gov') == search_gov]
        
        st.write(f"**عدد العملاء المطابقين:** {len(filtered_data)}")
        
        for i, c in enumerate(filtered_data):  
            balance = calculate_balance(c.get('history', []))
            # تلوين حسب المديونية
            balance_color = "#ff4444" if balance > 0 else "#44ff44" if balance < 0 else "#888888"
            
            with st.expander(f"👤 **{c.get('name', '')}** | الرصيد: <span style='color:{balance_color}'>{balance:,.0f} ج.م</span> | المحافظة: {c.get('gov', '---')}", unsafe_allow_html=True):  
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.write(f"**ID:** {c.get('id', '')}")
                with col_info2:
                    st.write(f"**الفرع:** {c.get('branch', '---')}")
                with col_info3:
                    st.write(f"**عدد العمليات:** {len(c.get('history', []))}")
                
                with st.form(f"adm_f_{c.get('id', i)}"):  
                    c['gov'] = st.text_input("المحافظة", value=c.get('gov', ''), key=f"gov_{c.get('id', i)}")  
                    c['branch'] = st.text_input("الفرع", value=c.get('branch', ''), key=f"branch_{c.get('id', i)}")  
                    
                    col_form1, col_form2 = st.columns(2)
                    with col_form1:
                        a_add = st.number_input("إضافة مديونية (+)", min_value=0.0, key=f"add_{c.get('id', i)}")  
                    with col_form2:
                        a_rem = st.number_input("خصم مبلغ (تحصيل) (-)", min_value=0.0, key=f"rem_{c.get('id', i)}")  
                    
                    note = st.text_input("بيان العملية", value="تسويه إدارية", key=f"note_{c.get('id', i)}")  
                    
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.form_submit_button("💾 حفظ التعديلات", use_container_width=True):  
                            if a_add > 0 or a_rem > 0:  
                                c['history'].append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                                    "note": note, 
                                    "tech": "الإدارة", 
                                    "debt": a_add, 
                                    "price": a_rem
                                })  
                                create_backup()
                            save_json("customers.json", st.session_state.data)
                            st.success("تم الحفظ بنجاح!")
                            st.rerun()
                
                # أزرار إضافية
                col_actions1, col_actions2, col_actions3 = st.columns(3)
                with col_actions1:
                    if st.button("🖼️ باركود", key=f"qr_{c.get('id', i)}", use_container_width=True):  
                        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app/?id={c.get('id', '')}"
                        st.image(qr_url)  
                with col_actions2:
                    if st.button("📋 سجل العمليات", key=f"history_{c.get('id', i)}", use_container_width=True):
                        st.write(f"**سجل عمليات {c.get('name', '')}:**")
                        for h in reversed(c.get('history', [])):
                            st.write(f"- {h.get('date', '')}: {h.get('note', '')} ({h.get('tech', '')})")
                with col_actions3:
                    if st.button("🗑️ حذف العميل", key=f"delete_{c.get('id', i)}", use_container_width=True):
                        confirm = st.checkbox(f"تأكيد حذف العميل {c.get('name', '')}?", key=f"confirm_del_{c.get('id', i)}")
                        if confirm:
                            st.session_state.data.remove(c)
                            save_json("customers.json", st.session_state.data)
                            create_backup()
                            st.success("تم حذف العميل")
                            st.rerun()

    elif menu == "➕ إضافة عميل":  
        with st.form("new_c"):  
            n = st.text_input("اسم العميل")  
            g = st.text_input("المحافظة")  
            b = st.text_input("الفرع")  
            d = st.number_input("مديونية افتتاحية", min_value=0.0)  
            
            col_add1, col_add2 = st.columns(2)
            with col_add1:
                if st.form_submit_button("➕ إضافة عميل", use_container_width=True):  
                    try:
                        ids = [x.get('id', 0) for x in st.session_state.data]
                        new_id = max(ids) + 1 if ids else 1
                        new_customer = {
                            "id": new_id, 
                            "name": n, 
                            "gov": g, 
                            "branch": b, 
                            "history": []
                        }
                        
                        if d > 0:
                            new_customer['history'] = [{
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                                "note": "رصيد افتتاحى", 
                                "tech": "الإدارة", 
                                "debt": d, 
                                "price": 0
                            }]
                        
                        st.session_state.data.append(new_customer)
                        save_json("customers.json", st.session_state.data)
                        create_backup()
                        st.success("تم إضافة العميل بنجاح!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ في إضافة العميل: {e}")
            with col_add2:
                if st.form_submit_button("🗑️ مسح الحقول", use_container_width=True):
                    st.rerun()

    elif menu == "📊 الحسابات":  
        total = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)  
        st.metric("إجمالي مديونيات السوق", f"{total:,.0f} ج.م")  
        
        # إحصائيات متقدمة
        st.subheader("📈 إحصائيات متقدمة")
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            total_customers = len(st.session_state.data)
            customers_with_balance = len([c for c in st.session_state.data if calculate_balance(c.get('history', [])) > 0])
            st.metric("عملاء لديهم مديونيات", f"{customers_with_balance}/{total_customers}")
        
        with col_stat2:
            total_transactions = sum(len(c.get('history', [])) for c in st.session_state.data)
            st.metric("إجمالي العمليات", total_transactions)
        
        with col_stat3:
            avg_balance = total / total_customers if total_customers > 0 else 0
            st.metric("متوسط المديونية", f"{avg_balance:,.0f} ج.م")
        
        # تصدير البيانات
        st.subheader("📤 تصدير البيانات")
        if st.button("📊 تصدير إلى Excel", use_container_width=True):
            filename = export_to_excel()
            if filename:
                try:
                    with open(filename, "rb") as f:
                        st.download_button(
                            label="⬇️ تحميل ملف Excel",
                            data=f,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                except Exception as e:
                    st.error(f"خطأ في تحميل الملف: {e}")
        
        # جدول بأكبر المدينين
        st.subheader("📋 أكبر 10 مدينين")
        customers_with_balance = []
        for c in st.session_state.data:
            name = c.get('name', '')
            balance = calculate_balance(c.get('history', []))
            if balance > 0:
                customers_with_balance.append((name, balance))
        
        customers_with_balance.sort(key=lambda x: x[1], reverse=True)
        customers_with_balance = customers_with_balance[:10]
        
        if customers_with_balance:
            for name, balance in customers_with_balance:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(name)
                with col2:
                    st.write(f"{balance:,.0f} ج.م")
        else:
            st.info("لا يوجد عملاء لديهم مديونيات حالياً")

    elif menu == "🛠️ الفنيين":  
        st.subheader("إدارة الفنيين")
        
        col_tech1, col_tech2 = st.columns(2)
        with col_tech1:
            with st.form("add_tech"):
                tech_name = st.text_input("اسم الفني")
                tech_pass = st.text_input("كلمة السر", type="password")
                tech_phone = st.text_input("رقم الهاتف (اختياري)")
                if st.form_submit_button("➕ إضافة فني"):
                    if tech_name and tech_pass:
                        new_tech = {"name": tech_name, "pass": tech_pass}
                        if tech_phone:
                            new_tech["phone"] = tech_phone
                        st.session_state.techs.append(new_tech)
                        save_json("techs.json", st.session_state.techs)
                        st.success(f"تم إضافة الفني {tech_name}")
                        st.rerun()
                    else:
                        st.error("الرجاء إدخال اسم الفني وكلمة السر")
        
        with col_tech2:
            st.write("**قائمة الفنيين الحاليين:**")
            if st.session_state.techs:
                for tech in st.session_state.techs:
                    with st.expander(f"🛠️ {tech.get('name', '')}"):
                        st.write(f"كلمة السر: {tech.get('pass', '')}")
                        if tech.get('phone'):
                            st.write(f"الهاتف: {tech.get('phone', '')}")
                        if st.button(f"🗑️ حذف {tech.get('name', '')}", key=f"del_tech_{tech.get('name', '')}"):
                            st.session_state.techs.remove(tech)
                            save_json("techs.json", st.session_state.techs)
                            st.rerun()
            else:
                st.info("لا يوجد فنيين مسجلين")

    elif menu == "📁 النسخ الاحتياطية":
        st.subheader("النسخ الاحتياطية")
        
        if st.button("💾 إنشاء نسخة احتياطية الآن", use_container_width=True):
            if create_backup():
                st.success("تم إنشاء نسخة احتياطية بنجاح!")
        
        # عرض النسخ الاحتياطية المتاحة
        backup_dir = "backups"
        if os.path.exists(backup_dir):
            backup_files = sorted([f for f in os.listdir(backup_dir) if f.endswith('.json')], reverse=True)
            
            st.write(f"**النسخ الاحتياطية المتاحة ({len(backup_files)})**")
            for backup_file in backup_files[:10]:  # عرض آخر 10 فقط
                file_path = os.path.join(backup_dir, backup_file)
                try:
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        # تنسيق اسم الملف لعرضه بشكل أفضل
                        display_name = backup_file.replace('customers_backup_', '').replace('.json', '')
                        st.write(display_name)
                    with col2:
                        st.write(f"{file_size:.1f} كيلوبايت")
                    with col3:
                        if st.button("🔄 استعادة", key=f"restore_{backup_file}"):
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    restored_data = json.load(f)
                                st.session_state.data = restored_data
                                save_json("customers.json", st.session_state.data)
                                st.success("تم استعادة النسخة الاحتياطية!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"خطأ في استعادة النسخة: {e}")
                except:
                    pass
        else:
            st.info("لا توجد نسخ احتياطية حتى الآن")

    elif menu == "🚪 خروج": 
        del st.session_state.role
        st.rerun()

# ================== 6. واجهة الفني الكاملة ==================

elif st.session_state.role == "tech":
    st.sidebar.title(f"🛠️ {st.session_state.tech_name}")
    
    # إحصائيات للفني
    tech_customers = []
    tech_total_debt = 0
    tech_total_collected = 0
    
    for customer in st.session_state.data:
        for history in customer.get('history', []):
            if history.get('tech') == st.session_state.tech_name:
                tech_total_debt += float(history.get('debt', 0))
                tech_total_collected += float(history.get('price', 0))
                if customer not in tech_customers:
                    tech_customers.append(customer)
    
    st.sidebar.metric("👥 عملاء خدمتهم", len(tech_customers))
    st.sidebar.metric("💰 إجمالي التحصيل", f"{tech_total_collected:,.0f} ج.م")
    
    # قائمة العملاء
    customer_names = [c.get('name', '') for c in st.session_state.data]
    if customer_names:
        selected_customer_name = st.selectbox("اختر العميل", customer_names)
        target = next((c for c in st.session_state.data if c.get('name') == selected_customer_name), None)
    else:
        st.warning("لا يوجد عملاء مسجلين")
        target = None
    
    if target:
        # عرض معلومات العميل المختار
        current_balance = calculate_balance(target.get('history', []))
        st.info(f"**👤 العميل:** {target.get('name', '')} | **الرصيد الحالي:** {current_balance:,.0f} ج.م")
        
        with st.form("tech_visit"):
            col_visit1, col_visit2 = st.columns(2)
            with col_visit1:
                v_add = st.number_input("تكلفة الصيانة", min_value=0.0, value=0.0)
            with col_visit2:
                v_rem = st.number_input("المبلغ المحصل", min_value=0.0, value=0.0)
            
            note = st.text_area("وصف الزيارة", placeholder="وصف المشكلة والحل المقدم...")
            
            col_submit1, col_submit2 = st.columns(2)
            with col_submit1:
                if st.form_submit_button("💾 حفظ الزيارة", use_container_width=True):
                    if target:
                        new_history = {
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"), 
                            "note": note, 
                            "tech": st.session_state.tech_name, 
                            "debt": v_add, 
                            "price": v_rem
                        }
                        if 'history' not in target:
                            target['history'] = []
                        target['history'].append(new_history)
                        save_json("customers.json", st.session_state.data)
                        create_backup()
                        st.success("تم حفظ الزيارة بنجاح!")
                        st.rerun()
            with col_submit2:
                if st.form_submit_button("🗑️ مسح الحقول", use_container_width=True):
                    st.rerun()
        
        # تاريخ زيارات الفني للعميل
        st.subheader("📋 سجل زياراتي للعميل")
        if target.get('history'):
            tech_visits = [h for h in target.get('history', []) if h.get('tech') == st.session_state.tech_name]
            
            if tech_visits:
                for visit in reversed(tech_visits):
                    st.write(f"**{visit.get('date', '')}** - {visit.get('note', '')}")
                    debt = float(visit.get('debt', 0))
                    price = float(visit.get('price', 0))
                    if debt > 0:
                        st.write(f"  ↳ تكلفة: {debt:,.0f} ج.م")
                    if price > 0:
                        st.write(f"  ↳ محصل: {price:,.0f} ج.م")
                    st.write("---")
            else:
                st.info("لم تقم بزيارة هذا العميل من قبل")
    
    if st.sidebar.button("🚪 خروج", use_container_width=True): 
        del st.session_state.role
        st.rerun()
