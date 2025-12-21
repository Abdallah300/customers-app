import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# ================== 1. إعدادات المظهر الفاخر والمبسط ==================
st.set_page_config(page_title="Power Life System", page_icon="💧", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #000000 0%, #001f3f 100%); color: #ffffff; }
    * { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تنسيق كارت بيانات العميل الأساسي */
    .header-card { 
        background: rgba(255, 255, 255, 0.08); 
        border-radius: 12px; 
        padding: 15px; 
        border: 1px solid #007bff; 
        margin-bottom: 20px; 
    }
    .main-balance { font-size: 26px; color: #00d4ff; font-weight: bold; text-align: center; margin-top: 10px; }
    
    /* تنسيق كروت سجل العمليات (كل تسوية في مربع) */
    .operation-card { 
        background: #ffffff; 
        color: #000000; 
        border-radius: 10px; 
        padding: 15px; 
        margin-bottom: 12px; 
        border-right: 6px solid #007bff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ================== 2. وظائف إدارة البيانات ==================
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
    total_added = sum(float(h.get('debt', 0)) for h in history)
    total_removed = sum(float(h.get('price', 0)) for h in history)
    return total_added - total_removed

# ================== 3. واجهة تقرير العميل (الباركود) ==================
params = st.query_params
if "id" in params:
    try:
        cust_id = int(params["id"])
        c = next((item for item in st.session_state.data if item['id'] == cust_id), None)
        if c:
            st.markdown("<h2 style='text-align:center;'>Power Life 💧</h2>", unsafe_allow_html=True)
            bal = calculate_balance(c.get('history', []))
            
            # كارت رأس التقرير
            st.markdown(f"""
            <div class='header-card'>
                <div style='font-size:16px;'>👤 <b>الاسم:</b> {c['name']}</div>
                <div style='font-size:14px; margin-top:5px;'>📍 <b>المحافظة:</b> {c.get('gov', 'القاهرة')} | 🏛️ <b>الفرع:</b> {c.get('branch', 'فرع طنطا')}</div>
                <div style='font-size:14px; margin-top:5px;'>🔧 <b>الجهاز:</b> {c.get('device_type', 'جديد')}</div>
                <hr style='opacity:0.2;'>
                <div style='text-align:center; font-size:14px;'>إجمالي المديونية الحالية</div>
                <div class='main-balance'>{bal:,.0f} ج.م</div>
            </div>
            <h3 style='border-right: 4px solid #007bff; padding-right:10px; margin-bottom:15px;'>📋 سجل العمليات المالي</h3>
            """, unsafe_allow_html=True)
            
            # عرض كل تسوية في مربع منفصل وواضح
            if c.get('history'):
                for h in reversed(c['history']):
                    h_add = float(h.get('debt', 0))
                    h_rem = float(h.get('price', 0))
                    
                    # استخدام container لضمان ثبات الشكل على الموبايل
                    with st.container():
                        st.markdown(f"""
                        <div class="operation-card">
                            <div style="display:flex; justify-content:space-between; font-size:12px; color:#666;">
                                <span>📅 {h.get('date', '---')}</span>
                                <span>👤 المسؤول: {h.get('tech', 'الإدارة')}</span>
                            </div>
                            <div style="margin: 10px 0; font-size: 16px; font-weight: bold;">📝 {h.get('note', 'تسوية')}</div>
                            <div style="display: flex; gap: 20px;">
                                {f'<span style="color:red; font-weight:bold;">➕ مضاف: {h_add:,.0f} ج.م</span>' if h_add > 0 else ''}
                                {f'<span style="color:green; font-weight:bold;">➖ مخصوم: {h_rem:,.0f} ج.م</span>' if h_rem > 0 else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("لا توجد عمليات مسجلة.")
            
            st.stop() # منع ظهور صفحة الدخول تحت التقرير
    except:
        st.error("خطأ في جلب بيانات العميل.")
        st.stop()

# ================== 4. نظام تسجيل الدخول (للإدارة والفنيين) ==================
if "role" not in st.session_state:
    st.markdown("<h2 style='text-align:center; margin-top:50px;'>لوحة التحكم 🔒</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("🔑 دخول الإدارة", use_container_width=True): st.session_state.role = "admin_login"; st.rerun()
    if c2.button("🛠️ دخول الفني", use_container_width=True): st.session_state.role = "tech_login"; st.rerun()
    st.stop()

# (بقية الكود الخاص بالإدارة والفني يظل كما هو لإدارة البيانات)
if st.session_state.role == "admin_login":
    u = st.text_input("المستخدم")
    p = st.text_input("السر", type="password")
    if st.button("دخول"):
        if u == "admin" and p == "admin123": st.session_state.role = "admin"; st.rerun()
    if st.button("رجوع"): del st.session_state.role; st.rerun()
    st.stop()
