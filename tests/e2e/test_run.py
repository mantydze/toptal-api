import random
import unittest
import datetime

from app import create_app, db
from app.utils.roles import Role


class TestRun(unittest.TestCase):

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

    def login_user(self):
        self.client.get("/logout")
        user_data = {'username': 'user1', 'password': 'password1'}
        user = self.client.post("/login", json=user_data)
        return user.get_json()

    def login_manager(self):
        self.client.get("/logout")
        user_data = {'username': 'manager1', 'password': 'password1'}
        user = self.client.post("/login", json=user_data)
        return user.get_json()

    def login_admin(self):
        self.client.get("/logout")
        user_data = {'username': 'admin1', 'password': 'password1'}
        user = self.client.post("/login", json=user_data)
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

        user = self.login_user()

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
        """ Login as USER and create Run for other User """

        manager = self.login_manager()
        self.login_user()

        run_data = {
            "user_id": manager["data"]["user_id"],
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

        user = self.login_user()
        self.login_admin()

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

        user = self.login_user()

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

        self.login_admin()

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


if __name__ == '__main__':
    unittest.main()
