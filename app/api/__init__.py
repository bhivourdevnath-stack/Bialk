from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import users, errors, tokens  # noqa: E402,F401
