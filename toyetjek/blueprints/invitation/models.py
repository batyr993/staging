import datetime
from collections import OrderedDict
from hashlib import md5

import pytz
from flask import current_app
from flask_babel import lazy_gettext as _
from sqlalchemy import or_ , func
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from itsdangerous import URLSafeTimedSerializer, \
    TimedJSONWebSignatureSerializer

from lib.util_sqlalchemy import ResourceMixin, AwareDateTime
from toyetjek.extensions import db

class Invitation(ResourceMixin, db.Model):
	REGION = OrderedDict([
        ('Ashgabat',_('Ashgabat')),
        ('Dashoguz',_('Dashoguz')),
        ('Balkanabat',_('Balkanabat'))
    ])
	__tablename__ = 'invitations'
	id = db.Column(db.Integer(), primary_key=True)

	region = db.Column(db.Enum(*REGION, name='region_types', native_enum=False),
                     index=True, nullable=False, server_default='Ashgabat')

	names = db.Column(db.String(80))
	wedding_time = db.Column(db.Time())
	wedding_date = db.Column(db.Date())
	wedding_quote = db.Column(db.String(150))
	telephone = db.Column(db.String(12))
	payment = db.Column(db.Float, nullable=False, server_default='0.0')
	confirmed = db.Column('is_confirmed', db.Boolean(), nullable=False, 
                       server_default='0')
	image = db.Column(db.Text)

	def __init__(self, **kwargs):
	    #Call Flask-SQLAlchemy's constructor.
	    super(Invitation, self).__init__(**kwargs)

	@classmethod
	def find_by_identity(cls, identity):
		"""
		Find a invitation by their by their names.

		:param identity: Bride and Groom names
		:type identity: str
		:return: Invitation instance
		"""

		return Invitation.query.filter(Invitation.wedding_quote == identity | Invitation.names == identity).first()

	@classmethod
	def search(cls, query):
		"""
		Search a resource by 1 or more fields.

		:param query: Search query
		:type query: str
		:return: SQLAlchemy filter
		"""
		if not query:
			return ''

		search_query = '%{0}%'.format(query)
		search_chain = (Invitation.wedding_quote.ilike(search_query))

		return or_(*search_chain)

	def is_confirmed(self):
		"""
		Return whether or not the invitation is confirmed, this satisfies

		:return: bool
		"""
		return self.confirmed