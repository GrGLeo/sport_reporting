import streamlit as st
from front.user.user import User

st.header('Workout Planner')
user: User = st.session_state['user']


def display_step(index, sport, type):
    left, middle, right = st.columns(3)
    left.write(f'{type.capitalize()}: ')
    middle.number_input('timer', key=f'timer_{type}_{index}', step=1, min_value=0)
    if sport == 'Running':
        right.number_input('speed', key=f'work_{type}_{index}', step=0.1, min_value=0., value=10.)
    elif sport == 'Cycling':
        right.number_input('power', key=f'work_{type}_{index}', step=1, min_value=0, value=120)


def display_set(index, sport):
    left, _, _ = st.columns(3)
    left.number_input(label='Number of repeat', min_value=1, value=1, step=1, key=f'repeat_{index}')
    display_step(index, sport, 'active')
    display_step(index, sport, 'rest')


if 'rows' not in st.session_state:
    st.session_state['rows'] = 1


def increase_rows():
    st.session_state['rows'] += 1


st.button('Add step', on_click=increase_rows)
sport = st.selectbox('Sport', ['Cycling', 'Running'])

with st.form("my_form"):
    st.date_input(label="Workout date", key='wkt_date')
    st.divider()
    st.text_input(label="Workout name")
    st.divider()
    display_step(0, sport, 'warmup')
    st.divider()
    i = 1
    for i in range(1, st.session_state['rows']):
        display_set(i, sport)
        st.divider()
    display_step(i+1, sport, 'cooldown')
    submitted = st.form_submit_button("Submit")
    if submitted:
        result = {}
        result['warmup'] = {
                'timer': st.session_state['timer_warmup_0'],
                'work': st.session_state['work_warmup_0']
        }
        for i in range(1, st.session_state['rows']):
            result[f'set_{i}'] = {
                f'step_{j}': {
                    'active': {
                        'timer': st.session_state[f'timer_active_{i}'],
                        'work': st.session_state[f'work_active_{i}']
                    },
                    'rest': {
                        'timer': st.session_state[f'timer_rest_{i}'],
                        'work': st.session_state[f'work_rest_{i}']
                    }
                } for j in range(st.session_state['repeat_1'])
            }
        result['cooldown'] = {
                'timer': st.session_state[f'timer_cooldown_{i+1}'],
                'work': st.session_state[f'work_cooldown_{i+1}']
        }
        date = st.session_state['wkt_date']
        pushed = user.push_programmed_wkt(date, sport, result)
        if pushed:
            st.toast('Threshold updated', icon="✅")
