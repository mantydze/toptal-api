import random
import string
import unittest
from app import create_app
from app.utils.query_string import QueryString
from app.utils.query_builder import QueryBuilder
from app.modules.users.models import User


class TestQueryBuilder(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def create_user(self, login=True):
        name = "".join(random.choice(string.ascii_letters) for i in range(8))
        data = {"username": name, "password": name}
        user = self.client.post("/register", json=data)

        if login:
            user = self.client.post("/login", json=data)

        return user.get_json()

    def test_1_valid_query(self):
        """ Parse valid query and build Query"""

        self.create_user(login=False)
        self.create_user(login=False)
        self.create_user()

        qs_parts = []
        qs_parts.append("page[size]=1")
        qs_parts.append("page[number]=2")
        qs_parts.append("sort=username,-user_id")
        qs_parts.append("filter=(username ne 'abc') OR (username ne 'bca')")

        qs = QueryString("?" + "&".join(qs_parts), User.public)
        qs.parse()

        self.app.config["SERVER_NAME"] = "http://localhost"
        with self.app.app_context():
            qb = QueryBuilder(qs, User)
            qb.build_query()

    @classmethod
    def tearDownClass(cls):
        pass
