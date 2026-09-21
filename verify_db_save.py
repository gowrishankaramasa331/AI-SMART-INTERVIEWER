import sqlite3

conn = sqlite3.connect('interview_system.db')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT id, question_number, score, status, perfect_answer, improvement FROM interview_questions WHERE session_id = 60').fetchall()
print(f"Total questions found for session 60: {len(rows)}")
for r in rows:
    print(f"Q{r['question_number']}: score={r['score']}, status='{r['status']}', has_perfect={bool(r['perfect_answer'])}, has_improve={bool(r['improvement'])}")
