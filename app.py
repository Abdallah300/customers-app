import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر (برستيج المدير) ==================
st.set_page_config(page_title="Power Life Admin", page_icon="💼", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: #000b1a; color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق الكروت الإحصائية للمدير */
    .metric-card {
        background: linear-gradient(135deg, #001f3f 0%, #007bff 100%);
        padding: 20px; border-radius: 15px; border: 1px solid #00d4ff;
        text-align: center; margin-bottom: 20px;
    }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. معالجة البيانات ==================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return default
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'data' not in st.session_state: st.session_state.data = load_json("customers.json", [])
if 'techs' not in st.session_state: st.session_state.techs = load_json("techs.json", [])

def calculate_balance(history):
    return sum(float(h.get('debt', 0)) for h in history) - sum(float(h.get('price', 0)) for h in history)

# ================== 3. واجهة المدير الرئيسية ==================

# التحقق من صلاحية الدخول (المدير فقط)
if "role" not in st.session_state or st.session_state.role != "admin":
    st.markdown("<h2 style='text-align:center;'>دخول نظام المدير 🔑</h2>", unsafe_allow_html=True)
    with st.container():
        u = st.text_input("اسم المستخدم الإداري")
        p = st.text_input("كلمة السر", type="password")
        if st.button("دخول الإدارة"):
            if u == "admin" and p == "admin123": 
                st.session_state.role = "admin"
                st.rerun()
            else: st.error("خطأ في بيانات الدخول")
    st.stop()

# قائمة التنقل الجانبية للمدير
st.sidebar.markdown(f"### أهلاً بك يا مدير 👋")
admin_menu = st.sidebar.radio("انتقل إلى:", [
    "📊 لوحة المعلومات", 
    "👥 إدارة العملاء", 
    "🛠️ إدارة طاقم الفنيين", 
    "📈 تقارير الحسابات", 
    "🚪 تسجيل خروج"
])

# --- 📊 لوحة المعلومات ---
if admin_menu == "📊 لوحة المعلومات":
    st.title("الوضع المالي العام 📊")
    total_mkt_debt = sum(calculate_balance(c.get('history', [])) for c in st.session_state.data)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='metric-card'><p>إجمالي المديونيات في السوق</p><h2>{total_mkt_debt:,.0f} ج.م</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><p>عدد العملاء المسجلين</p><h2>{len(st.session_state.data)} عميل</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><p>عدد الفنيين</p><h2>{len(st.session_state.techs)} فني</h2></div>", unsafe_allow_html=True)

# --- 👥 إدارة العملاء ---
elif admin_menu == "👥 إدارة العملاء":
    st.title("إدارة العملاء 👤")
    tab1, tab2 = st.tabs(["البحث والتعديل", "إضافة عميل جديد"])
    
    with tab1:
        search = st.text_input("ابحث عن عميل (بالاسم أو الفرع)...")
        for c in st.session_state.data:
            if search.lower() in c['name'].lower() or search.lower() in c.get('branch', '').lower():
                with st.expander(f"💼 {c['name']} - {c.get('branch', 'بدون فرع')}"):
                    # تفاصيل العميل
                    current_bal = calculate_balance(c.get('history', []))
                    st.write(f"**المديونية الحالية:** {current_bal:,.2f} ج.م")
                    
                    with st.form(f"admin_edit_{c['id']}"):
                        col_a, col_b = st.columns(2)
                        new_gov = col_a.text_input("المحافظة", value=c.get('gov', ''))
                        new_branch = col_b.text_input("الفرع", value=c.get('branch', ''))
                        
                        st.write("---")
                        st.write("**تسوية مالية إدارية:**")
                        add_d = st.number_input("إضافة مبلغ للحساب (+)", min_value=0.0)
                        rem_p = st.number_input("خصم مبلغ من الحساب (-)", min_value=0.0)
                        reason = st.text_input("سبب التسوية", value="تعديل إداري")
                        
                        if st.form_submit_button("حفظ كل التغييرات"):
                            c['gov'] = new_gov
                            c['branch'] = new_branch
                            if add_d > 0 or rem_p > 0:
                                c['history'].append({
                                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "note": reason, "tech": "المدير", "debt": add_d, "price": rem_p
                                })
                            save_json("customers.json", st.session_state.data)
                            st.success("تم تحديث بيانات العميل بنجاح!")
                            st.rerun()

    with tab2:
        with st.form("new_customer_form"):
            st.write("### تسجيل عميل جديد في السيستم")
            name = st.text_input("اسم العميل الثلاثي")
            gov = st.text_input("المحافظة")
            branch = st.text_input("الفرع")
            opening_debt = st.number_input("المديونية الافتتاحية (إن وجد)", min_value=0.0)
            if st.form_submit_button("إضافة العميل نهائياً"):
                new_id = max([x['id'] for x in st.session_state.data], default=0) + 1
                st.session_state.data.append({
                    "id": new_id, "name": name, "gov": gov, "branch": branch,
                    "history": [{"date": datetime.now().strftime("%Y-%m-%d"), "note": "رصيد افتتاحى", "tech": "المدير", "debt": opening_debt, "price": 0}] if opening_debt > 0 else []
                })
                save_json("customers.json", st.session_state.data)
                st.success(f"تم تسجيل {name} بنجاح!")

# --- 🛠️ إدارة طاقم الفنيين ---
elif admin_menu == "🛠️ إدارة طاقم الفنيين":
    st.title("إدارة الفنيين 👨‍🔧")
    with st.form("add_tech"):
        st.write("### إضافة فني جديد للفريق")
        t_name = st.text_input("اسم الفني")
        t_pass = st.text_input("كلمة سر الدخول للفني", type="password")
        if st.form_submit_button("تعيين الفني"):
            if t_name and t_pass:
                st.session_state.techs.append({"name": t_name, "pass": t_pass})
                save_json("techs.json", st.session_state.techs)
                st.success(f"تم تعيين {t_name} بنجاح")
            else: st.warning("يرجى ملء كافة البيانات")
    
    st.write("---")
    st.write("### الفنيين الحاليين")
    if st.session_state.techs:
        df_techs = pd.DataFrame(st.session_state.techs)
        st.table(df_techs[['name']]) # إظهار الأسماء فقط للأمان
    else: st.info("لا يوجد فنيين مسجلين بعد")

# --- 🚪 تسجيل خروج ---
elif admin_menu == "🚪 تسجيل خروج":
    del st.session_state.role
    st.rerun()
