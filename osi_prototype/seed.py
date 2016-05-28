#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Seeds the database with some useful accounts."""
from flask_script import Command

from osi_prototype.database import db
from osi_prototype.user.models import User


class Seed(Command):
    """Seeds the database with some useful records."""

    def run(self):
        """Run command."""
        users = [
            User('admin', 'admin@example.com', 'passw0rd', user_type='admin'),
            User('parent1', 'parent1@example.com', 'passw0rd', user_type='parent'),
            User('parent2', 'parent2@example.com', 'passw0rd', user_type='parent'),
            User('parent3', 'parent3@example.com', 'passw0rd', user_type='parent'),
            User('agent1', 'agent1@example.com', 'passw0rd', user_type='agent'),
            User('agent2', 'agent2@example.com', 'passw0rd', user_type='agent'),
        ]
        for u in users:
            u.active = True

        db.session.query(User).delete()
        db.session.commit()

        db.session.add_all(users)
        db.session.commit()
