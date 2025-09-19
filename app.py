import streamlit as st
import os

# Set page config
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import the main interview assistant
try:
    from interview_assistant import main as interview_main
    interview_main()
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please ensure all dependencies are installed. Check requirements.txt")
except Exception as e:
    st.error(f"Application error: {e}")
    st.info("Please check the logs for more details")
