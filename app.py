from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    is_complete = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Routes
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for('login'))
    tasks = Task.query.filter_by(user_id=session["user_id"]).all()
    return render_template("index.html", tasks=tasks)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for("register"))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("home"))
        flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out successfully!")
    return redirect(url_for("login"))

@app.route("/add", methods=["POST"])
def add_task():
    if "user_id" not in session:
        return redirect(url_for("login"))
    title = request.form["title"]
    task = Task(title=title, user_id=session["user_id"])
    db.session.add(task)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit/<int:task_id>", methods=["POST"])
def edit_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    task = Task.query.get_or_404(task_id)
    task.title = request.form["title"]
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    task = Task.query.get_or_404(task_id)
    task.is_complete = not task.is_complete
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure the database tables are created
    app.run(debug=True)
