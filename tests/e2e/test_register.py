import unittest

from app import create_app, db


class TestRegister(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = create_app()

        with app.app_context():
            db.drop_all()
            db.create_all()

        cls.client = app.test_client()

    def test_01_register_valid(self):
        """ Register with valid username and password """

        data = {'username': 'user', 'password': 'password'}
        result = self.client.post("/register", json=data)
        assert result.status_code == 200

    def test_02_register_duplicate(self):
        """ Register with duplicate username """
        data = {'username': 'user', 'password': 'password'}
        result = self.client.post("/register", json=data)
        assert result.status_code == 400

    def test_03_register_empty_username(self):
        """ Register with empty username """
        data = {'username': '', 'password': 'password'}
        result = self.client.post("/register", json=data)
        assert result.status_code == 400

    def test_04_register_empty_password(self):
        """ Register with empty password """
        data = {'username': 'username', 'password': ''}
        result = self.client.post("/register", json=data)
        assert result.status_code == 400

    def test_05_register_long_username(self):
        """ Register with too long username """
        data = {'username': '123456789012345678901234', 'password': 'password'}
        result = self.client.post("/register", json=data)
        assert result.status_code == 400

    def test_06_register_long_password(self):
        """ Register with too long password """
        data = {'username': 'username', 'password': '123456789012345678901234'}
        result = self.client.post("/register", json=data)
        assert result.status_code == 400

    def test_07_register_invalid_input(self):
        """ Register with no credentials """
        data = {}
        result = self.client.post("/register", json=data)
        assert result.status_code == 400

    @classmethod
    def tearDownClass(cls):
        pass
