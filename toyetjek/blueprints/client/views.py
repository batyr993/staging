from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    url_for,
    render_template)

from flask_login import current_user
from flask_babel import gettext as _
from config import settings
from toyetjek.blueprints.client.forms import ClientForm
from toyetjek.blueprints.client.models import Client, client_user

client = Blueprint('client', __name__, template_folder='templates')

@client.route('/client', methods=['GET','POST'])
def index():
	form = ClientForm()

	if form.validate_on_submit():
		client = Client()
		form.populate_obj(client)

		client.save()

		flash(_('Thanks! toyetjek Team will contact you ASAP!'),'success')
		return redirect(url_for('client.index'))

	return render_template('client/apply.html', form=form)

@client.route('/client_list')
def client_list():
	clients = Client.query.filter(Client.status == 'approved').all()

	return render_template('client/client_list.html', clients=clients)

@client.route('/assigned_clients/<int:id>')
def assigned_clients(id):
	user = current_user
	clients = Client.query

	count = 0

	if current_user.role == 'partner':
		for usr in user.clients:
			if usr.status == 'done':
				count += 1

	if current_user.role == 'admin':
		for client in clients:
			if client.status == 'done':
				count += 1

	user.wedding_count = count
	user.save()

	return render_template('client/assigned_clients.html', user=user, cnt = user.wedding_count)