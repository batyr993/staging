import os
from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    url_for,
    render_template)
from flask_login import (
    login_required,
    login_user,
    current_user,
    logout_user)

from flask_babel import gettext as _
from lib.safe_next_url import safe_next_url
from toyetjek.blueprints.user.decorators import anonymous_required, confirm_required
from toyetjek.blueprints.contact import contact
from toyetjek.blueprints.feedback import feedback
from toyetjek.blueprints.user.models import User
from toyetjek.blueprints.user.forms import (
    LoginForm,
    BeginPasswordResetForm,
    PasswordResetForm,
    SignupForm,
    WelcomeForm,
    UpdateCredentials,
    UpdateLocaleForm)

user = Blueprint('user', __name__, template_folder='templates')


@user.route('/login', methods=['GET', 'POST'])
@anonymous_required()
def login():
    form = LoginForm(next=request.args.get('next'))

    if form.validate_on_submit():
        u = User.find_by_identity(request.form.get('identity'))

        if u and u.authenticated(password=request.form.get('password')):
            # As you can see remember me is always enabled, this was a design
            # decision I made because more often than not users want this
            # enabled. This allows for a less complicated login form.
            #
            # If however you want them to be able to select whether or not they
            # should remain logged in then perform the following 3 steps:
            # 1) Replace 'True' below with: request.form.get('remember', False)
            # 2) Uncomment the 'remember' field in user/forms.py#LoginForm
            # 3) Add a checkbox to the login form with the id/name 'remember'
            if u.is_active() and login_user(u, remember=False):
                u.update_activity_tracking(request.remote_addr)

                # Handle optionally redirecting to the next URL safely.
                next_url = request.form.get('next')
                if next_url:
                    return redirect(safe_next_url(next_url))
                return redirect(url_for('user.settings'))
            else:
                flash(_('This account has been disabled.'), 'warning')
        else:
            flash(_('Identity or password is incorrect.'), 'danger')
        
    return render_template('user/login.html', form=form)

@user.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out.'), 'success')
    return redirect(url_for('user.login'))


@user.route('/account/begin_password_reset', methods=['GET', 'POST'])
@anonymous_required()
def begin_password_reset():
    form = BeginPasswordResetForm()

    if form.validate_on_submit():
        u = User.initialize_password_reset(request.form.get('identity'))

        flash(_('An email has been sent to {0}.').format(u.email), 'success')
        return redirect(url_for('user.login'))

    return render_template('user/begin_password_reset.html', form=form)


@user.route('/account/password_reset', methods=['GET', 'POST'])
@anonymous_required()
def password_reset():
    form = PasswordResetForm(reset_token=request.args.get('reset_token'))

    if form.validate_on_submit():
        u = User.deserialize_token(request.form.get('reset_token'))

        if u is None:
            flash(_('Your reset token has expired or was tampered with.'),
                  'error')
            return redirect(url_for('user.begin_password_reset'))

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('password'))
        u.save()

        if login_user(u):
            flash(_('Your password has been reset.'), 'success')
            return redirect(url_for('user.settings'))

    return render_template('user/password_reset.html', form=form)


@user.route('/signup', methods=['GET', 'POST'])
@anonymous_required()
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        u = User()

        form.populate_obj(u)
        u.password = User.encrypt_password(request.form.get('confirm_password'))
        u.save()

        if login_user(u):
            flash(_('Thanks for signing up!, Please visit our office to pay fee and confirm your account'), 'success')
            return redirect(url_for('user.confirmation'))

    return render_template('user/signup.html', form=form)


@user.route('/confirm_account')
def confirmation():
    return render_template('user/confirm_account.html')

@user.route('/welcome', methods=['GET', 'POST'])
@login_required
@confirm_required()
def welcome():
    if current_user.username:
        flash(_('You already picked a username.'), 'warning')
        return redirect(url_for('user.settings'))

    form = WelcomeForm()

    if form.validate_on_submit():
        current_user.username = request.form.get('username')
        current_user.save()

        flash(_('Sign up is complete, enjoy our services.'), 'success')
        return redirect(url_for('user.settings'))

    return render_template('user/welcome.html', form=form)


@user.route('/settings')
@login_required
@confirm_required()
def settings():

    folder_name = current_user.username

    current_filename = os.getcwd() + '/toyetjek/static/images/uploads/{}'.format(current_user.username)
    
    if os.path.exists(current_filename):
        image_names = os.listdir(os.getcwd() + '/toyetjek/static/images/uploads/{}'.format(folder_name))
        return render_template('user/settings.html', images=image_names)
    else:
        msg = "No Photos"
        return render_template('user/settings.html', msg = msg)




@user.route('/settings/update_credentials', methods=['GET', 'POST'])
@login_required
@confirm_required()
def update_credentials():
    form = UpdateCredentials(current_user)

    if form.validate_on_submit():
        new_password = request.form.get('password', '')
        current_user.email = request.form.get('email')

        if new_password:
            current_user.password = User.encrypt_password(new_password)

        current_user.save()

        flash(_('Your sign in settings have been updated.'), 'success')
        return redirect(url_for('user.settings'))

    return render_template('user/update_credentials.html', form=form)


@user.route('/settings/update_locale', methods=['GET', 'POST'])
@login_required
def update_locale():
    form = UpdateLocaleForm(locale=current_user.locale)

    if form.validate_on_submit():
        form.populate_obj(current_user)
        current_user.save()

        flash(_('Your locale settings have been updated.'), 'success')
        return redirect(url_for('user.settings'))

    return render_template('user/update_locale.html', form=form)
