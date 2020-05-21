import string
import random
import datetime
import unittest

from app import create_app, db
from app.utils.roles import Role


class TestUser(unittest.TestCase):

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

    def test_000_user_index(self):
        """ Login as USER and access endpoint /users """

        user = self.create_user()
        user = user["data"]

        result = self.client.get("/whoami")
        assert result.status_code == 200

        result = result.get_json()

        assert user["username"] == result["username"]

    def test_010_user_view_users(self):
        """ Login as USER and access endpoint /users """

        self.create_user()
        result = self.client.get("/users")
        assert result.status_code == 302

    def test_011_user_view_users(self):
        """ Login as USER and access endpoint /users """

        self.create_user()
        result = self.client.get("/users", follow_redirects=True)
        assert result.status_code == 200

    def test_012_user_view_other_user(self):
        """ Login as USER and access other user profile """

        user = self.create_user(login=False)
        user_id = user["data"]["user_id"]

        self.create_user()
        result = self.client.get("/users/{}".format(user_id))
        assert result.status_code == 403

    def test_012_manager_view_other_manager(self):
        """ Login as MANAGER and access other MANAGER profile """

        manager = self.create_manager(login=False)
        manager_id = manager["data"]["user_id"]

        self.create_manager()
        result = self.client.get("/users/{}".format(manager_id))
        assert result.status_code == 403

    def test_020_manager_view_users(self):
        """ Login as MANAGER and access endpoint /users.
            Should receive only USERS and self
        """

        manager = self.create_manager()
        manager_id = manager["data"]["user_id"]

        result = self.client.get("/users")
        rows = result.get_json()["data"]

        # Result set must be not empty
        assert len(rows) > 0

        for row in rows:
            # Resultset must containt only one manager - self
            if row["role"] == Role.MANAGER:
                assert row["user_id"] == manager_id
            else:
                # All remaining rows must containt USERs only
                assert row["role"] == Role.USER

    def test_030_user_update_self(self):
        """ Login as USER and update self """

        user = self.create_user()
        user_id = user["data"]["user_id"]
        data = {"username": "user11", "password": "password11"}
        result = self.client.put("/users/{}".format(user_id), json=data)
        result_user = result.get_json()["data"]

        assert result.status_code == 200
        assert result_user["username"] == data["username"]

    def test_031_user_login_after_update(self):
        """ Folloup on 041. Login with new credentials """

        data = {"username": "user11", "password": "password11"}
        result = self.client.post("/login", json=data)
        assert result.status_code == 200

    def test_032_user_update_user(self):
        """ Login as USER and update USER """

        user = self.create_user(login=False)
        user_id = user["data"]["user_id"]
        self.create_user()
        data = {"username": "user111", "password": "password11"}
        result = self.client.put("/users/{}".format(user_id), json=data)

        assert result.status_code == 403

    def test_033_user_update_duplicate(self):
        """ Login as USER and update self with duplicate name """

        user = self.create_user(login=False)
        data = {"username": user["data"]["username"], "password": "password11"}

        my_user = self.create_user()
        my_id = my_user["data"]["user_id"]
        result = self.client.put("/users/{}".format(my_id), json=data)

        assert result.status_code == 400

    def test_040_manager_update_user(self):
        """ Login as MANAGER and update USER """

        user = self.create_user(login=False)
        user_id = user["data"]["user_id"]
        self.create_manager()
        data = {"username": "user22", "password": "password22"}
        result = self.client.put("/users/{}".format(user_id), json=data)
        updated_user = result.get_json()["data"]

        assert result.status_code == 200
        assert updated_user["username"] == data["username"]

    def test_041_manager_update_manager(self):
        """ Login as MANAGER and update MANAGER """

        manager = self.create_manager(login=False)
        manager_id = manager["data"]["user_id"]
        self.create_manager()
        data = {"username": "manager11", "password": "password11"}
        result = self.client.put("/users/{}".format(manager_id), json=data)

        assert result.status_code == 403

    def test_050_admin_update_user(self):
        """ Login as ADMIN and update USER """

        user = self.create_user(login=False)
        user_id = user["data"]["user_id"]
        self.create_admin()
        data = {"username": "user33", "password": "password33"}
        result = self.client.put("/users/{}".format(user_id), json=data)
        updated_user = result.get_json()["data"]

        assert result.status_code == 200
        assert updated_user["username"] == data["username"]

    def test_051_admin_update_manager(self):
        """ Login as ADMIN and update MANAGER """

        manager = self.create_manager(login=False)
        manager_id = manager["data"]["user_id"]
        self.create_admin()
        data = {"username": "manager55",
                "password": "password55",
                "role": Role.ADMIN}

        result = self.client.put("/users/{}".format(manager_id), json=data)
        updated_manager = result.get_json()["data"]

        assert result.status_code == 200
        assert updated_manager["username"] == data["username"]
        assert updated_manager["role"] == data["role"]

    def test_052_admin_update_admin(self):
        """ Login as ADMIN and update ADMIN """

        admin = self.create_admin(login=False)
        admin_id = admin["data"]["user_id"]
        self.create_admin()
        data = {"username": "admin55", "password": "password55"}
        result = self.client.put("/users/{}".format(admin_id), json=data)
        updated_admin = result.get_json()["data"]

        assert result.status_code == 200
        assert updated_admin["username"] == data["username"]

    def test_060_user_delete_self(self):
        """ Login as USER and delete self """

        user = self.create_user()
        user_id = user["data"]["user_id"]
        result = self.client.delete("/users/{}".format(user_id))

        assert result.status_code == 204

    def test_061_user_delete_user(self):
        """ Login as USER and delete USER """

        user = self.create_user(login=False)
        user_id = user["data"]["user_id"]
        self.create_user()
        result = self.client.delete("/users/{}".format(user_id))

        assert result.status_code == 403

    def test_062_user_delete_manager(self):
        """ Login as USER and delete MANAGER """

        manager = self.create_manager(login=False)
        manager_id = manager["data"]["user_id"]
        self.create_user()
        result = self.client.delete("/users/{}".format(manager_id))

        assert result.status_code == 403

    def test_063_user_delete_admin(self):
        """ Login as USER and delete ADMIN """

        admin = self.create_admin(login=False)
        admin_id = admin["data"]["user_id"]
        self.create_user()
        result = self.client.delete("/users/{}".format(admin_id))

        assert result.status_code == 403

    def test_071_manager_delete_user(self):
        """ Login as MANAGER and delete USER """

        user = self.create_user(login=False)
        user_id = user["data"]["user_id"]
        self.create_manager()
        result = self.client.delete("/users/{}".format(user_id))

        assert result.status_code == 204

    def test_072_manager_delete_manager(self):
        """ Login as MANAGER and delete MANAGER """

        manager = self.create_manager(login=False)
        manager_id = manager["data"]["user_id"]
        self.create_manager()
        result = self.client.delete("/users/{}".format(manager_id))

        assert result.status_code == 403

    def test_073_manager_delete_admin(self):
        """ Login as MANAGER and delete ADMIN """

        admin = self.create_admin(login=False)
        admin_id = admin["data"]["user_id"]
        self.create_manager()
        result = self.client.delete("/users/{}".format(admin_id))

        assert result.status_code == 403

    def test_080_admin_delete_user(self):
        """ Login as ADMIN and delete USER """

        user = self.create_user(login=False)
        user_id = user["data"]["user_id"]
        self.create_manager()
        result = self.client.delete("/users/{}".format(user_id))

        assert result.status_code == 204

    def test_081_admin_delete_manager(self):
        """ Login as ADMIN and delete MANAGER """

        manager = self.create_manager(login=False)
        manager_id = manager["data"]["user_id"]
        self.create_admin()
        result = self.client.delete("/users/{}".format(manager_id))

        assert result.status_code == 204

    def test_082_admin_delete_admin(self):
        """ Login as ADMIN and delete ADMIN """

        admin = self.create_admin(login=False)
        admin_id = admin["data"]["user_id"]
        self.create_admin()
        result = self.client.delete("/users/{}".format(admin_id))

        assert result.status_code == 204

    def test_090_user_view_report(self):
        """ Login as USER and view self report """

        user = self.create_user()
        user_id = user["data"]["user_id"]

        # Create few runs
        run_data = {
            "user_id": user_id,
            "date": datetime.date.today().isoformat(),
            "duration": random.randint(100, 1000),
            "distance": random.randint(100, 1000),
            "latitude": 54.687157,
            "longitude": 25.279652
        }
        self.client.post("/runs", json=run_data)
        self.client.post("/runs", json=run_data)

        result = self.client.get("/users/{}/report".format(user_id))
        assert result.status_code == 200

    def test_091_user_view_other_user_report(self):
        """ Login as USER and access other user report """

        user = self.create_user(login=False)
        user_id = user["data"]["user_id"]

        self.create_user()
        result = self.client.get("/users/{}/report".format(user_id))
        assert result.status_code == 403

    def test_092_manager_view_other_manager_report(self):
        """ Login as MANAGER and access other MANAGER report """

        manager = self.create_manager(login=False)
        manager_id = manager["data"]["user_id"]

        self.create_manager()
        result = self.client.get("/users/{}/report".format(manager_id))
        assert result.status_code == 403

    @classmethod
    def tearDownClass(cls):
        pass
