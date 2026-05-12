# app/main.py
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import sqlite3
import time
import os

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "todos.db")

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["endpoint"])

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN DEFAULT 0
            )
        """)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

@app.route("/todos", methods=["GET"])
def get_todos():
    start = time.time()
    search = request.args.get("search", "")
    with get_db() as conn:
        # INTENTIONAL VULNERABILITY: SQL injection via string formatting
        # Bandit will flag this — we'll fix it in Phase 3
        rows = conn.execute(
            f"SELECT * FROM todos WHERE title LIKE '%{search}%'"
        ).fetchall()
    REQUEST_COUNT.labels("GET", "/todos", 200).inc()
    REQUEST_LATENCY.labels("/todos").observe(time.time() - start)
    return jsonify([dict(r) for r in rows])

@app.route("/todos", methods=["POST"])
def create_todo():
    data = request.get_json()
    if not data or "title" not in data:
        return jsonify({"error": "title is required"}), 400
    with get_db() as conn:
        conn.execute("INSERT INTO todos (title) VALUES (?)", (data["title"],))
    REQUEST_COUNT.labels("POST", "/todos", 201).inc()
    return jsonify({"message": "created"}), 201

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    with get_db() as conn:
        conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    REQUEST_COUNT.labels("DELETE", "/todos/<id>", 200).inc()
    return jsonify({"message": "deleted"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)