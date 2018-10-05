from flask_wtf import FlaskForm
from toyetjek.blueprints.client.models import Client
from flask_babel import lazy_gettext as _
from lib.util_wtforms import ModelForm, choices_from_dict
from wtforms import StringField, SelectField
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import DateField

class ClientForm(FlaskForm):
	region = SelectField(_('Region'),[DataRequired()],
	                    choices=choices_from_dict(Client.REGION,
	                                            prepend_blank=False))
	name = StringField(_('Name'), [DataRequired(), Length(3, 254)])
	lastname = StringField(_('Lastname'), [DataRequired(), Length(3,254)])
	telephone1 = StringField(_('Telephone'), [DataRequired(), Length(max=12)])
	wedding_date = DateField(_('Wedding Date'), [DataRequired()])
