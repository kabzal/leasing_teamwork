from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from .models import Department


class LoginForm(FlaskForm):
    email = StringField("Email: ", validators=[Email("Некорректный email"), ])
    password = PasswordField("Пароль: ", validators=[
        DataRequired(),
        Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    remember = BooleanField("Запомнить меня", default=False)
    submit = SubmitField("Войти")


class RegisterForm(FlaskForm):
    username = StringField("Имя: ", validators=[Length(min=4, max=100, message="Имя должно быть от 4 до 100 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email"), ])
    password = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=4, max=100, message="Пароль должен быть от 4 до 100 символов")])
    password2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('password', message="Пароли должны совпадать")])
    role = StringField("Должность/роль: ", validators=[Length(min=4, max=100, message="Роль должна быть от 4 до 100 символов")])
    department = SelectField("Отдел: ", validators=[DataRequired()])
    submit = SubmitField("Регистрация")

    def __init__(self, departments=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.department.choices = [(dept.id, dept.department_name) for dept in departments]