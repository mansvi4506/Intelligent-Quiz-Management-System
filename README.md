# Intelligent Quiz Management System

A Django web application for creating and taking AI-generated quizzes. Users can choose a category, topic, and difficulty, then review results, track quiz history and streaks, earn badges, and compare scores on a leaderboard.

## Features

- User registration, login, and profile editing
- Quizzes generated for selected topics and difficulty levels
- AI-generated answer explanations
- Quiz results, history, and retakes
- User streaks, badges, and leaderboard

## Built with

- Python and Django
- SQLite for local development
- Groq API through its OpenAI-compatible client for quiz generation and explanations

## Getting started

### Requirements

- Python 3.10 or newer
- A Groq API key for AI quiz generation and explanations

### Install and run

1. Clone the repository and enter the project directory:

   ```bash
   git clone https://github.com/YOUR-USERNAME/Intelligent-Quiz-Management-System.git
   cd Intelligent-Quiz-Management-System
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   ```

   Windows PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   macOS or Linux:

   ```bash
   source venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   pip install Django==5.2.6 openai python-dotenv
   ```

4. Create a `.env` file in the project root. Add a new Django secret key and your Groq API key:

   ```env
   DJANGO_SECRET_KEY=replace-with-a-generated-secret
   GROQ_API_KEY=your-groq-api-key
   ```

   Keep `.env` private and never commit real keys. Configure Django to read `DJANGO_SECRET_KEY` from the environment before using it; do not put the key directly in `settings.py`.

5. Create the local database tables and start Django:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

6. Visit <http://127.0.0.1:8000/>.

## Configuration and data

The project uses SQLite for local development. The database file, `.env` files, and uploaded files in `media/` are excluded by `.gitignore`. Each developer creates their own local database by running migrations.

The application expects `GROQ_API_KEY` to be available through the environment. AI-powered quiz generation and explanations need a valid key.

## License

No license has been selected. All rights are reserved by default unless a license is added.
