import streamlit as st import json, os, hashlib, csv from datetime import datetime, timedelta from pathlib import Path from urllib.parse import quote_plus

------------------ إعداد مسارات وملفات ------------------

DATA_DIR = Path('.') CUSTOMERS_FILE = DATA_DIR / 'customers.json' TECHS_FILE = DATA_DIR / 'techs.json' SETTINGS_FILE = DATA_DIR / 'settings.json' BASE_URL = "https://customers-app-ap57kjvz3rvcdsjhfhwxpt.streamlit.app"

------------------ إعداد الصفحة ------------------

st.set_page_config("Power Life Pro 💧", "💧", layout="wide")

------------------ ستايل بسيط ------------------

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"] {direction: rtl; background:#000b1a;}
* {font-family:Cairo; color:white;}
.card {background:#001529; border:2px solid #007bff; border-radius:15px; padding:20px; margin:15px 0;}
.hist {background:rgba(255,255,255,.07); border-right:5px solid #00d4ff; padding:10px; border-radius:10px; margin:10px 0;}
</style>""", unsafe_allow_html=True)

------------------ أدوات ------------------

def hash_pass(p: str) -> str: return hashlib.sha256(p.encode('utf8')).hexdigest()

def load_file(file: Path): if file.exists(): try: return json.loads(file.read_text(encoding='utf8')) except Exception: return [] return []

def save_file(file: Path, data): file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')

def balance(hist): return sum(float(h.get('debt', 0)) for h in hist) - sum(float(h.get('paid', 0)) for h in hist)

def ensure_files(): # ملفات البيانات الافتراضية if not SETTINGS_FILE.exists(): settings = {'admin_hash': hash_pass('1010')} save_file(SETTINGS_FILE, settings) if not CUSTOMERS_FILE.exists(): save_file(CUSTOMERS_FILE, []) if not TECHS_FILE.exists(): save_file(TECHS_FILE, [])

------------------ تحميل البيانات ------------------

ensure_files() if 'customers' not in st.session_state: st.session_state.customers = load_file(CUSTOMERS_FILE) if 'techs' not in st.session_state: st.session_state.techs = load_file(TECHS_FILE) if 'settings' not in st.session_state: st.session_state.settings = load_file(SETTINGS_FILE)

دوال مساعدة لحماية PIN بتخزين الهاش

def set_pin_raw(pin: str): return hash_pass(pin)

def verify_pin(pin_raw: str, stored_hash: str): return hash_pass(pin_raw) == stored_hash

------------------ صفحة عرض العميل بواسطة id في query params ------------------

params = st.experimental_get_query_params() if 'id' in params: try: cid = int(params['id'][0]) except Exception: st.error('معرف العميل غير صالح') st.stop() c = next((x for x in st.session_state.customers if x['id'] == cid), None) if not c: st.error('العميل غير موجود') st.stop()

pin = st.text_input('🔐 أدخل الرقم السري', type='password')
if not pin:
    st.stop()

if not verify_pin(pin, c.get('pin_hash', '')):
    st.error('الرقم السري غير صحيح')
    st.stop()

bal = balance(c.get('history', []))
st.markdown(f"""
<div class="card">
    <h2 style="text-align:center">{c['name']}</h2>
    <h3 style="text-align:center;color:{'#00ffcc' if bal<=0 else '#ff4b4b'}">
    الرصيد: {bal:,.2f} ج.م
    </h3>
    <p style="text-align:center">📅 الصيانة القادمة: {c.get('next','قريبًا')}</p>
</div>
""", unsafe_allow_html=True)

for idx, h in enumerate(reversed(c.get('history', []))):
    st.markdown(f"""
    <div class="hist">
    📅 {h.get('date')}<br>
    👨‍🔧 {h.get('tech')}<br>
    📝 {h.get('note')}<br>
    ➕ {h.get('debt')} | ➖ {h.get('paid')}
    </div>
    """, unsafe_allow_html=True)
st.stop()

------------------ شاشة اختيار الدور (مدير / فني) ------------------

if 'role' not in st.session_state: st.title('Power Life 💧') col1, col2 = st.columns(2) if col1.button('🔑 مدير'): st.session_state.role = 'admin_login' st.experimental_rerun() if col2.button('🛠️ فني'): st.session_state.role = 'tech_login' st.experimental_rerun() st.stop()

------------------ تسجيل دخول المدير ------------------

if st.session_state.get('role') == 'admin_login': p = st.text_input('كلمة مرور المدير', type='password') if st.button('دخول'): if hash_pass(p) == st.session_state.settings.get('admin_hash'): st.session_state.role = 'admin' st.experimental_rerun() else: st.error('كلمة المرور خاطئة') if st.button('رجوع'): del st.session_state.role st.experimental_rerun() st.stop()

------------------ تسجيل دخول الفني ------------------

if st.session_state.get('role') == 'tech_login': names = [t['name'] for t in st.session_state.techs] if not names: st.warning('لا يوجد فنيين بعد. اطلب من المدير إضافة فني.') u = st.selectbox('اسم الفني', names) p = st.text_input('كلمة المرور', type='password') if st.button('دخول'): t = next((x for x in st.session_state.techs if x['name'] == u), None) if t and hash_pass(p) == t['pass']: st.session_state.role = 'tech' st.session_state.user = u st.experimental_rerun() else: st.error('بيانات الدخول خاطئة') if st.button('رجوع'): del st.session_state.role st.experimental_rerun() st.stop()

------------------ لوحة المدير ------------------

if st.session_state.get('role') == 'admin': st.sidebar.title('لوحة المدير') m = st.sidebar.radio('القائمة', ['👥 العملاء', '🛠️ الفنيين', '⚙️ إعدادات', '📊 تقرير', '🚪 خروج'])

# --- عملاء ---
if m == '👥 العملاء':
    st.header('قائمة العملاء')
    # بحث / فلتر
    q = st.text_input('بحث باسم العميل أو جزء منه')
    show_negative = st.checkbox('عرض العملاء المدينين فقط')

    customers = st.session_state.customers
    if q:
        customers = [c for c in customers if q.strip() in c['name']]
    if show_negative:
        customers = [c for c in customers if balance(c.get('history', [])) > 0]

    if st.button('➕ عميل جديد'):
        nid = max([c['id'] for c in st.session_state.customers], default=0) + 1
        new_c = {
            'id': nid,
            'name': f'عميل {nid}',
            'pin_hash': set_pin_raw('1234'),
            'history': [],
            'next': 'قريبًا'
        }
        st.session_state.customers.append(new_c)
        save_file(CUSTOMERS_FILE, st.session_state.customers)
        st.experimental_rerun()

    for c in customers:
        with st.expander(f"{c['name']} | {balance(c.get('history', [])):,.0f}"):
            st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={quote_plus(f'{BASE_URL}?id={c['id']}')}")
            new_name = st.text_input('الاسم', c['name'], key=f'name_{c['id']}')
            if new_name != c['name']:
                c['name'] = new_name
            # تغيير PIN
            new_pin = st.text_input('PIN (اتركه فارغ للاحتفاظ)', type='password', key=f'pin_{c['id']}')
            if new_pin:
                c['pin_hash'] = set_pin_raw(new_pin)
            st.write('الرصيد الحالي:', balance(c.get('history', [])))

            # حذف عميل
            if st.button('حذف العميل', key=f'del_{c['id']}'):
                st.session_state.customers = [x for x in st.session_state.customers if x['id'] != c['id']]
                save_file(CUSTOMERS_FILE, st.session_state.customers)
                st.success('تم حذف العميل')
                st.experimental_rerun()

            if st.button('حفظ التغييرات', key=f'save_{c['id']}'):
                save_file(CUSTOMERS_FILE, st.session_state.customers)
                st.success('تم الحفظ')

# --- فنيين ---
if m == '🛠️ الفنيين':
    st.header('إدارة الفنيين')
    n = st.text_input('اسم الفني')
    p = st.text_input('كلمة المرور', type='password')
    if st.button('إضافة'):
        if not n or not p:
            st.error('أدخل اسم وكلمة مرور')
        else:
            st.session_state.techs.append({'name': n, 'pass': hash_pass(p)})
            save_file(TECHS_FILE, st.session_state.techs)
            st.success('تمت الإضافة')
            st.experimental_rerun()
    st.table([{'name': t['name']} for t in st.session_state.techs])

# --- إعدادات ---
if m == '⚙️ إعدادات':
    st.header('إعدادات')
    if st.button('تغيير كلمة مرور المدير'):
        old = st.text_input('كلمة المرور الحالية', type='password', key='old_admin')
        new = st.text_input('كلمة المرور الجديدة', type='password', key='new_admin')
        if st.button('تأكيد التغيير'):
            if hash_pass(old) == st.session_state.settings.get('admin_hash'):
                st.session_state.settings['admin_hash'] = hash_pass(new)
                save_file(SETTINGS_FILE, st.session_state.settings)
                st.success('تم تغيير كلمة المرور')
                st.experimental_rerun()
            else:
                st.error('كلمة المرور الحالية خاطئة')

# --- تقرير ---
if m == '📊 تقرير':
    st.header('تقرير')
    total = sum(balance(c.get('history', [])) for c in st.session_state.customers)
    st.metric('إجمالي المديونية', f"{total:,.2f} ج.م")

    # تصدير CSV
    if st.button('تصدير بيانات العملاء CSV'):
        csv_lines = []
        for c in st.session_state.customers:
            csv_lines.append({
                'id': c['id'], 'name': c['name'], 'balance': balance(c.get('history', [])), 'next': c.get('next','')
            })
        # إنشاء نص CSV
        si = 'id,name,balance,next\n'
        for r in csv_lines:
            si += f"{r['id']},\"{r['name']}\",{r['balance']},{r['next']}\n"
        st.download_button('تحميل CSV', si, file_name='customers.csv', mime='text/csv')

if m == '🚪 خروج':
    del st.session_state.role
    st.experimental_rerun()

------------------ لوحة الفني ------------------

if st.session_state.get('role') == 'tech': st.header(f"🛠️ {st.session_state.user}") ids = {c['id']: c['name'] for c in st.session_state.customers} if not ids: st.warning('لا يوجد عملاء حتى الآن') else: cid = st.selectbox('اختر العميل', list(ids.keys()), format_func=lambda x: ids[x]) c = next(x for x in st.session_state.customers if x['id'] == cid)

st.info(f"الرصيد الحالي: {balance(c.get('history', [])):,.2f}")

    with st.form('add'):
        note = st.text_area('الوصف')
        d = st.number_input('مديونية', min_value=0.0, value=0.0)
        p = st.number_input('مدفوع', min_value=0.0, value=0.0)
        nxt = st.date_input('الصيانة القادمة', datetime.now() + timedelta(days=90))
        if st.form_submit_button('حفظ'):
            if p > d + balance(c.get('history', [])):
                st.error('قيمة المدفوع أكبر من المطلوب')
            else:
                c['history'].append({
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'note': note, 'tech': st.session_state.user,
                    'debt': float(d), 'paid': float(p)
                })
                c['next'] = str(nxt)
                save_file(CUSTOMERS_FILE, st.session_state.customers)
                st.success('تم')
                st.experimental_rerun()

    # عرض وتحرير التاريخ
    st.subheader('سجل الصيانة')
    for i, h in enumerate(c.get('history', [])):
        cols = st.columns([3, 1])
        with cols[0]:
            st.write(f"{i+1}. {h.get('date')} — {h.get('tech')} — {h.get('note')} — (+{h.get('debt')} / -{h.get('paid')})")
        with cols[1]:
            if st.button('حذف', key=f'del_hist_{i}'):
                c['history'].pop(i)
                save_file(CUSTOMERS_FILE, st.session_state.customers)
                st.experimental_rerun()

    if st.button('🚪 خروج'):
        del st.session_state.role
        st.experimental_rerun()
