import datetime
from collections import OrderedDict
from hashlib import md5

import pytz
from flask import current_app
from sqlalchemy import or_ , func
from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

from itsdangerous import URLSafeTimedSerializer, \
    TimedJSONWebSignatureSerializer

from flask_babel import lazy_gettext as _
from lib.util_sqlalchemy import ResourceMixin, AwareDateTime
from toyetjek.blueprints.client.models import Client, client_user
from toyetjek.extensions import db

class Services(ResourceMixin, db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)

    #Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                    onupdate='CASCADE',
                                                    ondelete='CASCADE'),
                        index=True, nullable=False)
    #Service details
    description = db.Column(db.Text)
    price = db.Column(db.Float)

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(Services, self).__init__(**kwargs)


class Payments(ResourceMixin, db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)

    #Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',
                                                    onupdate='CASCADE',
                                                    ondelete='CASCADE'),
                        index=True, nullable=False)
    #Payment details
    amount = db.Column(db.Float)
    reason = db.Column(db.String(80))

    def __init__(self, **kwargs):
        #Call Flask-SQLAlchemy's constructor.
        super(Payments, self).__init__(**kwargs)


class User(UserMixin, ResourceMixin, db.Model):
    ROLE = OrderedDict([
        ('partner', 'Partner'),
        ('admin', 'Admin')
    ])
    TYPE = OrderedDict([
        ('Wedding Services',_('Wedding service')),
        ('Restaurants',_('Restaurant')),
        ('Singers',_('Singer')),
        ('DJ',_('DJ')),
        ('Musicians',_('Musician')),
        ('Tamada',_('Tamada')),
        ('Dancers',_('Dancer')),
        ('Decorations',_('Decorations')),
        ('Wedding Cars',_('Wedding Car')),
        ('Beauty Salons', _('Beauty Salon')),
        ('Hair Stylists', _('Hair Stylist')),
        ('Wedding Dresses', _('Wedding House')),
        ('Florists', _('Florists')),
        ('Mens Wear', _('Mens Wear')),
        ('Photographers', _('Photographer')),
        ('Videographers',_('Videographer')),
        ('Jewelers', _('Jeweler')),
        ('Artists',_('Artist')),
        ('Cooks',_('Cook')),
        ('Kebab Chefs',_('Kebab Chef')),
        ('Bridal Gifts',_('Bridal Gifts')),
        ('Small Presents', _('Small Presents')),
        ('Beverages', _('Wedding Beverages')),
        ('Comedians', _('Comedian'))
    ])

    REGION = OrderedDict([
        ('Ashgabat',_('Ashgabat')),
        ('Dashoguz',_('Dashoguz')),
        ('Balkanabat',_('Balkanabat'))
    ])

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    #Relationship
    services = db.relationship(Services, backref='users', passive_deletes=True)
    payments = db.relationship(Payments, backref='users', passive_deletes=True)
    #Many-to-Many Relationship
    clients = db.relationship(Client, secondary=client_user, backref=db.backref('assign'), cascade='all,delete', lazy='joined')

    # Authentication.
    role = db.Column(db.Enum(*ROLE, name='role_types', native_enum=False),
                     index=True, nullable=False, server_default='partner')
    category = db.Column(db.Enum(*TYPE, name='category_types', native_enum=False))
    region = db.Column(db.Enum(*REGION, name='region_types', native_enum=False),
                     index=True, nullable=False, server_default='Ashgabat')
    active = db.Column('is_active', db.Boolean(), nullable=False,
                       server_default='1')
    confirmed = db.Column('is_confirmed', db.Boolean(), nullable=False, 
                       server_default='0')
    username = db.Column(db.String(24), unique=True, index=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_name_ru = db.Column(db.String(100))
    wedding_count = db.Column(db.Integer(), nullable=False, server_default='0')
    telephone = db.Column(db.String(50))
    telephone_2 = db.Column(db.String(50))
    telephone_3 = db.Column(db.String(50))
    image_name = db.Column(db.String(50))
    image_count = db.Column(db.Integer)
    payment = db.Column(db.Float)
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    description_ru = db.Column(db.Text)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False,
                      server_default='')
    password = db.Column(db.String(128), nullable=False, server_default='')
    profile_pic = db.Column(db.Text())

    # Additional settings.
    locale = db.Column(db.String(5), nullable=False, server_default='en')


    # Activity tracking.
    sign_in_count = db.Column(db.Integer, nullable=False, default=0)
    current_sign_in_on = db.Column(AwareDateTime())
    current_sign_in_ip = db.Column(db.String(45))
    last_sign_in_on = db.Column(AwareDateTime())
    last_sign_in_ip = db.Column(db.String(45))

    def __init__(self, **kwargs):
        # Call Flask-SQLAlchemy's constructor.
        super(User, self).__init__(**kwargs)

        self.password = User.encrypt_password(kwargs.get('password', ''))

    @classmethod
    def find_by_identity(cls, identity):
        """
        Find a user by their e-mail or username.

        :param identity: Email or username
        :type identity: str
        :return: User instance
        """
        #current_app.logger.debug('{0} has tried to login'.format(identity))

        return User.query.filter(
          (User.email == identity) | (User.username == identity)).first()

    @classmethod
    def encrypt_password(cls, plaintext_password):
        """
        Hash a plaintext string using PBKDF2. This is good enough according
        to the NIST (National Institute of Standards and Technology).

        In other words while bcrypt might be superior in practice, if you use
        PBKDF2 properly (which we are), then your passwords are safe.

        :param plaintext_password: Password in plain text
        :type plaintext_password: str
        :return: str
        """
        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None

    @classmethod
    def deserialize_token(cls, token):
        """
        Obtain a user from de-serializing a signed token.

        :param token: Signed token.
        :type token: str
        :return: User instance or None
        """
        private_key = TimedJSONWebSignatureSerializer(
            current_app.config['SECRET_KEY'])
        try:
            decoded_payload = private_key.loads(token)

            return User.find_by_identity(decoded_payload.get('user_email'))
        except Exception:
            return None

    @classmethod
    def initialize_password_reset(cls, identity):
        """
        Generate a token to reset the password for a specific user.

        :param identity: User e-mail address or username
        :type identity: str
        :return: User instance
        """
        u = User.find_by_identity(identity)
        reset_token = u.serialize_token()

        # This prevents circular imports.
        from toyetjek.blueprints.user.tasks import (
            deliver_password_reset_email)
        deliver_password_reset_email.delay(u.id, reset_token)

        return u

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
        search_chain = (User.email.ilike(search_query),
                        User.username.ilike(search_query))

        return or_(*search_chain)

    @classmethod
    def is_last_admin(cls, user, new_role, new_active):
        """
        Determine whether or not this user is the last admin account.

        :param user: User being tested
        :type user: User
        :param new_role: New role being set
        :type new_role: str
        :param new_active: New active status being set
        :type new_active: bool
        :return: bool
        """
        is_demoting_admin = user.role == 'admin' and new_role != 'admin'
        is_changing_active = user.active is True and new_active is None
        admin_count = User.query.filter(User.role == 'admin').count()

        if is_demoting_admin and admin_count == 1:
            return True

        if is_changing_active and user.role == 'admin' and admin_count == 1:
            return True

        return False

    def is_active(self):
        """
        Return whether or not the user account is active, this satisfies
        Flask-Login by overwriting the default value.

        :return: bool
        """
        return self.active

    def is_confirmed(self):
        """
        Return whether or not the user account is confirmed, this satisfies
        Flask-Login by overwriting the default value.

        :return: bool
        """
        return self.confirmed

    def get_auth_token(self):
        """
        Return the user's auth token. Use their password as part of the token
        because if the user changes their password we will want to invalidate
        all of their logins across devices. It is completely fine to use
        md5 here as nothing leaks.

        This satisfies Flask-Login by providing a means to create a token.

        :return: str
        """
        private_key = current_app.config['SECRET_KEY']

        serializer = URLSafeTimedSerializer(private_key)
        data = [str(self.id), md5(self.password.encode('utf-8')).hexdigest()]

        return serializer.dumps(data)

    def authenticated(self, with_password=True, password=''):
        """
        Ensure a user is authenticated, and optionally check their password.

        :param with_password: Optionally check their password
        :type with_password: bool
        :param password: Optionally verify this as their password
        :type password: str
        :return: bool
        """
        if with_password:
            return check_password_hash(self.password, password)

        return True

    def serialize_token(self, expiration=3600):
        """
        Sign and create a token that can be used for things such as resetting
        a password or other tasks that involve a one off token.

        :param expiration: Seconds until it expires, defaults to 1 hour
        :type expiration: int
        :return: JSON
        """
        private_key = current_app.config['SECRET_KEY']

        serializer = TimedJSONWebSignatureSerializer(private_key, expiration)
        return serializer.dumps({'user_email': self.email}).decode('utf-8')

    def update_activity_tracking(self, ip_address):
        """
        Update various fields on the user that's related to meta data on their
        account, such as the sign in count and ip address, etc..

        :param ip_address: IP address
        :type ip_address: str
        :return: SQLAlchemy commit results
        """
        self.sign_in_count += 1

        self.last_sign_in_on = self.current_sign_in_on
        self.last_sign_in_ip = self.current_sign_in_ip

        self.current_sign_in_on = datetime.datetime.now(pytz.utc)
        self.current_sign_in_ip = ip_address

        return self.save()



