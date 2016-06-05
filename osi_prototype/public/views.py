# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from osi_prototype.extensions import login_manager
from osi_prototype.public.forms import LoginForm
from osi_prototype.user.forms import RegisterForm
from osi_prototype.user.models import User
from osi_prototype.utils import flash_errors

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


@blueprint.route('/', methods=['GET', 'POST'])
def home():
    """Home page."""
    form = LoginForm(request.form)
    return render_template('public/home.html', form=form)


@blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    """Login."""
    form = LoginForm(request.form)
    # Handle logging in
    if request.method == 'POST':
        if form.validate_on_submit():
            login_user(form.user)
            if request.args.get('next'):
                redirect_url = request.args.get('next')
            elif current_user.user_type == 'parent':
                redirect_url = url_for('user.profile')
            else:
                redirect_url = url_for('user.messages')

            return redirect(redirect_url)
        else:
            flash_errors(form)
    return render_template('public/login.html', form=form)


@blueprint.route('/logout/')
@login_required
def logout():
    """Logout."""
    logout_user()
    return redirect(url_for('public.home'))


@blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """Register new user."""
    form = RegisterForm(request.form, csrf_enabled=False)
    if form.validate_on_submit():
        User.create(first_name=form.firstname.data, last_name=form.lastname.data,
                    username=form.username.data, email=form.email.data, password=form.password.data,
                    user_type=form.usertype.data, active=True,
                    blurb='Case Worker' if (form.usertype.data == 'agent') else 'Parent')

        flash('Thank you for registering. You can now log in.', 'success')
        return redirect(url_for('public.home'))
    else:
        flash_errors(form)
    return render_template('public/register.html', form=form)


@blueprint.route('/about/')
def about():
    """About page."""
    return render_template('public/about.html')


@blueprint.route('/search/')
def search():
    """Show agency search page."""
    return render_template('public/search.html')
