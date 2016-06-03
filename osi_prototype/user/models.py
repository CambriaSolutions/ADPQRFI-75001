# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask import url_for
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
    profile_photo = Column(db.String(64), nullable=True)
    profile_image = Column(db.LargeBinary())

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

    def get_profile_photo_url(self, placeholder_size=100):
        """Get a profile photo url or return a placeholder image."""
        if self.profile_photo:
            return url_for('user.profile_photo', username=self.username,
                           filename=self.profile_photo)
        else:
            return 'http://placehold.it/{}'.format(placeholder_size)

    def set_profile_photo(self, name, photo):
        """Set a profile photo given a file."""
        self.update(profile_photo=name, profile_image=photo)

    def messages_between(self, other, limit=10):
        """Return partial query for messages between this user and another user."""
        return Message.messages_between(self, other)

    def threads_involved_in(self):
        """Return threads this user is involved in."""
        thread_list = []
        users_seen = set()
        users_seen.add(self.id)

        # De-duplicate threads for (2, 5) and (5, 2) into one.
        ordered_threads = Message.threads_involving(self).all()
        ordered_threads.sort(key=lambda t: t[3], reverse=True)

        for (from_id, to_id, is_unread, time) in ordered_threads:
            # At least one of the users in this thread should be unseen.
            if (from_id not in users_seen) or (to_id not in users_seen):
                thread = {}

                if from_id == self.id:
                    # From me to someone else.
                    other_username = User.get_by_id(to_id).username
                    users_seen.add(to_id)
                else:
                    # From someone else to me.
                    other_username = User.get_by_id(from_id).username
                    users_seen.add(from_id)

                # I have unread messages in this thread if I received a message
                # that is unread. If I was the most recent person to send a
                # message, I should not have any unread messages.
                has_unread = (self.id == to_id) and is_unread == 1

                thread['other_username'] = other_username
                thread['last_updated'] = time
                thread['has_unread'] = has_unread
                thread_list.append(thread)

        return thread_list

    def unread_msg_count(self):
        """Return the number of unread messages."""
        # Select count(*) from messages where to_user_id = CurrentUser and is_read = 0.
        return Message.query\
                      .filter(Message.to_user_id == self.id,
                              Message.is_unread == 1)\
                      .count()

    @classmethod
    def get_by_username(cls, username, show_404=False):
        """Look up a user by their username."""
        query = cls.query.filter_by(username=username)
        if show_404:
            return query.first_or_404()
        else:
            return query.first()

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
    is_unread = Column(db.SmallInteger(), nullable=True, default=1)

    @classmethod
    def messages_between(cls, user_a, user_b):
        """Return a partial query for all messages between two users."""
        messages = cls.query.filter(
            db.or_(db.and_(cls.from_user_id == user_a.id,
                           cls.to_user_id == user_b.id),
                   db.and_(cls.from_user_id == user_b.id,
                           cls.to_user_id == user_a.id)))

        return messages

    @classmethod
    def threads_involving(cls, user):
        """Return a partial query for all threads this user involved in."""
        threads = cls.query.with_entities(
            cls.from_user_id,
            cls.to_user_id,
            db.func.max(cls.is_unread),
            db.func.max(cls.created_at)
        ).filter(db.or_(cls.from_user_id == user.id,
                        cls.to_user_id == user.id))\
         .group_by(cls.from_user_id, cls.to_user_id)

        return threads

    def __repr__(self):
        """Represent instance as a unique string."""
        return '<Message({from_user}=>{to_user}: {body})>'.format(
            from_user=self.from_user_id,
            to_user=self.to_user_id,
            body=self.body[:24])
