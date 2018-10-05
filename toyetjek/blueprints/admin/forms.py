from collections import OrderedDict

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, StringField, BooleanField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length, Optional, Regexp
from wtforms.fields.html5 import DateField
from wtforms_components import Unique, TimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from lib.util_wtforms import ModelForm, choices_from_dict, choices_from_db
from toyetjek.blueprints.user.models import db, User
from toyetjek.blueprints.client.models import Client
from toyetjek.blueprints.invitation.models import Invitation


class SearchForm(FlaskForm):
    q = StringField('Search terms', [Optional(), Length(1, 256)])


class BulkDeleteForm(FlaskForm):
    SCOPE = OrderedDict([
        ('all_selected_items', 'All selected items'),
        ('all_search_results', 'All search results')
    ])

    scope = SelectField('Privileges', [DataRequired()],
                        choices=choices_from_dict(SCOPE, prepend_blank=False))

class UserForm(ModelForm):
    username_message = 'Letters, numbers and underscores only please.'

    username = StringField(validators=[
        Unique(
            User.username,
            get_session=lambda: db.session
        ),
        DataRequired(),
        Length(1, 16),
        Regexp('^\w+$', message=username_message)
    ])

    role = SelectField('Privileges', [DataRequired()],
                       choices=choices_from_dict(User.ROLE,
                                                 prepend_blank=False))
    category = SelectField('Category',[DataRequired()], choices=choices_from_dict(User.TYPE, prepend_blank=False))
    region = SelectField('Region',[DataRequired()], choices=choices_from_dict(User.REGION, prepend_blank=False))
    telephone = StringField('Telephone number', [DataRequired(), Length(12)])
    telephone_2 = StringField('Telephone number 2', [Optional(), Length(12)])
    telephone_3 = StringField('Telephone number 3', [Optional(), Length(12)])
    description = TextAreaField('Description (EN)', [Optional(), Length(max=200)])
    description_ru = TextAreaField('Description (RU)', [Optional(), Length(max=200)])
    company_name = StringField('Company name or First Name (EN)', [DataRequired()])
    company_name_ru = StringField('Company name or First Name (RU)')
    active = BooleanField('Yes, allow this user to sign in')
    confirmed = BooleanField('Confirm this Account')

class UploadForm(FlaskForm):
    photo = FileField('Upload Photos', [FileAllowed(['jpg','png','jpeg'], 'Image only!'), FileRequired('File was empty!')])

class ServiceForm(ModelForm):
    description = TextAreaField('*Description', [DataRequired(), Length(max=200)])
    price = DecimalField('*Price', [DataRequired()])

class PaymentForm(ModelForm):
    amount = DecimalField('*Amount',[DataRequired()])
    reason = StringField('*Reason', [DataRequired(), Length(max=50)])

class ClientPaymentForm(ModelForm):
    amount = DecimalField('*Amount',[DataRequired()])
    reason = StringField('*Reason', [DataRequired(), Length(max=50)])

class ClientForm(ModelForm):
    name = StringField("Name",
                       [DataRequired(), Length(3, 254)])
    region = SelectField('Region',[DataRequired()], choices=choices_from_dict(Client.REGION, prepend_blank=False))
    lastname = StringField('Lastname',
                        [DataRequired(), Length(3, 254)])
    nickname = StringField('Nickname',
                        [DataRequired(), Length(max=50)])
    telephone1 = StringField('Telephone',
                        [DataRequired(), Length(max=12)])
    telephone2 = StringField('Telephone2',
                        [Length(max=12)])
    wedding_date = DateField('Wedding Date', [DataRequired()])
    wedding_details = TextAreaField('Wedding Details',[DataRequired()])

    status = SelectField('Status', [DataRequired()],
                        choices=choices_from_dict(Client.STATUS,
                                                    prepend_blank=False))
    address = StringField('Address', [Length(max=80)])
    confirmed = BooleanField('Confirm this Client')

class AssignClientForm(ModelForm):
    assign_client = SelectField('Client', choices=[], coerce=int)

class AddCategory(ModelForm):
    category_name = StringField('Category Name',[DataRequired(), Length(max=50)])
    photo = FileField('Upload a Photo',[FileAllowed(['jpg','JPG','jpeg','JPEG','png','PNG'], 'Image only!')])

class InvitationForm(ModelForm):
    names = StringField('Groom & Bride', [DataRequired(), Length(max=80)])
    region = SelectField('Region',[DataRequired()], choices=choices_from_dict(Invitation.REGION, prepend_blank=False))
    telephone = StringField('Telephone', [DataRequired()])
    wedding_quote = StringField('Wedding Place', [DataRequired()])
    wedding_time = TimeField('Wedding Time', [DataRequired()])
    wedding_date = DateField('Wedding Date', [DataRequired()])
    payment = DecimalField('Price', [DataRequired()])
    photo = FileField('Upload a Photo',[FileAllowed(['jpg','JPG','jpeg','JPEG','png','PNG'], 'Image only!')])
    confirmed = BooleanField('Confirm Invitation')
