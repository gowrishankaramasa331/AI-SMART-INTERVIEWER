"""
AI Smart Interview System — Flask Application
"""
import os
import json
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, session, render_template, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import SECRET_KEY, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH
from database import (
    init_db, create_student, get_student_by_email, get_student_by_id,
    update_student, create_session, get_session, update_session,
    get_student_sessions, add_question, update_question,
    get_session_questions, get_question, get_student_recent_questions
)
from ai_engine import (
    generate_questions, generate_initial_question, generate_adaptive_question,
    evaluate_answer, generate_followup, generate_final_feedback
)

# ── App Setup ─────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload dir exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Disable caching for instant updates in development
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_cache_control_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Initialize DB
init_db()


# ── Helpers ───────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'student_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def sanitize_student(student):
    """Remove sensitive fields before sending to frontend."""
    if not student:
        return None
    s = dict(student)
    s.pop('password_hash', None)
    return s


# ── Page Routes ───────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health():
    """Health check endpoint for UptimeRobot to keep Render alive."""
    return jsonify({'status': 'ok'})


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    student = get_student_by_id(session['student_id'])
    if not student or student.get('resume_filename') != filename:
        return jsonify({'error': 'Unauthorized'}), 403
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ── Auth API ──────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    college = data.get('college', '').strip()

    # Validation
    if not name or len(name) < 2:
        return jsonify({'error': 'Name must be at least 2 characters'}), 400
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email is required'}), 400
    if not password or len(password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400

    # Check existing
    if get_student_by_email(email):
        return jsonify({'error': 'Email already registered'}), 409

    password_hash = generate_password_hash(password)
    student = create_student(name, email, password_hash, college)

    if not student:
        return jsonify({'error': 'Registration failed'}), 500

    session.clear()
    session['student_id'] = student['id']
    return jsonify({'message': 'Registration successful', 'student': sanitize_student(student)}), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    student = get_student_by_email(email)
    if not student or not check_password_hash(student['password_hash'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    session.clear()
    session['student_id'] = student['id']
    return jsonify({'message': 'Login successful', 'student': sanitize_student(student)})


@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


@app.route('/api/session-check', methods=['GET'])
def session_check():
    if 'student_id' in session:
        student = get_student_by_id(session['student_id'])
        if student:
            return jsonify({'authenticated': True, 'student': sanitize_student(student)})
        session.clear()
    return jsonify({'authenticated': False})


# ── Profile API ───────────────────────────────────────────

@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    student = get_student_by_id(session['student_id'])
    return jsonify({'student': sanitize_student(student)})


@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    update_student(session['student_id'], **data)
    student = get_student_by_id(session['student_id'])
    return jsonify({'message': 'Profile updated', 'student': sanitize_student(student)})


@app.route('/api/profile/resume', methods=['POST'])
@login_required
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Allowed file types: PDF, DOC, DOCX'}), 400

    filename = secure_filename(f"resume_{session['student_id']}_{file.filename}")
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    update_student(session['student_id'], resume_filename=filename)

    return jsonify({'message': 'Resume uploaded successfully', 'filename': filename})


# ── Interview API ─────────────────────────────────────────

@app.route('/api/interview/start', methods=['POST'])
@login_required
def start_interview():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    interview_type = data.get('type', 'general').strip().lower()
    difficulty = data.get('difficulty', 'medium').strip().lower()
    try:
        num_questions = int(data.get('num_questions', 5))
    except (ValueError, TypeError):
        num_questions = 5

    valid_types = ['hr', 'technical', 'coding', 'communication', 'general']
    valid_diffs = ['easy', 'medium', 'hard']
    if interview_type not in valid_types:
        return jsonify({'error': f'Invalid interview type. Choose from: {valid_types}'}), 400
    if difficulty not in valid_diffs:
        return jsonify({'error': f'Invalid difficulty. Choose from: {valid_diffs}'}), 400
    num_questions = max(3, min(num_questions, 20))

    # Get student info for personalized questions
    student = get_student_by_id(session['student_id'])
    skills = student.get('skills', '') if student else ''
    career_goal = student.get('career_goal', '') if student else ''

    # Get recently asked questions to avoid repetition
    recent_questions = get_student_recent_questions(session['student_id'], limit=40)

    # Generate initial question (Question 1)
    q1_text = generate_initial_question(
        interview_type=interview_type,
        difficulty=difficulty,
        skills=skills,
        career_goal=career_goal,
        exclude_questions=recent_questions
    )

    # Create session with target question count
    session_id = create_session(session['student_id'], interview_type, difficulty, num_questions)

    # Store Question 1 in DB
    q1_id = add_question(session_id, 1, q1_text)

    return jsonify({
        'session_id': session_id,
        'interview_type': interview_type,
        'difficulty': difficulty,
        'questions': [{'id': q1_id, 'number': 1, 'text': q1_text}],
        'total_questions': num_questions,
    })


@app.route('/api/interview/answer', methods=['POST'])
@login_required
def submit_answer():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    question_id = data.get('question_id')
    answer_text = data.get('answer', '').strip()
    session_id = data.get('session_id')

    if not question_id:
        return jsonify({'error': 'Question ID is required'}), 400

    question = get_question(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404

    # Get session info for context and verify ownership
    interview_session = get_session(session_id or question['session_id'])
    if not interview_session:
        return jsonify({'error': 'Session not found'}), 404
    if interview_session['student_id'] != session['student_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    interview_type = interview_session['interview_type'] if interview_session else 'general'
    difficulty = interview_session['difficulty'] if interview_session else 'medium'
    total_questions = interview_session.get('num_questions') or interview_session.get('total_questions', 5)

    # Evaluate answer
    evaluation = evaluate_answer(question['question_text'], answer_text, interview_type, difficulty)

    # Update question with answer and scores
    update_question(question_id,
        answer_text=answer_text,
        score=evaluation['score'],
        technical_knowledge=evaluation['technical_knowledge'],
        communication=evaluation['communication'],
        confidence=evaluation['confidence'],
        relevance=evaluation['relevance'],
        clarity=evaluation['clarity'],
        problem_solving=evaluation['problem_solving'],
        feedback=evaluation['feedback'],
        status=evaluation.get('status', ''),
        perfect_answer=evaluation.get('perfect_answer', ''),
        improvement=evaluation.get('improvement', ''),
        answered_at=datetime.now().isoformat(),
    )

    # ── Dynamic Adaptive Question Generation ──────────────────
    # The next question (Q2, Q3, etc.) is generated dynamically based on
    # the candidate's previous answer and evaluation.
    next_question_data = None
    current_q_num = question['question_number']

    if current_q_num < total_questions:
        next_num = current_q_num + 1
        existing_qs = get_session_questions(interview_session['id'])
        existing_next = next((q for q in existing_qs if q['question_number'] == next_num), None)

        if existing_next:
            next_question_data = {
                'id': existing_next['id'],
                'number': next_num,
                'text': existing_next['question_text'],
                'is_adaptive': True
            }
        else:
            student = get_student_by_id(session['student_id'])
            skills = student.get('skills', '') if student else ''
            career_goal = student.get('career_goal', '') if student else ''

            next_q_text = generate_adaptive_question(
                prev_question=question['question_text'],
                prev_answer=answer_text,
                evaluation=evaluation,
                interview_type=interview_type,
                difficulty=difficulty,
                skills=skills,
                career_goal=career_goal,
                next_q_num=next_num,
                total_questions=total_questions,
                history=existing_qs
            )

            next_qid = add_question(interview_session['id'], next_num, next_q_text, is_followup=True)
            next_question_data = {
                'id': next_qid,
                'number': next_num,
                'text': next_q_text,
                'is_adaptive': True
            }

    return jsonify({
        'evaluation': evaluation,
        'next_question': next_question_data,
        'followup': None,
    })


@app.route('/api/interview/complete', methods=['POST'])
@login_required
def complete_interview():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'error': 'Session ID is required'}), 400

    interview_session = get_session(session_id)
    if not interview_session:
        return jsonify({'error': 'Session not found'}), 404
    if interview_session['student_id'] != session['student_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    # Get all questions & answers
    questions_data = get_session_questions(session_id)

    # If already completed, return existing results immediately
    if interview_session.get('status') == 'completed':
        def safe_json_list(val):
            try:
                parsed = json.loads(val or '[]')
                return parsed if isinstance(parsed, list) else []
            except:
                return []
        return jsonify({
            'session': dict(interview_session),
            'questions': questions_data,
            'scores': {
                'overall': interview_session.get('overall_score', 0),
                'technical_knowledge': interview_session.get('technical_knowledge', 0),
                'communication': interview_session.get('communication', 0),
                'confidence': interview_session.get('confidence', 0),
                'relevance': interview_session.get('relevance', 0),
                'clarity': interview_session.get('clarity', 0),
                'problem_solving': interview_session.get('problem_solving', 0),
            },
            'feedback': {
                'feedback_summary': interview_session.get('feedback_summary', ''),
                'strengths': safe_json_list(interview_session.get('strengths')),
                'weaknesses': safe_json_list(interview_session.get('weaknesses')),
                'improvements': safe_json_list(interview_session.get('improvements')),
                'recommendations': safe_json_list(interview_session.get('recommendations')),
                'readiness_pct': interview_session.get('readiness_pct', 0),
            },
        })

    # Calculate average scores
    answered = [q for q in questions_data if q.get('answer_text')]
    if not answered:
        overall_score = 0
        technical_knowledge = 0
        communication = 0
        confidence = 0
        relevance = 0
        clarity = 0
        problem_solving = 0
        feedback = {
            'feedback_summary': 'Interview concluded. No answers were submitted in this session.',
            'strengths': ['Attempted interview session'],
            'weaknesses': ['No answers provided'],
            'improvements': ['Practice typing or speaking answers for each question'],
            'recommendations': ['Review the question bank and practice responses'],
            'readiness_pct': 0,
        }
    else:
        avg = lambda key: sum(q.get(key, 0) for q in answered) / len(answered)
        avg_raw_score = avg('score')
        # Normalize 0-10 per-question score to 0-100 for overall session tracking
        overall_score = avg_raw_score * 10 if avg_raw_score <= 10 else avg_raw_score
        technical_knowledge = avg('technical_knowledge') * (10 if avg('technical_knowledge') <= 10 else 1)
        communication = avg('communication') * (10 if avg('communication') <= 10 else 1)
        confidence = avg('confidence') * (10 if avg('confidence') <= 10 else 1)
        relevance = avg('relevance') * (10 if avg('relevance') <= 10 else 1)
        clarity = avg('clarity') * (10 if avg('clarity') <= 10 else 1)
        problem_solving = avg('problem_solving') * (10 if avg('problem_solving') <= 10 else 1)

        # Generate comprehensive feedback
        feedback = generate_final_feedback(
            questions_data,
            interview_session['interview_type'],
            interview_session['difficulty']
        )

    # Update session
    update_session(session_id,
        overall_score=round(overall_score, 1),
        technical_knowledge=round(technical_knowledge, 1),
        communication=round(communication, 1),
        confidence=round(confidence, 1),
        relevance=round(relevance, 1),
        clarity=round(clarity, 1),
        problem_solving=round(problem_solving, 1),
        strengths=json.dumps(feedback.get('strengths', [])),
        weaknesses=json.dumps(feedback.get('weaknesses', [])),
        improvements=json.dumps(feedback.get('improvements', [])),
        recommendations=json.dumps(feedback.get('recommendations', [])),
        feedback_summary=feedback.get('feedback_summary', ''),
        readiness_pct=feedback.get('readiness_pct', 0),
        status='completed',
        completed_at=datetime.now().isoformat(),
    )

    # Return full results
    updated_session = get_session(session_id)

    return jsonify({
        'session': dict(updated_session),
        'questions': questions_data,
        'scores': {
            'overall': round(overall_score, 1),
            'technical_knowledge': round(technical_knowledge, 1),
            'communication': round(communication, 1),
            'confidence': round(confidence, 1),
            'relevance': round(relevance, 1),
            'clarity': round(clarity, 1),
            'problem_solving': round(problem_solving, 1),
        },
        'feedback': feedback,
    })


@app.route('/api/interview/history', methods=['GET'])
@login_required
def interview_history():
    sessions = get_student_sessions(session['student_id'])
    # Only return completed sessions
    completed = [s for s in sessions if s.get('status') == 'completed']
    return jsonify({'sessions': completed})


@app.route('/api/interview/<int:session_id>', methods=['GET'])
@login_required
def interview_detail(session_id):
    interview_session = get_session(session_id)
    if not interview_session:
        return jsonify({'error': 'Session not found'}), 404
    if interview_session['student_id'] != session['student_id']:
        return jsonify({'error': 'Unauthorized'}), 403

    questions = get_session_questions(session_id)

    # Parse JSON fields
    result = dict(interview_session)
    for field in ['strengths', 'weaknesses', 'improvements', 'recommendations']:
        try:
            result[field] = json.loads(result.get(field) or '[]')
        except (json.JSONDecodeError, TypeError):
            result[field] = []

    scores = {
        'overall': interview_session.get('overall_score', 0),
        'technical_knowledge': interview_session.get('technical_knowledge', 0),
        'communication': interview_session.get('communication', 0),
        'confidence': interview_session.get('confidence', 0),
        'relevance': interview_session.get('relevance', 0),
        'clarity': interview_session.get('clarity', 0),
        'problem_solving': interview_session.get('problem_solving', 0),
    }

    feedback = {
        'feedback_summary': interview_session.get('feedback_summary', ''),
        'strengths': result['strengths'],
        'weaknesses': result['weaknesses'],
        'improvements': result['improvements'],
        'recommendations': result['recommendations'],
        'readiness_pct': interview_session.get('readiness_pct', 0),
    }

    return jsonify({
        'session': result,
        'questions': questions,
        'scores': scores,
        'feedback': feedback,
    })


# ── Run ───────────────────────────────────────────────────

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "=" * 55)
    print("   AI Smart Interview System")
    print(f"   http://localhost:{port}")
    print("=" * 55 + "\n")
    app.run(debug=True, host='0.0.0.0', port=port)
