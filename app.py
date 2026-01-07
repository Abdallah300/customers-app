🚀 Power Life Pro – Water Filters Company Edition

واجهات محسّنة: عميل / مدير / فني

import streamlit as st import json, hashlib from datetime import datetime, timedelta from pathlib import Path from urllib.parse import quote_plus

================== إعدادات عامة ==================

BASE_URL = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app" DATA_DIR = Path('.') CUSTOMERS_FILE = DATA_DIR / 'customers.json' TECHS_FILE = DATA_DIR / 'techs.json' SETTINGS_FILE = DATA_DIR / 'settings.json'

st.set_page_config("Power Life Pro 💧", "💧", layout="wide")

================== ستايل ==================

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {direction: rtl; background:#000b1a;}
* {font-family:Cairo; color:white;}
.card {background:#001529; border-radius:15px; padding:20px; margin:10px 0;}
.good {color:#00ffcc;} .bad{color:#ff4b4b;}
</style>""", unsafe_allow_html=True)

================== أدوات ==================

def hash_pass(p): return hashlib.sha256(p.encode()).hexdigest()

def load(file): if file.exists(): return json.loads(file.read_text(encoding='utf8')) return []

def save(file,data): file.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def balance(hist): return sum(h['debt'] for h in hist) - sum(h['paid'] for h in hist)

================== تهيئة ملفات ==================

if not SETTINGS_FILE.exists(): save(SETTINGS_FILE,{'admin':hash_pass('1010')}) if not CUSTOMERS_FILE.exists(): save(CUSTOMERS_FILE,[]) if not TECHS_FILE.exists(): save(TECHS_FILE,[])

customers = load(CUSTOMERS_FILE) techs = load(TECHS_FILE) settings = load(SETTINGS_FILE)

================== صفحة العميل ==================

params = st.experimental_get_query_params() if 'id' in params: cid = int(params['id'][0]) c = next((x for x in customers if x['id']==cid),None) if not c: st.error('العميل غير موجود'); st.stop()

pin = st.text_input('🔐 الرقم السري',type='password')
if hash_pass(pin)!=c['pin']: st.stop()

bal = balance(c['history'])

col1,col2,col3 = st.columns(3)
col1.metric('الاسم',c['name'])
col2.metric('الرصيد',f"{bal:,.0f} ج",delta="مدين" if bal>0 else "سليم")
col3.metric('الصيانة القادمة',c['next'])

st.subheader('📜 سجل الصيانات')
for h in reversed(c['history']):
    st.write(f"🛠 {h['date']} | {h['note']} | +{h['debt']} -{h['paid']}")
st.stop()

================== اختيار الدور ==================

if 'role' not in st.session_state: st.title('Power Life 💧') if st.button('🔑 مدير'): st.session_state.role='admin_login' if st.button('🛠️ فني'): st.session_state.role='tech_login' st.stop()

================== مدير ==================

if st.session_state.role=='admin_login': p=st.text_input('كلمة مرور المدير',type='password') if st.button('دخول') and hash_pass(p)==settings['admin']: st.session_state.role='admin'; st.experimental_rerun() st.stop()

if st.session_state.role=='admin': st.header('📊 لوحة المدير') total = sum(balance(c['history']) for c in customers) col1,col2,col3 = st.columns(3) col1.metric('عدد العملاء',len(customers)) col2.metric('المديونية',f"{total:,.0f}") col3.metric('عملاء مدينين',len([c for c in customers if balance(c['history'])>0]))

st.subheader('👥 العملاء')
for c in customers:
    with st.expander(f"{c['name']} | {balance(c['history']):,.0f}"):
        st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={quote_plus(BASE_URL+'?id='+str(c['id']))}")
        c['name']=st.text_input('الاسم',c['name'],key=c['id'])
        if st.button('حفظ',key='s'+str(c['id'])): save(CUSTOMERS_FILE,customers)

if st.button('🚪 خروج'): del st.session_state.role; st.experimental_rerun()

================== فني ==================

if st.session_state.role=='tech_login': names=[t['name'] for t in techs] u=st.selectbox('الفني',names) p=st.text_input('كلمة المرور',type='password') if st.button('دخول'): t=next(x for x in techs if x['name']==u) if hash_pass(p)==t['pass']: st.session_state.role='tech'; st.session_state.user=u; st.experimental_rerun() st.stop()

if st.session_state.role=='tech': st.header(f"🛠️ الفني: {st.session_state.user}") cid=st.selectbox('العميل',{c['id']:c['name'] for c in customers},format_func=lambda x: next(c['name'] for c in customers if c['id']==x)) c=next(x for x in customers if x['id']==cid) st.metric('الرصيد الحالي',balance(c['history']))

with st.form('add'):
    note=st.selectbox('نوع الخدمة',['تغيير شمعات','صيانة دورية','تصليح'])
    d=st.number_input('مديونية',0.0)
    p=st.number_input('مدفوع',0.0)
    nxt=st.date_input('الصيانة القادمة',datetime.now()+timedelta(days=90))
    if st.form_submit_button('حفظ'):
        c['history'].append({'date':datetime.now().strftime('%Y-%m-%d'),'note':note,'tech':st.session_state.user,'debt':d,'paid':p})
        c['next']=str(nxt)
        save(CUSTOMERS_FILE,customers)
        st.success('تم الحفظ')

if st.button('🚪 خروج'): del st.session_state.role; st.experimental_rerun()
