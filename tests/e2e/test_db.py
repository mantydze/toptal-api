import string
import random
import unittest

from app import create_app, db
from app.utils.roles import Role


class TestDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.drop_all()

    def create_user(self, role=Role.USER, login=True):
        name = "".join(random.choice(string.ascii_letters) for i in range(8))
        data = {"username": name, "password": name}
        user = self.client.post("/register", json=data)

        with self.app.app_context():
            db.engine.execute("""
                    UPDATE USER
                    SET ROLE="{role}"
                    WHERE USERNAME = '{name}'""".format(role=role, name=name))

        if login:
            user = self.client.post("/login", json=data)

        return user.get_json()

    @classmethod
    def tearDownClass(cls):
        pass
