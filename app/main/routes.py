from datetime import datetime, timezone
from urllib.parse import urlsplit
import sqlalchemy as sa
from flask import current_app, flash, g, redirect, render_template, request, url_for
from flask_babel import get_locale
from flask_login import current_user, login_required, login_user, logout_user
from langdetect import detect, LangDetectException
from app import db
from app.models import Message, Notification, Post, User
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, MessageForm, PostForm, SearchForm
from app.translate import translate



@bp.route('/', methods=['GET', 'POST'])

@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
        except LangDetectException:
            language = None
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    query = current_user.following_posts()
    posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Home', user=current_user, form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)



@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = str(get_locale())



@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)





@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).where(Post.user_id == user.id).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, form=form)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    return render_template('user_popup.html', user=user, form=EmptyForm())


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = db.first_or_404(sa.select(User).where(User.username == recipient))
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(author=current_user, recipient=user,
                          body=form.message.data)
        db.session.add(message)
        user.add_notification('unread_message_count', user.unread_message_count())
        db.session.commit()
        flash(_('Your message has been sent.'))
        return redirect(url_for('main.user', username=recipient))
    return render_template('send_message.html', title=_('Send Message'),
                           form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.now(timezone.utc)
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    query = current_user.messages_received.select().order_by(
        Message.timestamp.desc())
    message_page = db.paginate(
        query, page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.messages', page=message_page.next_num) \
        if message_page.has_next else None
    prev_url = url_for('main.messages', page=message_page.prev_num) \
        if message_page.has_prev else None
    return render_template('messages.html', messages=message_page.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    query = current_user.notifications.select().where(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    items = db.session.scalars(query)
    return [{'name': item.name, 'data': item.get_data(),
             'timestamp': item.timestamp} for item in items]


@bp.route('/export_posts')
@login_required
def export_posts():
    if current_user.get_task_in_progress('export_posts'):
        flash(_('An export task is currently in progress'))
    else:
        current_user.launch_task('export_posts', _('Exporting posts...'))
        db.session.commit()
    return redirect(url_for('main.user', username=current_user.username))



@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot unfollow youself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f"You are not following {username}.")
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))



@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))




@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title='Explore', user=current_user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(
        g.search_form.q.data, page, current_app.config['POSTS_PER_PAGE'])
    per_page = current_app.config['POSTS_PER_PAGE']
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * per_page else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', title='Search', posts=posts,
                           next_url=next_url, prev_url=prev_url)



@bp.route('/translate', methods=['POST'])
@login_required
def translate_post():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('post_id'), int):
        return {'error': 'A valid post_id is required.'}, 400

    post = db.session.get(Post, data['post_id'])
    if post is None or not post.language:
        return {'error': 'This post cannot be translated.'}, 404

    source_language = post.language.split('-')[0].lower()
    dest_language = (getattr(g, 'locale', None) or 'en').split('-')[0].lower()
    if source_language == dest_language:
        return {'text': post.body}

    try:
        return {'text': translate(post.body, source_language, dest_language)}
    except RuntimeError as error:
        return {'error': str(error)}, 502


