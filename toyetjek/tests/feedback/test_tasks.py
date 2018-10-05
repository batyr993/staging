from toyetjek.extensions import mail
from toyetjek.blueprints.feedback.tasks import deliver_contact_email


class TestTasks(object):
    def test_deliver_support_email(self):
        """ Deliver a contact email. """
        form = {
          'email': 'foo@bar.com',
          'message': 'Test feedback from toyetjek.com',
          'terms' : True
        }

        with mail.record_messages() as outbox:
            deliver_contact_email(form.get('email'), form.get('message'), form.get('terms'))

            assert len(outbox) == 1
            assert form.get('email') in outbox[0].body