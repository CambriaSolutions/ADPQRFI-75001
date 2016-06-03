# -*- coding: utf-8 -*-
"""User forms."""
from flask_wtf import Form
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional

from .models import User


class RegisterForm(Form):
    """Register form."""

    firstname = StringField('First Name',
                            validators=[DataRequired(), Length(min=1, max=30)])
    lastname = StringField('Last Name',
                           validators=[DataRequired(), Length(min=1, max=30)])
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email',
                        validators=[DataRequired(), Email(), Length(min=6, max=40)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=6, max=40)])
    confirm = PasswordField('Verify Password',
                            [DataRequired(), EqualTo('password', message='Passwords must match')])
    usertype = SelectField('Case Worker?', choices=[('parent', 'No'), ('agent', 'Yes')])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(RegisterForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append('Username already registered')
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append('Email already registered')
            return False
        return True


class EditForm(Form):
    """Edit form."""

    blurb = StringField(
        'Blurb', validators=[Optional(), Length(min=0, max=128)])
    email = StringField(
        'Email', validators=[Optional(), Email(), Length(min=6, max=40)])
    address = StringField(
        'Address', validators=[Optional(), Length(min=5, max=128)])
    first_name = StringField(
        'First name', validators=[Optional(), Length(min=1, max=40)])
    last_name = StringField(
        'Last name', validators=[Optional(), Length(min=1, max=40)])
    phone_number = StringField(
        'Phone number', validators=[
            Optional(), Length(min=10, max=10, message='Phone number must be 10 digits long')])
    license_number = StringField(
        'License number', validators=[
            Optional(), Length(min=6, max=6, message='License must be 6 digits long')])
    num_adults = IntegerField(
        'Parents', validators=[Optional(), NumberRange(0, 4)])
    num_children = IntegerField(
        'Children', validators=[Optional(), NumberRange(0, 10)])
    num_capacity = IntegerField(
        'Capacity', validators=[Optional(), NumberRange(0, 10)])
    pref_girls = BooleanField(
        'Girls', validators=[Optional()])
    pref_boys = BooleanField(
        'Boys', validators=[Optional()])
    pref_1_to_5 = BooleanField(
        '1 to 5', validators=[Optional()])
    pref_6_to_9 = BooleanField(
        '6 to 9', validators=[Optional()])
    pref_10_to_18 = BooleanField(
        '10 to 18', validators=[Optional()])
    pref_siblings = BooleanField(
        'Siblings', validators=[Optional()])
    pref_behavioral = BooleanField(
        'Behavioral', validators=[Optional()])
    pref_respite = BooleanField(
        'Respite', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(EditForm, self).__init__(*args, **kwargs)

    def validate(self):
        """Validate the form."""
        initial_validation = super(EditForm, self).validate()
        if not initial_validation:
            return False
        if self.email.data:
            user = User.query.filter_by(email=self.email.data).first()
            if user:
                self.email.errors.append('Email already registered')
                return False
        else:
            del self.email

        return True


class MessageForm(Form):
    """New message form."""

    from_username = StringField('From',
                                validators=[Optional(), Length(min=3, max=30)])
    to_username = StringField('To',
                              validators=[DataRequired(), Length(min=3, max=30)])
    body = TextAreaField('New Message',
                         validators=[DataRequired(), Length(min=3, max=1500)])
