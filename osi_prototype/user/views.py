# -*- coding: utf-8 -*-
"""User views."""
import json

from flask import Blueprint, render_template, request
from flask_login import current_user, login_required

from osi_prototype.user.forms import EditForm

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


@blueprint.route('/search/')
@login_required
def search():
    """Show agency search page."""
    return render_template('user/profile.html')


@blueprint.route('/inbox/')
@login_required
def inbox():
    """Show private inbox page."""
    return render_template('user/profile.html')
