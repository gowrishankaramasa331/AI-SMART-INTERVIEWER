"""
Automated end-to-end integration test for adaptive interview flow
"""
import requests

BASE_URL = "http://localhost:5000"
session = requests.Session()

def test_flow():
    print("1. Logging in / registering test user...")
    test_user = {
        "email": "student_adaptive_test@example.com",
        "password": "Password123!",
        "name": "Alex Mercer",
        "college": "Tech Institute"
    }

    # Attempt login, if not exists, register
    res = session.post(f"{BASE_URL}/api/login", json={"email": test_user["email"], "password": test_user["password"]})
    if res.status_code != 200:
        res = session.post(f"{BASE_URL}/api/register", json=test_user)
        assert res.status_code in [200, 201], f"Registration failed: {res.text}"
        print("Registered new test user successfully.")
    else:
        print("Logged in existing test user successfully.")

    # Update profile with skills
    session.put(f"{BASE_URL}/api/profile", json={"skills": "React, Node.js, Python, PostgreSQL", "career_goal": "Full Stack Developer"})

    print("\n2. Starting interview (3 questions, technical, medium)...")
    start_payload = {
        "type": "technical",
        "difficulty": "medium",
        "num_questions": 3
    }
    res = session.post(f"{BASE_URL}/api/interview/start", json=start_payload)
    assert res.status_code == 200, f"Start interview failed: {res.text}"
    start_data = res.json()
    session_id = start_data["session_id"]
    questions = start_data["questions"]
    print(f"Session ID: {session_id}")
    print(f"Total Questions configured: {start_data.get('total_questions')}")
    print(f"Initial Question 1: {questions[0]['text']}")
    q1 = questions[0]

    print("\n3. Submitting Answer 1 with specific technologies (React, Node.js, PostgreSQL)...")
    ans1_payload = {
        "session_id": session_id,
        "question_id": q1["id"],
        "answer": "In my previous project, I built a web application using React on the frontend and Node.js with Express on the backend. We used a PostgreSQL database with relational tables, and implemented RESTful API endpoints for user orders."
    }
    res = session.post(f"{BASE_URL}/api/interview/answer", json=ans1_payload)
    assert res.status_code == 200, f"Submit answer 1 failed: {res.text}"
    ans1_data = res.json()
    print(f"Answer 1 Score: {ans1_data['evaluation']['score']}/10 ({ans1_data['evaluation']['status']})")
    
    next_q = ans1_data.get("next_question")
    assert next_q is not None, "Error: next_question was not returned in answer 1 response!"
    print(f"\n===> DYNAMICALLY GENERATED QUESTION 2 (Based on Answer 1):")
    print(f"Number: {next_q['number']}")
    print(f"Text: {next_q['text']}")
    print(f"Adaptive flag: {next_q.get('is_adaptive')}")

    print("\n4. Submitting Answer 2 to Question 2...")
    ans2_payload = {
        "session_id": session_id,
        "question_id": next_q["id"],
        "answer": "To prevent performance bottlenecks and maintain data integrity, we configured database connection pooling, created B-Tree indexes on query foreign keys, and used Docker containers for consistent deployment."
    }
    res = session.post(f"{BASE_URL}/api/interview/answer", json=ans2_payload)
    assert res.status_code == 200, f"Submit answer 2 failed: {res.text}"
    ans2_data = res.json()
    print(f"Answer 2 Score: {ans2_data['evaluation']['score']}/10 ({ans2_data['evaluation']['status']})")
    
    q3 = ans2_data.get("next_question")
    assert q3 is not None, "Error: next_question was not returned in answer 2 response!"
    print(f"\n===> DYNAMICALLY GENERATED QUESTION 3 (Based on Answer 2):")
    print(f"Number: {q3['number']}")
    print(f"Text: {q3['text']}")

    print("\n5. Submitting Answer 3 to Question 3 (Final Question)...")
    ans3_payload = {
        "session_id": session_id,
        "question_id": q3["id"],
        "answer": "We implemented automated health checks, multi-stage Docker builds, and monitored latency with Prometheus and Grafana."
    }
    res = session.post(f"{BASE_URL}/api/interview/answer", json=ans3_payload)
    assert res.status_code == 200, f"Submit answer 3 failed: {res.text}"
    ans3_data = res.json()
    print(f"Answer 3 Score: {ans3_data['evaluation']['score']}/10")
    print(f"Next question after final: {ans3_data.get('next_question')} (expected None because total_questions reached)")

    print("\n6. Completing interview...")
    res = session.post(f"{BASE_URL}/api/interview/complete", json={"session_id": session_id})
    assert res.status_code == 200, f"Complete interview failed: {res.text}"
    comp_data = res.json()
    print(f"Overall Interview Score: {comp_data['scores']['overall']}")
    print(f"Questions answered count: {len(comp_data['questions'])}")
    print(f"Readiness Pct: {comp_data['feedback']['readiness_pct']}%")
    print("\nAll integration checks passed successfully!")

if __name__ == '__main__':
    test_flow()
