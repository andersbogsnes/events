import unittest
from main import create_app
from model import db, User
from config import TestConfig
import json


def json_body(resp):
    return json.loads(resp.data.decode('utf-8'))

def create_user(user_data, app, db):
    with app.app_context():
        user = User.create(**user_data)
        db.session.add(user)
        db.session.commit()


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

        self.test_users = [{"name": "Test Mctesterson", "email": "test@tester.com", "phone": 123456},
                           {"name": "Sons Sonsserson", "email": "son@sonsserion.com", "phone": 239874}]


    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_create_user_and_get_created_user(self):
        resp = self.client.post('/user', data=json.dumps(self.test_users[0]))
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, json_body(resp)["success"])

        resp = self.client.get("/user/1")
        data = json_body(resp)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, data["id"])
        self.assertEqual(self.test_users[0]["name"], data["name"])

    def test_get_multiple_users(self):
        for user in self.test_users:
            create_user(user, self.app, db)
        resp = self.client.get("/users")
        data = json_body(resp)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(2, len(data))
        self.assertEqual(self.test_users[0]["name"], data[0]["name"])
        self.assertEqual(self.test_users[1]["phone"], data[1]["phone"])
        self.assertEqual(1, data[0]["id"])
        self.assertEqual(2, data[1]["id"])

    def test_turn_nr_is_initialized_on_user(self):
        create_user(self.test_users[0], self.app, db)
        with self.app.app_context():
            user = db.session.query(User).first()
            self.assertEqual(1, user.turn)

    def test_turn_is_incremented_correctly(self):
        for user in self.test_users:
            create_user(user, self.app, db)

        with self.app.app_context():
            users = db.session.query(User).all()
            self.assertEqual(1, users[0].turn)
            self.assertEqual(2, users[1].turn)


