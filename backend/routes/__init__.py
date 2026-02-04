from flask import Blueprint
from routes.auth_routes import auth_bp
from routes.task_routes import tasks_bp
from routes.project_routes import projects_bp
from routes.comment_routes import comments_bp
from routes.history_routes import history_bp
from routes.notification_routes import notifications_bp
from routes.report_routes import reports_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(comments_bp, url_prefix="/api/comments")
    app.register_blueprint(history_bp, url_prefix="/api/history")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
