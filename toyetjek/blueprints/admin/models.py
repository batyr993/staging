from sqlalchemy import func

from toyetjek.blueprints.user.models import db, User, Payments
from toyetjek.blueprints.client.models import Client
from toyetjek.blueprints.invitation.models import Invitation


class Dashboard(object):
    @classmethod
    def group_and_count_users(cls):
        """
        Perform a group by/count on all users.

        :return: dict
        """
        return Dashboard._group_and_count(User, User.role)

    @classmethod
    def group_and_count_clients(cls):
        """
        Perform a group by/count on all subscriber types.

        :return: dict
        """
        return Dashboard._group_and_count(Client, Client.status)

    @classmethod
    def group_and_count_invitations(cls):
        """
        Perform a group by/count on all subscriber types.

        :return: dict
        """
        return Dashboard._group_and_count(Invitation, Invitation.confirmed)

    @classmethod
    def group_and_count_payments(cls):

        return Dashboard._group_and_count(Payments, Payments.amount)


    @classmethod
    def _group_and_count(cls, model, field):
        """
        Group results for a specific model and field.

        :param model: Name of the model
        :type model: SQLAlchemy model
        :param field: Name of the field to group on
        :type field: SQLAlchemy field
        :return: dict
        """
        count = func.count(field)
        query = db.session.query(count, field).group_by(field).all()

        results = {
            'query': query,
            'total': model.query.count()
        }

        return results



