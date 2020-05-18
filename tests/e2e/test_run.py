import string
import random
import unittest
import datetime

from app import create_app, db
from app.utils.roles import Role


class TestRun(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.drop_all()
            db.create_all()

    def create_manager(self, login=True):
        return self.create_user(Role.MANAGER, login)

    def create_admin(self, login=True):
        return self.create_user(Role.ADMIN, login)

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

    def test_01_create_run_unauth(self):
        """ Create run without authorization """

        self.client.get("/logout")

        run_data = {
            "user_id": 0,
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        result = self.client.post("/runs", json=run_data)

        assert result.status_code == 401

    def test_02_create_run_user_self(self):
        """ Login as USER and create own Run """

        user = self.create_user()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        result = self.client.post("/runs", json=run_data)

        assert result.status_code == 200

    def test_03_create_run_user_other(self):
        """ Login as USER and create Run for other USER """

        user = self.create_user(login=False)
        self.create_user()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        result = self.client.post("/runs", json=run_data)

        assert result.status_code == 403

    def test_04_create_run_admin_other(self):
        """ Login as ADMIN and create Run for other User """

        user = self.create_user(login=False)
        self.create_admin()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        result = self.client.post("/runs", json=run_data)

        assert result.status_code == 200

    def test_05_create_run_invalid_data(self):
        """ Login as USER and create Run with invalid data """

        user = self.create_user()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": "2020-02-30",
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 504.687157,
            "longitude": 205.279652
        }

        result = self.client.post("/runs", json=run_data)

        assert result.status_code == 400

    def test_06_create_run_admin_nonexist(self):
        """ Login as ADMIN and create Run for non existing User """

        self.create_admin()

        run_data = {
            "user_id": 99999999,
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        result = self.client.post("/runs", json=run_data)

        assert result.status_code == 404

    @classmethod
    def tearDownClass(cls):
        pass
