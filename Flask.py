import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Transaction, Goal, Subscription, Debt
from datetime import datetime

app = Flask(__name__)

# 🔹 Конфігурація
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = "static/icons/avatars"
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# 🔹 Ініціалізація бази даних та Flask-Login
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ ГОЛОВНА СТОРІНКА
@app.route("/")
def index():
    if current_user.is_authenticated:
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
        return render_template("index.html", transactions=transactions, user=current_user)
    return render_template("index.html", transactions=[], user=None)

# ✅ РЕЄСТРАЦІЯ
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Email вже зареєстрований!", "danger")
            return redirect(url_for("register"))

        new_user = User(email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Акаунт створено! Тепер увійдіть.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ✅ ВХІД
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Вхід виконано!", "success")
            return redirect(url_for("profile"))
        else:
            flash("Невірний email або пароль", "danger")

    return render_template("login.html")

# ✅ ВИХІД
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Ви вийшли з акаунту.", "info")
    return redirect(url_for("login"))

# ✅ ОСОБИСТИЙ КАБІНЕТ
@app.route("/profile")
@login_required
def profile():
    avatar_url = url_for("static", filename=f"icons/avatars/{current_user.avatar}") if current_user.avatar else url_for("static", filename="icons/default.png")
    return render_template("profile.html", user=current_user, avatar_url=avatar_url)

# ✅ ЗМІНА ПАРОЛЮ
@app.route("/change_password", methods=["POST"])
@login_required
def change_password():
    new_password = request.form["new_password"]
    current_user.set_password(new_password)
    db.session.commit()
    flash("Пароль успішно змінено!", "success")
    return redirect(url_for("profile"))