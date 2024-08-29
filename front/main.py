import streamlit as st
from parsing import fit_parsing


st.title("Welcome to My Multi-Page Streamlit App")
st.write("Use the sidebar to navigate between pages.")

# File uploader widget
uploaded_file = st.file_uploader("Choose a file", type=['fit', 'fits'])

if uploaded_file is not None:
    if uploaded_file.type == "application/fit" or uploaded_file.type == "application/fits":
        df = fit_parsing(uploaded_file)
        st.write(df)

        power = df.power
        power = power.rolling(window=30).mean()
        power = power ** 4
        power = power.mean()
        np = power ** 0.25
        intf = np / 305
        duration = df.index.size
        tss = (duration * np * intf) / (305 * 3600) * 100
        st.write(np, intf, duration)
        st.write(tss)

    else:
        st.write("Uploaded file is not a fit file")
else:
    st.write("Please upload a file.")
