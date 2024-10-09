import streamlit as st

st.header('Workout Planner')


def display_input_row(index):
    left, middle, right = st.columns(3)
    left.selectbox('Step', ['warmup', 'active', 'rest', 'cooldown'], key=f'step_{index}')
    middle.number_input('Timer', key=f'timer_{index}', step=1, min_value=0)
    right.number_input('Speed', key=f'speed_{index}', step=0.1, min_value=0., value=10.)

if 'rows' not in st.session_state:
    st.session_state['rows'] = 0

def increase_rows():
    st.session_state['rows'] += 1

st.button('Add line', on_click=increase_rows)

with st.form("my_form"):
    st.date_input(label="wkt_date")
    for i in range(st.session_state['rows']):
        display_input_row(i)
    submitted = st.form_submit_button("Submit")
    if submitted:
        result = []
        for i in range(st.session_state['rows']):
            step = st.session_state[f'step_{i}']
            timer = st.session_state[f'timer_{i}']
            speed = st.session_state[f'speed_{i}']
            result.append({'step': step, 'timer': timer, 'speed': speed})
        st.write(result)
