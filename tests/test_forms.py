# -*- coding: utf-8 -*-
"""Test forms."""

from werkzeug.datastructures import ImmutableMultiDict as IMultidict

from osi_prototype.public.forms import LoginForm
from osi_prototype.user.forms import EditForm, MessageForm, RegisterForm


class TestRegisterForm:
    """Register form."""

    def test_validate_user_already_registered(self, user):
        """Enter username that is already registered."""
        form = RegisterForm(firstname='test first name', lastname='test last name',
                            username=user.username, email='foo@bar.com',
                            password='example', confirm='example',
                            usertype='parent')

        assert form.validate() is False
        assert 'Username already registered' in form.username.errors

    def test_validate_email_already_registered(self, user):
        """Enter email that is already registered."""
        form = RegisterForm(firstname='test first name', lastname='test last name',
                            username='unique', email=user.email,
                            password='example', confirm='example',
                            usertype='parent')

        assert form.validate() is False
        assert 'Email already registered' in form.email.errors

    def test_validate_success(self, db):
        """Register with success."""
        form = RegisterForm(firstname='test first name', lastname='test last name',
                            username='newusername', email='new@test.test',
                            password='example', confirm='example',
                            usertype='parent')
        assert form.validate() is True

    def test_validate_missing_fields(self, db):
        """Register with failure due to missing fields."""
        form = RegisterForm(username='test', email='foo@bar.com',
                            password='example', confirm='example',
                            usertype='parent')

        assert form.validate() is False
        assert any('required' in e for e in form.lastname.errors)
        assert any('required' in e for e in form.firstname.errors)

    def test_validate_bad_user_type(self, db):
        """Register with failure due to bad user type."""
        form = RegisterForm(firstname='first', lastname='last',
                            username='test', email='foo@bar.com',
                            password='example', confirm='example',
                            usertype='bad')

        assert form.validate() is False
        assert any('valid choice' in e for e in form.usertype.errors)


class TestLoginForm:
    """Login form."""

    def test_validate_success(self, user):
        """Login successful."""
        user.set_password('example')
        user.save()
        form = LoginForm(username=user.username, password='example')
        assert form.validate() is True
        assert form.user == user

    def test_validate_unknown_username(self, db):
        """Unknown username."""
        form = LoginForm(username='unknown', password='example')
        assert form.validate() is False
        assert 'Unknown username' in form.username.errors
        assert form.user is None

    def test_validate_invalid_password(self, user):
        """Invalid password."""
        user.set_password('example')
        user.save()
        form = LoginForm(username=user.username, password='wrongpassword')
        assert form.validate() is False
        assert 'Invalid password' in form.password.errors

    def test_validate_inactive_user(self, user):
        """Inactive user."""
        user.active = False
        user.set_password('example')
        user.save()
        # Correct username and password, but user is not activated
        form = LoginForm(username=user.username, password='example')
        assert form.validate() is False
        assert 'User not activated' in form.username.errors


class TestEditForm:
    """Edit form."""

    def test_validate_no_edits(self, user):
        """Successful even with no edits."""
        form = EditForm()
        assert form.validate() is True

    def test_validate_bad_numbers(self, db):
        """Unsuccessful with bad numbers."""
        data = IMultidict({'num_adults': -5,
                           'num_children': 500,
                           'num_capacity': -1})
        form = EditForm(data)
        assert form.validate() is False
        assert len(form.num_adults.errors) > 0
        assert len(form.num_children.errors) > 0
        assert len(form.num_children.errors) > 0


class TestMessageForm:
    """Message form."""

    def test_validate_success(self, user):
        """Successful message sent."""
        form = MessageForm(from_username='abc', to_username='def', body='xyz')
        assert form.validate() is True

    def test_validate_message_too_short(self, user):
        """Message too short."""
        form = MessageForm(from_username='abc', to_username='def', body='xy')
        assert form.validate() is False
