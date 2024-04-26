from flask import Blueprint, redirect, url_for, render_template, flash, current_app, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User, Department
from app.forms import LoginForm, RegisterForm
from config import Config

auth = Blueprint('auth', __name__)

app = None

mainmenu = [{'title': 'Главная', 'url': '/'},
            {'title': 'Выйти из профиля', 'url': '/logout'}]

@auth.before_request
def before_request():
    global app
    app = current_app


@auth.teardown_request
def teardown_request(request):
    global app
    app = None
    return request


@auth.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.profile', user_id=current_user.id))

    form = LoginForm()
    if form.validate_on_submit():
        user = app.db_session.query(User).filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            rm = form.remember.data
            login_user(user, remember=rm)
            return redirect(request.args.get("next") or url_for("auth.profile", user_id=user.id))

        flash("Неверно введен логин или пароль", "error")
    return render_template('auth/login.html', title="Авторизация", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('auth.login'))


@auth.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    is_admin = (current_user.username == Config.ADMIN_EMAIL)
    user_chosen = app.db_session.query(User).filter(User.id == user_id).first()
    return render_template('auth/user_profile.html',
                           title=f"Профиль пользователя {user_chosen.username}",
                           user=user_chosen,
                           menu=mainmenu,
                           is_admin=is_admin)


