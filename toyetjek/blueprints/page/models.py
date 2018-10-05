from lib.util_sqlalchemy import ResourceMixin
from toyetjek.extensions import db

class Categories(ResourceMixin, db.Model):
	__tablename__ = 'categories'
	id = db.Column(db.Integer(), primary_key=True, index=True)
	category_name = db.Column(db.String(50))
	image = db.Column(db.Text)

	def __init__(self, **kwargs):
	    #Call Flask-SQLAlchemy's constructor.
	    super(Categories, self).__init__(**kwargs)