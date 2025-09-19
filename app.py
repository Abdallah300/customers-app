# app.py
# Streamlit Multi-Company Modern App
# Requirements: see requirements.txt below

import os
import io
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import pydeck as pdk

# SQLAlchemy + Passlib
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from passlib.hash import bcrypt

# ---------------------------
# Configuration
# ---------------------------
# Use DATABASE_URL env var for production (Postgres). If not set, fallback to sqlite file.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///barolife_local.db")
LOGO_FILENAME = "logo.png"  # place logo in project root or upload via UI

# ---------------------------
# Database setup (SQLAlchemy)
# ---------------------------
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine)
dbsession = SessionLocal()

# Models
class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship("User", back_populates="company")
    customers = relationship("Customer", back_populates="company")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="technician")  # admin / technician
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    company = relationship("Company", back_populates="users")

    def verify_password(self, password):
        return bcrypt.verify(password, self.password_hash)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    location = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    region = Column(String, nullable=True)
    last_visit = Column(DateTime, nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    company = relationship("Company", back_populates="customers")

# create tables
Base.metadata.create_all(bind=engine)

# ---------------------------
# Helpers: DB operations
# ---------------------------
def get_companies():
    return dbsession.query(Company).order_by(Company.name).all()

def create_company(name):
    comp = dbsession.query(Company).filter_by(name=name).first()
    if comp:
        return comp
    comp = Company(name=name)
    dbsession.add(comp)
    dbsession.commit()
    return comp

def create_user(username, password, role="technician", company=None):
    pw_hash = bcrypt.hash(password)
    user = User(username=username, password_hash=pw_hash, role=role)
    if company:
        user.company = company
    dbsession.add(user)
    dbsession.commit()
    return user

def find_user(username, company=None):
    if company:
        return dbsession.query(User).filter_by(username=username, company=company).first()
    return dbsession.query(User).filter_by(username=username).first()

def authenticate(username, password, company=None):
    user = find_user(username, company)
    if not user:
        return None
    if user.verify_password(password):
        return user
    return None

def add_customer_db(company, data: dict):
    last_visit = None
    try:
        if data.get("last_visit"):
            last_visit = pd.to_datetime(data.get("last_visit"))
    except:
        last_visit = None
    cust = Customer(
        name=data.get("name"),
        phone=data.get("phone"),
        lat=data.get("lat"),
        lon=data.get("lon"),
        location=data.get("location"),
        notes=data.get("notes"),
        category=data.get("category"),
        region=data.get("region"),
        last_visit=last_visit,
        company=company
    )
    dbsession.add(cust)
    dbsession.commit()
    return cust

def get_customers_for_company(company):
    return dbsession.query(Customer).filter_by(company=company).order_by(Customer.name).all()

def search_customers_company(company, keyword):
    kw = f"%{keyword}%"
    return dbsession.query(Customer).filter(
        Customer.company==company,
    ).filter(
        (Customer.name.ilike(kw)) | (Customer.phone.ilike(kw)) | (Customer.region.ilike(kw))
    ).all()

# ---------------------------
# Initial admin/company if empty
# ---------------------------
if not get_companies():
    comp = create_company("Power Life")
    # create admin default (change password after deploy)
    if not find_user("admin", comp):
        create_user("admin", "admin1234", role="admin", company=comp)
# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Power Life - CRM", layout="wide", initial_sidebar_state="expanded")

# session defaults
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "company_id" not in st.session_state:
    st.session_state.company_id = None
if "logo_bytes" not in st.session_state:
    st.session_state.logo_bytes = None
if "lang" not in st.session_state:
    st.session_state.lang = "ar"

# ---------------------------
# Translations
# ---------------------------
LANGS = {
    "ar": {
        "welcome": "💧 باور لايف ترحب بكم",
        "login": "تسجيل الدخول",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "submit": "دخول",
        "logout": "تسجيل الخروج",
        "dashboard": "لوحة التحكم",
        "add_customer": "➕ إضافة عميل",
        "show_customers": "📋 قائمة العملاء",
        "search": "🔎 البحث عن عميل",
        "reminders": "⏰ العملاء المطلوب زيارتهم (30+ يوم)",
        "add_technician": "➕ إضافة فني",
        "map": "🗺️ خريطة العملاء (قمر صناعي)",
        "export": "⬇️ تصدير CSV",
        "no_customers": "❌ لا يوجد عملاء بعد",
        "save": "حفظ",
        "add_company": "إنشاء شركة",
        "upload_logo": "رفع شعار الشركة",
    },
    "en": {
        "welcome": "💧 Power Life welcomes you",
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "submit": "Submit",
        "logout": "Logout",
        "dashboard": "Dashboard",
        "add_customer": "➕ Add Customer",
        "show_customers": "📋 Customers List",
        "search": "🔎 Search Customer",
        "reminders": "⏰ Customers to Visit (30+ days)",
        "add_technician": "➕ Add Technician",
        "map": "🗺️ Customers Map (Satellite)",
        "export": "⬇️ Export CSV",
        "no_customers": "❌ No customers yet",
        "save": "Save",
        "add_company": "Create Company",
        "upload_logo": "Upload Company Logo",
    }
}
T = LANGS[st.session_state.lang]

# Sidebar - language select & logo
with st.sidebar:
    # language switch
    lang_sel = st.radio("Language / اللغة", ["ar","en"], index=0 if st.session_state.lang=="ar" else 1)
    st.session_state.lang = lang_sel
    T = LANGS[st.session_state.lang]

    # logo section: allow uploading or use file in project
    st.markdown("### " + T["upload_logo"])
    uploaded = st.file_uploader("", type=["png","jpg","jpeg"], key="logo_upload")
    if uploaded:
        st.session_state.logo_bytes = uploaded.read()
        # save to file (optional)
        try:
            with open(LOGO_FILENAME, "wb") as f:
                f.write(st.session_state.logo_bytes)
        except Exception:
            pass

    # if no uploaded but static file exists, load it
    if not st.session_state.logo_bytes and os.path.exists(LOGO_FILENAME):
        try:
            with open(LOGO_FILENAME, "rb") as f:
                st.session_state.logo_bytes = f.read()
        except Exception:
            st.session_state.logo_bytes = None

    if st.session_state.logo_bytes:
        st.image(st.session_state.logo_bytes, width=160)

    st.markdown("---")
    st.subheader(T["dashboard"])
    # Companies
    comps = get_companies()
    comp_names = ["-- new --"] + [c.name for c in comps]
    company_choice = st.selectbox("Company / الشركة", comp_names, index=1 if comps else 0)
    if company_choice == "-- new --":
        new_comp_name = st.text_input(T["add_company"])
        if st.button(T["add_company"]):
            if new_comp_name.strip():
                comp = create_company(new_comp_name.strip())
                st.success(f"Created {comp.name}")
                st.experimental_rerun()
    else:
        # set current company in session
        selected_comp = next((c for c in comps if c.name == company_choice), None)
        if selected_comp:
            st.session_state.company_id = selected_comp.id

    st.markdown("---")
    st.write("")

# Header area: show logo and title
col1, col2 = st.columns([1,5])
with col1:
    if st.session_state.logo_bytes:
        st.image(st.session_state.logo_bytes, width=120)
    else:
        # fallback simple text logo
        st.write("")
with col2:
    st.markdown(f"# {T['welcome']}")

# ---------------------------
# Authentication UI
# ---------------------------
if not st.session_state.logged_in:
    st.markdown("## " + T["login"])
    login_col1, login_col2 = st.columns([2,1])
    with login_col1:
        username = st.text_input(T["username"], key="login_user")
        password = st.text_input(T["password"], type="password", key="login_pass")
    with login_col2:
        role_choice = st.selectbox("Role", ["admin", "technician"])
        if st.button(T["submit"]):
            # authenticate under selected company (if any)
            comp = None
            if st.session_state.company_id:
                comp = dbsession.query(Company).get(st.session_state.company_id)
            user = authenticate(username, password, company=comp)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user.id
                st.session_state.user_role = user.role
                st.success(f"{T['welcome']} {user.username}")
                st.experimental_rerun()
            else:
                st.error(T["no_customers"] if False else "❌ " + ("اسم مستخدم/كلمة مرور خاطئة" if st.session_state.lang=="ar" else "Wrong username/password"))
    st.markdown("---")
    st.stop()

# If logged in, load user and company
current_user = dbsession.query(User).get(st.session_state.user_id)
current_company = dbsession.query(Company).get(st.session_state.company_id) if st.session_state.company_id else None

# Top-right logout
if st.button(T["logout"]):
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.user_role = None
    st.experimental_rerun()

# Main menu
if current_user.role == "admin":
    menu = st.radio(T["dashboard"], [T["add_customer"], T["show_customers"], T["search"], T["reminders"], T["add_technician"], T["map"], T["export"]])
else:
    menu = st.radio(T["dashboard"], [T["show_customers"], T["search"], T["reminders"], T["map"]])

# ---------------------------
# Add Customer
# ---------------------------
if menu == T["add_customer"]:
    st.subheader(T["add_customer"])
    with st.form("add_customer_form"):
        name = st.text_input("Name / الاسم")
        phone = st.text_input("Phone / التليفون")
        lat = st.text_input("Latitude (optional)")
        lon = st.text_input("Longitude (optional)")
        region = st.text_input("Region / المنطقة")
        category = st.selectbox("Category / التصنيف", ["Home / منزل", "Company / شركة", "School / مدرسة"])
        notes = st.text_area("Notes / ملاحظات")
        last_visit = st.date_input("Last Visit / آخر زيارة", datetime.today())
        submitted = st.form_submit_button(T["save"])
        if submitted:
            try:
                latv = float(lat) if lat else None
                lonv = float(lon) if lon else None
            except:
                latv = None
                lonv = None
            location = f"https://www.google.com/maps?q={latv},{lonv}" if latv and lonv else ""
            add_customer_db(current_company, {
                "name": name,
                "phone": phone,
                "lat": latv,
                "lon": lonv,
                "location": location,
                "notes": notes,
                "category": category,
                "region": region,
                "last_visit": str(last_visit)
            })
            st.success("✅ Saved")
            st.experimental_rerun()

# ---------------------------
# Show Customers
# ---------------------------
elif menu == T["show_customers"]:
    st.subheader(T["show_customers"])
    if not current_company:
        st.info("Please select a company from the sidebar / اختر شركة من الشريط الجانبي")
    else:
        customers = get_customers_for_company(current_company)
        if not customers:
            st.info(T["no_customers"])
        else:
            # present table
            df = pd.DataFrame([{
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "region": c.region,
                "category": c.category,
                "last_visit": (c.last_visit.strftime("%Y-%m-%d") if c.last_visit else ""),
                "lat": c.lat,
                "lon": c.lon
            } for c in customers])
            st.dataframe(df, use_container_width=True)

            # per-customer quick actions
            for c in customers:
                with st.expander(f"{c.name} - {c.phone}"):
                    st.write("Region:", c.region)
                    st.write("Category:", c.category)
                    st.write("Last visit:", c.last_visit)
                    st.write("Notes:", c.notes)
                    if c.lat and c.lon:
                        st.markdown(f"[Open map]({c.location})")
                    # whatsapp quick message
                    if c.phone:
                        wa_text = f"مرحباً {c.name} - هذا من Power Life"
                        wa_link = f"https://wa.me/{c.phone}?text={wa_text}"
                        st.markdown(f"[Send WhatsApp]({wa_link})")

# ---------------------------
# Search
# ---------------------------
elif menu == T["search"]:
    st.subheader(T["search"])
    q = st.text_input("Search by name, phone, region / ابحث")
    if q:
        results = search_customers_company(current_company, q)
        if not results:
            st.warning("لا يوجد نتائج / No results")
        else:
            df = pd.DataFrame([{
                "id": r.id,
                "name": r.name, "phone": r.phone, "region": r.region,
                "category": r.category, "last_visit": (r.last_visit.strftime("%Y-%m-%d") if r.last_visit else "")
            } for r in results])
            st.dataframe(df)

# ---------------------------
# Reminders
# ---------------------------
elif menu == T["reminders"]:
    st.subheader(T["reminders"])
    customers = get_customers_for_company(current_company)
    if not customers:
        st.info(T["no_customers"])
    else:
        today = datetime.utcnow()
        needs_visit = []
        for c in customers:
            if c.last_visit:
                days = (today - c.last_visit).days
                if days >= 30:
                    needs_visit.append((c, days))
            else:
                needs_visit.append((c, None))  # never visited
        if not needs_visit:
            st.success("✅ No customers need visit / لا يوجد عملاء يحتاجون زيارة")
        else:
            for c, days in needs_visit:
                label = f"{c.name} - {c.phone}"
                if days is not None:
                    label += f" ({days} days since last visit)"
                else:
                    label += " (No last visit recorded)"
                with st.expander(label):
                    st.write("Region:", c.region)
                    st.write("Notes:", c.notes)
                    if c.phone:
                        wa = f"https://wa.me/{c.phone}?text=مرحباً%20{c.name}%20من%20Power%20Life"
                        st.markdown(f"[Send WhatsApp reminder]({wa})")

# ---------------------------
# Add Technician (admin only)
# ---------------------------
elif menu == T["add_technician"]:
    st.subheader(T["add_technician"])
    new_user = st.text_input("Username / اسم المستخدم")
    new_pass = st.text_input("Password / كلمة السر", type="password")
    if st.button("Create / إنشاء"):
        if new_user and new_pass and current_company:
            existing = dbsession.query(User).filter_by(username=new_user, company=current_company).first()
            if existing:
                st.error("User exists")
            else:
                create_user(new_user, new_pass, role="technician", company=current_company)
                st.success("Created")
        else:
            st.error("Please fill fields and select company")

# ---------------------------
# Map (pydeck)
# ---------------------------
elif menu == T["map"]:
    st.subheader(T["map"])
    customers = get_customers_for_company(current_company)
    df = pd.DataFrame([{"name": c.name, "lat": c.lat, "lon": c.lon, "region": c.region} for c in customers if c.lat and c.lon])
    if df.empty:
        st.info(T["no_customers"])
    else:
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/satellite-v9',
            initial_view_state=pdk.ViewState(
                latitude=df["lat"].mean(),
                longitude=df["lon"].mean(),
                zoom=11,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[lon, lat]',
                    get_radius=200,
                    pickable=True
                )
            ],
            tooltip={"text": "{name} - {region}"}
        ))

# ---------------------------
# Export CSV
# ---------------------------
elif menu == T["export"]:
    st.subheader(T["export"])
    customers = get_customers_for_company(current_company)
    if not customers:
        st.info(T["no_customers"])
    else:
        df = pd.DataFrame([{
            "id": c.id,
            "name": c.name,
            "phone": c.phone,
            "region": c.region,
            "category": c.category,
            "last_visit": (c.last_visit.strftime("%Y-%m-%d") if c.last_visit else "")
        } for c in customers])
        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download CSV", csv, file_name=f"{current_company.name}_customers.csv", mime="text/csv")
