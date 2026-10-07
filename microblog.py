import sqlalchemy as sa
import sqlalchemy.orm as so
from app import create_app, db
from app.models import Message, Notification, Post, Task, User

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post,
            'Message': Message, 'Notification': Notification, 'Task': Task}

if __name__ == "__main__":
    app.run()
