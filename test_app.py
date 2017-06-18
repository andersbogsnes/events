import unittest
from main import create_app
from model import db, User, Turns,swap_turn
from config import TestConfig
import json


def json_body(resp):
    return json.loads(resp.data.decode('utf-8'))


def create_user(user_data, app):
    with app.app_context():
        User.create(**user_data)


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

    def test_index_exists(self):
        resp = self.client.get('/')

        self.assertEqual(200, resp.status_code)
        self.assertEqual("Here will be usage instructions for api", resp.data.decode('utf-8'))

    def test_create_user_and_get_created_user(self):
        resp = self.client.post('/user', data=json.dumps(self.test_users[0]))
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, json_body(resp)["success"])

        resp = self.client.get("/user/1")
        data = json_body(resp)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, data["id"])
        self.assertEqual(self.test_users[0]["name"], data["name"])
        self.assertEqual(1, data["turn"])

    def test_user_repr_is_as_expected(self):
        for user in self.test_users:
            create_user(user, self.app)

        with self.app.app_context():
            user = User.query.get(1)
            self.assertEqual("<User Test Mctesterson>", user.__repr__())

    def test_posting_invalid_data_to_user(self):
        resp = self.client.post('/user')
        data = json_body(resp)
        self.assertEqual(401, resp.status_code)
        self.assertIn("error", data)

    def test_get_multiple_users(self):
        for user in self.test_users:
            create_user(user, self.app)
        resp = self.client.get("/users")
        data = json_body(resp)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(2, len(data))
        self.assertEqual(self.test_users[0]["name"], data[0]["name"])
        self.assertEqual(self.test_users[1]["phone"], data[1]["phone"])
        self.assertEqual(1, data[0]["id"])
        self.assertEqual(2, data[1]["id"])
        self.assertEqual(1, data[0]["turn"])
        self.assertEqual(2, data[1]["turn"])

    def test_turn_nr_is_initialized_on_user(self):
        create_user(self.test_users[0], self.app)
        with self.app.app_context():
            user = User.query.get(1)
            self.assertEqual(1, user.turn.turn_id)

    def test_turn_is_incremented_correctly(self):
        for user in self.test_users:
            create_user(user, self.app)

        with self.app.app_context():
            users = db.session.query(User).all()
            turns = db.session.query(Turns).all()
            self.assertEqual(1, users[0].turn.turn_id)
            self.assertEqual(2, users[1].turn.turn_id)
            self.assertEqual(self.test_users[0]["name"], turns[0].user.name)
            self.assertEqual(self.test_users[1]["phone"], turns[1].user.phone)

    def test_find_next_turn(self):
        for user in self.test_users:
            create_user(user, self.app)

        with self.app.app_context():
            next_turn = Turns.next_turn()
            self.assertEqual(self.test_users[0]["name"], next_turn.user.name)

            first_user = db.session.query(User).first()
            first_user.turn.finished = True
            db.session.add(first_user)
            db.session.commit()

            next_turn = Turns.next_turn()
            self.assertEqual(self.test_users[1]["name"], next_turn.user.name)

    def test_get_turn(self):
        for user in self.test_users:
            create_user(user, self.app)

        resp = self.client.get('/turn/1')
        data = json_body(resp)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, data["id"])

    def test_get_next_turn(self):
        for user in self.test_users:
            create_user(user, self.app)

        resp = self.client.get("/turn")
        data = json_body(resp)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.test_users[0]["name"], data["name"])

        # Test if turns "roll over" when exceeding max
        with self.app.app_context():
            users = db.session.query(User).all()
            for user in users:
                user.turn.finished = True
                db.session.add(user)
            db.session.commit()

            # Make sure that first user turn is now finished
            user = User.query.get(1)
            self.assertEqual(True, user.turn.finished)

            resp = self.client.get("/turn")
            data = json_body(resp)

            self.assertEqual(1, data["id"])
            self.assertEqual(self.test_users[0]["name"], data["name"])
            user = db.session.query(User).filter_by(id=1).first()
            self.assertEqual(False, user.turn.finished)

    def test_mark_turn_as_completed(self):
        for user in self.test_users:
            create_user(user, self.app)

        resp = self.client.put('/turn/1', data=json.dumps({"finished": True}))
        data = json_body(resp)
        self.assertEqual(200, resp.status_code)
        self.assertTrue(data["finished"])

        with self.app.app_context():
            user = db.session.query(User).filter_by(id=1).first()
            self.assertTrue(user.turn.finished)

    def test_that_turn_pop_sets_old_turn_as_finished_and_adds_new(self):
        for user in self.test_users:
            create_user(user, self.app)

        with self.app.app_context():
            user = User.query.get(1)
            self.assertEqual(1, user.turn.turn_id)

            Turns.pop(user.id)
            user = User.query.get(1)
            self.assertEqual(3, user.turn.turn_id)

            turns = Turns.query.filter(Turns.user_id == user.id).all()
            self.assertTrue(1, len(turns))
            self.assertFalse(turns[0].finished)
            self.assertEqual(1, turns[0].user.id)

    def test_swapping_turns_between_users_works_as_expected(self):
        for user in self.test_users:
            create_user(user, self.app)

        with self.app.app_context():
            user = User.query.get(1)
            self.assertFalse(user.turn.finished)
            user2 = User.query.get(2)
            self.assertFalse(user2.turn.finished)

            turn1_id = user.turn.turn_id
            turn2_id = user2.turn.turn_id

            swap_turn(user, user2)

            user = User.query.get(1)
            self.assertEqual(turn2_id, user.turn.turn_id)
            self.assertEqual(turn1_id, user2.turn.turn_id)

            turn1 = Turns.query.get(turn1_id)
            self.assertEqual(user2.id, turn1.user.id)
            turn2 = Turns.query.get(turn2_id)
            self.assertEqual(user.id, turn2.user.id)
