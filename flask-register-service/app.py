import os
import logging
import boto3
from flask import Flask, request, render_template_string
from werkzeug.security import generate_password_hash

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Flask app setup
app = Flask(__name__)

# AWS Configuration
AWS_REGION = os.environ["AWS_REGION"]
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "Users")
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

# Simple HTML registration form
REGISTER_FORM = """
<!DOCTYPE html>
<html>
  <body>
    <h1>Register User</h1>
    <form method="POST" action="/register">
      <label>Username:</label>
      <input type="text" name="username" required/>
      <br/><br/>
      <label>Password:</label>
      <input type="password" name="password" required/>
      <br/><br/>
      <button type="submit">Register</button>
    </form>
  </body>
</html>
"""
@app.route("/")
def home():
    return "Flask App is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)