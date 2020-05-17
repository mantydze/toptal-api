import unittest

from app import create_app
from app.modules.users.models import User
from app.utils.roles import Role


class TestUser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()

        cls.input_json = {"username": "username123", "password": "password123"}
        cls.user = User.create(cls.input_json, save_commit=False)

    def test_01_check_role(self):
        assert self.user.role == Role.USER

    def test_02_check_password(self):
        assert self.user.password != self.input_json["password"]

    @classmethod
    def tearDownClass(cls):
        pass
