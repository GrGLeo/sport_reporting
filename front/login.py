import streamlit as st
import time
import requests


def login_page():
    st.title("Login")
    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password")
        submit = st.form_submit_button("Login")

        if submit:
            success, token = auth_user(username, password)

            if success:
                st.session_state["user_token"] = token
                st.success("Login sucess")
                st.rerun()
            else:
                st.error("Invalid username or password")

    create_user_button = st.button("Create account")
    if create_user_button:
        create_user_page()


def create_user_page():
    st.title("Create user")

    with st.form(key='create_user_form'):
        new_username = st.text_input('New Username')
        new_password = st.text_input('New Password', type='password')
        new_email = st.text_input('New Email')
        submit_button = st.form_submit_button('Create')

        if submit_button:
            success, token = create_user(new_username, new_password, new_email)
            if success:
                st.success("User created successfully!")
                st.rerun()
            else:
                st.error("User creation failed. Username might already exist.")


def auth_user(username, password):
    response = requests.post(
            "http://127.0.0.1:8000/login",
            json={"username": username, "password": password}
    )
    if response.status_code == 200:
        token = response.json()["token"]
        return True, token
    elif response.status_code == 401:
        return False, None


def create_user(username, password, email):
    print('1')
    response = requests.post(
            "http://127.0.0.1:8000/create_user",
            json={"username": username, "password": password, "email": email}
    )
    if response.status_code == 200:
        token = response.json()["token"]
        return True, token
