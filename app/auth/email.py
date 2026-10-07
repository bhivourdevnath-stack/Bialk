from flask import current_app, render_template
from flask_mail import Message
from app import mail
from threading import Thread


def send_password_reset_email(user):
    if not current_app.config.get('MAIL_PASSWORD'):
        current_app.logger.error(
            'Cannot send password reset email: MAIL_PASSWORD is not configured. '
            'Use a Gmail app password, not the normal account password.'
        )
        return
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=current_app.config['MAIL_USERNAME'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt', user=user, token=token),
               html_body=render_template('email/reset_password.html', user=user, token=token))

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception:
            current_app.logger.exception(
                'Could not send password reset email through %s:%s',
                current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']
            )


def send_email(subject, sender, recipients, text_body, html_body,
               attachments=None, sync=False):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if attachments:
        for attachment in attachments:
            msg.attach(*attachment)
    if sync:
        mail.send(msg)
    else:
        Thread(target=send_async_email,
               args=(current_app._get_current_object(), msg)).start()


