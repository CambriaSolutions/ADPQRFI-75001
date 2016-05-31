# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt
from collections import defaultdict

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

    def messages_between(self, other_username, limit=10):
        """Returns messages between this user and another user."""
        other_user = User.get_by_username(other_username)
        return Message.messages_between(self, other_user).limit(limit).all()

    def threads_involved_in(self):
        """Returns threads this user is involved in."""
        threads = defaultdict(dict)
        # De-duplicate threads for (2, 5) and (5, 2) into one.
        for (from_id, to_id, time) in Message.threads_involving(self).all():
            if from_id == self.id:
                # From me to someone else.
                to_username = User.get_by_id(to_id).username
                threads[to_username]['last_sent'] = time
            else:
                # From someone else to me.
                from_username = User.get_by_id(from_id).username
                threads[from_username]['last_received'] = time
        return threads

    @classmethod
    def get_by_username(cls, username):
        """Looks up a user by their username."""
        return cls.query.filter_by(username=username).first()

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<User({username!r})>'.format(username=self.username)


class Message(SurrogatePK, Model):
    """A message from a user to another user of the app."""

    __tablename__ = 'messages'
    from_user_id = reference_col('users', nullable=False)
    from_user = db.relationship(
        'User',
        backref=db.backref('outbox', lazy='dynamic', uselist=True),
        foreign_keys='Message.from_user_id')

    to_user_id = reference_col('users', nullable=False)
    to_user = db.relationship(
        'User',
        backref=db.backref('inbox', lazy='dynamic', uselist=True),
        foreign_keys='Message.to_user_id')

    body = Column(db.Text(), nullable=False)

    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    is_read = Column(db.Boolean, nullable=False, default=False)

    @classmethod
    def messages_between(cls, user_a, user_b):
        """Returns a partial query for all messages between two users."""
        messages = cls.query.filter(
            db.or_(db.and_(cls.from_user_id == user_a.id,
                           cls.to_user_id == user_b.id),
                   db.and_(cls.from_user_id == user_b.id,
                           cls.to_user_id == user_a.id)))\
           .order_by(cls.created_at.desc())
        return messages

    @classmethod
    def threads_involving(cls, user):
        """Returns a partial query for all threads this user involved in."""
        threads = cls.query.with_entities(cls.from_user_id,
                                          cls.to_user_id,
                                          db.func.max(cls.created_at))\
                     .filter(db.or_(cls.from_user_id == user.id,
                                    cls.to_user_id   == user.id))\
                     .group_by(cls.from_user_id, cls.to_user_id)\
                     .order_by(cls.created_at)
        return threads

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Message({from_user}=>{to_user}: {body})>'.format(
            from_user=self.from_user_id,
            to_user=self.to_user_id,
            body=self.body[:24])
