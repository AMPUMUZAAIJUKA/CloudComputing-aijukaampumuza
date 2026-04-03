from flask import Flask, request, jsonify
import psycopg2
import os

app = Flask(__name__)

def get_db():
    conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            course VARCHAR(100) NOT NULL,
            grade VARCHAR(10)
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def home():
    return jsonify({"message": "Railway PaaS App is running!", "status": "ok"})

# CREATE
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (name, course, grade) VALUES (%s, %s, %s) RETURNING id",
        (data['name'], data['course'], data.get('grade', 'N/A'))
    )
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Student added", "id": new_id}), 201

# READ ALL
@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    students = [{"id": r[0], "name": r[1], "course": r[2], "grade": r[3]} for r in rows]
    return jsonify(students)

# READ ONE
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE id = %s", (id,))
    r = cur.fetchone()
    cur.close()
    conn.close()
    if r:
        return jsonify({"id": r[0], "name": r[1], "course": r[2], "grade": r[3]})
    return jsonify({"error": "Student not found"}), 404

# UPDATE
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "UPDATE students SET name=%s, course=%s, grade=%s WHERE id=%s",
        (data['name'], data['course'], data.get('grade', 'N/A'), id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Student updated"})

# DELETE
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Student deleted"})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)