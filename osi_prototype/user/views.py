# -*- coding: utf-8 -*-
"""User views."""
import json

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from osi_prototype.database import db
from osi_prototype.user.forms import EditForm
from osi_prototype.user.models import Message

blueprint = Blueprint('user', __name__, static_folder='../static')


@blueprint.route('/profile/')
@login_required
def profile():
    """Show profile dashboard page."""
    return render_template('user/profile.html')


@blueprint.route('/profile/edit', methods=('POST',))
@login_required
def edit_profile():
    """Show profile dashboard page."""
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
        print(message)
        return json.dumps({'success': False, 'message': message})


@blueprint.route('/messages/')
@login_required
def messages():
    """Show private messaging page."""
    threads = current_user.threads_involved_in()
    return render_template('user/messages.html', threads=threads)


@blueprint.route('/messages/<other_username>')
@login_required
def message_thread(other_username):
    """Show message thread page."""
    messages = current_user.messages_between(other_username)

    ordered_messages = messages.order_by(Message.created_at.desc()).all()
    rendered = render_template('user/thread.html', messages=ordered_messages)

    # Update as read.
    messages.update({'is_read': True})
    db.session.commit()

    return rendered
