import unittest

from app import create_app
from app.modules.users.models import User
from app.utils.roles import Role


class TestUser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()

    def test_01_new_user_role_password(self):
        """ Create new user. Check if default role is set and password hashed
        """

        create_json = {"username": "username123", "password": "password123"}
        user = User.create(create_json, save=False, commit=False)

        assert user.role == Role.USER
        assert user.password != create_json["password"]

    def test_02_update_user(self):
        """ Update user. Check if username and password are changed """

        create_json = {"username": "username123", "password": "password123"}
        user = User.create(create_json, save=False, commit=False)
        prev_password = user.password

        update_json = {"username": "username321", "password": "password321"}

        user.update(update_json, commit=False)

        assert user.username == update_json["username"]
        assert user.password != update_json["password"]
        assert user.password != prev_password

    @classmethod
    def tearDownClass(cls):
        pass
