import os
import re

import requests
import streamlit as st

API = os.getenv("API_AUTH", "http://127.0.0.1:8080")

def login_page():
    login_tab, create_tab = st.tabs(["Login", "Create account"])
    with login_tab:
        st.title("Login")
        with st.form(key="login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                success, token = auth_user(username, password)
                if success:
                    st.session_state["user_token"] = token
                    st.success("Login sucess")
                    st.rerun()
                else:
                    st.error(token["detail"])

    with create_tab:
        create_user_page()


def create_user_page():
    st.title("Create user")

    with st.form(key="create_user_form"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        new_email = st.text_input("New Email")
        submit_button = st.form_submit_button("Create")

        if submit_button:
            email_valid, password_valid = validate_user_input(new_email, new_password)
            if not email_valid:
                st.error("Invalid mail format")
            elif not password_valid:
                st.error(
                    "Password must contain at least one lower and one upper character, and one number"
                )
            else:
                success, token = create_user(new_username, new_password, new_email)
                if success:
                    st.success("User created successfully!")
                    st.success("You can now login")
                    # st.session_state["user_token"] = token
                else:
                    st.error(f"User creation failed. {token["detail"]}")


def auth_user(username, password):
    response = requests.post(
        f"{API}/login/", json={"username": username, "password": password}
    )
    if response.status_code == 200:
        token = response.json()
        return True, token
    elif response.status_code != 200:
        return False, response.text


def create_user(username, password, email):
    response = requests.post(
        f"{API}/users/",
        json={"username": username, "password": password, "email": email},
    )
    if response.status_code == 201:
        token = response.json()["token"]
        return True, token
    elif response.status_code == 401:
        return False, response.json()


def validate_user_input(email, password):
    email_valid = False
    password_valid = False
    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(email_pattern, email):
        email_valid = True
    password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{7,}$"
    if re.match(password_pattern, password):
        password_valid = True
    return email_valid, password_valid
