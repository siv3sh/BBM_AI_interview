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
import io
import asyncio

# Optional imports with fallbacks
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    st.warning("Speech recognition not available. Voice input disabled.")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    st.warning("Edge TTS not available. Text-to-speech may be limited.")

# Page configuration
st.set_page_config(
    page_title="AI Interview Assistant - Manual Questions",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for conversational UI
st.markdown("""
<style>
    .assistant-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    .conversation-bubble {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        animation: slideIn 0.5s ease-out;
    }
    
    .user-bubble {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        margin-left: 2rem;
    }
    
    .assistant-bubble {
        background: #f3e5f5;
        border-left: 4px solid #9c27b0;
        margin-right: 2rem;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .voice-indicator {
        display: inline-block;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        margin-right: 10px;
        animation: pulse 1.5s infinite;
    }
    
    .listening {
        background-color: #4caf50;
    }
    
    .speaking {
        background-color: #ff9800;
    }
    
    .thinking {
        background-color: #2196f3;
    }
    
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.7; transform: scale(1.1); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    .status-bar {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
</style>
""", unsafe_allow_html=True)

class ConversationalInterviewAssistant:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize speech recognition and TTS
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None
            
        if PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self.setup_tts()
            except Exception as e:
                st.warning(f"Local TTS initialization failed: {e}. Using web-based TTS only.")
                self.tts_engine = None
        else:
            self.tts_engine = None
        
        # Conversation state
        self.conversation_history = []
        self.interview_context = {}
        self.current_mode = "greeting"
        self.current_question_index = 0
        self.questions = []
        self.start_time = None
        
    def setup_tts(self):
        """Configure text-to-speech engine for conversational feel"""
        try:
            voices = self.tts_engine.getProperty('voices')
            if voices:
                for voice in voices:
                    if any(name in voice.name.lower() for name in ['samantha', 'alex', 'victoria', 'karen']):
                        self.tts_engine.setProperty('voice', voice.id)
                        break
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
            
            self.tts_engine.setProperty('rate', 170)
            self.tts_engine.setProperty('volume', 0.8)
            self.tts_engine.setProperty('pitch', 0.6)
        except Exception as e:
            # Fallback: disable local TTS if eSpeak is not available
            st.warning(f"Local TTS not available: {e}. Using web-based TTS only.")
            self.tts_engine = None
    
    def speak_edge_tts(self, text: str, emotion: str = "friendly"):
        """Use Microsoft Edge TTS (free and high-quality)"""
        if not EDGE_TTS_AVAILABLE:
            return self.speak_gtts_streamlit(text, emotion)
            
        try:
            emotion_icons = {
                "friendly": "😊",
                "encouraging": "👍",
                "thoughtful": "🤔",
                "excited": "🎉",
                "concerned": "😟"
            }
            
            icon = emotion_icons.get(emotion, "🤖")
            st.markdown(f"""
            <div class="assistant-bubble">
                <div class="voice-indicator speaking"></div>
                <strong>{icon} Assistant:</strong> {text}
            </div>
            """, unsafe_allow_html=True)
            
            # Use selected voice or default based on emotion
            if hasattr(st.session_state, 'selected_voice'):
                voice = st.session_state.selected_voice
            else:
                voice = "en-US-AriaNeural"
                if emotion == "excited":
                    voice = "en-US-JennyNeural"
                elif emotion == "thoughtful":
                    voice = "en-US-GuyNeural"
                elif emotion == "encouraging":
                    voice = "en-US-EmmaNeural"
            
            # Create async function for Edge TTS
            async def generate_speech():
                communicate = edge_tts.Communicate(text, voice)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data
            
            # Run async function
            audio_data = asyncio.run(generate_speech())
            
            # Convert to base64 for Streamlit
            audio_base64 = base64.b64encode(audio_data).decode()
            
            # Auto-play audio
            audio_html = f"""
            <audio controls autoplay style="width: 100%; margin: 10px 0;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const audio = document.querySelector('audio');
                    if (audio) {{
                        audio.play().catch(e => console.log('Autoplay prevented:', e));
                    }}
                }});
            </script>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Edge TTS Error: {e}")
            return self.speak_gtts_streamlit(text, emotion)
    
    def speak_gtts_streamlit(self, text: str, emotion: str = "friendly"):
        """Fallback to gTTS with Streamlit integration"""
        if not GTTS_AVAILABLE:
            # Final fallback to text display only
            st.markdown(f"""
            <div class="assistant-bubble">
                <strong>🤖 Assistant:</strong> {text}
            </div>
            """, unsafe_allow_html=True)
            return
            
        try:
            emotion_icons = {
                "friendly": "😊",
                "encouraging": "👍",
                "thoughtful": "🤔",
                "excited": "🎉",
                "concerned": "😟"
            }
            
            icon = emotion_icons.get(emotion, "🤖")
            st.markdown(f"""
            <div class="assistant-bubble">
                <div class="voice-indicator speaking"></div>
                <strong>{icon} Assistant:</strong> {text}
            </div>
            """, unsafe_allow_html=True)
            
            # Use gTTS for high quality
            tts = gTTS(text=text, lang='en', slow=False, tld='com')
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Convert to base64 for Streamlit
            audio_data = audio_buffer.getvalue()
            audio_base64 = base64.b64encode(audio_data).decode()
            
            # Auto-play audio
            audio_html = f"""
            <audio controls autoplay style="width: 100%; margin: 10px 0;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const audio = document.querySelector('audio');
                    if (audio) {{
                        audio.play().catch(e => console.log('Autoplay prevented:', e));
                    }}
                }});
            </script>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
            
            audio_buffer.close()
            
        except Exception as e:
            st.error(f"gTTS Error: {e}")
            # Final fallback to text display
            st.markdown(f"""
            <div class="assistant-bubble">
                <strong>🤖 Assistant:</strong> {text}
            </div>
            """, unsafe_allow_html=True)
    
    def speak_conversationally(self, text: str, emotion: str = "friendly"):
        """Main conversational speech method using only free TTS options"""
        return self.speak_edge_tts(text, emotion)
    
    def listen_for_command(self) -> str:
        """Listen for voice commands with conversational context"""
        if not SPEECH_RECOGNITION_AVAILABLE or not self.recognizer:
            st.error("Speech recognition not available. Please use text input.")
            return "Speech recognition not available"
            
        try:
            with sr.Microphone() as source:
                st.markdown("""
                <div class="status-bar">
                    <div class="voice-indicator listening"></div>
                    <strong>🎤 Listening for your response...</strong>
                </div>
                """, unsafe_allow_html=True)
                
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=20)
            
            st.markdown("""
            <div class="status-bar">
                <div class="voice-indicator thinking"></div>
                <strong>🔄 Processing your response...</strong>
            </div>
            """, unsafe_allow_html=True)
            
            text = self.recognizer.recognize_google(audio, language='en-US')
            
            # Display user response
            st.markdown(f"""
            <div class="user-bubble">
                <strong>👤 You:</strong> {text}
            </div>
            """, unsafe_allow_html=True)
            
            return text
            
        except sr.WaitTimeoutError:
            return "No response detected"
        except sr.UnknownValueError:
            return "Could not understand clearly"
        except Exception as e:
            st.error(f"Listening error: {e}")
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
    
    def generate_interview_plan(self, resume_text: str, job_role: str, num_questions: int) -> Dict[str, Any]:
        """Generate high-quality, resume-specific interview plan"""
        
        try:
            # Use AI to analyze resume and generate targeted questions
            prompt = f"""
            You are an expert HR interviewer. Analyze this resume and generate {num_questions} high-quality, targeted interview questions for a {job_role} position.
            
            RESUME CONTENT:
            {resume_text[:2000]}  # Limit to avoid token limits
            
            JOB ROLE: {job_role}
            NUMBER OF QUESTIONS: {num_questions}
            
            Generate questions that:
            1. Focus on the candidate's ACTUAL experience from their resume
            2. Test relevant skills mentioned in their background
            3. Explore specific projects or achievements they listed
            4. Assess technical competencies relevant to {job_role}
            5. Include behavioral questions based on their work history
            6. Are progressive (start easy, get more challenging)
            
            Return JSON format:
            {{
                "rounds": [
                    {{
                        "name": "Round Name",
                        "duration": "X minutes",
                        "questions": [
                            {{
                                "question": "Specific question based on resume content",
                                "expected_time": "2-3 minutes",
                                "follow_up": "Follow-up question",
                                "focus_area": "What this question tests"
                            }}
                        ]
                    }}
                ],
                "greeting": "Personalized greeting mentioning their background",
                "closing": "Professional closing message"
            }}
            
            Make questions:
            - Specific to their resume content
            - Progressive in difficulty
            - Relevant to {job_role}
            - Professional and engaging
            - Include technical, behavioral, and situational questions
            
            IMPORTANT: Base questions on ACTUAL content from their resume, not generic questions.
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean and parse JSON
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            interview_plan = json.loads(response_text)
            
            # Validate structure
            if 'rounds' not in interview_plan:
                raise ValueError("Invalid response structure")
            
            return interview_plan
            
        except Exception as e:
            st.error(f"Error generating AI interview plan: {e}")
            # Fallback to resume-based questions
            return self.get_resume_based_plan(resume_text, job_role, num_questions)
    
    def get_resume_based_plan(self, resume_text: str, job_role: str, num_questions: int) -> Dict[str, Any]:
        """Generate resume-based questions as fallback"""
        
        # Extract key information from resume
        resume_lower = resume_text.lower()
        
        # Detect technical skills
        tech_skills = []
        common_skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes', 
                        'machine learning', 'data analysis', 'web development', 'mobile development', 'devops']
        
        for skill in common_skills:
            if skill in resume_lower:
                tech_skills.append(skill)
        
        # Detect experience level
        experience_keywords = ['senior', 'lead', 'manager', 'director', 'principal', 'architect']
        is_senior = any(keyword in resume_lower for keyword in experience_keywords)
        
        # Detect education
        education_keywords = ['bachelor', 'master', 'phd', 'university', 'college', 'degree']
        has_education = any(keyword in resume_lower for keyword in education_keywords)
        
        # Generate targeted questions based on resume content
        questions = []
        
        # Technical questions based on detected skills
        if tech_skills:
            for i, skill in enumerate(tech_skills[:min(3, num_questions//2)]):
                questions.append({
                    "question": f"I see you have experience with {skill.title()}. Can you walk me through a specific project where you used {skill} and explain the challenges you faced?",
                    "expected_time": "3-4 minutes",
                    "follow_up": "What was the impact of this project on your team or company?",
                    "focus_area": f"{skill.title()} Technical Skills"
                })
        
        # Experience-based questions
        if is_senior:
            questions.append({
                "question": "Given your senior-level experience, can you describe a time when you had to lead a team through a difficult technical challenge?",
                "expected_time": "3-4 minutes",
                "follow_up": "How did you ensure knowledge transfer to junior team members?",
                "focus_area": "Leadership & Problem Solving"
            })
        
        # Project-specific questions
        questions.append({
            "question": "Looking at your resume, I'm interested in one of your recent projects. Can you pick one that you're most proud of and explain the technical architecture and your specific contributions?",
            "expected_time": "4-5 minutes",
            "follow_up": "What would you do differently if you had to rebuild this project today?",
            "focus_area": "Project Experience & Technical Depth"
        })
        
        # Behavioral questions based on work history
        questions.append({
            "question": "I notice your work history shows progression in your career. Can you tell me about a time when you had to learn a completely new technology or skill to complete a project?",
            "expected_time": "3-4 minutes",
            "follow_up": "How do you typically approach learning new technologies?",
            "focus_area": "Learning Agility & Adaptability"
        })
        
        # Role-specific questions
        if 'data' in resume_lower or 'analytics' in resume_lower:
            questions.append({
                "question": "I see you have experience with data analysis. Can you describe a time when you had to make a data-driven decision that significantly impacted a project or business outcome?",
                "expected_time": "3-4 minutes",
                "follow_up": "How did you validate your findings and communicate them to stakeholders?",
                "focus_area": "Data Analysis & Business Impact"
            })
        
        # Fill remaining questions with role-specific content
        remaining = num_questions - len(questions)
        for i in range(remaining):
            questions.append({
                "question": f"Based on your experience with {job_role.lower()}, can you describe how you would approach solving a complex problem in this domain?",
                "expected_time": "3-4 minutes",
                "follow_up": "What resources or methodologies would you use?",
                "focus_area": f"{job_role} Problem Solving"
            })
        
        # Organize into rounds
        if num_questions <= 5:
            rounds = [{"name": "Comprehensive Assessment", "duration": f"{num_questions * 3} minutes", "questions": questions}]
        elif num_questions <= 10:
            mid_point = num_questions // 2
            rounds = [
                {"name": "Technical Deep Dive", "duration": f"{mid_point * 3} minutes", "questions": questions[:mid_point]},
                {"name": "Experience & Behavioral", "duration": f"{(num_questions - mid_point) * 3} minutes", "questions": questions[mid_point:]}
            ]
        else:
            third = num_questions // 3
            rounds = [
                {"name": "Technical Skills", "duration": f"{third * 3} minutes", "questions": questions[:third]},
                {"name": "Project Experience", "duration": f"{third * 3} minutes", "questions": questions[third:2*third]},
                {"name": "Leadership & Growth", "duration": f"{(num_questions - 2*third) * 3} minutes", "questions": questions[2*third:]}
            ]
        
        return {
            "rounds": rounds,
            "greeting": f"Hello! I'm your AI interview assistant. I've reviewed your resume and prepared {num_questions} targeted questions based on your experience with {', '.join(tech_skills[:3]) if tech_skills else job_role.lower()}. Let's begin!",
            "closing": "Thank you for sharing your experiences. I'll now evaluate your responses based on your resume and the role requirements."
        }
    
    def generate_final_evaluation(self, all_answers: Dict[str, str], interview_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final selection/rejection decision with detailed analysis"""
        try:
            # Collect all answers
            answers_text = "\n".join([f"Q{i+1}: {answer}" for i, answer in all_answers.items()])
            
            prompt = f"""
            You are a senior HR manager making a final hiring decision. Analyze all interview answers and provide a comprehensive evaluation.
            
            Interview Plan: {interview_plan.get('greeting', '')}
            All Answers: {answers_text}
            
            IMPORTANT: You must make a clear SELECTED or REJECTED decision. Be decisive and professional.
            
            Return JSON format:
            {{
                "decision": "SELECTED" or "REJECTED",
                "overall_score": 85,
                "strengths": ["Strong technical knowledge", "Good communication skills", "Relevant experience"],
                "weaknesses": ["Lack of experience in specific area", "Could improve problem-solving approach"],
                "reasoning": "Clear explanation of why the candidate was SELECTED or REJECTED. Be specific about what influenced your decision.",
                "recommendations": ["Specific actionable advice for improvement", "Areas to focus on for future interviews", "Skills to develop"],
                "next_steps": ["What happens next if selected", "Timeline for next steps", "Contact information"]
            }}
            
            Evaluation Criteria:
            - Technical skills and knowledge
            - Communication and presentation
            - Problem-solving ability
            - Cultural fit and attitude
            - Relevant experience
            - Overall potential
            
            Be thorough, professional, and decisive. If REJECTED, provide specific improvement suggestions.
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean JSON
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            evaluation = json.loads(response_text)
            return evaluation
            
        except Exception as e:
            st.error(f"Error generating final evaluation: {e}")
            return {
                "decision": "UNDECIDED",
                "overall_score": 5,
                "strengths": ["Completed the interview"],
                "weaknesses": ["Evaluation error occurred"],
                "reasoning": "Technical error prevented proper evaluation",
                "recommendations": "Please try the interview again",
                "next_steps": "Contact support"
            }


def main():
    # Check if running on Streamlit Cloud
    is_cloud = "share.streamlit.io" in st.get_option("server.baseUrlPath") or "share.streamlit.io" in str(st.get_option("server.headless"))
    
    st.markdown(f"""
    <div class="assistant-container">
        <h1>🤖 AI Interview Assistant</h1>
        <p>Manual Question Count - Clear SELECTED/REJECTED Results</p>
        {"<p style='font-size: 0.8em; opacity: 0.8;'>☁️ Running on Streamlit Cloud</p>" if is_cloud else ""}
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Setup")
        
        # Try to get API key from secrets first (for Streamlit Cloud)
        try:
            api_key = st.secrets["GOOGLE_AI_API_KEY"]
            st.success("✅ API key loaded from secrets")
        except:
            # Fallback to manual input (for local development)
            api_key = st.text_input(
                "Google AI API Key:",
                type="password",
                help="Get your API key from https://aistudio.google.com/app/apikey"
            )
        
        if not api_key:
            st.warning("⚠️ Please enter your Google AI API key")
            st.info("💡 For Streamlit Cloud: Add your API key in the secrets section")
            return
        
        # Free TTS Options
        st.markdown("### 🎤 Voice Options")
        st.success("🆓 **Microsoft Edge TTS** - Free & High-quality neural voices")
        
        # Voice selection for Edge TTS
        voice_options = {
            "Aria (Friendly Female)": "en-US-AriaNeural",
            "Jenny (Energetic Female)": "en-US-JennyNeural", 
            "Guy (Professional Male)": "en-US-GuyNeural",
            "Emma (Encouraging Female)": "en-US-EmmaNeural",
            "Davis (Confident Male)": "en-US-DavisNeural"
        }
        
        selected_voice = st.selectbox(
            "Choose Voice:",
            list(voice_options.keys()),
            help="Select your preferred voice for the interview"
        )
        
        # Store selected voice in session state
        st.session_state.selected_voice = voice_options[selected_voice]
        
        st.markdown("### 💼 Interview Settings")
        
        job_role = st.text_input(
            "Job Role:",
            value="Software Engineer"
        )
        
        # Number of questions selection
        num_questions = st.number_input(
            "Number of Questions:",
            min_value=3,
            max_value=20,
            value=5,
            help="Select how many questions you want in the interview."
        )
        
        st.markdown("### 📄 Resume")
        uploaded_file = st.file_uploader(
            "Upload Resume:",
            type=['pdf', 'docx']
        )
        
        if uploaded_file:
            st.success(f"✅ {uploaded_file.name}")
    
    # Main interface
    if not api_key or not job_role or not uploaded_file:
        st.info("👈 Please complete the setup in the sidebar to begin")
        return
    
    # Initialize assistant
    if 'assistant' not in st.session_state:
        st.session_state.assistant = ConversationalInterviewAssistant(api_key=api_key)
    
    assistant = st.session_state.assistant
    
    # Extract resume and generate plan
    if 'interview_plan' not in st.session_state:
        with st.spinner("🤖 Analyzing your resume and preparing personalized questions..."):
            resume_text = assistant.extract_text_from_resume(uploaded_file.read(), uploaded_file.name)
            
            # Show resume analysis
            st.markdown("### 📄 Resume Analysis")
            
            # Extract key information for display
            resume_lower = resume_text.lower()
            tech_skills = []
            common_skills = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'kubernetes', 
                            'machine learning', 'data analysis', 'web development', 'mobile development', 'devops']
            
            for skill in common_skills:
                if skill in resume_lower:
                    tech_skills.append(skill.title())
            
            experience_keywords = ['senior', 'lead', 'manager', 'director', 'principal', 'architect']
            is_senior = any(keyword in resume_lower for keyword in experience_keywords)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="conversation-bubble">
                    <h4>🔍 Detected Skills</h4>
                    <p>{', '.join(tech_skills[:5]) if tech_skills else 'General technical skills'}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="conversation-bubble">
                    <h4>👔 Experience Level</h4>
                    <p>{'Senior/Leadership' if is_senior else 'Mid-level/Individual Contributor'}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="conversation-bubble">
                    <h4>🎯 Question Focus</h4>
                    <p>Resume-specific & {job_role} relevant</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.session_state.interview_plan = assistant.generate_interview_plan(
                resume_text, job_role, num_questions
            )
            
            # Extract questions from rounds structure
            all_questions = []
            if 'rounds' in st.session_state.interview_plan:
                for round_data in st.session_state.interview_plan['rounds']:
                    for question in round_data['questions']:
                        all_questions.append(question)
            else:
                # Fallback to default questions
                all_questions = [
                    {"question": "Tell me about yourself", "type": "behavioral"},
                    {"question": "What are your technical skills?", "type": "technical"},
                    {"question": "Why do you want this job?", "type": "behavioral"}
                ]
            
            st.session_state.questions = all_questions
            
            st.success(f"✅ Generated {len(all_questions)} personalized questions based on your resume!")
    
    interview_plan = st.session_state.interview_plan
    questions = st.session_state.questions
    
    # Interview flow
    if 'interview_started' not in st.session_state:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Start Continuous Interview", use_container_width=True):
                st.session_state.interview_started = True
                st.session_state.continuous_mode = True
                st.session_state.current_question = 0
                st.session_state.start_time = datetime.now()
                
                # Start continuous conversation
                assistant.speak_conversationally(interview_plan['greeting'], "friendly")
                st.rerun()
        
        with col2:
            if st.button("🎤 Start Manual Interview", use_container_width=True):
                st.session_state.interview_started = True
                st.session_state.continuous_mode = False
                st.session_state.current_question = 0
                st.session_state.start_time = datetime.now()
                
                # Start with greeting
                assistant.speak_conversationally(interview_plan['greeting'], "friendly")
                st.rerun()
    
    # Interview conversation
    if st.session_state.get('interview_started', False):
        current_q = st.session_state.current_question
        
        # Show current question
        if current_q < len(questions):
            question_data = questions[current_q]
            
            # Show progress indicator
            progress = (current_q + 1) / len(questions)
            st.progress(progress, text=f"Question {current_q + 1} of {len(questions)}")
            
            # Enhanced question display with focus area
            focus_area = question_data.get('focus_area', 'General Assessment')
            expected_time = question_data.get('expected_time', '2-3 minutes')
            
            st.markdown(f"""
            <div class="conversation-bubble">
                <h3>❓ Question {current_q + 1}</h3>
                <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <strong>🎯 Focus Area:</strong> {focus_area}<br>
                    <strong>⏱️ Expected Time:</strong> {expected_time}
                </div>
                <p><strong>{question_data['question']}</strong></p>
                {f"<p style='color: #666; font-style: italic;'>💡 Follow-up: {question_data.get('follow_up', '')}</p>" if question_data.get('follow_up') else ''}
            </div>
            """, unsafe_allow_html=True)
            
            # Continuous mode - automatic question asking
            if st.session_state.get('continuous_mode', False):
                st.markdown("""
                <div class="status-bar">
                    <div class="voice-indicator speaking"></div>
                    <strong>🔄 Continuous Mode - AI will ask questions automatically</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # Auto-ask current question if not already asked
                if f'question_asked_{current_q}' not in st.session_state:
                    assistant.speak_conversationally(question_data['question'], "friendly")
                    st.session_state[f'question_asked_{current_q}'] = True
                
                # Answer input options
                st.markdown("### 💬 How would you like to respond?")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    voice_disabled = not SPEECH_RECOGNITION_AVAILABLE
                    if st.button("🎧 Voice Answer", use_container_width=True, disabled=voice_disabled):
                        answer = assistant.listen_for_command()
                        
                        if answer and answer not in ["No response detected", "Could not understand clearly", "Speech recognition not available"]:
                            # Store answer and move to next question
                            st.session_state[f'answer_{current_q}'] = answer
                            st.session_state.current_question += 1
                            st.rerun()
                
                with col2:
                    if st.button("⌨️ Type Answer", use_container_width=True):
                        st.session_state[f'show_text_input_{current_q}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("⏸️ Pause Interview", use_container_width=True):
                        st.session_state.continuous_mode = False
                        st.rerun()
                
                if voice_disabled:
                    st.info("🎤 Voice input not available. Please use text input.")
                
                # Text input for typing answers
                if st.session_state.get(f'show_text_input_{current_q}', False):
                    st.markdown("### ✍️ Type your answer:")
                    typed_answer = st.text_area(
                        "Your answer:",
                        height=150,
                        placeholder="Type your answer here...",
                        key=f"text_answer_{current_q}"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Submit Answer", use_container_width=True):
                            if typed_answer.strip():
                                # Store answer and move to next question
                                st.session_state[f'answer_{current_q}'] = typed_answer.strip()
                                st.session_state.current_question += 1
                                st.rerun()
                            else:
                                st.warning("Please enter an answer before submitting.")
                    
                    with col2:
                        if st.button("❌ Cancel", use_container_width=True):
                            st.session_state[f'show_text_input_{current_q}'] = False
                            st.rerun()
            
            # Manual mode - traditional button interface
            else:
                st.markdown("""
                <div class="status-bar">
                    <div class="voice-indicator thinking"></div>
                    <strong>🎤 Manual Mode - Click buttons to control the interview</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # Question and answer controls
                st.markdown("### 🎤 Question Controls:")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🎤 Ask Question"):
                        assistant.speak_conversationally(question_data['question'], "friendly")
                
                with col2:
                    if st.button("➡️ Next Question"):
                        st.session_state.current_question += 1
                        st.rerun()
                
                # Answer input options
                st.markdown("### 💬 How would you like to respond?")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    voice_disabled = not SPEECH_RECOGNITION_AVAILABLE
                    if st.button("🎧 Voice Answer", disabled=voice_disabled):
                        answer = assistant.listen_for_command()
                        
                        if answer and answer not in ["No response detected", "Could not understand clearly", "Speech recognition not available"]:
                            # Store answer
                            st.session_state[f'answer_{current_q}'] = answer
                            st.success("Answer recorded! Moving to next question...")
                            st.rerun()
                
                with col2:
                    if st.button("⌨️ Type Answer"):
                        st.session_state[f'show_text_input_{current_q}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("🔄 Switch to Continuous"):
                        st.session_state.continuous_mode = True
                        st.rerun()
                
                if voice_disabled:
                    st.info("🎤 Voice input not available. Please use text input.")
                
                # Text input for typing answers
                if st.session_state.get(f'show_text_input_{current_q}', False):
                    st.markdown("### ✍️ Type your answer:")
                    typed_answer = st.text_area(
                        "Your answer:",
                        height=150,
                        placeholder="Type your answer here...",
                        key=f"text_answer_{current_q}"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Submit Answer"):
                            if typed_answer.strip():
                                # Store answer
                                st.session_state[f'answer_{current_q}'] = typed_answer.strip()
                                
                                # Clear text input
                                st.session_state[f'show_text_input_{current_q}'] = False
                                st.success("Answer recorded! Moving to next question...")
                                st.rerun()
                            else:
                                st.warning("Please enter an answer before submitting.")
                    
                    with col2:
                        if st.button("❌ Cancel"):
                            st.session_state[f'show_text_input_{current_q}'] = False
                            st.rerun()
        
        # Interview complete
        else:
            st.markdown(f"""
            <div class="conversation-bubble">
                <h3>🎉 Interview Complete!</h3>
                <p>{interview_plan['closing']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            assistant.speak_conversationally(interview_plan['closing'], "excited")
            
            # Generate final evaluation
            if 'final_evaluation' not in st.session_state:
                # Collect all answers
                all_answers = {}
                for i in range(len(questions)):
                    if f'answer_{i}' in st.session_state:
                        all_answers[i] = st.session_state[f'answer_{i}']
                
                # Generate final evaluation
                final_eval = assistant.generate_final_evaluation(all_answers, interview_plan)
                st.session_state.final_evaluation = final_eval
            
            # Show insights and summary before evaluation
            st.markdown("### 📊 Interview Summary")
            
            # Count answered questions
            answered_count = 0
            for i in range(len(questions)):
                if f'answer_{i}' in st.session_state:
                    answered_count += 1
            
            st.markdown(f"""
            <div class="conversation-bubble">
                <h4>📈 Your Performance Summary</h4>
                <p><strong>Questions Answered:</strong> {answered_count}/{len(questions)}</p>
                <p><strong>Questions Planned:</strong> {len(questions)} questions</p>
                <p><strong>Mode:</strong> {'Continuous' if st.session_state.get('continuous_mode', False) else 'Manual'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show round information if available
            if 'rounds' in interview_plan:
                st.markdown("### 🎯 Interview Rounds Completed")
                for i, round_data in enumerate(interview_plan['rounds']):
                    st.markdown(f"""
                    <div class="conversation-bubble">
                        <h5>Round {i+1}: {round_data['name']}</h5>
                        <p><strong>Duration:</strong> {round_data['duration']}</p>
                        <p><strong>Questions:</strong> {len(round_data['questions'])}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Show evaluation progress
            st.markdown("""
            <div class="conversation-bubble">
                <h3>🔄 Generating Your Evaluation...</h3>
                <p>Please wait while I analyze your responses and prepare your detailed evaluation.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Stay in interview tab - show evaluation here
            st.markdown("### 🎯 Final Evaluation")
            
            # Display final evaluation
            final_eval = st.session_state.final_evaluation
            
            # Decision with clear status
            decision = final_eval.get('decision', 'UNDECIDED')
            overall_score = final_eval.get('overall_score', 0)
            
            if decision == 'SELECTED':
                st.success(f"🎉 **CONGRATULATIONS! YOU ARE SELECTED!**")
                st.markdown(f"**Overall Score:** {overall_score}/100")
                st.markdown("**Status:** ✅ **SELECTED** - You have successfully passed the interview!")
            else:
                st.error(f"❌ **NOT SELECTED**")
                st.markdown(f"**Overall Score:** {overall_score}/100")
                st.markdown("**Status:** ❌ **REJECTED** - You did not meet the requirements for this position.")
            
            # Detailed evaluation
            st.markdown("### 📊 Detailed Evaluation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ✅ Strengths")
                strengths = final_eval.get('strengths', [])
                for strength in strengths:
                    st.markdown(f"• {strength}")
            
            with col2:
                st.markdown("#### ⚠️ Areas for Improvement")
                weaknesses = final_eval.get('weaknesses', [])
                for weakness in weaknesses:
                    st.markdown(f"• {weakness}")
            
            # Reasoning
            st.markdown("#### 🧠 Evaluation Reasoning")
            reasoning = final_eval.get('reasoning', 'No reasoning provided.')
            st.markdown(reasoning)
            
            # Recommendations - Enhanced for rejected candidates
            if decision == 'REJECTED':
                st.markdown("### 💡 How to Improve for Next Time")
                st.markdown("""
                <div class="conversation-bubble" style="background-color: #fff3cd; border-color: #ffeaa7;">
                    <h4>🎯 Focus Areas for Improvement</h4>
                    <p>Based on your interview performance, here are specific areas to work on:</p>
                </div>
                """, unsafe_allow_html=True)
                
                recommendations = final_eval.get('recommendations', [])
                if recommendations:
                    for i, rec in enumerate(recommendations, 1):
                        st.markdown(f"**{i}.** {rec}")
                else:
                    st.markdown("• Practice more technical questions related to your field")
                    st.markdown("• Prepare specific examples of your past work")
                    st.markdown("• Improve your communication and explanation skills")
                    st.markdown("• Research the company and role more thoroughly")
            else:
                st.markdown("### 💡 Recommendations")
                recommendations = final_eval.get('recommendations', [])
                for rec in recommendations:
                    st.markdown(f"• {rec}")
            
            # Next steps
            st.markdown("#### 🚀 Next Steps")
            next_steps = final_eval.get('next_steps', [])
            for step in next_steps:
                st.markdown(f"• {step}")
            
            # Start new interview button
            st.markdown("---")
            if st.button("🔄 Start New Interview", type="primary"):
                # Reset session state
                for key in list(st.session_state.keys()):
                    if key.startswith('answer_') or key.startswith('current_question') or key in ['interview_complete', 'final_evaluation', 'continuous_mode', 'interview_started']:
                        del st.session_state[key]
                st.rerun()
    
    # JavaScript for voice commands
    st.markdown("""
    <script>
    function startConversation() {
        console.log('Starting conversation...');
    }
    
    function nextQuestion() {
        console.log('Next question requested...');
    }
    
    function repeatQuestion() {
        console.log('Repeat question requested...');
    }
    
    function showHelp() {
        console.log('Help requested...');
    }
    
    // Auto-request microphone access
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            console.log('Microphone access granted');
            stream.getTracks().forEach(track => track.stop());
        })
        .catch(err => console.log('Microphone access denied:', err));
    </script>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
