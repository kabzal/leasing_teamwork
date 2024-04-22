from sqlalchemy import Column, Integer, String, ForeignKey, Text, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from flask_login import UserMixin

Base = declarative_base()


# таблица Пользователей
class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(500), unique=True, nullable=False)
    role = Column(String(100), default="Роль не определена")
    department = Column(Integer, ForeignKey('departments.id'))
    avatar = Column(String(100), default='static/default_avatar.png')


class Department(Base):
    __tablename__ = 'departments'
    id = Column(Integer, primary_key=True)
    department_name = Column(String(500), nullable=False)


class Status(Base):
    __tablename__ = 'statuses'
    id = Column(Integer, primary_key=True)
    status_name = Column(String(500), nullable=False)


class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    project_name = Column(String(500), nullable=False)
    project_description = Column(Text, nullable=False)
    status = Column(Integer, ForeignKey('statuses.id'))

    team_lead_id = Column(Integer, ForeignKey('users.id'))
    team_lead = relationship('User', backref='projects_lead', foreign_keys=[team_lead_id])
    team = relationship('User', secondary='project_members', backref='projects_participated')


project_members = Table('project_members', Base.metadata,
                        Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
                        Column('project_id', Integer, ForeignKey('projects.id'), primary_key=True)
                        )


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    task_title = Column(String(200), nullable=False)
    task_description = Column(Text)
    status = Column(Integer, ForeignKey('statuses.id'))
    deadline = Column(DateTime, nullable=False)

    project_id = Column(Integer, ForeignKey('projects.id'))
    executor_id = Column(Integer, ForeignKey('users.id'))
    executor = relationship('User', backref='tasks_assigned', foreign_keys=[executor_id])
