from lib.flask_mailplus import send_template_message
from toyetjek.app import create_celery_app

celery = create_celery_app()


@celery.task()
def deliver_contact_email(email, message, terms):
    """
    Send a contact e-mail.

    :param email: E-mail address of the visitor
    :type user_id: str
    :param message: E-mail message
    :type user_id: str
    :return: None
    """
    ctx = {'email': email, 'message': message, 'terms': terms}

    send_template_message(subject='[toyetjek.com] Feedback',
                          sender=email,
                          recipients=[celery.conf.get('MAIL_USERNAME')],
                          reply_to=email,
                          template='feedback/mail/index', ctx=ctx)

    return None