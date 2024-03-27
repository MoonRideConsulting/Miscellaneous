import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="SunPower Overview Dash",page_icon="🧑‍🚀",layout="wide")

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(
    worksheet="Zips",
    ttl="10m",
    usecols=[0, 1, 2, 3]
)

st.write(df)

def password_protection():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        
    if not st.session_state.authenticated:
        password = st.text_input("Enter Password:", type="password")
        correct_hashed_password = "Sunpower1234"
        
        if st.button("Login"):
            if password == correct_hashed_password:
                st.session_state.authenticated = True
                main_dashboard()
            else:
                st.error("Incorrect Password. Please try again or contact the administrator.")
    else:
        main_dashboard()

def main_dashboard():
    st.markdown("<h1 style='text-align: center;'>SunPower Overview Dash</h1>", unsafe_allow_html=True)
    
    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(
        worksheet="Zips",
        ttl="10m",
        usecols=[0, 1, 2, 3]
    )

    st.write(df)


if __name__ == '__main__':
    password_protection()
