from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, DateField
from wtforms.fields.choices import SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from .models import Department


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("⚠️ Некорректный email"), ])
    password = PasswordField("Пароль: ", validators=[
        DataRequired(),
        Length(min=4, max=100, message="⚠️ Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить меня", default=False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    username = StringField("Имя: ", validators=[Length(min=4, max=100, message="⚠️ Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("⚠️ Некорректный email"), ])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="⚠️ Пароль должен быть от 4 до 100 символов")])
    password2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('password', message="⚠️ Пароли должны совпадать")])
    role = StringField("Должность/роль: ", validators=[Length(min=4, max=100, message="⚠️ Роль должна быть от 4 до 100 символов")])
    department = SelectField("Отдел: ", validators=[DataRequired()])
    submit = SubmitField("Регистрация")

    def __init__(self, departments=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department.choices = [(dept.id, dept.department_name) for dept in departments]


class UserEditForm(FlaskForm):
    username = StringField("Имя: ", validators=[Length(min=4, max=100, message="⚠️ Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("⚠️ Некорректный email"), ])
    role = StringField("Должность/роль: ",
                       validators=[Length(min=4, max=100, message="⚠️ Роль должна быть от 4 до 100 символов")])
    department = SelectField("Отдел: ", validators=[DataRequired()])
    submit = SubmitField("Сохранить изменения")

    def __init__(self, departments=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department.choices = [(0, "Оставить без изменений")] + [(dept.id, dept.department_name) for dept in departments]


class ProjectForm(FlaskForm):
    project_name = StringField("Название проекта: ", validators=[
        DataRequired(),
        Length(min=4, max=100, message="⚠️ Название должно быть от 4 до 100 символов")])
    project_description = TextAreaField("Описание проекта: ")
    status = SelectField("Статус: ", validators=[DataRequired()])
    team = SelectMultipleField("Команда проекта: ")
    submit = SubmitField("Создать проект")

    def __init__(self, statuses=[], employees=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status.choices = [(st.id, st.status_name) for st in statuses]
        self.team.choices = [(employee.id, employee.username) for employee in employees]


class ProjectEditForm(FlaskForm):
    project_name = StringField("Название проекта: ", validators=[
        DataRequired(),
        Length(min=4, max=100, message="⚠️ Название должно быть от 4 до 100 символов")])
    project_description = TextAreaField("Описание проекта: ")
    status = SelectField("Статус: ", validators=[DataRequired()])
    team_lead = SelectField("Тимлид: ", validators=[DataRequired()])
    team = SelectMultipleField("Команда проекта: ")
    submit = SubmitField("Сохранить изменения")

    def __init__(self, statuses=[], employees=[], team=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status.choices = [(0, "Оставить без изменений")] + [(st.id, st.status_name) for st in statuses]
        self.team.choices = [(employee.id, employee.username) for employee in employees]
        self.team_lead.choices = [(0, "Оставить без изменений")] + [(employee.id, employee.username) for employee in employees]


class TaskForm(FlaskForm):
    task_title = StringField("Заголовок: ", validators=[
        DataRequired(),
        Length(min=4, max=200, message="⚠️ Название должно быть от 4 до 100 символов")])
    task_description = TextAreaField("Описание задания: ", validators=[DataRequired()])
    status = SelectField("Статус: ", validators=[DataRequired()])
    deadline = DateField("Срок исполнения: ", validators=[DataRequired()])
    executor = SelectField("Исполнитель: ", validators=[DataRequired()])
    submit = SubmitField("Создать задачу")

    def __init__(self, statuses=[], employees=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status.choices = [(st.id, st.status_name) for st in statuses]
        self.executor.choices = [(employee.id, employee.username) for employee in employees]


class TaskEditForm(FlaskForm):
    task_title = StringField("Заголовок: ", validators=[
        DataRequired(),
        Length(min=4, max=200, message="⚠️ Название должно быть от 4 до 100 символов")])
    task_description = TextAreaField("Описание задания: ", validators=[DataRequired()])
    status = SelectField("Статус: ")
    deadline = DateField("Срок исполнения: ", default=None)
    executor = SelectField("Исполнитель: ")
    submit = SubmitField("Сохранить изменения")

    def __init__(self, statuses=[], employees=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status.choices = [(0, "Оставить без изменений")] + [(st.id, st.status_name) for st in statuses]
        self.executor.choices = [(0, "Оставить без изменений")] + [(employee.id, employee.username) for employee in employees]


class ObjCreateForm(FlaskForm):
    obj_name = StringField("Наименование: ", validators=[
        DataRequired(),
        Length(min=4, max=200, message="⚠️ Название должно быть от 4 до 100 символов")])
    submit = SubmitField("Сохранить")


class PasswordChangeForm(FlaskForm):
    password = PasswordField("Пароль: ",
                             validators=[DataRequired(),
                                         Length(min=4, max=100, message="⚠️ Пароль должен быть от 4 до 100 символов")])
    password2 = PasswordField("Повтор пароля: ",
                              validators=[DataRequired(),
                                          EqualTo('password', message="⚠️ Пароли должны совпадать")])
    submit = SubmitField("Сохранить")