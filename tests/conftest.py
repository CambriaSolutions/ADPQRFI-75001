# -*- coding: utf-8 -*-
"""Defines fixtures available to all tests."""

import pytest
from flask_webtest import TestApp

from osi_prototype.app import create_app
from osi_prototype.database import db as _db
from osi_prototype.settings import TestConfig

from .factories import UserFactory


@pytest.yield_fixture(scope='function')
def app():
    """An application for the tests."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='function')
def testapp(app):
    """A Webtest app."""
    return TestApp(app)


@pytest.yield_fixture(scope='function')
def db(app):
    """A database for the tests."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    # Explicitly close DB connection
    _db.session.close()
    _db.drop_all()


@pytest.fixture
def user(db):
    """A user for the tests."""
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user


@pytest.fixture
def logged_in_user(db, testapp):
    """A logged-in user for the tests."""
    user = UserFactory(password='passw0rd')
    db.session.commit()
    with testapp.session_transaction() as sess:
        sess['user_id'] = 1
    return user
