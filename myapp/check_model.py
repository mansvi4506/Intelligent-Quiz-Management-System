import os
import sys
import django

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "first_project.settings")
django.setup()

from django.conf import settings

from myapp.ai import get_ai_client

# Initialize the OpenAI-compatible Groq client
client = get_ai_client()

# List all available models
try:
    models = client.models.list()
    print("Models your key can access:\n")
    for m in models.data:
        print("-", m.id)
except Exception as e:
    print("Error fetching models:", e)
