from flask import Blueprint
from .main_views import main
from .auth_views import auth
from .admin_views import admin

main_bl = main
auth_bl = auth
admin_bl = admin
