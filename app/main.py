#!/usr/bin/env python3
"""
PyLingo Pro - Python IDE + Remote Control

Remote code execution is intentionally disabled until an isolated sandbox
runner with resource limits and an authenticated job protocol is available.
"""
import os
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template, request

PORT = 8000
DB_PATH = Path("pylingo.db")

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )"""
    )
    c.execute(
        """CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            starter_code TEXT,
            solution TEXT,
            xp_reward INTEGER
        )"""
    )
    c.execute("SELECT COUNT(*) FROM lessons")
    if c.fetchone()[0] == 0:
        lessons = [
            ("Hello World", "Выведи 'Hello, World!'", "print('Привет мир!')", "print('Hello, World!')", 10),
            ("Переменные", "Создай переменную name = 'Alex'", "name = ''", "name = 'Alex'", 15),
            ("Калькулятор", "Вычисли 2 + 2 * 10", "result = 0", "result = 2 + 2 * 10", 20),
            ("Списки", "Создай список [1,2,3,4,5]", "numbers = []", "numbers = [1, 2, 3, 4, 5]", 25),
            ("Цикл for", "Выведи числа от 1 до 3", "for i in range(1,4):\n    print(i)", "for i in range(1,4):\n    print(i)", 30),
        ]
        c.executemany(
            "INSERT INTO lessons (title, description, starter_code, solution, xp_reward) VALUES (?,?,?,?,?)",
            lessons,
        )
        conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/run", methods=["POST"])
def run_code():
    # Never execute client-supplied Python in the web process.
    return jsonify({
        "error": "Выполнение кода временно отключено до подключения изолированного sandbox.",
        "code": "CODE_EXECUTION_DISABLED",
    }), 410


@app.route("/api/lessons")
def get_lessons():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM lessons")
    lessons = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(lessons)


@app.route("/api/save_progress", methods=["POST"])
def save_progress():
    data = request.get_json(silent=True) or {}
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO users (username, xp) VALUES (?, ?)",
        (data.get("username", "anonymous"), data.get("xp", 0)),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


if __name__ == "__main__":
    init_db()
    print(f"PyLingo Pro запущен: http://127.0.0.1:{PORT}")
    app.run(host="127.0.0.1", port=PORT, debug=False)
