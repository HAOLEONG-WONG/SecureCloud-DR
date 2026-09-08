from flask import Flask, request, render_template_string
import sqlite3
import logging
import json
from datetime import datetime, timezone

app = Flask(__name__)

# Configure structured logging to a dedicated file
logging.basicConfig(
    filename="/home/azureuser/webapp/auth.log",
    level=logging.INFO,
    format="%(message)s"
)
auth_logger = logging.getLogger("auth")

LOGIN_PAGE = """
<h2>SecureCloud-DR Lab Login</h2>
<form method="POST" action="/login">
Username: <input type="text" name="username"><br><br>
Password: <input type="password" name="password"><br><br>
<input type="submit" value="Login">
</form>
<p>{{ message }}</p>
"""

def log_auth_event(username, result, source_ip):
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": "authentication",
        "username": username,
        "result": result,
        "source_ip": source_ip
    }
    auth_logger.info(json.dumps(event))

@app.route("/")
def home():
    return "Hello from SecureCloud-DR Lab! This is Phase 3 running. <a href='/login'>Login</a>"

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        source_ip = request.remote_addr

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        c.execute(query)
        result = c.fetchone()
        conn.close()

        if result:
            message = f"Welcome, {username}! Login successful."
            log_auth_event(username, "SUCCESS", source_ip)
        else:
            message = "Login failed. Invalid credentials."
            log_auth_event(username, "FAILURE", source_ip)

    return render_template_string(LOGIN_PAGE, message=message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)