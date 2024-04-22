from flask import Blueprint, render_template, request, redirect, url_for

# Создание "синего принта"
main = Blueprint('main', __name__)

mainmenu = [{'title': 'Главная', 'url': '/'}]

"""Основные страницы """
# Главная страница
@main.route('/')
def index():
    return render_template('index.html', menu=mainmenu)  # Возвращаем шаблон


# Страница проектов
@main.route('/project')
def projects():
    # Логика для получения списка проектов
    return render_template('project.html', menu=mainmenu)  # Возвращаем шаблон
