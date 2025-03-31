import streamlit as st
import pandas as pd
import requests
import json
import os
import time
import base64
import firebase_admin
from firebase_admin import auth, credentials
from dateutil import parser
from datetime import datetime

# 🏠 Page Configuration
st.set_page_config(page_title="Charlotte Apartment Finder", page_icon="🏠", layout="wide")

# 📡 Firebase Authentication Setup (Using Base64 Encoding)
firebase_key_b64 = os.getenv("FIREBASE_KEY_B64")  # Retrieve Base64-encoded key

if firebase_key_b64:
    try:
        firebase_key_json = base64.b64decode(firebase_key_b64).decode("utf-8")  # Decode to JSON string
        firebase_key_dict = json.loads(firebase_key_json)  # Convert JSON string to dictionary

        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_key_dict)
            firebase_admin.initialize_app(cred)

        print("✅ Firebase successfully initialized!")
    except Exception as e:
        st.error(f"⚠️ Firebase initialization failed: {e}")
        st.stop()
else:
    st.error("⚠️ FIREBASE_KEY_B64 is missing in environment variables.")
    st.stop()

# 🔑 Firebase Web API Key
FIREBASE_WEB_API_KEY = "AIzaSyAdWQkhvXlzK4wRy7JxCbWkOGIC3Wkts38"

def authenticate_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload)
    data = response.json()
    return data if "idToken" in data else None

if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None

def login_page():
    st.title("🔐 Login to Apartment Finders AI")
    st.sidebar.image("Logo Ai.png", width=200)
    email = st.text_input("📧 Email", key="email")
    password = st.text_input("🔑 Password", type="password", key="password")

    if st.button("Login"):
        user_data = authenticate_user(email, password)
        if user_data:
            firebase_user = auth.get_user_by_email(email)
            user_role = firebase_user.custom_claims.get("role", "agent")
            st.session_state.user = user_data
            st.session_state.role = user_role
            st.success(f"✅ Successfully logged in as {user_role.capitalize()}!")
            st.rerun()
        else:
            st.error("❌ Invalid email or password. Please try again.")

if st.session_state.user:
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

if not st.session_state.user:
    login_page()
    st.stop()

st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to", ["Apartment Finder", "Property Map"])

BACKEND_URL = "https://apartment-finder-backend.onrender.com/search"
JSON_FILE = "data.json"
REFRESH_INTERVAL = 86400

@st.cache_data
def fetch_data():
    if os.path.exists(JSON_FILE):
        file_mod_time = os.path.getmtime(JSON_FILE)
        if time.time() - file_mod_time < REFRESH_INTERVAL:
            with open(JSON_FILE, "r") as f:
                return pd.DataFrame(json.load(f))

    response = requests.get(BACKEND_URL)
    if response.status_code == 200:
        data = response.json()
        with open(JSON_FILE, "w") as f:
            json.dump(data, f)
        return pd.DataFrame(data)
    else:
        st.error("⚠️ Failed to fetch data from backend.")
        return pd.DataFrame()

df = fetch_data()

LOGO_URL = "https://raw.githubusercontent.com/cltaptfinders/apartment-finder/main/Logo%20Ai.png"
PRIMARY_COLOR = "#2F80ED"

st.sidebar.image(LOGO_URL, width=200)

if page == "Property Map":
    st.title("📍 Charlotte Apartment Map")
    st.markdown("### Browse all partner properties on a live interactive map.")
    df_map = df.copy()
    df_map.rename(columns={"Latitude": "lat", "Longitude": "lon"}, inplace=True)
    if "lat" in df_map.columns and "lon" in df_map.columns:
        st.map(df_map[["lat", "lon"]])
    else:
        st.error("⚠️ Latitude and Longitude data not found!")

if page == "Apartment Finder":
    st.markdown("### Find Your Dream Apartment in Charlotte ✨")

    st.sidebar.header("🔍 Search Filters")
    apartment_name = st.sidebar.text_input("Apartment Name (Optional)", "")
    move_date = st.sidebar.date_input("Move-In Date (Optional)", value=None)
    max_price = st.sidebar.number_input("Max Rent ($) (Optional)", value=0, step=100)
    neighborhood = st.sidebar.text_input("Neighborhood (Optional)", "")
    bedrooms = st.sidebar.text_input("Bedrooms (Optional, e.g., Studio, 1 Bed, 2 Beds)", "")
    min_sqft = st.sidebar.number_input("Minimum Square Footage (Optional)", value=0, step=50)
    show_all_units = st.sidebar.checkbox("Show all matching units", value=False)

    def parse_availability(value):
        value = str(value).strip()
        today = datetime.today().date()
        if value.lower() in ["now", "soon"]:
            return today
        try:
            return parser.parse(value, fuzzy=True).date()
        except:
            return None

    def format_fees(fees_list):
        if not isinstance(fees_list, list) or not fees_list:
            return "Not specified"
        extracted_fees = []
        for category in fees_list:
            if isinstance(category, dict) and "fees" in category:
                for fee in category["fees"]:
                    key = fee.get("key", "").strip()
                    value = fee.get("value", "").strip()
                    if key and value and value != "--":
                        extracted_fees.append(f"{key}: {value}")
        return ", ".join(extracted_fees) if extracted_fees else "Not specified"

    if st.sidebar.button("🔎 Search"):
        filtered_df = df.copy()

        required_columns = ["Property Name", "Unit Number", "Rent", "Square Footage", "Availability"]
        for col in required_columns:
            if col not in filtered_df.columns:
                st.error(f"⚠️ Error: '{col}' column missing from data. Please check backend response.")
                st.stop()

        filtered_df["Rent"] = filtered_df["Rent"].astype(str).str.replace("[$,]", "", regex=True)
        filtered_df["Rent"] = pd.to_numeric(filtered_df["Rent"], errors="coerce").fillna(0).astype(int)
        filtered_df["Square Footage"] = pd.to_numeric(filtered_df["Square Footage"], errors="coerce")
        filtered_df["Availability"] = filtered_df["Availability"].astype(str).str.strip()
        filtered_df["Availability Date"] = filtered_df["Availability"].apply(parse_availability)
        filtered_df["Availability Date"] = pd.to_datetime(filtered_df["Availability Date"], errors="coerce").dt.date
        filtered_df["Parking Fees"] = filtered_df["Parking Fees"].apply(lambda x: format_fees(eval(x)) if isinstance(x, str) else format_fees(x))
        filtered_df["Pet Fees"] = filtered_df["Pet Fees"].apply(lambda x: format_fees(eval(x)) if isinstance(x, str) else format_fees(x))
        filtered_df["Application Fee"] = filtered_df.get("Application Fee", "N/A")

        if move_date:
            filtered_df = filtered_df[(filtered_df["Availability Date"].notna()) & (filtered_df["Availability Date"] <= move_date)]
        if apartment_name:
            filtered_df = filtered_df[filtered_df["Property Name"].str.contains(apartment_name, case=False, na=False)]
        if max_price > 0:
            filtered_df = filtered_df[filtered_df["Rent"] <= max_price]
        if neighborhood:
            filtered_df = filtered_df[filtered_df["Neighborhood"].str.contains(neighborhood, case=False, na=False)]
        if bedrooms:
            filtered_df = filtered_df[filtered_df["Bedrooms"].str.contains(bedrooms, case=False, na=False)]
        if min_sqft > 0:
            filtered_df = filtered_df[filtered_df["Square Footage"] >= min_sqft]

        if not show_all_units:
            filtered_df = filtered_df.sort_values(by="Rent").drop_duplicates(subset=["Property Name"], keep="first")

        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                st.markdown(f"""
                <div class='apartment-card'>
                    <h2 style="color: {PRIMARY_COLOR};">🏢 {row["Property Name"]}</h2>
                    <p>📍 <b>Address:</b> {row["Address"]} - {row["Neighborhood"]}</p>
                    <p class='rent-price'>💰 Rent: ${row["Rent"]:,.0f}</p>
                    <p>📅 <b>Availability:</b> {row["Availability"]}</p>
                    <p>🏠 <b>Floorplan:</b> {row["Floorplan"]}</p>
                    <p>🔢 <b>Unit Number:</b> {row["Unit Number"]}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No apartments found. Try adjusting your search criteria.")