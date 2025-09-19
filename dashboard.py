import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import random


# ---- PAGE CONFIG ----
st.set_page_config(
    page_title="Christ Career Campus",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- USER CREDENTIALS ----
USER_CREDENTIALS = {
    "admin": "12345",
    "placement_officer": "placement123",
    "student": "student123",
}

# ---- CUSTOM CSS ----
def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        .main {
            font-family: 'Inter', sans-serif;
        }
        
        /* Login Card */
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 80vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        .login-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 400px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .login-card h1 {
            color: #2c3e50;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }
        
        .login-subtitle {
            color: #7f8c8d;
            margin-bottom: 2rem;
            font-weight: 400;
        }
        
        /* Dashboard Header */
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .dashboard-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .dashboard-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
        }
        
        /* Stats Cards */
        .stat-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            text-align: center;
            border: 1px solid #f0f0f0;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #7f8c8d;
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.9rem;
            letter-spacing: 1px;
        }
        
        /* News Ticker */
        .news-ticker {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 2rem 0;
            overflow: hidden;
        }
        
        .news-content {
            animation: scroll 20s linear infinite;
            white-space: nowrap;
        }
        
        @keyframes scroll {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        
        /* Sidebar Styling */
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        /* Remove Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# ---- SAMPLE DATA GENERATION ----
@st.cache_data
def generate_sample_data():
    # Companies data
    companies = ['TCS', 'Infosys', 'Wipro', 'Accenture', 'IBM', 'Microsoft', 'Google', 'Amazon', 'Deloitte', 'Capgemini']
    departments = ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical', 'Civil', 'MBA']
    
    # Placement data
    placement_data = []
    for i in range(300):
        placement_data.append({
            'Student_ID': f'CHR{2024}{i+1:03d}',
            'Name': f'Student {i+1}',
            'Department': random.choice(departments),
            'Company': random.choice(companies),
            'Package': random.randint(300000, 2500000),
            'Placement_Date': datetime.now() - timedelta(days=random.randint(0, 365)),
            'Job_Role': random.choice(['Software Engineer', 'Data Analyst', 'Consultant', 'Developer', 'Manager']),
            'Status': random.choice(['Placed', 'In Process', 'Shortlisted'])
        })
    
    return pd.DataFrame(placement_data)

# ---- LOGIN FUNCTION ----
def login():
    inject_custom_css()
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('''
            <div class="login-card">
                <h1>🎓 Christ Career Campus</h1>
                <p class="login-subtitle">Placement Tracking System</p>
            </div>
        ''', unsafe_allow_html=True)
        
        with st.container():
            st.markdown("### 🔐 Login to Continue")
            
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                if st.button("🚀 Login", use_container_width=True):
                    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_role = username
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
            
            # Demo credentials
            with st.expander("💡 Demo Credentials"):
                st.code("admin / 12345")
                st.code("placement_officer / placement123")
                st.code("student / student123")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---- DASHBOARD COMPONENTS ----
def create_kpi_cards():
    df = generate_sample_data()
    
    # Calculate KPIs
    total_students = len(df)
    placed_students = len(df[df['Status'] == 'Placed'])
    avg_package = df[df['Status'] == 'Placed']['Package'].mean()
    placement_rate = (placed_students / total_students) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
            <div class="stat-card">
                <div class="stat-number">{total_students}</div>
                <div class="stat-label">Total Students</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
            <div class="stat-card">
                <div class="stat-number">{placed_students}</div>
                <div class="stat-label">Students Placed</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
            <div class="stat-card">
                <div class="stat-number">{placement_rate:.1f}%</div>
                <div class="stat-label">Placement Rate</div>
            </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
            <div class="stat-card">
                <div class="stat-number">₹{avg_package/100000:.1f}L</div>
                <div class="stat-label">Avg Package</div>
            </div>
        ''', unsafe_allow_html=True)

def create_department_chart():
    df = generate_sample_data()
    dept_data = df[df['Status'] == 'Placed'].groupby('Department').size().reset_index(name='Count')
    
    fig = px.bar(dept_data, x='Department', y='Count', 
                 title='Placements by Department',
                 color='Count',
                 color_continuous_scale='Viridis')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=20,
        title_x=0.5
    )
    return fig

def create_package_distribution():
    df = generate_sample_data()
    placed_df = df[df['Status'] == 'Placed']
    
    fig = px.histogram(placed_df, x='Package', nbins=20,
                       title='Package Distribution',
                       labels={'Package': 'Package (₹)', 'count': 'Number of Students'})
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=20,
        title_x=0.5
    )
    return fig

def create_company_wise_chart():
    df = generate_sample_data()
    company_data = df[df['Status'] == 'Placed'].groupby('Company').agg({
        'Student_ID': 'count',
        'Package': 'mean'
    }).reset_index()
    company_data.columns = ['Company', 'Students_Hired', 'Avg_Package']
    
    fig = px.scatter(company_data, x='Students_Hired', y='Avg_Package',
                     size='Students_Hired', hover_name='Company',
                     title='Companies: Students Hired vs Average Package')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=20,
        title_x=0.5
    )
    return fig

def create_timeline_chart():
    df = generate_sample_data()
    placed_df = df[df['Status'] == 'Placed'].copy()
    placed_df['Month'] = placed_df['Placement_Date'].dt.to_period('M')
    timeline_data = placed_df.groupby('Month').size().reset_index(name='Count')
    timeline_data['Month'] = timeline_data['Month'].astype(str)
    
    fig = px.line(timeline_data, x='Month', y='Count',
                  title='Placement Timeline',
                  markers=True)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        title_font_size=20,
        title_x=0.5
    )
    return fig

# ---- NEWS TICKER ----
def create_news_ticker():
    news_items = [
        "🎉 Microsoft recruits 25 students from CSE department with packages up to ₹18 LPA",
        "📈 Placement rate increases by 15% compared to last year",
        "🚀 Google conducts campus interview next week - 50 students shortlisted",
        "💼 TCS offers 100+ positions across all departments",
        "🏆 Christ Career Campus achieves 95% placement rate this year"
    ]
    
    news_text = " | ".join(news_items * 2)  # Repeat for continuous scroll
    
    st.markdown(f'''
        <div class="news-ticker">
            <div class="news-content">
                📢 {news_text}
            </div>
        </div>
    ''', unsafe_allow_html=True)

# ---- MAIN DASHBOARD ----
def dashboard():
    inject_custom_css()
    
    # Header
    st.markdown('''
        <div class="dashboard-header">
            <div class="dashboard-title">🎓 Christ Career Campus</div>
            <div class="dashboard-subtitle">Placement Analytics Dashboard</div>
        </div>
    ''', unsafe_allow_html=True)
    
    # User info and logout
    col1, col2, col3 = st.columns([6, 2, 2])
    with col2:
        st.success(f"👋 Welcome, {st.session_state.username}")
    with col3:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    # News ticker
    create_news_ticker()
    
    # KPI Cards
    st.markdown("### 📊 Key Metrics")
    create_kpi_cards()
    
    st.markdown("---")
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_department_chart(), use_container_width=True)
        st.plotly_chart(create_company_wise_chart(), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_package_distribution(), use_container_width=True)
        st.plotly_chart(create_timeline_chart(), use_container_width=True)
    
    # Recent placements table
    st.markdown("### 📋 Recent Placements")
    df = generate_sample_data()
    recent_placements = df[df['Status'] == 'Placed'].sort_values('Placement_Date', ascending=False).head(10)
    recent_placements['Package'] = recent_placements['Package'].apply(lambda x: f"₹{x/100000:.1f}L")
    recent_placements['Placement_Date'] = recent_placements['Placement_Date'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        recent_placements[['Name', 'Department', 'Company', 'Job_Role', 'Package', 'Placement_Date']],
        use_container_width=True
    )

# ---- SIDEBAR FILTERS ----
def create_sidebar():
    with st.sidebar:
        st.markdown("### 🎛️ Dashboard Controls")
        
        # Department filter
        df = generate_sample_data()
        departments = ['All'] + list(df['Department'].unique())
        selected_dept = st.selectbox("📚 Filter by Department", departments)
        
        # Date range
        st.markdown("### 📅 Date Range")
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
        end_date = st.date_input("End Date", datetime.now())
        
        # Quick stats for sidebar
        st.markdown("### 📈 Quick Stats")
        if selected_dept != 'All':
            dept_df = df[df['Department'] == selected_dept]
        else:
            dept_df = df
            
        placed_count = len(dept_df[dept_df['Status'] == 'Placed'])
        st.metric("Placed Students", placed_count)
        
        avg_package = dept_df[dept_df['Status'] == 'Placed']['Package'].mean()
        st.metric("Avg Package", f"₹{avg_package/100000:.1f}L")
        
        # Export options
        st.markdown("### 📤 Export Data")
        if st.button("📊 Export to Excel"):
            st.success("✅ Data exported successfully!")

# ---- MAIN APP ----
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login()
    else:
        create_sidebar()
        dashboard()

if __name__ == "__main__":
    main()