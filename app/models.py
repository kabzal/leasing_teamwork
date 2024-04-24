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
    avatar = Column(String(100), default='static/default_avatar.png')

    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship('Department', backref='dept', foreign_keys=[department_id])


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

    status_id = Column(Integer, ForeignKey('statuses.id'))
    status = relationship('Status', backref='statused_projects', foreign_keys=[status_id])

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
    deadline = Column(DateTime, nullable=False)

    status_id = Column(Integer, ForeignKey('statuses.id'))
    status = relationship('Status', backref='statused_tasks', foreign_keys=[status_id])

    project_id = Column(Integer, ForeignKey('projects.id'))
    project = relationship('Project', backref='project_tasks', foreign_keys=[project_id])

    executor_id = Column(Integer, ForeignKey('users.id'))
    executor = relationship('User', backref='tasks_assigned', foreign_keys=[executor_id])
