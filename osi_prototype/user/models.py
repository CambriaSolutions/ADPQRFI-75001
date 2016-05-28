# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from osi_prototype.database import Column, Model, SurrogatePK, db, reference_col, relationship
from osi_prototype.extensions import bcrypt


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = 'roles'
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col('users', nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Role({name})>'.format(name=self.name)


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = 'users'
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    #: The hashed password
    password = Column(db.String(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)
    user_type = Column(db.String(16), default='parent')
    blurb = Column(db.Text(), nullable=True)
    address = Column(db.String(128), nullable=True)
    license_number = Column(db.String(32), nullable=True)
    phone_number = Column(db.String(32), nullable=True)

    num_adults = Column(db.SmallInteger(), nullable=True, default=1)
    num_children = Column(db.SmallInteger(), nullable=True, default=0)
    num_capacity = Column(db.SmallInteger(), nullable=True, default=1)

    pref_boys = Column(db.Boolean(), nullable=True, default=False)
    pref_girls = Column(db.Boolean(), nullable=True, default=False)
    pref_1_to_5 = Column(db.Boolean(), nullable=True, default=False)
    pref_6_to_9 = Column(db.Boolean(), nullable=True, default=False)
    pref_10_to_18 = Column(db.Boolean(), nullable=True, default=False)
    pref_siblings = Column(db.Boolean(), nullable=True, default=False)
    pref_behavioral = Column(db.Boolean(), nullable=True, default=False)
    pref_respite = Column(db.Boolean(), nullable=True, default=False)

    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Full user name."""
        return '{0} {1}'.format(self.first_name, self.last_name)

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)
