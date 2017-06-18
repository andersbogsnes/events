import json
from app.model import User
import unittest
from app.config import TestConfig
from app.main import create_app
from app.model import db


class BaseTestClass(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

        self.test_users = [{"name": "Test Mctesterson", "email": "test@tester.com", "phone": 123456},
                           {"name": "Sons Sonsserson", "email": "son@sonsserion.com", "phone": 239874},
                           {"name": "Mr Superson", "email": "mr@superson.com", "phone": 2133435}]
        self.create_all_users()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    @staticmethod
    def json_body(resp):
        return json.loads(resp.data.decode('utf-8'))

    def create_user(self, user_data):
        with self.app.app_context():
            User.create(**user_data)

    def create_all_users(self):
        for user in self.test_users:
            self.create_user(user)
