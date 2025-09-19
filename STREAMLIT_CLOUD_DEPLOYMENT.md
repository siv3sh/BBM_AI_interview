# Streamlit Cloud Deployment Guide

## 🚀 Deploying to Streamlit Cloud

### Prerequisites
1. GitHub repository: https://github.com/siv3sh/BBM_AI_interview.git
2. Streamlit Cloud account: https://share.streamlit.io/

### Deployment Steps

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io/
   - Sign in with your GitHub account

2. **Create New App**
   - Click "New app"
   - Select your repository: `siv3sh/BBM_AI_interview`
   - Choose branch: `main`
   - Main file path: `interview_assistant.py`

3. **Configure Secrets**
   - Go to "Advanced settings"
   - Add secrets in the format:
   ```
   GOOGLE_AI_API_KEY = "your_actual_api_key"
   GROQ_API_KEY = "your_groq_api_key"
   ```

4. **Deploy**
   - Click "Deploy!"
   - Wait for deployment to complete

### Required API Keys

#### Google AI API Key (Required)
- Get from: https://aistudio.google.com/app/apikey
- Used for: Interview question generation and evaluation

#### Groq API Key (Optional - for ATS module)
- Get from: https://console.groq.com/keys
- Used for: Resume optimization

### Features Available in Cloud

✅ **AI Interview Assistant**
- Resume analysis and question generation
- Voice and text input options
- Clear SELECTED/REJECTED feedback
- High-quality TTS (Microsoft Edge TTS - free)

✅ **Resume-Specific Questions**
- Questions based on actual resume content
- Progressive difficulty levels
- Focus areas and expected times

✅ **Professional UI**
- Responsive design
- Progress tracking
- Interview summary

### Limitations in Cloud

❌ **File Upload**
- Resume upload works but files are temporary
- No persistent storage

❌ **Microphone Access**
- Voice input may be limited
- Browser permissions required

❌ **Local TTS**
- Uses web-based TTS (Edge TTS)
- No local audio processing

### Troubleshooting

1. **API Key Issues**
   - Ensure keys are correctly set in secrets
   - Check API key validity

2. **Import Errors**
   - All dependencies are in requirements.txt
   - Streamlit Cloud will install automatically

3. **Performance**
   - First load may be slow due to dependency installation
   - Subsequent loads will be faster

### Environment Variables

The app uses these environment variables:
- `GOOGLE_AI_API_KEY`: Required for AI functionality
- `GROQ_API_KEY`: Optional for ATS features

### Support

For issues:
1. Check Streamlit Cloud logs
2. Verify API keys are correct
3. Ensure all dependencies are installed
4. Check browser console for errors
