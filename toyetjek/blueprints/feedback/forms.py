from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField
from wtforms_components import EmailField
from wtforms.validators import DataRequired, Length


class FeedbackForm(FlaskForm):
    email = EmailField("Your email address",
                       [DataRequired(), Length(3, 254)])
    message = TextAreaField("Your feedback here",
                            [DataRequired(), Length(1, 8192)])
    terms = BooleanField("Do you agree to our terms and services?",
    						[DataRequired()])