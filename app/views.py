from flask import Blueprint, render_template, request, redirect, url_for

# Создание "синего принта"
main = Blueprint('main', __name__)

mainmenu = {'title': 'Главная', 'url': '/'}


# Главная страница
@main.route('/')
def index():
    return render_template('index.html', menu=mainmenu)  # Возвращаем шаблон


# Страница профиля пользователя
@main.route('/profile')
def profile():
    # Логика для получения информации о пользователе
    return render_template('user_profile.html', menu=mainmenu)  # Возвращаем шаблон


# Страница проектов
@main.route('/projects')
def projects():
    # Логика для получения списка проектов
    return render_template('projects.html', menu=mainmenu)  # Возвращаем шаблон
