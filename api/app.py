from flask import Flask, jsonify, request
import os
import psycopg2

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )

@app.route("/")
def home():
    return {
        "message": "Zero Trust API Running",
        "status": "secure"
    }

@app.route("/status")
def status():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, message, created_at FROM lab_status ORDER BY id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {"id": row[0], "message": row[1], "created_at": str(row[2])}
        for row in rows
    ])

@app.route("/add", methods=["POST"])
def add_status():
    api_key = request.headers.get("X-API-Key")
    if api_key != os.environ.get("API_KEY"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json()
    message = data.get("message", "No message provided")

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO lab_status (message) VALUES (%s) RETURNING id, message, created_at;",
        (message,)
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "id": row[0],
        "message": row[1],
        "created_at": str(row[2])
    }), 201

app.run(host="0.0.0.0", port=5000)
