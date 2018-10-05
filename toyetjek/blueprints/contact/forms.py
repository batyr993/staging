from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms_components import EmailField
from wtforms.validators import DataRequired, Length
from flask_babel import lazy_gettext as _


class ContactForm(FlaskForm):
    email = EmailField(_("What's your e-mail address?"),
                       [DataRequired(), Length(3, 254)])
    message = TextAreaField(_("What's your question or issue?"),
                            [DataRequired(), Length(1, 8192)])