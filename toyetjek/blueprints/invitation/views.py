import datetime
from datetime import timedelta, tzinfo
import time
from pytz import timezone
from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    url_for,
    render_template)
from flask_babel import gettext as _
from lib.util_datetime import tzware_datetime
from toyetjek.blueprints.invitation.models import Invitation
from toyetjek.blueprints.invitation.forms import InvitationForm


invitation = Blueprint('invitation', __name__, template_folder='templates')


@invitation.route('/register', methods=['GET','POST'])
def register():
	form = InvitationForm()
	inv = Invitation()

	if form.validate_on_submit():
		form.populate_obj(inv)
		
		inv.save()

		flash(_('One step left, please visit our office to pay 100 DTM fee'), 'success')
		return redirect(url_for('invitation.processing'))

	return render_template('invitation/register.html', form=form)

@invitation.route('/processing')
def processing():
	return render_template('invitation/processing.html')

@invitation.route('/einvitation/<int:id>')
def einvitation(id):

	inv = Invitation.query.get(id)

	a = datetime.datetime.combine(inv.wedding_date, inv.wedding_time)

	precise_time = a.strftime("%B %d, %Y %H:%M:%S")

	we_date = inv.wedding_date.strftime("%A, %B %d, %Y")

	return render_template('invitation/einvitation.html', inv=inv, wedding_date=precise_time, we_date=we_date)
