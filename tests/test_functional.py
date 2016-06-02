# -*- coding: utf-8 -*-
"""Functional tests using WebTest.

See: http://webtest.readthedocs.org/
"""
from flask import url_for

from osi_prototype.user.models import Message, User

from .factories import UserFactory


class TestLoggingIn:
    """Login."""

    def test_can_log_in_returns_200(self, user, testapp):
        """Login successful."""
        # Goes to homepage
        res = testapp.get(url_for('public.login'))
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['username'] = user.username
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200

    def test_sees_alert_on_log_out(self, user, testapp):
        """Show alert on logout."""
        res = testapp.get(url_for('public.login'))
        # Fills out login form in navbar
        form = res.forms['loginForm']
        form['username'] = user.username
        form['password'] = 'myprecious'
        # Submits
        res = form.submit().follow()
        res = testapp.get(url_for('public.logout')).follow()
        # no option to log out on home page
        assert 'Logout' not in res

    def test_sees_error_message_if_password_is_incorrect(self, user, testapp):
        """Show error if password is incorrect."""
        # Goes to homepage
        res = testapp.get(url_for('public.login'))
        # Fills out login form, password incorrect
        form = res.forms['loginForm']
        form['username'] = user.username
        form['password'] = 'wrong'
        # Submits
        res = form.submit()
        # sees error
        assert 'Invalid password' in res

    def test_sees_error_message_if_username_doesnt_exist(self, user, testapp):
        """Show error if username doesn't exist."""
        # Goes to homepage
        res = testapp.get(url_for('public.login'))
        # Fills out login form, password incorrect
        form = res.forms['loginForm']
        form['username'] = 'unknown'
        form['password'] = 'myprecious'
        # Submits
        res = form.submit()
        # sees error
        assert 'Unknown user' in res


class TestRegistering:
    """Register a user."""

    def test_can_register(self, user, testapp):
        """Register a new user."""
        old_count = len(User.query.all())
        res = testapp.get(url_for('public.register'))
        # Fills out the form
        form = res.forms['registerForm']
        form['firstname'] = 'first name'
        form['lastname'] = 'last name'
        form['username'] = 'foobar'
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['confirm'] = 'secret'
        form['usertype'] = 'parent'
        # Submits
        res = form.submit().follow()
        assert res.status_code == 200
        # A new user was created
        assert len(User.query.all()) == old_count + 1

    def test_sees_error_message_if_passwords_dont_match(self, user, testapp):
        """Show error if passwords don't match."""
        # Goes to registration page
        res = testapp.get(url_for('public.register'))
        # Fills out form, but passwords don't match
        form = res.forms['registerForm']
        form['firstname'] = 'first name'
        form['lastname'] = 'last name'
        form['username'] = 'foobar'
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['confirm'] = 'secrets'
        form['usertype'] = 'parent'
        # Submits
        res = form.submit()
        # sees error message
        assert 'Passwords must match' in res

    def test_sees_error_message_if_user_already_registered(self, user, testapp):
        """Show error if user already registered."""
        user = UserFactory(active=True)  # A registered user
        user.save()
        # Goes to registration page
        res = testapp.get(url_for('public.register'))
        # Fills out form, but username is already registered
        form = res.forms['registerForm']
        form['firstname'] = 'first name'
        form['lastname'] = 'last name'
        form['username'] = user.username
        form['email'] = 'foo@bar.com'
        form['password'] = 'secret'
        form['confirm'] = 'secret'
        form['usertype'] = 'parent'
        # Submits
        res = form.submit()
        # sees error
        assert 'Username already registered' in res


class TestMessaging:
    """Send a message to another user."""

    def test_can_send_message(self, logged_in_user, user, testapp):
        """Send a message to another user."""
        old_count = len(Message.query.all())
        res = testapp.get(url_for('user.message_thread', to_username=user.username))
        # Fills out the form
        form = res.forms['message_form']
        form['body'] = 'hello, world'
        # Submits
        res = form.submit()
        assert res.status_code == 200
        assert 'message has been sent' in res
        # A new message was created
        assert len(Message.query.all()) == old_count + 1

    def test_sees_error_message_if_body_too_short(self, logged_in_user, user, testapp):
        """Show error if message is too short."""
        old_count = len(Message.query.all())
        res = testapp.get(url_for('user.message_thread', to_username=user.username))
        # Fills out the form
        form = res.forms['message_form']
        form['body'] = 'x'
        # Submits
        res = form.submit()
        assert res.status_code == 200
        assert 'message must contain at least' in res
        # A new message was created
        assert len(Message.query.all()) == old_count
