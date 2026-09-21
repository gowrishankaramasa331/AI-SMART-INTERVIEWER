# AI Smart Interview System

An AI-powered interview practice platform that helps students prepare for interviews with instant AI-based feedback.

## Features

- **5 Interview Types**: HR, Technical, Coding, Communication, General
- **3 Difficulty Levels**: Easy, Medium, Hard
- **AI-Generated Questions**: Dynamic questions tailored to your skills
- **Real-time Evaluation**: Instant scoring on 7 performance categories
- **Follow-up Questions**: AI generates contextual follow-up questions
- **Detailed Feedback**: Strengths, weaknesses, improvement areas, study recommendations
- **Progress Tracking**: Track your interview performance over time
- **Voice Input**: Answer using your microphone (Chrome/Edge)
- **Professional Dashboard**: Visualize your scores with charts and progress bars

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **Database**: SQLite
- **AI**: Google Gemini API (with built-in fallback)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser (Chrome or Edge recommended)

### Steps

1. **Open or download** the project folder.

2. **Install dependencies**:
   ```bash
   cd "Create project"
   pip install -r requirements.txt
   ```

3. **(Optional) Set up Gemini API key** for AI-powered question generation:
   ```bash
   # Windows
   set GEMINI_API_KEY=your_api_key_here

   # Mac/Linux
   export GEMINI_API_KEY=your_api_key_here
   ```
   Get a free API key at: https://aistudio.google.com/apikey

   > **Note**: The system works without an API key using a built-in question bank and rule-based evaluation.

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Open in browser**:
   ```
   http://localhost:5000
   ```
   > **Webcam & Microphone Note**: Google Chrome and Microsoft Edge require a **Secure Context** (`http://localhost:5000` or `https://`) for camera and microphone permissions. Please use `http://localhost:5000` to practice with live webcam and voice features.

## Usage

1. **Register** with your name, email, and password
2. **Complete your profile** — add skills, branch, career goal
3. **Select an interview** — choose type, difficulty, and number of questions
4. **Take the interview** — answer questions via typing or voice
5. **Review your results** — see detailed scores and AI feedback
6. **Track progress** — view history and improvement over time

## Project Structure

```
├── app.py              # Flask application
├── config.py           # Configuration
├── database.py         # SQLite database layer
├── ai_engine.py        # AI integration & fallback
├── requirements.txt    # Python dependencies
├── uploads/            # Resume uploads
├── static/
│   ├── css/style.css   # Stylesheet
│   ├── js/             # JavaScript modules
│   └── img/            # Images
└── templates/
    └── index.html      # Single-page app
```

## Customization

Edit `config.py` to change:
- `DEVELOPER_NAME` — Your name
- `COLLEGE_NAME` — Your college
- `PROJECT_YEAR` — Year

## License

This project is developed for educational purposes.

---

**AI Smart Interview System** | Developed for College Project Demonstration
