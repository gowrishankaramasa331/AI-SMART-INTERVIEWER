"""
Test script for verifying adaptive question generation and question bank expansion
"""
import re
import random

# Sample concept map
TOPIC_QUESTIONS = {
    'react': [
        "You discussed using React. How did you handle component state and side effects, and why did you choose that approach over Context API or Redux?",
        "Following up on your experience with React: how do you prevent unnecessary re-renders and optimize virtual DOM performance in high-frequency update scenarios?",
        "When building React applications, what is your approach to testing components and mocking API dependencies?",
        "How do you handle client-side routing, code-splitting, and lazy loading in React applications to maintain fast initial page loads?",
    ],
    'node': [
        "You touched on Node.js. How does the asynchronous event loop handle heavy I/O operations without blocking the single execution thread?",
        "In Node.js, how do you handle unhandled Promise rejections and rate-limiting to protect your server from being overwhelmed?",
        "How do you structure your backend architecture (controllers, services, repositories) in Node.js to keep business logic clean and maintainable?",
    ],
    'python': [
        "Since you mentioned Python, how do you handle concurrency or CPU-bound tasks given Python's Global Interpreter Lock (GIL)?",
        "In Python, how do you leverage generators or list comprehensions to optimize memory consumption when processing large datasets?",
        "How do you structure exception handling, custom errors, and logging in Python backend applications for production reliability?",
    ],
    'sql': [
        "You highlighted relational databases and SQL. How would you analyze an EXPLAIN query plan to identify and fix slow query bottlenecks in production?",
        "Explain how indexing (such as B-Tree indexes) speeds up search queries and what trade-offs it introduces during write-heavy workloads.",
        "How do ACID properties protect data integrity during concurrent transactions, and what database isolation level do you typically configure?",
    ],
    'api': [
        "Following up on your API discussion: what HTTP status codes and payload structures do you use to handle client errors and validation gracefully?",
        "How do you design a REST API to be idempotent, especially for payment or order processing endpoints?",
        "When designing web APIs, how do you handle authentication, authorization, and token refreshing using JWT or OAuth2?",
    ],
    'docker': [
        "You mentioned Docker and containers. How do multi-stage Docker builds help minimize container image size and improve security in production?",
        "How do you manage environment variables, configuration secrets, and container orchestration across environments?",
    ],
    'git': [
        "You touched on Git. What branching strategy do you prefer when collaborating with multiple engineers, and how do you safely resolve tricky merge conflicts?",
        "What is the difference between git merge and git rebase, and in what scenarios would you avoid rebasing shared branches?",
    ],
    'oop': [
        "Building on your explanation of Object-Oriented Programming: how do you balance inheritance with composition, and can you describe a time where composition was a better choice?",
        "Can you explain the Single Responsibility Principle or Open/Closed Principle from SOLID with a concrete example from code you've written?",
    ],
    'team': [
        "You mentioned collaborating in a team. Can you describe a specific time you had a strong technical disagreement with a colleague, and how you reached a consensus?",
        "How do you give constructive feedback during code reviews without discouraging your team members?",
    ],
    'project': [
        "In the project you just described, what was the single biggest technical obstacle or bottleneck you ran into, and how did you diagnose and overcome it?",
        "If you were asked to rebuild that project from scratch today, what technical decisions or architectural choices would you make differently?",
        "What trade-offs did you make in that project between delivering features quickly and writing clean, scalable code?",
    ]
}

def test_adaptive():
    samples = [
        ("Tell me about a project you worked on.", "I built a web application using React and Node.js for an online store with payment processing.", 8),
        ("What is your experience with databases?", "I have used PostgreSQL and written SQL queries for managing user data and products.", 7),
        ("What are your strengths?", "I work well in a team and communicate effectively with colleagues during sprint planning.", 8),
        ("What is a stack?", "Stack is lifo.", 4),
    ]
    print("Testing sample answers...")
    for q, a, score in samples:
        print(f"\nQ: {q}")
        print(f"A: {a} (Score: {score})")
        # Find matching topics
        a_lower = a.lower()
        matched = []
        for topic, qlist in TOPIC_QUESTIONS.items():
            if re.search(r'\b' + re.escape(topic) + r'\b', a_lower):
                matched.append(topic)
        print(f"Detected topics: {matched}")
        if matched:
            print(f"Generated Q2: {TOPIC_QUESTIONS[matched[0]][0]}")
        else:
            print(f"Generated Q2: Following up on your answer regarding your experience, can you elaborate further on...")

if __name__ == '__main__':
    test_adaptive()
