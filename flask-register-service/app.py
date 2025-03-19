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

# @app.route("/register", methods=["GET", "POST"])
# def register():
#     if request.method == "GET":
#         return render_template_string(REGISTER_FORM)
    
#     username = request.form.get("username")
#     password = request.form.get("password")
    
#     if not username or not password:
#         logger.warning("Username or password missing.")
#         return "Username and password are required.", 400
    
#     hashed_password = generate_password_hash(password)
    
#     try:
#         table.put_item(
#             Item={
#                 "username": username,
#                 "password": hashed_password  # Store hashed password
#             }
#         )
#         logger.info("User '%s' registered successfully.", username)
#         return f"User '{username}' registered successfully!"
#     except Exception as exc:
#         logger.exception("Error registering user in DynamoDB.")
#         return f"Error registering user: {str(exc)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)