"""
Environment Configuration Loader for PlacementHelper
This script helps load environment variables from .env file
"""

import os
from dotenv import load_dotenv

def load_environment():
    """
    Load environment variables from .env file
    """
    # Load .env file if it exists
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print("✅ Environment variables loaded from .env file")
    else:
        print("⚠️  No .env file found. Using default values.")
    
    # Set default values if not provided
    defaults = {
        'GROQ_API_KEY': '',
        'GOOGLE_API_KEY': '',
        'STREAMLIT_SERVER_PORT': '8501',
        'STREAMLIT_SERVER_ADDRESS': 'localhost',
        'CHROMA_DB_PATH': './chroma_db',
        'CHROMA_COLLECTION_NAME': 'deepseekkk_rag1',
        'GROQ_MODEL': 'llama3-8b-8192',
        'GOOGLE_MODEL': 'gemini-1.5-flash',
        'EMBEDDING_MODEL': 'models/embedding-001',
        'RAG_SIMILARITY_THRESHOLD': '0.7',
        'LOG_LEVEL': 'INFO',
        'DEBUG_MODE': 'false'
    }
    
    for key, default_value in defaults.items():
        if not os.getenv(key):
            os.environ[key] = default_value
    
    return os.environ

def get_api_keys():
    """
    Get API keys from environment variables
    """
    return {
        'groq_api_key': os.getenv('GROQ_API_KEY', ''),
        'google_api_key': os.getenv('GOOGLE_API_KEY', ''),
    }

def check_api_keys():
    """
    Check if API keys are configured
    """
    api_keys = get_api_keys()
    
    print("\n🔑 API Keys Status:")
    print(f"Groq API Key: {'✅ Set' if api_keys['groq_api_key'] else '❌ Not set'}")
    print(f"Google API Key: {'✅ Set' if api_keys['google_api_key'] else '❌ Not set'}")
    
    if not any(api_keys.values()):
        print("\n⚠️  No API keys configured. Some features may not work.")
        print("   Please set up your API keys in the .env file.")
    
    return api_keys

if __name__ == "__main__":
    # Load environment
    env = load_environment()
    
    # Check API keys
    check_api_keys()
    
    print("\n🚀 Environment configuration complete!")
    print("   You can now run the PlacementHelper application.")
