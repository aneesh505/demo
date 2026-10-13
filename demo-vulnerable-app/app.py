from flask import Flask, request, jsonify
import sqlite3
import os
import subprocess
import shlex

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return "Vulnerable App running. Endpoints: /login (POST), /export (GET)"

# VULNERABILITY 1: SQL Injection (CWE-89)
@app.route('/login', methods=['POST'])
def login():
    data = request.json or request.form
    username = data.get('username', '')
    password = data.get('password', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    # UNSECURE: Raw string formatting allows SQL Injection (' OR '1'='1)
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

    try:
        cursor.execute(query)
        user = cursor.fetchone()
        conn.close()
        if user:
            return jsonify({"status": "success", "message": f"Welcome back, {user['username']}!"})
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    except Exception as e:
        conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500

# VULNERABILITY 2: OS Command Injection (CWE-78)
@app.route('/export', methods=['GET'])
def export_report():
    format_type = request.args.get('format', 'pdf')
    filename = request.args.get('filename', 'report')

    # UNSECURE: Passing untrusted parameter directly to shell via os.system or shell=True
    if format_type == 'pdf':
        cmd = f"echo Generating PDF for {filename}"
        os.system(cmd)  # Vulnerable to command injection via filename like 'report; id'
        return jsonify({"status": "success", "message": f"Exported {filename}.pdf"})

    return jsonify({"status": "error", "message": "Unsupported format"}), 400

if __name__ == '__main__':
    # Initialize DB
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'secret123')")
    conn.commit()
    conn.close()

    app.run(host='0.0.0.0', port=5000, debug=True)
