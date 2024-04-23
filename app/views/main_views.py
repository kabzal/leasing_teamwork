from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from flask_login import current_user, login_required

from app.forms import ProjectForm
from app.models import Status, User, Project

# Создание "синего принта"
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

mainmenu = [{'title': 'Главная', 'url': '/'}]

"""Основные страницы """
# Главная страница
@login_required
@main.route('/')
def index():
    if current_user.is_authenticated:
        projects = current_user.projects_participated
        return render_template("index.html", projects=projects, menu=mainmenu)
    else:
        return redirect(url_for("auth.login"))


# Страница проектов
@login_required
@main.route('/create_project', methods=["POST", "GET"])
def create_project():
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
                status=form.status.data,
                team=selected_team,
                team_lead_id=current_user.id
            )
            app.db_session.add(new_project)
            app.db_session.commit()
            flash("Вы успешно зарегистрированы", "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            app.db_session.rollback()
            flash("Ошибка при добавлении проекта в БД", "error")
            print(str(e))

    return render_template('create_project.html', title="Создание нового проекта", menu=mainmenu, form=form)  # Возвращаем шаблон

@login_required
@main.route('/project/<int:project_id>')
def project(project_id: int):
    project_chosen = app.db_session.query(Project).filter(Project.id == project_id).first()
    st = app.db_session.query(Status).filter(Status.id == project_chosen.status).first()

    return render_template('project.html', title=project_chosen.project_name, proj=project_chosen, proj_st=st)