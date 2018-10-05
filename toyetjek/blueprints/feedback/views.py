from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    url_for,
    render_template)

from toyetjek.blueprints.feedback.forms import FeedbackForm

feedback = Blueprint('feedback', __name__, template_folder='templates')


@feedback.route('/feedback', methods=['GET', 'POST'])
def index():
    form = FeedbackForm()

    if form.validate_on_submit():
        # This prevents circular imports.
        from toyetjek.blueprints.feedback.tasks import deliver_contact_email

        deliver_contact_email.delay(request.form.get('email'),
                                    request.form.get('message'),
                                    request.form.get('terms'))

        flash('Thanks, expect a response shortly.', 'success')
        return redirect(url_for('feedback.index'))

    return render_template('feedback/index.html', form=form)
