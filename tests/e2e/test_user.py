import unittest

from app import create_app, db
from app.utils.roles import Role


class TestUser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = create_app()
        cls.client = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

            # Create 10 users for each role
            for role in Role.roles():
                for i in range(1, 11):
                    data = {"username": "{}{}".format(role, i),
                            "password": "password{}".format(i)}

                    cls.client.post("/register", json=data)

                # Default role is USER, set MANAGER and ADMIN roles
                db.engine.execute("""
                    UPDATE USER
                    SET ROLE='{0}'
                    WHERE USERNAME LIKE '%{0}%'""".format(role))

    def test_01_simple_user(self):
        """ login as simple user and access enpoind /users """

        self.client.get("/logout")

        data = {'username': 'user1', 'password': 'password1'}
        self.client.post("/login", json=data)

        result = self.client.get("/users")

        assert result.status_code == 302

    def test_01_simple_user_follow_redirect(self):
        """ login as simple user and access enpoind /users """

        self.client.get("/logout")

        data = {'username': 'user1', 'password': 'password1'}
        self.client.post("/login", json=data)

        result = self.client.get("/users", follow_redirects=True)

        assert result.status_code == 200

    @classmethod
    def tearDownClass(cls):
        pass
