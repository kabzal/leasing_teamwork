from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import current_user, login_required
from sqlalchemy import asc

from app.forms import ProjectForm, TaskForm, ProjectEditForm, TaskEditForm
from app.models import Status, User, Project, Task, Department
from config import Config

main = Blueprint('main', __name__)


app = None


@main.before_request
def before_request():
    global app
    app = current_app


@main.teardown_request
def teardown_request(request):
    global app
    app = None
    return request


"""Основные страницы """


# Главная страница
@login_required
@main.route('/')
def index():
    if current_user.is_authenticated:
        projects = sorted(current_user.projects_participated, key=lambda x: x.id)
        is_admin = (current_user.email == Config.ADMIN_EMAIL)
        if is_admin:
            all_projects = app.db_session.query(Project).order_by(asc(Project.id)).all()
        else:
            all_projects = None
        return render_template("index.html",
                               projects=projects,
                               is_admin=is_admin,
                               all_projects=all_projects)
    else:
        return redirect(url_for("auth.login"))


# Страница проектов
@login_required
@main.route('/create_project', methods=["POST", "GET"])
def create_project():
    is_admin = (current_user.email == Config.ADMIN_EMAIL)
    statuses = app.db_session.query(Status).all()
    employees = app.db_session.query(User).all()

    form = ProjectForm(statuses=statuses, employees=employees)

    if form.validate_on_submit():
        try:
            selected_team = [app.db_session.query(User).filter(User.id==user_id).first() for user_id in form.team.data]
            if current_user not in selected_team:
                selected_team.append(current_user)

            new_project = Project(
                project_name=form.project_name.data,
                project_description=form.project_description.data,
                status_id=form.status.data,
                team=selected_team,
                team_lead_id=current_user.id
            )
            app.db_session.add(new_project)
            app.db_session.commit()
            flash("✔️ Проект успешно создан", "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            app.db_session.rollback()
            flash("⚠️ Ошибка при добавлении проекта в БД", "error")
            print(str(e))

    return render_template('create_project.html',
                           title="Создание нового проекта",
                           form=form,
                           is_admin=is_admin)


@login_required
@main.route('/project/<int:project_id>')
def project(project_id: int):
    project_chosen = app.db_session.query(Project).filter(Project.id == project_id).first()
    is_admin = (current_user.email == Config.ADMIN_EMAIL)

    return render_template('project.html',
                           title=project_chosen.project_name,
                           proj=project_chosen,
                           is_admin=is_admin)


@login_required
@main.route('/project/<int:project_id>/edit', methods=["POST", "GET"])
def edit_project(project_id):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)
    project_chosen = app.db_session.query(Project).filter(Project.id == project_id).first()

    if not project_chosen:
        flash("⚠️ Проект не найден", "error")
        return redirect(url_for("main.index"))

    if current_user.id != project_chosen.team_lead_id and not is_admin:
        flash(f"🔒 Только тимлид {project_chosen.team_lead.username} и администратор сайта могут редактировать этот проект", "error")
        return redirect(url_for('main.project', project_id=project_id))

    statuses = app.db_session.query(Status).all()
    employees = app.db_session.query(User).all()
    form = ProjectEditForm(statuses=statuses, employees=employees)

    if request.method == "GET":
        form.project_name.data = project_chosen.project_name
        form.project_description.data = project_chosen.project_description

    if form.validate_on_submit():
        try:
            project_chosen.project_name = form.project_name.data
            project_chosen.project_description = form.project_description.data

            if form.status.data != '0':
                project_chosen.status_id = form.status.data

            if form.team.data:
                project_chosen.team = [app.db_session.query(User).filter(User.id == user_id).first() for user_id in form.team.data]

            if form.team_lead.data != '0':
                chosen_team_lead = app.db_session.query(User).filter(User.id == form.team_lead.data).first()
                if not chosen_team_lead in project_chosen.team:
                    project_chosen.team.append(chosen_team_lead)
                project_chosen.team_lead_id = form.team_lead.data

            app.db_session.commit()
            flash("✔️ Проект успешно обновлен", "success")
            return redirect(url_for('main.project', project_id=project_id))
        except Exception as e:
            app.db_session.rollback()
            flash(f"⚠️ Ошибка при обновлении проекта: {e}", "error")

    return render_template('edit_project.html',
                           form=form,
                           proj=project_chosen,
                           is_admin=is_admin)


@login_required
@main.route('/project/<int:project_id>/add_task', methods=["POST", "GET"])
def add_task(project_id: int):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)
    project_chosen = app.db_session.query(Project).filter(Project.id == project_id).first()
    statuses = app.db_session.query(Status).all()
    employees = project_chosen.team

    if current_user not in employees and not is_admin:
        flash("🔒 Вы не можете добавлять задачи в данном проекте, так как не являетесь частью команды проекта", "error")
        return redirect(url_for('main.project', project_id=project_id))

    form = TaskForm(statuses=statuses, employees=employees)

    if form.validate_on_submit():
        try:
            new_task = Task(
                task_title=form.task_title.data,
                task_description=form.task_description.data,
                status_id=form.status.data,
                deadline=form.deadline.data,
                project_id=project_id,
                executor_id=form.executor.data
            )
            app.db_session.add(new_task)
            app.db_session.commit()
            flash("✔️ Вы успешно создали задачу", "success")
            return redirect(url_for('main.project', project_id=project_id))
        except Exception as e:
            app.db_session.rollback()
            flash("⚠️ Ошибка при добавлении задачи в БД", "error")
            print(str(e))

    return render_template('add_task.html',
                           title="Создание новой задачи",
                           form=form,
                           is_admin=is_admin,
                           proj_id=project_id)


@login_required
@main.route('/project/<int:project_id>/task/<int:task_id>')
def task(project_id, task_id):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)
    task_chosen = app.db_session.query(Task).filter(Task.id == task_id).first()

    return render_template('task.html',
                           title=f"Задача: {task_chosen.task_title}",
                           task=task_chosen,
                           project_id=project_id,
                           is_admin=is_admin)


@login_required
@main.route('/project/<int:project_id>/task/<int:task_id>/edit', methods=["POST", "GET"])
def edit_task(project_id, task_id):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)
    task_chosen = app.db_session.query(Task).filter(Task.id == task_id).first()

    if not task_chosen:
        flash("⚠️ Задача не найдена", "error")
        return redirect(url_for("main.project", project_id=project_id))

    if task_chosen.project.id != project_id:
        flash("⚠️ Неверный запрос задачи", "error")
        return redirect(url_for("main.index"))

    if current_user.id != task_chosen.project.team_lead_id and current_user.id != task_chosen.executor and not is_admin:
        flash(f"🔒 Редактировать эту задачу могут только тимлид {task_chosen.project.team_lead.username}, исполнитель {task_chosen.executor.username} и администратор сайта", "error")
        return redirect(url_for('main.project', project_id=project_id))

    statuses = app.db_session.query(Status).all()
    employees = task_chosen.project.team
    form = TaskEditForm(statuses=statuses, employees=employees)

    if request.method == "GET":
        form.task_title.data = task_chosen.task_title
        form.task_description.data = task_chosen.task_description
        form.deadline.data = task_chosen.deadline

    if form.validate_on_submit():
        try:
            task_chosen.task_title = form.task_title.data
            task_chosen.task_description = form.task_description.data

            if form.status.data != '0':
                task_chosen.status_id = form.status.data

            if form.deadline.data:
                task_chosen.deadline = form.deadline.data

            if form.executor.data != '0':
                task_chosen.executor_id = form.executor.data

            app.db_session.commit()
            flash("✔️ Задача успешно обновлена", "success")
            return redirect(url_for('main.task', project_id=project_id, task_id=task_id))
        except Exception as e:
            app.db_session.rollback()
            flash(f"⚠️ Ошибка при обновлении задачи: {e}", "error")

    return render_template('edit_task.html',
                           form=form,
                           task=task_chosen,
                           is_admin=is_admin)


@login_required
@main.route('/department/<int:dept_id>')
def department_view(dept_id):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)
    department_chosen = app.db_session.query(Department).filter(Department.id == dept_id).first()
    dept_employees = app.db_session.query(User).filter(User.department_id == dept_id).all()

    return render_template('department.html',
                           dept=department_chosen,
                           dept_employees=dept_employees,
                           is_admin=is_admin)


@login_required
@main.route('/status/<int:status_id>')
def status_view(status_id):
    is_admin = (current_user.email == Config.ADMIN_EMAIL)
    status_chosen = app.db_session.query(Status).filter(Status.id == status_id).first()
    status_projects = app.db_session.query(Project).filter(Project.status_id == status_id).all()

    return render_template('status.html',
                           status=status_chosen,
                           status_projects=status_projects,
                           is_admin=is_admin)
