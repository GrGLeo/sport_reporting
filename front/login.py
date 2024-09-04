import streamlit as st


def login_page():
    st.title("Login")

    with st.form(key="login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password")
        submit = st.form_submit_button("Login")

        if submit:
            token = auth_user(username, password)

            if token:
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
        submit_button = st.form_submit_button('Create')

    if submit_button:
        success = create_user(new_username, new_password)
        if success:
            st.success("User created successfully!")
            st.experimental_rerun()
        else:
            st.error("User creation failed. Username might already exist.")


def auth_user(username, password):
    return True


def create_user(username, password, mail):
    return True
