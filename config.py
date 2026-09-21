"""
AI Smart Interview System — Configuration
"""
import os

# Flask
SECRET_KEY = os.environ.get('SECRET_KEY', 'ai-smart-interview-secret-key-2026')

# Database
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'interview_system.db')

# Uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

# AI API — Google Gemini
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Branding
DEVELOPER_NAME = "Your Name"
COLLEGE_NAME = "Your College Name"
PROJECT_YEAR = "2026"
