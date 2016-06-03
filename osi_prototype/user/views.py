# -*- coding: utf-8 -*-
"""User views."""
import io
import json

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from osi_prototype.database import db
from osi_prototype.user.forms import EditForm, MessageForm
from osi_prototype.user.models import Message, User

blueprint = Blueprint('user', __name__, static_folder='../static')


@blueprint.route('/profile/')
@login_required
def profile():
    """Show profile dashboard page."""
    return render_template('user/profile.html',
                           user=current_user)


@blueprint.route('/profile/edit', methods=('POST',))
@login_required
def edit_profile():
    """Show profile dashboard page."""
    print(request.form)
    form = EditForm(request.form)
    if form.validate_on_submit():
        updates = {k: v for k, v in form.data.items()
                   if k in request.form}
        current_user.update(commit=True, **updates)
        return json.dumps({'success': True})
    else:
        errors = list(form.errors.values())
        message = 'server error'
        # Get first error.
        for field_errors in errors:
            for error in field_errors:
                message = error
                break
        return json.dumps({'success': False, 'message': message})


@blueprint.route('/messages/')
@login_required
def messages():
    """Show private messaging page."""
    threads = current_user.threads_involved_in()
    if current_user.user_type == 'parent':
        users = User.query.filter_by(user_type='agent')
    else:
        users = User.query.filter_by(user_type='parent')
    users_by_username = {user.username: user for user in users}
    return render_template('user/threads.html', threads=threads, users=users_by_username)


@blueprint.route('/messages/<to_username>', methods=['GET', 'POST'])
@login_required
def message_thread(to_username):
    """Show message thread page."""
    to_user = User.get_by_username(to_username, show_404=True)

    form = MessageForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        Message.create(from_user=current_user,
                       to_user=to_user,
                       body=form.body.data,
                       is_unread=1)
        flash('Your message has been sent!', 'success')
        form.body.data = ''
    elif request.method == 'POST':
        flash('Your message must contain at least 3 characters.', 'warning')
    messages = current_user.messages_between(to_user)

    ordered_messages = messages.order_by(Message.created_at.desc()).all()
    rendered = render_template('user/messages.html',
                               messages=ordered_messages,
                               to_user=to_user,
                               form=form)

    # Update messages to this user as read.
    messages.filter_by(to_user_id=current_user.id).update({'is_unread': 0})
    db.session.commit()

    return rendered


@blueprint.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload a photo to the upload set."""
    if 'photo' in request.files:
        photo = request.files['photo']
        current_user.set_profile_photo(photo.filename, photo.read())
        flash('Photo saved.', 'success')
    else:
        flash('Please provide a photo!', 'error')
    return redirect(url_for('.profile'))


@blueprint.route('/photo/<username>/<filename>', methods=['GET'])
@login_required
def profile_photo(username, filename):
    """Serve the profile photo for this user."""
    user = User.get_by_username(username, show_404=True)

    if filename == user.profile_photo:
        return send_file(io.BytesIO(user.profile_image))
    else:
        return abort(404)
