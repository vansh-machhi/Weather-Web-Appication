import streamlit as st
import requests
import sqlite3
import pandas as pd

# -----------------------------
# DATABASE SETUP
# -----------------------------
con = sqlite3.connect("app.db", check_same_thread=False)
cursor = con.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

# Create notes table
cursor.execute("""
CREATE TABLE IF NOT EXISTS notes(
    username TEXT,
    note TEXT
)
""")

con.commit()

# -----------------------------
# SESSION STATE INITIALIZATION
# -----------------------------
if "logged" not in st.session_state:
    st.session_state.logged = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "login"

# -----------------------------
# REGISTER PAGE
# -----------------------------
def register_page():
    st.title("📝 Register Page")

    new_user = st.text_input("Create Username")
    new_pass = st.text_input("Create Password", type="password")

    if st.button("Register"):
        cursor.execute("SELECT * FROM users WHERE username=?", (new_user,))
        if cursor.fetchone():
            st.error("Username already exists ❌")
        else:
            cursor.execute("INSERT INTO users VALUES (?, ?)", (new_user, new_pass))
            con.commit()
            st.success("Registration Successful ✅")
            st.session_state.page = "login"
            st.rerun()

    if st.button("Go to Login"):
        st.session_state.page = "login"
        st.rerun()

# -----------------------------
# LOGIN PAGE
# -----------------------------
def login_page():
    st.title("🔐 Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            st.session_state.logged = True
            st.session_state.username = username
            st.success("Login Successful ✅")
            st.rerun()
        else:
            st.error("Invalid Credentials ❌")

    if st.button("Go to Register"):
        st.session_state.page = "register"
        st.rerun()

# -----------------------------
# DASHBOARD
# -----------------------------
def dashboard():
    st.title("🏠 Dashboard")
    st.success(f"Welcome {st.session_state.username} 👋")

    menu = st.sidebar.selectbox(
        "Select Option",
        ["Weather API", "Add Note", "View Notes", "Show Users Dataset", "Logout"]
    )

    # -------------------------
    # WEATHER API
    # -------------------------
    if menu == "Weather API":
        st.header("🌦️ Weather API Example")

        city = st.text_input("Enter City")

        if city:
            API_KEY = "1f9d35d79c83758a7866c648b9e79c65"
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

            r = requests.get(url)

            if r.status_code == 200:
                data = r.json()
                st.write("🌡️ Temperature:", data["main"]["temp"], "°C")
                st.write("☁️ Weather:", data["weather"][0]["description"])
            else:
                st.error("City Not Found")

    # -------------------------
    # ADD NOTE
    # -------------------------
    elif menu == "Add Note":
        st.header("📝 Add Note")

        note = st.text_area("Write your note")

        if st.button("Save Note"):
            cursor.execute(
                "INSERT INTO notes VALUES (?, ?)",
                (st.session_state.username, note)
            )
            con.commit()
            st.success("Note Saved Successfully ✅")

    # -------------------------
    # VIEW NOTES
    # -------------------------
    elif menu == "View Notes":
        st.header("📒 Your Notes")

        cursor.execute(
            "SELECT note FROM notes WHERE username=?",
            (st.session_state.username,)
        )

        rows = cursor.fetchall()

        if rows:
            for i, row in enumerate(rows):
                st.write(f"{i+1}. {row[0]}")
        else:
            st.info("No Notes Found")

    # -------------------------
    # SHOW USERS DATASET
    # -------------------------
    elif menu == "Show Users Dataset":
        st.header("📊 Registered Users Data")

        df = pd.read_sql_query("SELECT * FROM users", con)
        st.dataframe(df)

    # -------------------------
    # LOGOUT
    # -------------------------
    elif menu == "Logout":
        st.session_state.logged = False
        st.session_state.username = ""
        st.session_state.page = "login"
        st.rerun()

# -----------------------------
# MAIN CONTROL
# -----------------------------
if st.session_state.logged:
    dashboard()
else:
    if st.session_state.page == "login":
        login_page()
    else:
        register_page()

