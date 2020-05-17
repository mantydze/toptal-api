import unittest

from app import create_app, db


class TestLogin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = create_app()

        with app.app_context():
            db.drop_all()
            db.create_all()

        cls.client = app.test_client()

    def test_01_login_valid(self):
        """ login with valid username and password """

        data = {'username': 'user', 'password': 'password'}

        # Create valid user first
        result = self.client.post("/register", json=data)

        result = self.client.post("/login", json=data)
        assert result.status_code == 204

    def test_02_login_invalid_input(self):
        """ login with no credentials """
        data = {}
        result = self.client.post("/login", json=data)
        assert result.status_code == 400

    def test_03_login_empty_username(self):
        """ login with empty username """
        data = {'username': '', 'password': 'password'}
        result = self.client.post("/login", json=data)
        assert result.status_code == 400

    def test_04_login_empty_password(self):
        """ login with empty password """
        data = {'username': 'username', 'password': ''}
        result = self.client.post("/login", json=data)
        assert result.status_code == 400

    def test_05_login_long_username(self):
        """ login with too long username """
        data = {'username': '123456789012345678901234', 'password': 'password'}
        result = self.client.post("/login", json=data)
        assert result.status_code == 400

    def test_06_login_long_password(self):
        """ login with too long password """
        data = {'username': 'username', 'password': '123456789012345678901234'}
        result = self.client.post("/login", json=data)
        assert result.status_code == 400

    @classmethod
    def tearDownClass(cls):
        pass
