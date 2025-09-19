#!/usr/bin/env python3
"""
Test script for ATS and Interview modules
"""

import sys
import os

def test_ats_module():
    """Test the ATS module imports and basic functionality"""
    print("🔍 Testing ATS Module...")
    
    try:
        # Test imports
        import streamlit as st
        import pdfplumber
        import docx
        from langchain_groq import ChatGroq
        from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
        from pydantic import BaseModel, Field
        
        print("✅ All ATS imports successful")
        
        # Test basic functionality
        from agenticATS import ResumeAnalysis, KeywordMatch, SkillsAnalysis
        
        # Create a sample analysis
        sample_analysis = ResumeAnalysis(
            score=85,
            keyword_match=KeywordMatch(
                matched_keywords=["Python", "Machine Learning"],
                missing_keywords=["Docker", "Kubernetes"],
                match_percentage=70
            ),
            missing_skills=SkillsAnalysis(
                technical_skills=["Cloud Computing"],
                programming_languages=["Go"],
                libraries_frameworks=["TensorFlow"],
                tools_platforms=["AWS"]
            ),
            soft_skills=["Leadership"],
            suggestions=["Add more cloud experience", "Include leadership examples"]
        )
        
        print("✅ ATS data models working")
        print(f"   Sample score: {sample_analysis.score}")
        print(f"   Matched keywords: {len(sample_analysis.keyword_match.matched_keywords)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ATS module error: {e}")
        return False

def test_interview_module():
    """Test the Interview module imports and basic functionality"""
    print("\n🔍 Testing Interview Module...")
    
    try:
        # Test imports
        import streamlit as st
        import google.generativeai as genai
        import json
        from datetime import datetime
        
        print("✅ All Interview imports successful")
        
        # Test basic functionality
        from interview import InterviewChatbot
        
        print("✅ Interview module loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Interview module error: {e}")
        return False

def test_api_keys():
    """Test if API keys are configured"""
    print("\n🔑 Testing API Keys...")
    
    try:
        from env_config import get_api_keys, check_api_keys
        api_keys = get_api_keys()
        
        groq_status = "✅ Set" if api_keys['groq_api_key'] else "❌ Not set"
        google_status = "✅ Set" if api_keys['google_api_key'] else "❌ Not set"
        
        print(f"Groq API Key: {groq_status}")
        print(f"Google API Key: {google_status}")
        
        return api_keys['groq_api_key'] and api_keys['google_api_key']
        
    except Exception as e:
        print(f"❌ API key test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing PlacementHelper Modules")
    print("=" * 50)
    
    # Test modules
    ats_ok = test_ats_module()
    interview_ok = test_interview_module()
    api_keys_ok = test_api_keys()
    
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"ATS Module: {'✅ PASS' if ats_ok else '❌ FAIL'}")
    print(f"Interview Module: {'✅ PASS' if interview_ok else '❌ FAIL'}")
    print(f"API Keys: {'✅ CONFIGURED' if api_keys_ok else '⚠️  NOT CONFIGURED'}")
    
    if ats_ok and interview_ok:
        print("\n🎉 All modules are working! You can now use the application.")
        print("🌐 Access at: http://localhost:8501")
    else:
        print("\n⚠️  Some modules have issues. Check the errors above.")
    
    return ats_ok and interview_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
