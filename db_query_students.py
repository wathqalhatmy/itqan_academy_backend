import sqlite3
import json

db_path = "db.sqlite3"

with open("db_output.txt", "w", encoding="utf-8") as f:
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, name, completed_juz FROM academy_student;")
        students = cursor.fetchall()
        f.write(f"Students Count: {len(students)}\n")
        for s in students:
            sid, name, completed_juz = s
            f.write(f"ID: {sid}, Name: {name}, completed_juz: {completed_juz} (Type: {type(completed_juz)})\n")
        conn.close()
    except Exception as e:
        f.write(f"Error: {e}\n")
