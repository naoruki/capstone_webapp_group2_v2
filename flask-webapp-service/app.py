import os
import logging
import boto3
from flask import Flask, request, render_template_string, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

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
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE")

if not DYNAMODB_TABLE:
    raise ValueError("Error: DYNAMODB_TABLE environment variable is not set!")


dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(DYNAMODB_TABLE)

# Bootstrap-styled Register Form
REGISTER_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Register</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

</head>
<body class="bg-light">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card mt-5">
                    <div class="card-header text-center">
                        <h3>Register</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="/register">
                            <div class="mb-3">
                                <label class="form-label">Username:</label>
                                <input type="text" name="username" class="form-control" required/>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password:</label>
                                <input type="password" name="password" class="form-control" required/>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Register</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

# Bootstrap-styled Login Form
LOGIN_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Login</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

</head>
<body class="bg-light">
    <div class="container">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card mt-5">
                    <div class="card-header text-center">
                        <h3>Login</h3>
                    </div>
                    <div class="card-body">
                        <form method="POST" action="/login">
                            <div class="mb-3">
                                <label class="form-label">Username:</label>
                                <input type="text" name="username" class="form-control" required/>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password:</label>
                                <input type="password" name="password" class="form-control" required/>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Login</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template_string(REGISTER_FORM)
    
    username = request.form.get("username")
    password = request.form.get("password")
    
    if not username or not password:
        logger.warning("Username or password missing.")
        return "Username and password are required.", 400
    
    hashed_password = generate_password_hash(password)
    
    try:
        table.put_item(
            Item={
                "username": username,
                "password": hashed_password  # Store hashed password
            }
        )
        logger.info("User '%s' registered successfully.", username)
        return redirect(url_for("regSuccess", username=username))
    except Exception as exc:
        logger.exception("Error registering user in DynamoDB.")
        return f"Error registering user: {str(exc)}", 500

@app.route("/regSuccess")
def regSuccess():
    username = request.args.get("username", "User")
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Success</title>
        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    </head>
    <body>
        <script>
            Swal.fire({
                title: "Success!",
                text: "User '{{ username | safe }}' registered successfully!",
                icon: "success",
                timer: 5000,  // Auto-close after 5 seconds
                showConfirmButton: false
            }).then(() => {
                window.location.href = "/login"; // Redirect to login page
            });
        </script>
    </body>
    </html>
    """, username=username)



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template_string(LOGIN_FORM)

    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    # Retrieve user from DynamoDB
    try:
        response = table.get_item(Key={"username": username})
        user = response.get("Item")

        if not user or not check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid credentials"}), 401

        # return jsonify({"message": "Login successful"}), 200
        return redirect(url_for("loginSuccess", username=username))
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return jsonify({"error": "Could not log in"}), 500

@app.route("/loginSuccess")
def loginSuccess():
    username = request.args.get("username", "User")
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Success</title>
        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
    </head>
    <body>
        <script>
            Swal.fire({
                title: "Success!",
                text: "User '{{ username | safe }}' login successfully!",
                icon: "success",
                timer: 5000,  // Auto-close after 5 seconds
                showConfirmButton: false
            }).then(() => {
                window.location.href = "/login"; // Redirect to login page
            });
        </script>
    </body>
    </html>
    """, username=username)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
    
