import streamlit as st
import json
import time
import google.generativeai as genai
from datetime import datetime
import re

# Page configuration
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
    
    .user-message {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .ai-message {
        background: linear-gradient(90deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .feedback-correct {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .feedback-incorrect {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
        margin: 0.5rem 0;
    }
    
    .score-display {
        background: linear-gradient(90deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .upload-section {
        border: 2px dashed #667eea;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class InterviewChatbot:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def analyze_resume_and_job(self, resume_text, job_role):
        prompt = f"""
        Analyze the following resume and job role to create an interview plan:
        
        RESUME:
        {resume_text}
        
        JOB ROLE: {job_role}
        
        Based on this analysis, create:
        1. 3-4 questions about the projects mentioned in the resume (focus on technical details, challenges, outcomes)
        2. 4-5 questions related to the job role requirements
        
        For each question, also provide:
        - The expected key points for a good answer
        - Difficulty level (Beginner/Intermediate/Advanced)
        
        Format your response as JSON with this structure:
        {{
            "resume_analysis": "Brief analysis of candidate's background",
            "job_match_score": "Score out of 10 with explanation",
            "resume_questions": [
                {{
                    "question": "Question text",
                    "expected_points": ["point1", "point2", "point3"],
                    "difficulty": "Beginner/Intermediate/Advanced",
                    "category": "Resume/Project"
                }}
            ],
            "job_role_questions": [
                {{
                    "question": "Question text",
                    "expected_points": ["point1", "point2", "point3"],
                    "difficulty": "Beginner/Intermediate/Advanced",
                    "category": "Job Role"
                }}
            ]
        }}
        
        Make questions specific and relevant. Avoid generic questions.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error analyzing resume: {str(e)}")
            return None
    
    def evaluate_answer(self, question, expected_points, user_answer, difficulty):
        prompt = f"""
        Evaluate this interview answer:
        
        QUESTION: {question}
        EXPECTED KEY POINTS: {', '.join(expected_points)}
        DIFFICULTY: {difficulty}
        USER ANSWER: {user_answer}
        
        Provide evaluation in JSON format:
        {{
            "is_correct": true/false,
            "score": 8,
            "feedback": "Detailed feedback explaining what was good/missing",
            "missed_points": ["points that were missed"],
            "strengths": ["what the candidate did well"],
            "suggestions": ["suggestions for improvement"]
        }}
        
        Be constructive and specific in your feedback. Return score as a number (0-10), not as a fraction.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error evaluating answer: {str(e)}")
            return None

def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_question_idx' not in st.session_state:
        st.session_state.current_question_idx = 0
    if 'interview_started' not in st.session_state:
        st.session_state.interview_started = False
    if 'scores' not in st.session_state:
        st.session_state.scores = []
    if 'interview_complete' not in st.session_state:
        st.session_state.interview_complete = False
    if 'resume_analysis' not in st.session_state:
        st.session_state.resume_analysis = ""

def extract_json_from_response(response_text):
    try:
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
        else:
            # If no JSON found, try parsing the entire response
            return json.loads(response_text)
    except:
        return None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Interview Assistant</h1>
        <p>Upload your resume, specify the job role, and let AI conduct your interview!</p>
    </div>
    """, unsafe_allow_html=True)
    
    initialize_session_state()
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.header("🔧 Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Enter your Google AI API Key:",
            type="password",
            placeholder="AIza...",
            help="Get your API key from https://aistudio.google.com/app/apikey"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your Google AI API key to continue")
            st.stop()
        
        st.divider()
        
        # Job Role input
        job_role = st.text_input(
            "Job Role:",
            placeholder="e.g., Full Stack Developer, Data Scientist, etc.",
            help="Enter the position you're interviewing for"
        )
        
        # Resume upload
        st.subheader("📄 Upload Resume")
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['txt', 'pdf'],
            help="Upload a text file or PDF containing your resume"
        )
        
        resume_text = ""
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                resume_text = str(uploaded_file.read(), "utf-8")
            else:
                st.info("PDF support requires additional libraries. Please use a .txt file for now.")
        
        # Manual resume input option
        if not resume_text:
            st.subheader("✍️ Or paste your resume:")
            resume_text = st.text_area(
                "Resume Content:",
                height=200,
                placeholder="Paste your resume content here..."
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display current statistics
        if st.session_state.scores:
            st.markdown("### 📊 Interview Progress")
            total_questions = len(st.session_state.questions)
            answered = len(st.session_state.scores)
            avg_score = sum(st.session_state.scores) / len(st.session_state.scores) if st.session_state.scores else 0
            
            st.metric("Questions Answered", f"{answered}/{total_questions}")
            st.metric("Average Score", f"{avg_score:.1f}/10")
            
            if st.session_state.interview_complete:
                st.success("Interview Complete! 🎉")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Start Interview Button
        if not st.session_state.interview_started and api_key and job_role and resume_text:
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            st.write("### Ready to start your interview!")
            st.write(f"**Job Role:** {job_role}")
            st.write(f"**Resume Length:** {len(resume_text.split())} words")
            
            if st.button("🚀 Start Interview", type="primary"):
                with st.spinner("Analyzing your resume and preparing questions..."):
                    chatbot = InterviewChatbot(api_key)
                    analysis_result = chatbot.analyze_resume_and_job(resume_text, job_role)
                    
                    if analysis_result:
                        parsed_result = extract_json_from_response(analysis_result)
                        if parsed_result:
                            st.session_state.resume_analysis = parsed_result.get('resume_analysis', '')
                            resume_questions = parsed_result.get('resume_questions', [])
                            job_questions = parsed_result.get('job_role_questions', [])
                            st.session_state.questions = resume_questions + job_questions
                            st.session_state.interview_started = True
                            st.session_state.chat_history.append({
                                "type": "ai",
                                "content": f"Welcome! I've analyzed your resume for the {job_role} position. Let's start with some questions about your projects and experience. Ready?",
                                "timestamp": datetime.now()
                            })
                            st.rerun()
                        else:
                            st.error("Failed to parse interview questions. Please try again.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat Interface
        if st.session_state.interview_started and st.session_state.questions:
            st.markdown("### 💬 Interview Chat")
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                st.markdown('<div class="chat-container">', unsafe_allow_html=True)
                
                for message in st.session_state.chat_history:
                    if message["type"] == "user":
                        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)
                    
                    if "feedback" in message:
                        feedback_class = "feedback-correct" if message["feedback"]["is_correct"] else "feedback-incorrect"
                        st.markdown(f'<div class="{feedback_class}">Score: {message["feedback"]["score"]}/10<br>{message["feedback"]["feedback"]}</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Current question or completion
            if not st.session_state.interview_complete:
                if st.session_state.current_question_idx < len(st.session_state.questions):
                    current_q = st.session_state.questions[st.session_state.current_question_idx]
                    
                    # Display current question
                    st.markdown("### Current Question:")
                    st.info(f"**Question {st.session_state.current_question_idx + 1}/{len(st.session_state.questions)}** ({current_q.get('difficulty', 'Medium')}) - {current_q.get('category', 'General')}")
                    st.write(current_q['question'])
                    
                    # Answer input
                    user_answer = st.text_area(
                        "Your Answer:",
                        key=f"answer_{st.session_state.current_question_idx}",
                        height=150,
                        placeholder="Type your detailed answer here..."
                    )
                    
                    col_a, col_b = st.columns([1, 4])
                    with col_a:
                        if st.button("Submit Answer", type="primary"):
                            if user_answer.strip():
                                # Add user message to chat
                                st.session_state.chat_history.append({
                                    "type": "user",
                                    "content": user_answer,
                                    "timestamp": datetime.now()
                                })
                                
                                # Evaluate answer
                                with st.spinner("Evaluating your answer..."):
                                    chatbot = InterviewChatbot(api_key)
                                    evaluation = chatbot.evaluate_answer(
                                        current_q['question'],
                                        current_q['expected_points'],
                                        user_answer,
                                        current_q.get('difficulty', 'Medium')
                                    )
                                    
                                    if evaluation:
                                        parsed_eval = extract_json_from_response(evaluation)
                                        if parsed_eval:
                                            # Store score - handle both "8/10" format and direct number
                                            score_raw = parsed_eval.get('score', '0')
                                            if isinstance(score_raw, str) and '/' in score_raw:
                                                score = float(score_raw.split('/')[0])
                                            elif isinstance(score_raw, (int, float)):
                                                score = float(score_raw)
                                            else:
                                                try:
                                                    score = float(str(score_raw))
                                                except:
                                                    score = 0.0
                                            st.session_state.scores.append(score)
                                            
                                            # Add AI feedback to chat
                                            st.session_state.chat_history.append({
                                                "type": "ai",
                                                "content": "Here's my evaluation of your answer:",
                                                "feedback": parsed_eval,
                                                "timestamp": datetime.now()
                                            })
                                            
                                            # Move to next question
                                            st.session_state.current_question_idx += 1
                                            
                                            if st.session_state.current_question_idx < len(st.session_state.questions):
                                                next_q = st.session_state.questions[st.session_state.current_question_idx]
                                                st.session_state.chat_history.append({
                                                    "type": "ai",
                                                    "content": f"Great! Let's move to the next question:\n\n**Question {st.session_state.current_question_idx + 1}:** {next_q['question']}",
                                                    "timestamp": datetime.now()
                                                })
                                            else:
                                                st.session_state.interview_complete = True
                                                avg_score = sum(st.session_state.scores) / len(st.session_state.scores)
                                                st.session_state.chat_history.append({
                                                    "type": "ai",
                                                    "content": f"🎉 Interview completed! Your overall performance: {avg_score:.1f}/10. Thank you for your time!",
                                                    "timestamp": datetime.now()
                                                })
                                            
                                            st.rerun()
                            else:
                                st.warning("Please provide an answer before submitting.")
                
                else:
                    st.success("🎉 Interview Completed!")
                    
    with col2:
        if st.session_state.interview_started:
            st.markdown("### 📈 Performance Summary")
            
            if st.session_state.resume_analysis:
                st.markdown("**Resume Analysis:**")
                st.write(st.session_state.resume_analysis)
            
            if st.session_state.scores:
                avg_score = sum(st.session_state.scores) / len(st.session_state.scores)
                
                st.markdown(f"""
                <div class="score-display">
                    <h3>Overall Score: {avg_score:.1f}/10</h3>
                    <p>Questions Answered: {len(st.session_state.scores)}/{len(st.session_state.questions)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Score breakdown
                st.markdown("**Question-wise Scores:**")
                for i, score in enumerate(st.session_state.scores):
                    q_type = st.session_state.questions[i].get('category', 'General')
                    st.write(f"Q{i+1} ({q_type}): {score}/10")
            
            if st.session_state.interview_complete:
                st.markdown("### 🎯 Interview Summary")
                if st.button("📊 Generate Detailed Report"):
                    st.info("Detailed report feature coming soon!")
                
                if st.button("🔄 Start New Interview"):
                    # Reset session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

if __name__ == "__main__":
    main()