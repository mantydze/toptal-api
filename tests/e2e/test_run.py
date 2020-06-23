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
        self.client.environ_base.pop("HTTP_AUTHORIZATION", None)
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
            access_token = "Bearer " + user.get_json()["data"]["access_token"]
            self.client.environ_base["HTTP_AUTHORIZATION"] = access_token

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

        assert result.status_code == 201

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

        assert result.status_code == 201

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

    def test_07_view_runs_non_admin(self):
        """ Login as USER and VIEW runs """

        user = self.create_user()
        user_id = user["data"]["user_id"]

        run_data = {
            "user_id": user_id,
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        result = self.client.post("/runs", json=run_data)
        assert result.status_code == 201

        runs = self.client.get("/runs")
        assert runs.status_code == 200

    def test_08_create_run_view(self):
        """ Login as USER and create own Run and view it"""

        user = self.create_user()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        run = self.client.post("/runs", json=run_data)
        assert run.status_code == 201

        run_id = run.get_json()["data"]["run_id"]
        result = self.client.get("/runs/{}".format(run_id))
        assert result.status_code == 200

    def test_09_create_run_view_other(self):
        """ Login as USER and create own Run and view it with other USER"""

        user = self.create_user()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        run = self.client.post("/runs", json=run_data)
        assert run.status_code == 201

        self.create_user()

        run_id = run.get_json()["data"]["run_id"]
        result = self.client.get("/runs/{}".format(run_id))
        assert result.status_code == 403

    def test_10_create_run_delete(self):
        """ Login as USER and create own Run and delete it"""

        user = self.create_user()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        run = self.client.post("/runs", json=run_data)
        assert run.status_code == 201

        run_id = run.get_json()["data"]["run_id"]
        result = self.client.delete("/runs/{}".format(run_id))
        assert result.status_code == 204

    def test_11_create_run_delete_other(self):
        """ Login as USER and create own Run and delete it with other user"""

        user = self.create_user()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        run = self.client.post("/runs", json=run_data)
        assert run.status_code == 201

        self.create_user()

        run_id = run.get_json()["data"]["run_id"]
        result = self.client.delete("/runs/{}".format(run_id))
        assert result.status_code == 403

    def test_12_create_run_update(self):
        """ Login as USER and create own Run and update it"""

        user = self.create_user()

        run1_data = {
            "user_id": user["data"]["user_id"],
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        result1 = self.client.post("/runs", json=run1_data)
        assert result1.status_code == 201

        run1 = result1.get_json()["data"]
        run_id = run1["run_id"]

        run2_data = {
            "date": "2000-03-14",
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 48.856613,
            "longitude": 2.352222
        }
        result2 = self.client.put("/runs/{}".format(run_id), json=run2_data)
        assert result2.status_code == 200

        run2 = result2.get_json()["data"]

        keys = list(run1_data.keys()) + ["weather"]
        keys.remove("user_id")

        for key in keys:
            assert run1[key] != run2[key]

    def test_13_create_run_update_other(self):
        """ Login as USER and create own Run and update it with other user"""

        user = self.create_user()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        run = self.client.post("/runs", json=run_data)
        assert run.status_code == 201

        self.create_user()

        run_data.pop("user_id", None)

        run_id = run.get_json()["data"]["run_id"]
        result = self.client.put("/runs/{}".format(run_id), json=run_data)
        assert result.status_code == 403

    def test_14_create_invalid_run(self):
        """ Login as USER and create invalid run"""

        user = self.create_user()

        run_data = {
            "user_id": user["data"]["user_id"],
            "date": "3030-03-03",
            "duration": -10,
            "distance": -10,
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        run = self.client.post("/runs", json=run_data)
        assert run.status_code == 400

    def test_15_create_valid_run_nested_endpoint(self):
        """ Login as USER and create using nested enpoint run"""

        user = self.create_user()

        run_data = {
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }

        run = self.client.post(
            "/users/{}/runs".format(user["data"]["user_id"]), json=run_data)

        assert run.status_code == 201

    @classmethod
    def tearDownClass(cls):
        pass
