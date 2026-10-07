import json
import sys
import time
from datetime import timezone

import sqlalchemy as sa
from flask import render_template
from rq import get_current_job

from app import create_app, db
from app.auth.email import send_email
from app.models import Post, Task, User

app = create_app()
app.app_context().push()


def _set_task_progress(progress):
    job = get_current_job()
    if job is None:
        return
    job.meta['progress'] = progress
    job.save_meta()
    task = db.session.get(Task, job.get_id())
    if task is None:
        return
    task.user.add_notification(
        'task_progress', {'task_id': job.get_id(), 'progress': progress})
    if progress >= 100:
        task.complete = True
    db.session.commit()


def export_posts(user_id):
    try:
        user = db.session.get(User, user_id)
        if user is None:
            raise ValueError(f'User {user_id} was not found')
        _set_task_progress(0)
        data = []
        total_posts = db.session.scalar(sa.select(sa.func.count()).select_from(
            user.posts.select().subquery()))
        for i, post in enumerate(db.session.scalars(
                user.posts.select().order_by(Post.timestamp.asc())), start=1):
            timestamp = post.timestamp
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            data.append({'body': post.body,
                         'timestamp': timestamp.isoformat().replace('+00:00', 'Z')})
            time.sleep(5)
            _set_task_progress(100 * i // total_posts)
        send_email(
            '[Microblog] Your blog posts',
            sender=app.config['ADMINS'][0], recipients=[user.email],
            text_body=render_template('email/export_posts.txt', user=user),
            html_body=render_template('email/export_posts.html', user=user),
            attachments=[('posts.json', 'application/json',
                          json.dumps({'posts': data}, indent=4))],
            sync=True)
    except Exception:
        app.logger.error('Unhandled exception in export_posts',
                         exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)
