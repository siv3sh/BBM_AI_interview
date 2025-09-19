import streamlit as st
import json
import time
import google.generativeai as genai
from datetime import datetime, timedelta
import re
import pdfplumber
import docx
import tempfile
import os
import base64
from typing import List, Dict, Any
import speech_recognition as sr
import pyttsx3
import threading
import queue

# Page configuration
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced UI
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
    
    .interview-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .question-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    }
    
    .answer-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    
    .timer-display {
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-listening {
        background-color: #28a745;
        animation: pulse 1.5s infinite;
    }
    
    .status-processing {
        background-color: #ffc107;
        animation: pulse 1.5s infinite;
    }
    
    .status-ready {
        background-color: #6c757d;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .camera-container {
        border: 2px solid #667eea;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f8f9fa;
    }
    
    .upload-section {
        border: 2px dashed #667eea;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class InterviewChatbot:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.questions = []
        self.current_question_index = 0
        self.answers = []
        self.scores = []
        self.start_time = None
        self.end_time = None
        
        # Initialize speech recognition and TTS
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
    def setup_tts(self):
        """Configure text-to-speech engine"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Find a better quality voice (prefer female voices for interviews)
            for voice in voices:
                if 'female' in voice.name.lower() or 'samantha' in voice.name.lower() or 'alex' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            else:
                # Fallback to first available voice
                self.tts_engine.setProperty('voice', voices[0].id)
        
        # Optimize settings for better quality
        self.tts_engine.setProperty('rate', 180)  # Slightly faster for better flow
        self.tts_engine.setProperty('volume', 0.8)  # Moderate volume
        self.tts_engine.setProperty('pitch', 0.5)  # Neutral pitch
        
    def speak_web(self, text: str):
        """Use web-based TTS for better quality"""
        try:
            # Create audio element with Web Speech API
            audio_html = f"""
            <script>
            function speakText() {{
                if ('speechSynthesis' in window) {{
                    const utterance = new SpeechSynthesisUtterance('{text}');
                    utterance.rate = 0.9;
                    utterance.pitch = 1.0;
                    utterance.volume = 0.8;
                    
                    // Try to use a better voice
                    const voices = speechSynthesis.getVoices();
                    const preferredVoice = voices.find(voice => 
                        voice.name.includes('Samantha') || 
                        voice.name.includes('Alex') || 
                        voice.name.includes('Victoria')
                    );
                    
                    if (preferredVoice) {{
                        utterance.voice = preferredVoice;
                    }}
                    
                    speechSynthesis.speak(utterance);
                }} else {{
                    console.log('Speech synthesis not supported');
                }}
            }}
            
            // Wait for voices to load
            if (speechSynthesis.getVoices().length === 0) {{
                speechSynthesis.addEventListener('voiceschanged', speakText);
            }} else {{
                speakText();
            }}
            </script>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Web TTS Error: {e}")
            # Fallback to local TTS
            self.speak(text)
    
    def speak(self, text: str):
        """Convert text to speech with improved quality (local fallback)"""
        try:
            # Try to use a better voice if available
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Look for high-quality voices
                for voice in voices:
                    if any(keyword in voice.name.lower() for keyword in ['samantha', 'alex', 'victoria', 'daniel']):
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            # Speak with pauses for better clarity
            sentences = text.split('. ')
            for sentence in sentences:
                if sentence.strip():
                    self.tts_engine.say(sentence.strip() + '.')
                    self.tts_engine.runAndWait()
                    time.sleep(0.3)  # Small pause between sentences
                    
        except Exception as e:
            st.error(f"TTS Error: {e}")
            # Fallback: show text prominently
            st.markdown(f"""
            <div style="background-color: #e3f2fd; padding: 1rem; border-radius: 5px; margin: 1rem 0;">
                <strong>🤖 AI Interviewer:</strong> {text}
            </div>
            """, unsafe_allow_html=True)
    
    def listen(self) -> str:
        """Listen for user speech input with improved quality"""
        try:
            with sr.Microphone() as source:
                st.info("🎤 Listening... Speak clearly now!")
                
                # Adjust for ambient noise with longer calibration
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                
                # Listen with better timeout and phrase time limit
                audio = self.recognizer.listen(
                    source, 
                    timeout=15,  # Longer timeout
                    phrase_time_limit=30  # Allow longer phrases
                )
                
            st.info("🔄 Processing your speech...")
            
            # Use Google Speech Recognition with better settings
            text = self.recognizer.recognize_google(
                audio, 
                language='en-US',
                show_all=False
            )
            
            return text
            
        except sr.WaitTimeoutError:
            return "No speech detected within the time limit"
        except sr.UnknownValueError:
            return "Could not understand the audio clearly"
        except sr.RequestError as e:
            st.error(f"Speech recognition service error: {e}")
            return "Speech recognition service unavailable"
        except Exception as e:
            st.error(f"Speech recognition error: {e}")
            return "Error in speech recognition"
    
    def extract_text_from_resume(self, file_content: bytes, filename: str) -> str:
        """Extract text from PDF or DOCX resume"""
        try:
            if filename.lower().endswith('.pdf'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(file_content)
                    tmp_file.flush()
                    
                    with pdfplumber.open(tmp_file.name) as pdf:
                        text = ""
                        for page in pdf.pages:
                            text += page.extract_text() or ""
                    
                    os.unlink(tmp_file.name)
                    return text
                    
            elif filename.lower().endswith('.docx'):
                with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                    tmp_file.write(file_content)
                    tmp_file.flush()
                    
                    doc = docx.Document(tmp_file.name)
                    text = ""
                    for paragraph in doc.paragraphs:
                        text += paragraph.text + "\n"
                    
                    os.unlink(tmp_file.name)
                    return text
                    
        except Exception as e:
            st.error(f"Error extracting text from resume: {e}")
            return ""
    
    def generate_interview_plan(self, resume_text: str, job_role: str, duration_minutes: int) -> Dict[str, Any]:
        """Generate interview plan based on resume, job role, and duration"""
        
        # Calculate complexity based on duration
        if duration_minutes <= 15:
            complexity = "basic"
            num_questions = 3
        elif duration_minutes <= 30:
            complexity = "intermediate"
            num_questions = 5
        else:
            complexity = "advanced"
            num_questions = 7
        
        prompt = f"""
        You are a professional HR interviewer conducting a {duration_minutes}-minute interview for a {job_role} position.
        
        Resume Summary:
        {resume_text[:1000]}...
        
        Generate an interview plan with {num_questions} questions of {complexity} complexity.
        
        Include:
        1. Professional greeting
        2. {num_questions} interview questions covering:
           - Technical skills
           - Behavioral questions
           - Role-specific questions
           - Problem-solving scenarios
        
        Format as JSON with this structure:
        {{
            "greeting": "Professional greeting message",
            "questions": [
                {{
                    "question": "Question text",
                    "category": "technical/behavioral/role-specific",
                    "expected_keywords": ["keyword1", "keyword2"],
                    "time_limit": estimated_time_in_seconds
                }}
            ],
            "closing": "Professional closing message"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            st.error(f"Error generating interview plan: {e}")
            return self.get_default_interview_plan(duration_minutes)
    
    def get_default_interview_plan(self, duration_minutes: int) -> Dict[str, Any]:
        """Fallback interview plan if AI generation fails"""
        if duration_minutes <= 15:
            questions = [
                {"question": "Tell me about yourself and your background.", "category": "behavioral", "expected_keywords": ["experience", "skills"], "time_limit": 120},
                {"question": "What are your key technical skills?", "category": "technical", "expected_keywords": ["programming", "tools"], "time_limit": 90},
                {"question": "Why are you interested in this role?", "category": "role-specific", "expected_keywords": ["passion", "growth"], "time_limit": 90}
            ]
        elif duration_minutes <= 30:
            questions = [
                {"question": "Tell me about yourself and your background.", "category": "behavioral", "expected_keywords": ["experience", "skills"], "time_limit": 120},
                {"question": "Describe a challenging project you worked on.", "category": "behavioral", "expected_keywords": ["problem", "solution"], "time_limit": 150},
                {"question": "What are your key technical skills?", "category": "technical", "expected_keywords": ["programming", "tools"], "time_limit": 90},
                {"question": "How do you handle tight deadlines?", "category": "behavioral", "expected_keywords": ["time management", "prioritization"], "time_limit": 120},
                {"question": "Why are you interested in this role?", "category": "role-specific", "expected_keywords": ["passion", "growth"], "time_limit": 90}
            ]
        else:
            questions = [
                {"question": "Tell me about yourself and your background.", "category": "behavioral", "expected_keywords": ["experience", "skills"], "time_limit": 120},
                {"question": "Describe a challenging project you worked on.", "category": "behavioral", "expected_keywords": ["problem", "solution"], "time_limit": 150},
                {"question": "What are your key technical skills?", "category": "technical", "expected_keywords": ["programming", "tools"], "time_limit": 90},
                {"question": "How do you handle tight deadlines?", "category": "behavioral", "expected_keywords": ["time management", "prioritization"], "time_limit": 120},
                {"question": "Describe a time you had to learn something new quickly.", "category": "behavioral", "expected_keywords": ["learning", "adaptability"], "time_limit": 120},
                {"question": "What's your approach to problem-solving?", "category": "technical", "expected_keywords": ["methodology", "analysis"], "time_limit": 120},
                {"question": "Why are you interested in this role?", "category": "role-specific", "expected_keywords": ["passion", "growth"], "time_limit": 90}
            ]
        
        return {
            "greeting": "Hello! Welcome to your interview. I'm your AI interviewer. Let's begin with a few questions to get to know you better.",
            "questions": questions,
            "closing": "Thank you for your time. The interview is now complete. We'll review your responses and get back to you soon."
        }
    
    def evaluate_answer(self, question: str, answer: str, expected_keywords: List[str]) -> Dict[str, Any]:
        """Evaluate candidate's answer using AI"""
        prompt = f"""
        Evaluate this interview answer:
        
        Question: {question}
        Answer: {answer}
        Expected Keywords: {', '.join(expected_keywords)}
        
        Provide evaluation in JSON format:
        {{
            "score": score_out_of_10,
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["area1", "area2"],
            "keyword_match": percentage_of_keywords_mentioned,
            "feedback": "detailed feedback message"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            st.error(f"Error evaluating answer: {e}")
            return {
                "score": 7,
                "strengths": ["Good response"],
                "areas_for_improvement": ["Could be more specific"],
                "keyword_match": 60,
                "feedback": "Answer received and processed."
            }

def main():
    st.markdown("""
    <div class="main-header">
        <h1>🎤 AI Interview Assistant</h1>
        <p>Professional AI-powered interview with voice interaction</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Interview Configuration")
        
        # API Key input
        api_key = st.text_input(
            "Enter your Google AI API Key:",
            type="password",
            help="Get your API key from https://aistudio.google.com/app/apikey"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your Google AI API key to continue")
            return
        
        # Job role input
        job_role = st.text_input(
            "Job Role/Position:",
            placeholder="e.g., Software Engineer, Data Scientist",
            value="Software Engineer"
        )
        
        # Interview duration
        duration_options = {
            "15 minutes (Basic)": 15,
            "30 minutes (Intermediate)": 30,
            "45 minutes (Advanced)": 45,
            "60 minutes (Comprehensive)": 60
        }
        
        duration_label = st.selectbox(
            "Interview Duration:",
            list(duration_options.keys())
        )
        duration_minutes = duration_options[duration_label]
        
        # Resume upload
        st.markdown("### 📄 Resume Upload")
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or DOCX):",
            type=['pdf', 'docx'],
            help="Upload your resume to get personalized interview questions"
        )
        
        if uploaded_file:
            st.success(f"✅ Resume uploaded: {uploaded_file.name}")
    
    # Main content area
    if not api_key or not job_role:
        st.info("👈 Please configure the interview settings in the sidebar")
        return
    
    if not uploaded_file:
        st.info("👈 Please upload your resume to begin the interview")
        return
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = InterviewChatbot(api_key)
    
    chatbot = st.session_state.chatbot
    
    # Extract resume text
    resume_text = chatbot.extract_text_from_resume(uploaded_file.read(), uploaded_file.name)
    
    if not resume_text:
        st.error("❌ Could not extract text from resume. Please try a different file.")
        return
    
    # Generate interview plan
    if 'interview_plan' not in st.session_state:
        with st.spinner("🤖 Generating personalized interview questions..."):
            st.session_state.interview_plan = chatbot.generate_interview_plan(
                resume_text, job_role, duration_minutes
            )
    
    interview_plan = st.session_state.interview_plan
    
    # Interview interface
    st.markdown(f"""
    <div class="interview-container">
        <h2>🎯 Interview Details</h2>
        <p><strong>Position:</strong> {job_role}</p>
        <p><strong>Duration:</strong> {duration_minutes} minutes</p>
        <p><strong>Questions:</strong> {len(interview_plan['questions'])} questions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Camera and microphone access with automatic request
    st.markdown("### 📹 Camera & Microphone Access")
    
    # JavaScript for automatic camera/mic access
    st.markdown("""
    <script>
    async function requestMediaAccess() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: true, 
                audio: true 
            });
            console.log('Camera and microphone access granted');
            
            // Update status indicators
            document.querySelectorAll('.status-indicator').forEach(indicator => {
                indicator.className = 'status-indicator status-listening';
            });
            
            // Stop the stream after getting permission
            stream.getTracks().forEach(track => track.stop());
            
            return true;
        } catch (error) {
            console.error('Error accessing media devices:', error);
            return false;
        }
    }
    
    // Request access when page loads
    window.addEventListener('load', requestMediaAccess);
    </script>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="camera-container">
        <p>🎥 <strong>Camera:</strong> <span class="status-indicator status-ready"></span> <span id="camera-status">Requesting Access...</span></p>
        <p>🎤 <strong>Microphone:</strong> <span class="status-indicator status-ready"></span> <span id="mic-status">Requesting Access...</span></p>
        <p><em>Camera and microphone access will be requested automatically.</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Start interview button
    if 'interview_started' not in st.session_state:
        if st.button("🚀 Start Interview", use_container_width=True):
            st.session_state.interview_started = True
            st.session_state.current_question = 0
            st.session_state.start_time = datetime.now()
            st.rerun()
    
    # Interview flow
    if st.session_state.get('interview_started', False):
        current_q = st.session_state.current_question
        
        # Timer
        elapsed_time = datetime.now() - st.session_state.start_time
        remaining_time = timedelta(minutes=duration_minutes) - elapsed_time
        
        if remaining_time.total_seconds() > 0:
            st.markdown(f"""
            <div class="timer-display">
                ⏱️ Time Remaining: {str(remaining_time).split('.')[0]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("⏰ Interview time is up!")
            return
        
        # Show greeting for first question
        if current_q == 0:
            st.markdown(f"""
            <div class="question-card">
                <h3>🤖 AI Interviewer</h3>
                <p>{interview_plan['greeting']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎤 Play Greeting"):
                chatbot.speak_web(interview_plan['greeting'])
        
        # Show current question
        if current_q < len(interview_plan['questions']):
            question_data = interview_plan['questions'][current_q]
            
            st.markdown(f"""
            <div class="question-card">
                <h3>❓ Question {current_q + 1}</h3>
                <p><strong>Category:</strong> {question_data['category'].title()}</p>
                <p><strong>Question:</strong> {question_data['question']}</p>
                <p><strong>Time Limit:</strong> {question_data['time_limit']} seconds</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎤 Ask Question"):
                    chatbot.speak_web(question_data['question'])
            
            with col2:
                if st.button("🎧 Listen for Answer"):
                    answer = chatbot.listen()
                    if answer and answer != "No speech detected":
                        st.session_state[f'answer_{current_q}'] = answer
                        
                        # Evaluate answer
                        evaluation = chatbot.evaluate_answer(
                            question_data['question'],
                            answer,
                            question_data['expected_keywords']
                        )
                        
                        st.session_state[f'evaluation_{current_q}'] = evaluation
                        
                        # Show answer and evaluation
                        st.markdown(f"""
                        <div class="answer-card">
                            <h4>💬 Your Answer:</h4>
                            <p>{answer}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="question-card">
                            <h4>📊 Evaluation:</h4>
                            <p><strong>Score:</strong> {evaluation['score']}/10</p>
                            <p><strong>Strengths:</strong> {', '.join(evaluation['strengths'])}</p>
                            <p><strong>Areas for Improvement:</strong> {', '.join(evaluation['areas_for_improvement'])}</p>
                            <p><strong>Feedback:</strong> {evaluation['feedback']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Move to next question
                        if st.button("➡️ Next Question"):
                            st.session_state.current_question += 1
                            st.rerun()
        
        # Show closing
        else:
            st.markdown(f"""
            <div class="question-card">
                <h3>🎉 Interview Complete!</h3>
                <p>{interview_plan['closing']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎤 Play Closing"):
                chatbot.speak_web(interview_plan['closing'])
            
            # Show final summary
            st.markdown("### 📊 Interview Summary")
            
            total_score = 0
            for i in range(len(interview_plan['questions'])):
                if f'evaluation_{i}' in st.session_state:
                    eval_data = st.session_state[f'evaluation_{i}']
                    total_score += eval_data['score']
            
            avg_score = total_score / len(interview_plan['questions']) if interview_plan['questions'] else 0
            
            st.markdown(f"""
            <div class="question-card">
                <h4>📈 Overall Performance</h4>
                <p><strong>Average Score:</strong> {avg_score:.1f}/10</p>
                <p><strong>Questions Answered:</strong> {len([k for k in st.session_state.keys() if k.startswith('answer_')])}</p>
                <p><strong>Total Time:</strong> {str(elapsed_time).split('.')[0]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Start New Interview"):
                # Reset session state
                for key in list(st.session_state.keys()):
                    if key.startswith(('interview_', 'answer_', 'evaluation_', 'current_question')):
                        del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()
