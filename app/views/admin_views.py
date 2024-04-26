from flask import Blueprint, redirect, url_for, render_template, flash, current_app, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User, Department, Status, Project, Task
from app.forms import LoginForm, RegisterForm, UserEditForm
from config import Config

admin = Blueprint('admin', __name__)

app = None

mainmenu = [{'title': 'Главная', 'url': '/'},
            {'title': 'Выйти из профиля', 'url': '/logout'}]

models_dict = {
    'users': User,
    'departments': Department,
    'statuses': Status,
    'projects': Project,
    'tasks': Task,
}

@admin.before_request
def before_request():
    global app
    app = current_app


@admin.teardown_request
def teardown_request(request):
    global app
    app = None
    return request


@login_required
@admin.route('/manage_groups/<string:group>')
def manage_groups(group):
    is_admin = current_user.email == Config.ADMIN_EMAIL

    if not is_admin:
        flash("Данный раздел доступен только администратору", "error")
        return redirect(url_for("main.index"))

    if group == 'all':
        objects = False
    elif group in models_dict.keys():
        objects = sorted(app.db_session.query(models_dict[group]).all(), key=lambda x: x.id)
    else:
        flash("Данная ссылка недействительна", "error")
        return redirect(url_for("main.index"))

    return render_template('admin/manage_groups.html',
                           group=group,
                           objects=objects,
                           menu=mainmenu,
                           is_admin=is_admin)


@login_required
@admin.route('/delete_obj/<string:group>/<int:obj_id>')
def delete_obj(group, obj_id):
    is_admin = current_user.email == Config.ADMIN_EMAIL

    if not is_admin:
        flash("Данный раздел доступен только администратору", "error")
        return redirect(url_for("main.index"))

    if group in models_dict.keys():
        if group == 'users' and obj_id == current_user.id:
            flash("Вы не можете удалить сами себя", "error")
            return redirect(url_for("admin.manage_groups", group='users'))

        try:
            obj_to_delete = app.db_session.query(models_dict[group]).filter(models_dict[group].id == obj_id).first()

            if obj_to_delete is None:
                flash("Объект не найден", "error")
                return redirect(url_for("admin.manage_groups", group=group))

            app.db_session.delete(obj_to_delete)
            app.db_session.commit()
            flash("Объект успешно удален", "error")
            return redirect(url_for("admin.manage_groups", group=group))

        except Exception as e:
            app.db_session.rollback()
            flash(f"Ошибка при удалении пользователя: {e}", "error")
            return redirect(url_for("admin.manage_groups", group=group))


@login_required
@admin.route("/create_user", methods=["POST", "GET"])
def create_user():
    if current_user.email != Config.ADMIN_EMAIL:
        flash("Создавать новых пользователей имеет право только администратор", "error")
        return redirect(url_for("main.index"))

    departments = app.db_session.query(Department).all()
    form = RegisterForm(departments=departments)
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        try:
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hash,
                role=form.role.data,
                department_id=form.department.data
            )
            app.db_session.add(new_user)
            app.db_session.commit()
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash("Ошибка при добавлении в БД", "error")
            print(str(e))

    return render_template("admin/create_user.html", title="Регистрация", form=form)


@login_required
@admin.route('/edit_user/<int:user_id>', methods=["POST", "GET"])
def edit_user(user_id: int):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)

    if not is_admin:
        flash("Вносить изменения в данные о пользователях имеет право только администратор", "error")
        return redirect(url_for("main.index"))

    user_chosen = app.db_session.query(User).filter(User.id == user_id).first()

    if not user_chosen:
        flash("Пользователь не найден", "error")
        return redirect(url_for("main.index"))

    departments = app.db_session.query(Department).all()
    form = UserEditForm(departments=departments)

    if request.method == "GET":
        form.username.data = user_chosen.username
        form.email.data = user_chosen.email
        form.role.data = user_chosen.role
        form.department.data = user_chosen.department

    if form.validate_on_submit():
        try:
            user_chosen.username = form.username.data
            user_chosen.email = form.email.data
            user_chosen.role = form.role.data

            if form.department.data != '0':
                user_chosen.department_id = form.department.data

            app.db_session.commit()
            flash("Задача успешно обновлена", "success")
            return redirect(url_for('auth.profile', user_id=user_id))

        except Exception as e:
            app.db_session.rollback()
            print(f"Ошибка при обновлении данных пользователя: {e}")
            flash(f"Ошибка при обновлении данных пользователя: {e}", "error")

    return render_template('admin/edit_user.html',
                           form=form,
                           user=user_chosen,
                           menu=mainmenu,
                           is_admin=is_admin)