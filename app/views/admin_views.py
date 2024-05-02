from flask import Blueprint, redirect, url_for, render_template, flash, current_app, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import User, Department, Status, Project, Task
from app.forms import LoginForm, RegisterForm, UserEditForm, ObjCreateForm, PasswordChangeForm
from config import Config

admin = Blueprint('admin', __name__)

app = None

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
        flash("🔒 Данный раздел доступен только администратору", "error")
        return redirect(url_for("main.index"))

    if group == 'all':
        objects = False
    elif group in models_dict.keys():
        objects = sorted(app.db_session.query(models_dict[group]).all(), key=lambda x: x.id)
    else:
        flash("⚠️ Данная ссылка недействительна", "error")
        return redirect(url_for("main.index"))

    return render_template('admin/manage_groups.html',
                           group=group,
                           objects=objects,
                           is_admin=is_admin)


@login_required
@admin.route('/create_obj/<string:group>', methods=["POST", "GET"])
def create_obj(group):
    is_admin = current_user.email == Config.ADMIN_EMAIL

    if not is_admin:
        flash("🔒 Данный раздел доступен только администратору", "error")
        return redirect(url_for("main.index"))

    if group in ('departments', 'statuses'):
        form = ObjCreateForm()
        if form.validate_on_submit():
            try:
                new_obj = None
                if group == 'departments':
                    new_obj = models_dict[group](
                        department_name=form.obj_name.data
                    )
                elif group == 'statuses':
                    new_obj = models_dict[group](
                        status_name=form.obj_name.data
                    )
                app.db_session.add(new_obj)
                app.db_session.commit()
                flash("✔️ Объект успешно добавлен", "success")
                return redirect(url_for("admin.manage_groups", group=group))

            except Exception as e:
                flash("⚠️ Ошибка при добавлении в БД", "error")
                print(str(e))
    else:
        flash("⚠️ Данная ссылка не поддерживается", "error")
        return redirect(url_for("admin.manage_groups", group=group))

    return render_template('admin/create_obj.html',
                               form=form,
                               is_admin=is_admin,
                               group=group)


@login_required
@admin.route('/edit_obj/<string:group>/<int:obj_id>', methods=["POST", "GET"])
def edit_obj(group, obj_id):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)

    if not is_admin:
        flash("🔒 Вносить изменения имеет право только администратор", "error")
        return redirect(url_for("admin.manage_groups", group=group))

    if group in ('departments', 'statuses'):
        form = ObjCreateForm()
        model_chosen = models_dict[group]
        obj_chosen = app.db_session.query(model_chosen).filter(model_chosen.id == obj_id).first()
    else:
        flash("⚠️ Страница не найдена", "error")
        return redirect(url_for("admin.manage_groups", group=group))

    if not obj_chosen:
        flash("⚠️ Объект не найден", "error")
        return redirect(url_for("main.index"))

    if request.method == "GET":
        if group == 'departments':
            form.obj_name.data = obj_chosen.department_name
        elif group == 'statuses':
            form.obj_name.data = obj_chosen.status_name

    if form.validate_on_submit():
        try:
            if group == 'departments':
                obj_chosen.department_name = form.obj_name.data
            elif group == 'statuses':
                obj_chosen.status_name = form.obj_name.data
            app.db_session.commit()
            flash("✔️ Объект успешно обновлен", "success")
            return redirect(url_for("admin.manage_groups", group=group))

        except Exception as e:
            app.db_session.rollback()
            flash(f"⚠️ Ошибка при обновлении данных: {e}", "error")

    return render_template('admin/edit_obj.html',
                           form=form,
                           obj=obj_chosen,
                           is_admin=is_admin,
                           group=group)


@login_required
@admin.route('/delete_obj/<string:group>/<int:obj_id>')
def delete_obj(group, obj_id):
    is_admin = current_user.email == Config.ADMIN_EMAIL

    if not is_admin:
        flash("🔒 Данный раздел доступен только администратору", "error")
        return redirect(url_for("main.index"))

    if group in models_dict.keys():
        if group == 'users' and obj_id == current_user.id:
            flash("⚠️ Вы не можете удалить сами себя", "error")
            return redirect(url_for("admin.manage_groups", group='users'))

        try:
            obj_to_delete = app.db_session.query(models_dict[group]).filter(models_dict[group].id == obj_id).first()

            if obj_to_delete is None:
                flash("⚠️ Объект не найден", "error")
                return redirect(url_for("admin.manage_groups", group=group))

            app.db_session.delete(obj_to_delete)
            app.db_session.commit()
            flash("✔️ Объект успешно удален", "error")
            return redirect(url_for("admin.manage_groups", group=group))

        except Exception as e:
            app.db_session.rollback()
            flash(f"⚠️ Ошибка при удалении пользователя: {e}", "error")
            return redirect(url_for("admin.manage_groups", group=group))
    else:
        flash("⚠️ Данная ссылка не поддерживается", "error")
        return redirect(url_for("admin.manage_groups", group=group))


@login_required
@admin.route("/create_user", methods=["POST", "GET"])
def create_user():
    is_admin = (current_user.email == Config.ADMIN_EMAIL)
    if not is_admin:
        flash("🔒 Создавать новых пользователей имеет право только администратор", "error")
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
            new_user_id = app.db_session.query(User).filter(User.email == form.email.data).first().id
            flash("✔️ Пользователь успешно создан", "success")
            return redirect(url_for('auth.profile', user_id=new_user_id))
        except Exception as e:
            flash(f"⚠️ Ошибка при добавлении в БД: {str(e)}", "error")

    return render_template("admin/create_user.html", title="Регистрация", form=form, is_admin=is_admin)


@login_required
@admin.route('/edit_user/<int:user_id>', methods=["POST", "GET"])
def edit_user(user_id: int):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)

    if not is_admin:
        flash("🔒 Вносить изменения в данные о пользователях имеет право только администратор", "error")
        return redirect(url_for("main.index"))

    user_chosen = app.db_session.query(User).filter(User.id == user_id).first()

    if not user_chosen:
        flash("⚠️ Пользователь не найден", "error")
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
            flash("✔️ Информация о пользователе успешно обновлена", "success")
            return redirect(url_for('auth.profile', user_id=user_id))

        except Exception as e:
            app.db_session.rollback()
            flash(f"⚠️ Ошибка при обновлении данных пользователя: {e}", "error")

    return render_template('admin/edit_user.html',
                           form=form,
                           user=user_chosen,
                           is_admin=is_admin)


@login_required
@admin.route('/change-password-for-user/<int:user_id>', methods=["POST", "GET"])
def change_password(user_id: int):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)
    if not is_admin:
        flash("🔒 Вносить изменения в данные о пользователях имеет право только администратор", "error")
        return redirect(url_for("auth.profile", user_id=user_id))

    user_chosen = app.db_session.query(User).filter(User.id == user_id).first()
    if not user_chosen:
        flash("⚠️ Пользователь не найден", "error")
        return redirect(url_for("main.index"))

    form = PasswordChangeForm()

    if form.validate_on_submit():
        try:
            if check_password_hash(user_chosen.password, form.password.data):
                flash("⚠️ Введенный вами пароль совпадает с уже назначенным", "error")
            else:
                hash = generate_password_hash(form.password.data)
                print(form.password.data, form.password2.data)
                user_chosen.password = hash
                app.db_session.commit()
                flash("✔️ Пароль успешно изменен", "success")
                return redirect(url_for('auth.profile', user_id=user_id))

        except Exception as e:
            app.db_session.rollback()
            flash("⚠️ Возникла ошибка при сохранении нового пароля в базу данных", "error")

    return render_template('admin/change_password.html',
                           form=form,
                           user=user_chosen,
                           is_admin=is_admin)



