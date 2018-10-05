from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SelectField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Optional, Regexp, EqualTo
from wtforms_components import EmailField, Email, Unique

from flask_babel import lazy_gettext as _
from config.settings import LANGUAGES
from lib.util_wtforms import ModelForm, choices_from_dict
from toyetjek.blueprints.user.models import User, db
from toyetjek.blueprints.user.validations import ensure_identity_exists, \
    ensure_existing_password_matches

class LoginForm(FlaskForm):
    next = HiddenField()
    identity = StringField(_('Username or email'),
                           [DataRequired(), Length(3, 254)])
    password = PasswordField('Password', [DataRequired(), Length(8, 128)])
    remember = BooleanField('Stay signed in')


class BeginPasswordResetForm(FlaskForm):
    identity = StringField(_('Username or email'),
                           [DataRequired(),
                            Length(3, 254),
                            ensure_identity_exists])


class PasswordResetForm(FlaskForm):
    reset_token = HiddenField()
    password = PasswordField(_('Password'), [DataRequired(), Length(8, 128)])


class SignupForm(ModelForm):
    company_name = StringField(_('Company Name or Firstname'), [DataRequired(), Length(2,50)])
    email = EmailField(validators=[
        DataRequired(),
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    password = PasswordField(_('Password'), [DataRequired(), Length(8, 128)])
    confirm_password = PasswordField(_('Confirm Password'), [DataRequired(), EqualTo('password'), Length(8,128)])
    telephone = StringField(_('Telephone number'),
                            [DataRequired(),
                            Length(12)])
    category = SelectField(_('Category'), [DataRequired()],
                       choices=choices_from_dict(User.TYPE,
                                                 prepend_blank=False))
    region = SelectField(_('Region'),[DataRequired()],
                        choices=choices_from_dict(User.REGION,
                                                prepend_blank=False))

class WelcomeForm(ModelForm):
    username_message = _('Letters, numbers and underscores only please.')

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session
        ),
        DataRequired(),
        Length(1, 16),
        Regexp('^\w+$', message=username_message)
    ])


class UpdateCredentials(ModelForm):
    current_password = PasswordField(_('Current password'),
                                     [DataRequired(),
                                      Length(8, 128),
                                      ensure_existing_password_matches])

    email = EmailField(validators=[
        Email(),
        Unique(
            User.email,
            get_session=lambda: db.session
        )
    ])
    password = PasswordField(_('Password'), [Optional(), Length(8, 128)])

class UpdateLocaleForm(FlaskForm):
    locale = SelectField(_('Language preference'), [DataRequired()],
                         choices=choices_from_dict(LANGUAGES,
                                                   prepend_blank=False))
