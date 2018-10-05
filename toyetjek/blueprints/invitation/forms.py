import datetime
from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, PasswordField, SelectField, BooleanField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Length, Optional, Regexp, EqualTo
from wtforms_components import EmailField, Email, Unique, TimeField

from flask_babel import lazy_gettext as _
from lib.util_wtforms import ModelForm, choices_from_dict
from toyetjek.blueprints.invitation.models import Invitation
from toyetjek.blueprints.user.validations import ensure_identity_exists, \
    ensure_existing_password_matches

class InvitationForm(ModelForm):

	names = StringField(_('Groom & Bride'), [DataRequired(), Length(max=80)])
	telephone = StringField(_('Telephone'), [DataRequired(), Length(max=12)])
	wedding_quote = StringField(_('Wedding Place'), [DataRequired()])
	wedding_time = TimeField(_('Wedding Time'), [DataRequired()])
	wedding_date = DateField(_('Wedding Date'),[DataRequired()])
	region = SelectField(_('Region'),[DataRequired()],
                        choices=choices_from_dict(Invitation.REGION,
                                                prepend_blank=False))