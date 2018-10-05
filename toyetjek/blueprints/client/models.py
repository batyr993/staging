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

#many-to-many relationship assigning client to user
client_user = db.Table('client_user',
                        db.Column('id',
                            db.Integer,
                            primary_key=True),
                        db.Column('user_id',
                            db.Integer,
                            db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE')),
                        db.Column('client_id',
                            db.Integer,
                            db.ForeignKey('clients.id', ondelete='CASCADE', onupdate='CASCADE')))

class ClientPayment(ResourceMixin, db.Model):
    __tablename__ = 'client_payments'
    id = db.Column(db.Integer, primary_key=True)

    #Relationships
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id',
                                                    onupdate='CASCADE',
                                                    ondelete='CASCADE'),
                        index=True, nullable=False)
    #Payment details
    amount = db.Column(db.Float)
    reason = db.Column(db.String(80))

    def __init__(self, **kwargs):
        #Call Flask-SQLAlchemy's constructor.
        super(ClientPayment, self).__init__(**kwargs)
        

class Client(ResourceMixin, db.Model):
	STATUS = OrderedDict([
		('pending','PENDING'),
		('cancelled', 'CANCELLED'),
		('approved', 'APPROVED'),
		('done', 'DONE')
	])

	REGION = OrderedDict([
        ('Ashgabat',_('Ashgabat')),
        ('Dashoguz',_('Dashoguz')),
        ('Balkanabat',_('Balkanabat'))
    ])

	__tablename__ = 'clients'
	id = db.Column(db.Integer, primary_key=True)

	status = db.Column(db.Enum(*STATUS, name='status_type', native_enum=False),
                     index=True, nullable=False, server_default='pending')
	region = db.Column(db.Enum(*REGION, name='region_types', native_enum=False),
                     index=True, nullable=False, server_default='Ashgabat')
	#Client details
	confirmed = db.Column('is_confirmed', db.Boolean(), nullable=False, 
                       server_default='0')
	name = db.Column(db.String(30))
	nickname = db.Column(db.String(50), unique=True)
	lastname = db.Column(db.String(30))
	telephone1 = db.Column(db.String(25))
	telephone2 = db.Column(db.String(25))
	wedding_date = db.Column(db.Date)
	wedding_details = db.Column(db.Text)
	address = db.Column(db.String(80))

	def __init__(self, **kwargs):

		super(Client, self).__init__(**kwargs)

	@classmethod
	def find_by_identity(cls, identity):
		"""
		Find a client by their e-mail or nickname.

		:param identity: Email or nickname
		:type identity: str
		:return: Client instance
		"""
		#current_app.logger.debug('{0} has tried to login'.format(identity))

		return Client.query.filter(
		  (Client.name == identity) | (Client.nickname == identity)).first()

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
		search_chain = (Client.name.ilike(search_query),
		                Client.nickname.ilike(search_query))

		return or_(*search_chain)

	def is_confirmed(self):
		"""
		Return whether or not the client account is confirmed, this satisfies
		Flask-Login by overwriting the default value.

		:return: bool
		"""
		return self.confirmed

