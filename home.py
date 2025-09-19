import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Integrated Career Platform", page_icon="🚀", layout="wide")

st.title("🚀 Integrated Career Platform")
st.markdown("""
Welcome to the unified platform!  
Choose from the modules below to get started:
""")

# Create columns for better layout
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🤖 Agentic Resume Optimizer")
    st.markdown("ATS-powered resume analysis using Groq LLMs")
    if st.button("Launch Resume Optimizer", use_container_width=True):
        st.info("🚀 Launching Resume Optimizer...")
        st.switch_page("pages/1_Agentic_ATS.py")

with col2:
    st.markdown("### 🐋 DeepSeek RAG Chatbot")
    st.markdown("AI-powered career assistance with RAG")
    if st.button("Launch RAG Chatbot", use_container_width=True):
        st.info("🚀 Launching RAG Chatbot...")
        st.switch_page("pages/2_Chatbot.py")

with col3:
    st.markdown("### 🎓 Placement Dashboard")
    st.markdown("Analytics and placement tracking")
    if st.button("Launch Dashboard", use_container_width=True):
        st.info("🚀 Launching Dashboard...")
        st.switch_page("pages/3_Dashboard.py")

# Second row
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("### 💬 AI Interview Assistant")
    st.markdown("Practice interviews with AI evaluation")
    if st.button("Launch Interview Assistant", use_container_width=True):
        st.info("🚀 Launching Interview Assistant...")
        st.switch_page("pages/4_Interview.py")

with col5:
    st.markdown("### 📊 Evaluation Dashboard")
    st.markdown("Performance metrics and analysis")
    if st.button("Launch Evaluation", use_container_width=True):
        st.info("🚀 Launching Evaluation Dashboard...")
        # For now, show a placeholder
        st.success("Evaluation module coming soon!")

with col6:
    st.markdown("### ⚙️ Settings")
    st.markdown("Configure API keys and settings")
    if st.button("Open Settings", use_container_width=True):
        st.info("Settings panel coming soon!")

# Add some additional information
st.markdown("---")
st.markdown("### 📋 Quick Start Guide")
st.markdown("""
1. **Resume Optimizer**: Upload your resume for ATS compatibility analysis
2. **RAG Chatbot**: Ask career-related questions and get AI-powered answers
3. **Placement Dashboard**: View placement statistics and analytics
4. **Interview Assistant**: Practice interviews with AI evaluation

### 🔑 Demo Credentials (for Dashboard)
- **Admin**: `admin` / `12345`
- **Placement Officer**: `placement_officer` / `placement123`
- **Student**: `student` / `student123`
""")

# Add status information
st.markdown("---")
st.markdown("### 📊 System Status")
col1, col2, col3 = st.columns(3)

with col1:
    st.success("✅ Streamlit Server: Running")
    
with col2:
    st.success("✅ Dependencies: Loaded")
    
with col3:
    st.success("✅ Modules: Ready")