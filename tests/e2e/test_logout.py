import unittest

from app import create_app, db


class TestLogout(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = create_app()

        with app.app_context():
            db.drop_all()
            db.create_all()

        cls.client = app.test_client()

    def test_01_logout_anonymous(self):
        """ Logout being anonymous (not logged in) """

        result = self.client.get("/logout")

        assert result.status_code == 401

    def test_02_login_logout(self):
        """ login with valid username and password """

        data = {"username": "user", "password": "password"}

        # Create valid user first
        self.client.post("/register", json=data)

        self.client.post("/login", json=data)

        # Session cookie is attached to the test client
        logout = self.client.get("/logout", json=data)

        assert logout.status_code == 204

    @classmethod
    def tearDownClass(cls):
        pass
