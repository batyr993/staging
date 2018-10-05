import os
import shutil
import sys
from flask import (
    Blueprint,
    redirect,
    request,
    flash,
    session,
    url_for,
    render_template)
from flask_login import login_required, current_user
from sqlalchemy import text, func

from toyetjek.blueprints.admin.models import Dashboard
from toyetjek.blueprints.user.decorators import role_required
from toyetjek.blueprints.user.models import db, User, Services, Payments, client_user
from toyetjek.blueprints.client.models import Client, ClientPayment
from toyetjek.blueprints.page.models import Categories
from toyetjek.blueprints.invitation.models import Invitation
from toyetjek.blueprints.admin.forms import (
    SearchForm,
    BulkDeleteForm,
    UserForm,
    UploadForm,
    ServiceForm,
    PaymentForm,
    ClientPaymentForm,
    ClientForm,
    AssignClientForm,
    AddCategory,
    InvitationForm
)

admin = Blueprint('admin', __name__,
                  template_folder='templates', url_prefix='/admin')

@admin.before_request
@login_required
@role_required('admin')
def before_request():
    """ Protect all of the admin endpoints. """
    pass


# Dashboard -------------------------------------------------------------------
@admin.route('')
def dashboard():
    group_and_count_users = Dashboard.group_and_count_users()
    group_and_count_clients = Dashboard.group_and_count_clients()
    group_and_count_invitations = Dashboard.group_and_count_invitations()

    #Ashgabat Region
    user_total_payments = db.session.query(func.sum(Payments.amount).label('total')).filter(Payments.user_id == User.id).filter(User.region == 'Ashgabat').all()
    client_total_payments = db.session.query(func.sum(ClientPayment.amount).label('total')).filter(ClientPayment.client_id == Client.id).filter(Client.region == 'Ashgabat').all()
    invitation_total_payments = db.session.query(func.sum(Invitation.payment)).filter(Invitation.region == 'Ashgabat').all()

    #Dashoguz Region
    dz_user_total_payments = db.session.query(func.sum(Payments.amount).label('dz_total')).filter(Payments.user_id == User.id).filter(User.region == 'Dashoguz').all()
    dz_client_total_payments = db.session.query(func.sum(ClientPayment.amount).label('dz_total')).filter(ClientPayment.client_id == Client.id).filter(Client.region == 'Dashoguz').all()
    dz_invitation_total_payments = db.session.query(func.sum(Invitation.payment)).filter(Invitation.region == 'Dashoguz').all()

    #Balkanabat Region
    bn_user_total_payments = db.session.query(func.sum(Payments.amount).label('bn_total')).filter(Payments.user_id == User.id).filter(User.region == 'Balkanabat').all()
    bn_client_total_payments = db.session.query(func.sum(ClientPayment.amount).label('bn_total')).filter(ClientPayment.client_id == Client.id).filter(Client.region == 'Balkanabat').all()
    bn_invitation_total_payments = db.session.query(func.sum(Invitation.payment)).filter(Invitation.region == 'Balkanabat').all()

    print (user_total_payments[0])
    print (dz_user_total_payments[0])

    return render_template('admin/page/dashboard.html',
                           group_and_count_users=group_and_count_users, 
                           group_and_count_clients=group_and_count_clients,
                           group_and_count_invitations=group_and_count_invitations,
                           user_total = user_total_payments[0],
                           client_total = client_total_payments[0],
                           invitation_total = invitation_total_payments[0],
                           dz_user_total = dz_user_total_payments[0],
                           dz_client_total = dz_client_total_payments[0],
                           dz_invitation_total = dz_invitation_total_payments[0],
                           bn_user_total = bn_user_total_payments[0],
                           bn_client_total = bn_client_total_payments[0],
                           bn_invitation_total = bn_invitation_total_payments[0])


# Users -----------------------------------------------------------------------
@admin.route('/users', defaults={'page': 1})
@admin.route('/users/page/<int:page>')
def users(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = User.sort_by(request.args.get('sort', 'created_on'),
                           request.args.get('direction', 'desc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_users = User.query \
        .filter(User.search(request.args.get('q', ''))) \
        .order_by(User.role.asc(), text(order_values)) \
        .paginate(page, 50, True)

    return render_template('admin/user/index.html',
                           form=search_form, bulk_form=bulk_form,
                           users=paginated_users)

# Clients ---------------------------------------------------------------------
@admin.route('/clients', defaults={'page': 1})
@admin.route('/clients/page/<int:page>')
def clients(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Client.sort_by(request.args.get('sort', 'created_on'),
                             request.args.get('direction','desc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_clients = Client.query \
        .filter(Client.search(request.args.get('q', ''))) \
        .order_by(Client.status.asc(), text(order_values)) \
        .paginate(page, 50, True)

    return render_template('admin/client/index.html',
                            form=search_form, bulk_form=bulk_form,
                            clients=paginated_clients)

# User Operations ---------------------------------------------------------------
@admin.route('/users/upload/<int:id>', methods=['GET', 'POST'])
def users_uploads(id):

    user = User.query.get(id)
    form = UploadForm()
    folder_name = user.username
    target = os.path.join(os.getcwd() + '/toyetjek/static/images/uploads/{}'.format(folder_name))

    if not os.path.isdir(target):
            os.mkdir(target)

    if user.image_count == None:
        count = 1
    else:
        count = user.image_count

    if form.validate_on_submit():

        for photo in request.files.getlist("photo"):

            ext = os.path.splitext(photo.filename)[1]
            if (ext == ".jpg") or (ext == ".jpeg") or (ext == ".png"):
                filename = folder_name + '_{}'.format(count) + ext
            else:
                return render_template('admin/user/upload.html', msg = "Image format is not supported!", form=form, user=user)
            destination = "/".join([target, filename])
            photo.save(destination)
            count+=1

        user.image_name = filename
        user.image_count = count
        user.save()

        return redirect(url_for('admin.users_uploads', id=user.id))

    image_names = os.listdir(os.getcwd() + '/toyetjek/static/images/uploads/{}'.format(folder_name))

    return render_template('admin/user/upload.html', form=form, user=user, images=image_names)

@admin.route('/users/delete_images/<int:id>/<string:image_name>')
def delete_images(id, image_name):
    user = User.query.get(id)
    current_filename = os.getcwd() + '/toyetjek/static/images/uploads/' + user.username + '/{}'.format(image_name)
    count = user.image_count

    if os.path.exists(current_filename):
        os.remove(current_filename)
        count-=1
        user.image_count = user.image_count - count
        user.save()
    else:
        user.image_count = None
        user.save()

    return redirect(url_for('admin.users_uploads', id=user.id))


@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
def users_edit(id):
    user = User.query.get(id)
    form = UserForm(obj=user)

    if form.validate_on_submit():

        if User.is_last_admin(user,
                              request.form.get('role'),
                              request.form.get('active')):
            flash('You are the last admin, you cannot do that.', 'error')
            return redirect(url_for('admin.users'))

        form.populate_obj(user)

        if not user.username:
            user.username = None

        user.save()

        flash('User has been saved successfully.', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/user/edit.html', form=form, user=user)


@admin.route('/users/bulk_delete', methods=['POST'])
def users_bulk_delete():
    form = BulkDeleteForm()
    

    if form.validate_on_submit():
        ids = User.get_bulk_action_ids(request.form.get('scope'),
                                       request.form.getlist('bulk_ids'),
                                       omit_ids=[current_user.id],
                                       query=request.args.get('q', ''))
            
        delete_count = User.bulk_delete(ids)

        flash('{0} user(s) were scheduled to be deleted.'.format(delete_count),
              'success')
    else:
        flash('No users were deleted, something wrong.', 'error')

    return redirect(url_for('admin.users'))

@admin.route('/users/add_service/<int:id>', methods=['GET', 'POST'])
def add_service(id):
    user = User.query.get(id)
    form = ServiceForm()
    service = Services()

    if form.validate_on_submit():
        service.user_id = user.id
        service.description = request.form.get('description')
        service.price = request.form.get('price')
        service.save()

        flash('The service was added successfully', 'success')
        return redirect(url_for('admin.service_list', user_id=user.id))


    return render_template('admin/user/add_service.html', form=form, service=service, user=user)

@admin.route('/users/service_list/<int:user_id>')
def service_list(user_id):
    user = User.query.get(user_id)
    services = Services.query.filter(Services.user_id == user.id)
    return render_template('admin/user/list_services.html', service=services, user=user)

@admin.route('/users/edit_service/<int:id>', methods=['GET','POST'])
def edit_service(id):
    service = Services.query.get(id)
    form = ServiceForm(obj=service)

    if form.validate_on_submit():
        form.populate_obj(service)
        service.save()

        flash('Service is successfully updated', 'success')
        return redirect(url_for('admin.service_list', user_id=service.user_id))
        
    return render_template('admin/user/edit_service.html', form=form, service=service)


@admin.route('/users/delete_service/<int:id>')
def delete_service(id):
    service = Services.query.get(id)
    service.delete()
    flash('The service is deleted successfully!', 'success')
    return redirect(url_for('admin.service_list', user_id=service.user_id))

@admin.route('/users/payments/<int:user_id>')
def payments(user_id):
    user = User.query.get(user_id)
    payments = Payments.query.filter(Payments.user_id == user.id).all()
    total_payments = db.session.query(func.sum(Payments.amount).label('total')).filter(Payments.user_id == User.id).filter(User.region == user.region).all()

    return render_template('admin/user/payments.html', payments=payments, user=user, total_payment = total_payments[0])

@admin.route('/users/add_payment/<int:id>', methods=['GET','POST'])
def add_payment(id):
    user = User.query.get(id)
    form = PaymentForm()
    payment = Payments()

    if form.validate_on_submit():
        payment.user_id = user.id
        payment.amount = request.form.get('amount')
        payment.reason = request.form.get('reason')
        payment.save()

        flash('The payment was added successfully', 'success')
        return redirect(url_for('admin.payments', user_id=user.id))


    return render_template('admin/user/add_payment.html', form=form, payment=payment, user=user)

@admin.route('/users/assign_client/<int:id>', methods=['GET','POST'])
def assign_client(id):
    user = User.query.get(id)
    client = Client.query.get(id)
    form = AssignClientForm()
    form.assign_client.choices=[(c.id, c.nickname) for c in Client.query.all()]
    choice = form.assign_client.data

    if form.validate_on_submit():
        cl=client_user.insert().values(user_id=user.id, client_id=form.assign_client.data)
        db.session.execute(cl)
        db.session.commit()
        return redirect(url_for('admin.client_list', id=user.id)) 

    return render_template('admin/user/assign_client.html', client=client, form=form, user=user)


@admin.route('/users/<int:user_id>/unassign_client/<int:client_id>')
def unassign_client(user_id, client_id):

    user = User.query.get(user_id)
    client = Client.query.get(client_id)


    user.clients.remove(client)
    db.session.commit()


    '''q = "DELETE FROM client_user WHERE client_id={}".format(client_id)
    r = db.engine.execute(q)'''

    flash('Client {} unassigned successfully'.format(client.nickname), 'success')


    return redirect(url_for('admin.client_list', id=user.id))


@admin.route('/users/client_list/<int:id>')
def client_list(id):

    user = User.query.get(id)
    return render_template('admin/user/client_list.html', user=user)

# Client Operations -------------------------------------------------------------------------------------------------

@admin.route('/clients/edit/<int:id>', methods=['GET', 'POST'])
def clients_edit(id):
    client = Client.query.get(id)
    form = ClientForm(obj=client)

    if form.validate_on_submit():

        form.populate_obj(client)

        if not client.nickname:
            client.nickname = None

        client.save()

        flash('Client has been saved successfully.', 'success')
        return redirect(url_for('admin.clients'))

    return render_template('admin/client/edit.html', form=form, client=client)

@admin.route('/clients/bulk_delete', methods=['POST'])
def clients_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Client.get_bulk_action_ids(request.form.get('scope'),
                                       request.form.getlist('bulk_ids'),
                                       query=request.args.get('q', ''))

        delete_count = Client.bulk_delete(ids)

        flash('{0} client(s) were scheduled to be deleted.'.format(delete_count),
              'success')
    else:
        flash('No clients were deleted, something wrong.', 'error')

    return redirect(url_for('admin.clients'))

@admin.route('/clients/payments/<int:client_id>')
def client_payments(client_id):
    client = Client.query.get(client_id)
    payments = ClientPayment.query.filter(ClientPayment.client_id == client.id).all()
    total_payments = db.session.query(func.sum(ClientPayment.amount).label('total')).filter(ClientPayment.client_id == Client.id).filter(Client.region == client.region).all()

    return render_template('admin/client/payments.html', payments=payments, client=client, total_payment = total_payments[0])

@admin.route('/clients/add_payment/<int:id>', methods=['GET','POST'])
def client_add_payment(id):
    client = Client.query.get(id)
    form = ClientPaymentForm()
    payment = ClientPayment()

    if form.validate_on_submit():
        payment.client_id = client.id
        payment.amount = request.form.get('amount')
        payment.reason = request.form.get('reason')
        payment.save()

        flash('The payment was added successfully', 'success')
        return redirect(url_for('admin.client_payments', client_id=client.id))


    return render_template('admin/client/add_payment.html', form=form, payment=payment, client=client)

# Categories Section ------------------------------------------------------------------------------------------------
@admin.route('page/categories')
def categories():
    cats = Categories.query
    return render_template('admin/page/categories.html', cats=cats)

@admin.route('page/add_category', methods=['GET','POST'])
def add_category():
    cats = Categories()
    form = AddCategory()

    target = os.path.join(os.getcwd() + '/toyetjek/static/images/categories/')


    if not os.path.isdir(target):
            os.mkdir(target)

    if form.validate_on_submit():

        cats.category_name = request.form.get('category_name')

        for photo in request.files.getlist("photo"):

            ext = os.path.splitext(photo.filename)[1]
            if (ext == ".jpg") or (ext == ".jpeg") or (ext == ".png") or (ext == ".JPEG") or (ext == ".PNG"):
                filename =  cats.category_name + photo.filename
            else:
                return render_template('admin/page/add_category.html', msg = "Image format is not supported!", form=form,)
            destination = "/".join([target, filename])
            photo.save(destination)

        cats.image = filename
        cats.save()

        return redirect(url_for('admin.categories'))

    image = os.listdir(os.getcwd() + '/toyetjek/static/images/categories/')

    return render_template('admin/page/add_category.html', form=form, cats=cats, image=image)

@admin.route('page/edit_category/<int:id>', methods=['GET','POST'])
def edit_category(id):
    cat = Categories.query.get(id)
    form = AddCategory(obj=cat)

    target = os.path.join(os.getcwd() + '/toyetjek/static/images/categories/')

    if form.validate_on_submit():
        form.populate_obj(cat)
        for photo in request.files.getlist("photo"):

            ext = os.path.splitext(photo.filename)[1]
            if (ext == ".jpg") or (ext == ".jpeg") or (ext == ".png") or (ext == ".JPEG") or (ext == ".PNG"):
                filename = cat.category_name + photo.filename
                cat.image = filename
            else:
                cat.image = cat.image
                return render_template('admin/page/edit_category.html', id=cat.id, msg = "Image format is not supported!", form=form)
            destination = "/".join([target, filename])
            photo.save(destination)

        cat.save()

        flash('The Category was saved successfully','success')

    return render_template('admin/page/edit_category.html', form=form, cat=cat)

@admin.route('page/delete_category/<int:id>/<string:filename>')
def delete_category(id, filename):
    cat = Categories.query.get(id)

    current_filename = os.getcwd() + '/toyetjek/static/images/categories/' + filename

    os.remove(current_filename)

    cat.delete()

    flash('The Category was deleted successfully', 'success')

    return redirect(url_for('admin.categories'))

# Invitation section -------------------------------------------------------------------------------------------
@admin.route('/invitations', defaults={'page': 1})
@admin.route('/invitations/page/<int:page>')
def invitations(page):
    search_form = SearchForm()
    bulk_form = BulkDeleteForm()

    sort_by = Invitation.sort_by(request.args.get('sort', 'created_on'),
                           request.args.get('direction', 'desc'))
    order_values = '{0} {1}'.format(sort_by[0], sort_by[1])

    paginated_invitations = Invitation.query \
        .filter(Invitation.search(request.args.get('q', ''))) \
        .order_by(Invitation.wedding_date.asc(), text(order_values)) \
        .paginate(page, 50, True)

    return render_template('admin/invitation/index.html',
                           form=search_form, bulk_form=bulk_form,
                           invitations=paginated_invitations)

@admin.route('/invitations/bulk_delete', methods=['POST'])
def invitations_bulk_delete():
    form = BulkDeleteForm()

    if form.validate_on_submit():
        ids = Invitation.get_bulk_action_ids(request.form.get('scope'),
                                       request.form.getlist('bulk_ids'),
                                       query=request.args.get('q', ''))

        delete_count = Invitation.bulk_delete(ids)
        flash('{0} invitation(s) were scheduled to be deleted.'.format(delete_count),
              'success')
    else:
        flash('No invitations were deleted, something wrong.', 'error')

    return redirect(url_for('admin.invitations'))

@admin.route('/invitations/edit/<int:id>', methods=['GET','POST'])
def invitation_edit(id):
    inv = Invitation.query.get(id)
    form = InvitationForm(obj=inv)
    #foldername = str(inv.names[:2])

    target = os.path.join(os.getcwd() + '/toyetjek/static/images/invitations/')

    if not os.path.isdir(target):
        os.mkdir(target)

    if form.validate_on_submit():

        form.populate_obj(inv)

        for photo in request.files.getlist("photo"):
 
            ext = os.path.splitext(photo.filename)[1]
            if (ext == ".jpg") or (ext == ".jpeg") or (ext == ".png") or (ext == ".JPEG") or (ext == ".PNG"):
                filename =  photo.filename
                inv.image = filename
            else:
                return render_template('admin/invitation/edit.html', msg = "Image format is not supported!", form=form)
            destination = "/".join([target, filename])
            photo.save(destination)


        inv.save()

        flash('Invitation has been saved successfully.', 'success')
        return redirect(url_for('admin.invitations'))

    
    image = os.listdir(os.getcwd() + '/toyetjek/static/images/invitations/')

    return render_template('admin/invitation/edit.html', form=form, inv=inv, image=image)

@admin.route('invitations/delete_image/<int:id>')
def delete_invitation_image(id):
    inv = Invitation.query.get(id)

    current_filename = os.getcwd() + '/toyetjek/static/images/invitations/{}'.format(inv.image)

    if os.path.exists(current_filename):
        os.remove(current_filename)
        inv.image = None
        inv.save()
        flash('The photo deleted successfully','success')

    return redirect(url_for('admin.invitation_edit', id=inv.id))
