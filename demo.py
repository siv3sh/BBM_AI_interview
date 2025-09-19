#!/usr/bin/env python3
"""
Demo script showing ATS and Interview module functionality
"""

import os
import sys

def demo_ats_functionality():
    """Demonstrate ATS functionality"""
    print("🤖 ATS Resume Optimizer Demo")
    print("=" * 40)
    
    # Read sample resume
    try:
        with open('sample_resume.txt', 'r') as f:
            resume_text = f.read()
        print("✅ Sample resume loaded")
        print(f"   Resume length: {len(resume_text)} characters")
        
        # Simulate ATS analysis
        print("\n📊 ATS Analysis Results:")
        print("   Overall Score: 85/100")
        print("   ✅ Strong technical skills section")
        print("   ✅ Good experience progression")
        print("   ✅ Relevant certifications")
        print("   ⚠️  Could add more quantifiable achievements")
        print("   ⚠️  Missing specific project metrics")
        
        # Keyword analysis
        print("\n🔍 Keyword Analysis:")
        print("   Matched Keywords: Python, JavaScript, AWS, Docker, React")
        print("   Missing Keywords: Agile, Scrum, CI/CD, Microservices")
        print("   Match Percentage: 75%")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_interview_functionality():
    """Demonstrate Interview functionality"""
    print("\n💬 AI Interview Assistant Demo")
    print("=" * 40)
    
    # Simulate interview questions
    print("🎯 Sample Interview Questions:")
    print("   1. Tell me about your experience with microservices architecture.")
    print("   2. How do you handle debugging in a production environment?")
    print("   3. Describe a challenging project you led and how you overcame obstacles.")
    print("   4. What's your approach to code review and team collaboration?")
    print("   5. How do you stay updated with new technologies?")
    
    # Simulate AI evaluation
    print("\n🤖 AI Evaluation:")
    print("   Overall Score: 8.5/10")
    print("   Strengths:")
    print("   ✅ Clear communication")
    print("   ✅ Technical depth")
    print("   ✅ Problem-solving approach")
    print("   Areas for Improvement:")
    print("   ⚠️  Add more specific examples")
    print("   ⚠️  Quantify achievements")
    
    return True

def show_usage_instructions():
    """Show how to use the modules"""
    print("\n📋 How to Use the Modules")
    print("=" * 40)
    
    print("🌐 Access the application at: http://localhost:8501")
    print("\n🤖 ATS Resume Optimizer:")
    print("   1. Click 'Launch Resume Optimizer'")
    print("   2. Upload your resume (PDF/DOCX)")
    print("   3. Get ATS compatibility score")
    print("   4. Review improvement suggestions")
    
    print("\n💬 AI Interview Assistant:")
    print("   1. Click 'Launch Interview Assistant'")
    print("   2. Enter your Google AI API key")
    print("   3. Upload your resume")
    print("   4. Specify job role")
    print("   5. Practice interview questions")
    print("   6. Get AI evaluation and feedback")
    
    print("\n🔑 API Keys Needed:")
    print("   • Groq API Key: https://console.groq.com/keys")
    print("   • Google AI API Key: https://aistudio.google.com/app/apikey")

def main():
    """Run the demo"""
    print("🚀 PlacementHelper ATS & Interview Demo")
    print("=" * 50)
    
    # Run demos
    ats_ok = demo_ats_functionality()
    interview_ok = demo_interview_functionality()
    
    # Show usage instructions
    show_usage_instructions()
    
    print("\n🎉 Demo Complete!")
    print("Both ATS and Interview modules are ready to use.")
    
    return ats_ok and interview_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
