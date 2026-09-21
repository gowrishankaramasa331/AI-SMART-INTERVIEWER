"""
Gunicorn configuration for Render deployment.
"""
import os

# Bind to the PORT env variable that Render sets, default 10000
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Workers — 2 is good for free tier (512 MB RAM)
workers = 2

# Timeout — generous for AI API calls
timeout = 120

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
