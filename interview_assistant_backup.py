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
from gtts import gTTS
import pygame
import io
import edge_tts
import asyncio

# Page configuration
st.set_page_config(
    page_title="AI Interview Assistant - Free TTS",
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
    
    .command-buttons {
        display: flex;
        gap: 10px;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .command-btn {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 14px;
    }
    
    .command-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .status-bar {
        background: rgba(255,255,255,0.1);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .conversation-history {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class ConversationalInterviewAssistant:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize speech recognition and TTS
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Conversation state
        self.conversation_history = []
        self.interview_context = {}
        self.current_mode = "greeting"  # greeting, interview, evaluation, closing
        self.current_question_index = 0
        self.questions = []
        self.start_time = None
        
    def setup_tts(self):
        """Configure text-to-speech engine for conversational feel"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Prefer friendly, conversational voices
            for voice in voices:
                if any(name in voice.name.lower() for name in ['samantha', 'alex', 'victoria', 'karen']):
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            else:
                self.tts_engine.setProperty('voice', voices[0].id)
        
        # Conversational settings
        self.tts_engine.setProperty('rate', 170)  # Natural speaking pace
        self.tts_engine.setProperty('volume', 0.8)
        self.tts_engine.setProperty('pitch', 0.6)  # Friendly pitch
    
    def speak_edge_tts(self, text: str, emotion: str = "friendly"):
        """Use Microsoft Edge TTS (free and high-quality)"""
        try:
            # Display with emotion indicator
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
                <strong>{icon} Assistant (Edge TTS):</strong> {text}
            </div>
            """, unsafe_allow_html=True)
            
            # Use selected voice or default based on emotion
            if hasattr(st.session_state, 'selected_voice'):
                voice = st.session_state.selected_voice
            else:
                # Default voice selection based on emotion
                voice = "en-US-AriaNeural"  # Default friendly voice
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
            
            # Add to conversation history
            self.conversation_history.append({
                "speaker": "assistant",
                "text": text,
                "emotion": emotion,
                "timestamp": datetime.now(),
                "tts_method": "edge_tts"
            })
            
        except Exception as e:
            st.error(f"Edge TTS Error: {e}")
            return self.speak_gtts_streamlit(text, emotion)
    
    def speak_gtts_streamlit(self, text: str, emotion: str = "friendly"):
        """Fallback to gTTS with Streamlit integration"""
        try:
            # Display with emotion indicator
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
                <strong>{icon} Assistant (gTTS):</strong> {text}
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
            
            # Add to conversation history
            self.conversation_history.append({
                "speaker": "assistant",
                "text": text,
                "emotion": emotion,
                "timestamp": datetime.now(),
                "tts_method": "gtts"
            })
            
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
        # Use Edge TTS (free and high-quality) as primary option
        return self.speak_edge_tts(text, emotion)
    
    def start_continuous_conversation(self, interview_plan: Dict[str, Any]):
        """Start a continuous conversation flow"""
        # Greeting
        assistant.speak_conversationally(interview_plan['greeting'], "friendly")
        time.sleep(2)  # Brief pause
        
        # Start asking questions automatically
        for i, question_data in enumerate(interview_plan['questions']):
            # Ask the question
            assistant.speak_conversationally(question_data['question'], "friendly")
            
            # Wait for answer (this would be handled by the UI)
            st.session_state[f'current_question_{i}'] = question_data
            
            # Brief pause before next question
            time.sleep(1)
    
    def process_continuous_answer(self, answer: str, question_index: int):
        """Process answer and automatically move to next question"""
        if question_index < len(st.session_state.questions):
            question_data = st.session_state.questions[question_index]
            
            # Store the answer (no immediate evaluation)
            st.session_state[f'answer_{question_index}'] = answer
            
            # Brief pause then ask next question
            time.sleep(1)
            
            # Move to next question automatically
            if question_index + 1 < len(st.session_state.questions):
                next_question = st.session_state.questions[question_index + 1]
                self.speak_conversationally(next_question['question'], "friendly")
                st.session_state.current_question = question_index + 1
            else:
                # All questions answered - mark as complete
                st.session_state.interview_complete = True
    
    def listen_for_command(self) -> str:
        """Listen for voice commands with conversational context"""
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
            
            # Add to conversation history
            self.conversation_history.append({
                "speaker": "user",
                "text": text,
                "timestamp": datetime.now()
            })
            
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
    
    def process_voice_command(self, command: str) -> str:
        """Process voice commands and return appropriate response"""
        command_lower = command.lower()
        
        # Interview control commands
        if any(word in command_lower for word in ["start", "begin", "ready"]):
            return "start_interview"
        elif any(word in command_lower for word in ["next", "continue", "move on"]):
            return "next_question"
        elif any(word in command_lower for word in ["repeat", "again", "say again"]):
            return "repeat_question"
        elif any(word in command_lower for word in ["pause", "stop", "wait"]):
            return "pause_interview"
        elif any(word in command_lower for word in ["help", "what can you do"]):
            return "show_help"
        elif any(word in command_lower for word in ["time", "how much time"]):
            return "show_time"
        elif any(word in command_lower for word in ["summary", "results", "how did i do"]):
            return "show_summary"
        else:
            return "continue_conversation"
    
    def generate_conversational_response(self, user_input: str, context: str = "") -> str:
        """Generate natural conversational responses using AI"""
        prompt = f"""
        You are a friendly, conversational AI interview assistant. You're having a natural conversation with a candidate.
        
        Context: {context}
        User said: {user_input}
        
        Respond naturally and conversationally, like a helpful assistant (Siri/Alexa style). 
        Keep responses brief, friendly, and encouraging. Use natural speech patterns.
        
        Examples:
        - "Great! Let's move on to the next question."
        - "That's interesting! Can you tell me more about that?"
        - "Perfect! I understand. Let's continue."
        - "No problem! Take your time."
        
        Respond in 1-2 sentences maximum.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return "I understand. Let's continue with the interview."
    
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
        """Generate interview plan based on number of questions"""
        
        # Calculate rounds based on number of questions
        if num_questions <= 5:
            rounds = [{"name": "General Assessment", "duration": f"{num_questions * 2} minutes", "questions": []}]
        elif num_questions <= 10:
            rounds = [
                {"name": "Technical", "duration": f"{num_questions // 2 * 2} minutes", "questions": []},
                {"name": "Behavioral", "duration": f"{(num_questions - num_questions // 2) * 2} minutes", "questions": []}
            ]
        else:
            rounds = [
                {"name": "Technical", "duration": f"{num_questions // 3 * 2} minutes", "questions": []},
                {"name": "Coding", "duration": f"{num_questions // 3 * 2} minutes", "questions": []},
                {"name": "Behavioral", "duration": f"{(num_questions - 2 * (num_questions // 3)) * 2} minutes", "questions": []}
            ]
        
        # Generate questions for each round
        questions_per_round = num_questions // len(rounds)
        remaining_questions = num_questions % len(rounds)
        
        for i, round_data in enumerate(rounds):
            round_questions = questions_per_round
            if i < remaining_questions:
                round_questions += 1
            
            round_questions_list = []
            for j in range(round_questions):
                question_num = sum(len(r.get("questions", [])) for r in rounds[:i]) + j + 1
                round_questions_list.append({
                    "question": f"Question {question_num}: Tell me about your experience with {job_role.lower()}.",
                    "expected_time": "2-3 minutes",
                    "follow_up": f"Can you provide a specific example?"
                })
            
            round_data["questions"] = round_questions_list
        
        return {
            "rounds": rounds,
            "greeting": f"Hello! I'm your AI interview assistant. Let's begin your {num_questions}-question interview.",
            "closing": "Thank you for your time. I'll now evaluate your responses."
        }
        
        Make questions detailed and comprehensive to fill the exact time. Include follow-up questions to extend discussions.
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean JSON
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            interview_plan = json.loads(response_text)
            return interview_plan
            
        except Exception as e:
            st.error(f"Error generating interview plan: {e}")
            return self.get_default_conversational_plan(duration_minutes)
    
    def get_default_conversational_plan(self, duration_minutes: int) -> Dict[str, Any]:
        """Default conversational interview plan with exact timing"""
        # Calculate exact question distribution to fill entire duration
        available_time = duration_minutes - 2  # 2 minutes for greeting/closing
        questions_per_minute = 0.3  # 3 minutes per question average
        total_questions = max(3, int(available_time * questions_per_minute))
        
        if duration_minutes <= 15:
            # Short interview: 1 comprehensive round
            rounds = [
                {
                    "name": "Comprehensive Assessment",
                    "duration": f"{available_time} minutes",
                    "questions": [
                        {"question": "Tell me about yourself - your background, experience, and what brings you here today. Please be detailed about your journey.", "type": "introduction", "expected_time": "4-5 minutes"},
                        {"question": "What are your key strengths and skills? Give specific examples of how you've applied them in real situations.", "type": "skills", "expected_time": "4-5 minutes"},
                        {"question": "Why are you interested in this position? What do you hope to achieve and contribute?", "type": "motivation", "expected_time": "3-4 minutes"},
                        {"question": "Do you have any questions for us about the role, company, or team?", "type": "closing", "expected_time": "2-3 minutes"}
                    ]
                }
            ]
        elif duration_minutes <= 30:
            # Medium interview: 2 rounds (Technical + HR)
            tech_questions = total_questions // 2
            hr_questions = total_questions - tech_questions
            rounds = [
                {
                    "name": "Technical Round",
                    "duration": f"{available_time//2} minutes",
                    "questions": [
                        {"question": "Tell me about your technical background and experience. Walk me through your most relevant projects.", "type": "technical", "expected_time": "5-6 minutes"},
                        {"question": "Describe a challenging technical project you worked on. What problems did you solve and how?", "type": "technical", "expected_time": "5-6 minutes"},
                        {"question": "What are your key technical skills? How do you stay updated with new technologies?", "type": "technical", "expected_time": "4-5 minutes"}
                    ]
                },
                {
                    "name": "HR Round",
                    "duration": f"{available_time//2} minutes",
                    "questions": [
                        {"question": "Why are you interested in this position? What excites you about this opportunity?", "type": "behavioral", "expected_time": "4-5 minutes"},
                        {"question": "How do you handle tight deadlines and pressure? Give me a specific example.", "type": "behavioral", "expected_time": "4-5 minutes"},
                        {"question": "Do you have any questions for us about the role, company culture, or team dynamics?", "type": "closing", "expected_time": "3-4 minutes"}
                    ]
                }
            ]
        else:
            # Long interview: 3 rounds (Technical + Behavioral + HR)
            questions_per_round = total_questions // 3
            remaining_questions = total_questions - (questions_per_round * 2)
            rounds = [
                {
                    "name": "Technical Round",
                    "duration": f"{available_time//3} minutes",
                    "questions": [
                        {"question": "Tell me about your technical background and experience. Walk me through your most relevant projects.", "type": "technical", "expected_time": "5-6 minutes"},
                        {"question": "Describe a challenging technical project you worked on. What problems did you solve and how?", "type": "technical", "expected_time": "5-6 minutes"},
                        {"question": "What are your key technical skills? How do you stay updated with new technologies?", "type": "technical", "expected_time": "4-5 minutes"}
                    ]
                },
                {
                    "name": "Behavioral Round",
                    "duration": f"{available_time//3} minutes",
                    "questions": [
                        {"question": "Tell me about a time you had to learn something new quickly. How did you approach it?", "type": "behavioral", "expected_time": "5-6 minutes"},
                        {"question": "What's your approach to problem-solving? Walk me through your process with an example.", "type": "behavioral", "expected_time": "5-6 minutes"},
                        {"question": "How do you handle tight deadlines and pressure? Give me a specific example.", "type": "behavioral", "expected_time": "4-5 minutes"}
                    ]
                },
                {
                    "name": "HR Round",
                    "duration": f"{available_time//3} minutes",
                    "questions": [
                        {"question": "Why are you interested in this position? What excites you about this opportunity?", "type": "behavioral", "expected_time": "4-5 minutes"},
                        {"question": "What are your career goals? Where do you see yourself in 5 years?", "type": "behavioral", "expected_time": "4-5 minutes"},
                        {"question": "Do you have any questions for us about the role, company culture, or team dynamics?", "type": "closing", "expected_time": "3-4 minutes"}
                    ]
                }
            ]
        
        return {
            "greeting": f"Hello! I'm your AI interview assistant. Let's begin your {duration_minutes}-minute interview.",
            "rounds": rounds,
            "closing": "Thank you for completing the interview. I'll now evaluate your performance."
        }
    
    def evaluate_answer_conversationally(self, question: str, answer: str) -> Dict[str, Any]:
        """Evaluate answers with conversational feedback"""
        prompt = f"""
        Evaluate this interview answer conversationally and provide feedback:
        
        Question: {question}
        Answer: {answer}
        
        Provide encouraging, conversational feedback like a friendly mentor would.
        Return JSON:
        {{
            "score": 8,
            "feedback": "That's a great example! You clearly explained your approach.",
            "strengths": ["Clear communication", "Good example"],
            "suggestions": ["Could add more specific details"],
            "encouragement": "You're doing really well! Keep it up."
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            evaluation = json.loads(response_text)
            return evaluation
            
        except Exception as e:
            return {
                "score": 7,
                "feedback": "Thanks for sharing that!",
                "strengths": ["Good response"],
                "suggestions": ["Keep going"],
                "encouragement": "You're doing great!"
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
    st.markdown("""
    <div class="assistant-container">
        <h1>🤖 AI Interview Assistant</h1>
        <p>Your conversational AI companion for interviews - completely free TTS!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main interface (no tabs - everything in one view)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Setup")
        
        # Google AI API Key (required)
        api_key = st.text_input(
            "Google AI API Key:",
            type="password",
            help="Get your API key from https://aistudio.google.com/app/apikey"
        )
        
        if not api_key:
            st.warning("⚠️ Please enter your Google AI API key")
            return
        
        # Free TTS Options
        st.markdown("### 🎤 Voice Options")
        st.success("🆓 **Microsoft Edge TTS** - Free & High-quality neural voices")
        st.info("💡 **No API keys required!** Using completely free TTS services.")
        
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
        with st.spinner("🤖 Preparing your personalized interview..."):
            resume_text = assistant.extract_text_from_resume(uploaded_file.read(), uploaded_file.name)
            st.session_state.interview_plan = assistant.generate_interview_plan(
                resume_text, job_role, num_questions
            )
            
            # Extract questions from rounds structure
            all_questions = []
            if 'rounds' in st.session_state.interview_plan:
                for round_data in st.session_state.interview_plan['rounds']:
                    for question in round_data['questions']:
                        all_questions.append(question)
            elif 'questions' in st.session_state.interview_plan:
                all_questions = st.session_state.interview_plan['questions']
            else:
                # Fallback to default questions
                all_questions = [
                    {"question": "Tell me about yourself", "type": "behavioral"},
                    {"question": "What are your technical skills?", "type": "technical"},
                    {"question": "Why do you want this job?", "type": "behavioral"}
                ]
            
            st.session_state.questions = all_questions
    
    interview_plan = st.session_state.interview_plan
    questions = st.session_state.questions
    
    # Conversation interface
    st.markdown("### 💬 Conversation")
    
    # Voice command buttons
    st.markdown("""
    <div class="command-buttons">
        <button class="command-btn" onclick="startConversation()">🎤 Start Talking</button>
        <button class="command-btn" onclick="nextQuestion()">➡️ Next Question</button>
        <button class="command-btn" onclick="repeatQuestion()">🔄 Repeat</button>
        <button class="command-btn" onclick="showHelp()">❓ Help</button>
    </div>
    """, unsafe_allow_html=True)
    
    # Conversation history
    if assistant.conversation_history:
        st.markdown("### 📝 Conversation History")
        with st.container():
            for msg in assistant.conversation_history[-5:]:  # Show last 5 messages
                if msg["speaker"] == "assistant":
                    st.markdown(f"""
                    <div class="assistant-bubble">
                        <strong>🤖 Assistant:</strong> {msg["text"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="user-bubble">
                        <strong>👤 You:</strong> {msg["text"]}
                    </div>
                    """, unsafe_allow_html=True)
    
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
        
        # Timer
        if st.session_state.start_time:
            elapsed = datetime.now() - st.session_state.start_time
            remaining = timedelta(minutes=duration_minutes) - elapsed
            
            if remaining.total_seconds() > 0:
                st.markdown(f"""
                <div class="status-bar">
                    ⏱️ <strong>Time Remaining:</strong> {str(remaining).split('.')[0]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("⏰ Time's up! Let's wrap up.")
                return
        
        # Show current question
        if current_q < len(questions):
            question_data = questions[current_q]
            
            # Show progress indicator
            progress = (current_q + 1) / len(questions)
            st.progress(progress, text=f"Question {current_q + 1} of {len(questions)}")
            
            st.markdown(f"""
            <div class="conversation-bubble">
                <h3>❓ Question {current_q + 1}</h3>
                <p><strong>{question_data['question']}</strong></p>
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
                    if st.button("🎧 Voice Answer", use_container_width=True):
                        answer = assistant.listen_for_command()
                        
                        if answer and answer not in ["No response detected", "Could not understand clearly"]:
                            # Process answer and move to next question automatically
                            assistant.process_continuous_answer(answer, current_q)
                            st.rerun()
                
                with col2:
                    if st.button("⌨️ Type Answer", use_container_width=True):
                        st.session_state[f'show_text_input_{current_q}'] = True
                        st.rerun()
                
                with col3:
                    if st.button("⏸️ Pause Interview", use_container_width=True):
                        st.session_state.continuous_mode = False
                        st.rerun()
                
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
                                # Process typed answer and move to next question automatically
                                assistant.process_continuous_answer(typed_answer.strip(), current_q)
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
                    if st.button("🎧 Voice Answer"):
                        answer = assistant.listen_for_command()
                        
                        if answer and answer not in ["No response detected", "Could not understand clearly"]:
                            # Process as conversation
                            command = assistant.process_voice_command(answer)
                            
                            if command == "next_question":
                                st.session_state.current_question += 1
                                st.rerun()
                            elif command == "repeat_question":
                                assistant.speak_conversationally(question_data['question'], "friendly")
                            elif command == "show_help":
                                assistant.speak_conversationally("You can say 'next question', 'repeat', or just answer the question naturally!", "encouraging")
                            else:
                                # Treat as answer (no immediate evaluation)
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
                                # Treat as answer (no immediate evaluation)
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
            
            # Generate final evaluation if not already done
            if 'final_evaluation' not in st.session_state:
                # Collect all answers
                all_answers = {}
                for i in range(len(questions)):
                    if f'answer_{i}' in st.session_state:
                        all_answers[i] = st.session_state[f'answer_{i}']
                
                # Generate final evaluation
                final_eval = assistant.generate_final_evaluation(all_answers, interview_plan)
                st.session_state.final_evaluation = final_eval
            
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
                    if key.startswith('answer_') or key.startswith('current_question') or key in ['interview_complete', 'final_evaluation', 'continuous_mode']:
                        del st.session_state[key]
                st.rerun()
    
    # JavaScript for voice commands
    st.markdown("""
    <script>
    function startConversation() {
        // Trigger voice listening
        console.log('Starting conversation...');
    }
    
    function nextQuestion() {
        // Move to next question
        console.log('Next question requested...');
    }
    
    function repeatQuestion() {
        // Repeat current question
        console.log('Repeat question requested...');
    }
    
    function showHelp() {
        // Show help
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
