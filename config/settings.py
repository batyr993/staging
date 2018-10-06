from datetime import timedelta
import os

DEBUG = True
TESTING = True
#LOG_LEVEL = 'DEBUG'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

#SERVER_NAME = '142.93.223.183'
SECRET_KEY = 'firstweddingportalofturkmenistan'

# Flask-Mail.
MAIL_DEFAULT_SENDER = 'contact@local.host'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'batyr.ata93@gmail.com'
MAIL_PASSWORD = 'id#100065673'

#Flask-Babel
LANGUAGES = {
	'en': 'English',
	'ru': 'Russian'
}
BABEL_DEFAULT_LOCALE = 'en'

#Assets
WEBPACK_MANIFEST_PATH = os.getcwd() + '/build/manifest.json'

# Celery.
CELERY_BROKER_URL = 'redis://:devpassword@redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:devpassword@redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5

# SQLAlchemy.
db_uri = 'postgresql://toyetjek:Toyetjek2018!@@postgres:5432/toyetjek'
SQLALCHEMY_DATABASE_URI = db_uri
SQLALCHEMY_TRACK_MODIFICATIONS = False

# User.
SEED_ADMIN_EMAIL = 'dev@local.host'
SEED_ADMIN_PASSWORD = 'Toyetjek2018!@'
SEED_ADMIN_COMPANY = 'toyetjek'
SEED_ADMIN_CONFIRMATION = True
REMEMBER_COOKIE_DURATION = timedelta(days=90)


