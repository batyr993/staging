import os
from flask import Blueprint, render_template
from toyetjek.blueprints.page.models import Categories
from toyetjek.blueprints.user.models import User
from config import settings


page = Blueprint('page', __name__, template_folder='templates')


@page.route('/')
def home():
	return render_template('page/home.html')


@page.route('/privacy')
def privacy():
	return render_template('page/privacy.html')


@page.route('/terms')
def terms():
	return render_template('page/terms.html')


@page.route('/faq')
def faq():
	return render_template('page/faq.html')

@page.route('/about')
def about():
	return render_template('page/about.html')

@page.route('/services')
def services():
	categories = Categories.query
	return render_template('page/services.html', categories=categories)

@page.route('/services/<string:category_name>')
def service(category_name):
	users = User.query.filter(User.category == category_name).filter(User.role == 'partner')

	return render_template("page/service.html", users = users, cname = category_name)

@page.route('/service_details/<int:id>')
def service_details(id):
	user = User.query.get(id)

	foldername = user.username
	image_names = os.listdir(os.getcwd() + '/toyetjek/static/images/uploads/{}'.format(foldername))

	return render_template("page/service_details.html", user = user, images = image_names)
	
