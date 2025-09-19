# 🎤 BBM AI Interview Assistant

A comprehensive AI-powered interview platform that provides realistic interview experiences with voice interaction, resume analysis, and intelligent evaluation.

## 🌟 Features

### 🎯 **Enhanced Interview Experience**
- **PDF/DOCX Resume Upload**: Automatic text extraction and analysis
- **Time-Based Interview Planning**: 15, 30, 45, or 60-minute sessions
- **Automatic Complexity Adjustment**: Questions adapt to interview duration
- **Professional Interview Flow**: Greeting, questions, and closing

### 🎤 **Voice Interaction**
- **Text-to-Speech**: High-quality voice synthesis using Web Speech API
- **Speech Recognition**: Real-time voice input processing
- **Automatic Camera/Microphone Access**: Seamless media device integration
- **Professional Voice Selection**: Optimized for interview scenarios

### 🤖 **AI-Powered Features**
- **Resume Analysis**: Extracts skills, experience, and qualifications
- **Personalized Questions**: Generates relevant questions based on resume
- **Real-time Evaluation**: AI-powered answer assessment
- **Detailed Feedback**: Comprehensive scoring and improvement suggestions

### 📊 **Interview Management**
- **Progress Tracking**: Real-time timer and question counter
- **Session Recording**: Complete interview session logging
- **Performance Analytics**: Detailed scoring and feedback reports
- **Export Options**: Download interview results and evaluations

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Google AI API Key
- Modern web browser with microphone/camera access

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/siv3sh/BBM_AI_interview.git
   cd BBM_AI_interview
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env file with your Google AI API key
   ```

4. **Run the application**
   ```bash
   streamlit run interview_enhanced.py --server.port 8501
   ```

5. **Access the application**
   - Open your browser to `http://localhost:8501`
   - Allow camera and microphone access when prompted

## 📋 Usage Guide

### 1. **Setup Interview**
- Enter your Google AI API key in the sidebar
- Select your desired job role
- Choose interview duration (15-60 minutes)
- Upload your resume (PDF or DOCX format)

### 2. **Start Interview**
- Click "Start Interview" to begin
- Allow camera and microphone access
- Listen to the AI greeting and instructions

### 3. **Answer Questions**
- Click "Ask Question" to hear the question
- Speak your answer clearly
- Click "Listen for Answer" to record your response
- Review AI feedback and scoring

### 4. **Complete Interview**
- Answer all questions in the session
- Listen to closing remarks
- Review your overall performance
- Download detailed evaluation report

## 🛠️ Technical Details

### **Architecture**
- **Frontend**: Streamlit web interface
- **AI Engine**: Google Generative AI (Gemini)
- **Voice Processing**: Web Speech API + SpeechRecognition
- **File Processing**: PDFPlumber + python-docx
- **Text-to-Speech**: pyttsx3 with Web Speech API fallback

### **Key Components**
- `interview_enhanced.py`: Main application with enhanced features
- `requirements.txt`: Python dependencies
- `env_template.txt`: Environment configuration template
- `sample_resume.txt`: Example resume for testing

### **Voice Quality Improvements**
- Web-based TTS for better voice quality
- Automatic voice selection (Samantha, Alex, Victoria)
- Optimized speech rate and pitch settings
- Sentence-by-sentence speaking with natural pauses
- Fallback to local TTS if web TTS fails

### **Speech Recognition Enhancements**
- Longer ambient noise calibration (2 seconds)
- Extended timeout (15 seconds) and phrase limit (30 seconds)
- Better error handling and user feedback
- Improved speech recognition settings

## 📁 Project Structure

```
BBM_AI_interview/
├── interview_enhanced.py      # Main enhanced interview application
├── requirements.txt          # Python dependencies
├── env_template.txt          # Environment variables template
├── sample_resume.txt        # Sample resume for testing
├── README.md                # This file
└── .env                     # Environment variables (create from template)
```

## 🔧 Configuration

### **Environment Variables**
Create a `.env` file with the following variables:
```
GOOGLE_API_KEY=your_google_ai_api_key_here
STREAMLIT_SERVER_PORT=8501
```

### **API Keys**
- **Google AI API**: Required for AI question generation and evaluation
- Get your API key from: https://makersuite.google.com/app/apikey

## 🎯 Interview Features

### **Duration Options**
- **15 minutes**: 3 questions, basic complexity
- **30 minutes**: 5 questions, intermediate complexity  
- **45 minutes**: 6 questions, advanced complexity
- **60 minutes**: 7 questions, expert complexity

### **Question Types**
- Technical skills assessment
- Behavioral questions
- Problem-solving scenarios
- Role-specific challenges
- Resume-based inquiries

### **Evaluation Criteria**
- **Content Quality**: Relevance and depth of answers
- **Communication**: Clarity and structure
- **Technical Accuracy**: Correctness of technical responses
- **Professionalism**: Appropriate language and demeanor

## 🚨 Troubleshooting

### **Common Issues**
1. **Voice not working**: Check microphone permissions and browser compatibility
2. **Camera access denied**: Ensure browser has camera permissions
3. **API errors**: Verify Google AI API key is correct and has sufficient quota
4. **File upload issues**: Ensure PDF/DOCX files are not corrupted

### **Browser Compatibility**
- Chrome/Chromium: Full support
- Firefox: Full support
- Safari: Limited Web Speech API support
- Edge: Full support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Generative AI for powerful language models
- Streamlit for the web framework
- SpeechRecognition library for voice processing
- PDFPlumber for document processing

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Built with ❤️ for BBM AI Interview Platform**