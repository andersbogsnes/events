import json

from app.model import User, db
from tests.utils import BaseTestClass


class TestApi(BaseTestClass):
    def test_index_exists(self):
        resp = self.client.get('/')

        self.assertEqual(200, resp.status_code)
        self.assertEqual("Here will be usage instructions for api", resp.data.decode('utf-8'))

    def test_create_user_and_get_created_user(self):
        # Make sure we have a clean database for this test
        with self.app.app_context():
            db.drop_all()
            db.create_all()
        resp = self.client.post('/user', data=json.dumps(self.test_users[0]))
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, self.json_body(resp)["success"])

        resp = self.client.get("/user/1")
        data = self.json_body(resp)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, data["id"])
        self.assertEqual(self.test_users[0]["name"], data["name"])
        self.assertEqual(1, data["turn"])

    def test_posting_invalid_data_to_user(self):
        resp = self.client.post('/user')
        data = self.json_body(resp)
        self.assertEqual(401, resp.status_code)
        self.assertIn("error", data)

    def test_get_multiple_users(self):
        resp = self.client.get("/users")
        data = self.json_body(resp)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(3, len(data))
        self.assertEqual(self.test_users[0]["name"], data[0]["name"])
        self.assertEqual(self.test_users[1]["phone"], data[1]["phone"])
        self.assertEqual(1, data[0]["id"])
        self.assertEqual(2, data[1]["id"])
        self.assertEqual(1, data[0]["turn"])
        self.assertEqual(2, data[1]["turn"])

    def test_get_turn(self):
        resp = self.client.get('/turn/1')
        data = self.json_body(resp)

        self.assertEqual(200, resp.status_code)
        self.assertEqual(1, data["id"])

    def test_get_next_turn(self):
        resp = self.client.get("/turn")
        data = self.json_body(resp)
        self.assertEqual(200, resp.status_code)
        self.assertEqual(self.test_users[0]["name"], data["name"])

    def test_complete_turn_for_user(self):
        # Get current turn
        resp = self.client.get('/turn')
        self.assertEqual(200, resp.status_code)

        # Current turn should be turn_nr 1
        self.assertEqual(1, self.json_body(resp)["id"])

        # Turn_nr 4 should not exist
        resp = self.client.get('/turn/4')
        self.assertEqual(404, resp.status_code)
        self.assertIn("error", self.json_body(resp))

        # Mark current turn as done
        resp = self.client.put('/turn/done')
        self.assertEqual(201, resp.status_code)

        # Check that new current turn is turn_nr 2
        resp = self.client.get('/turn')
        self.assertEqual(2, self.json_body(resp)["id"])

        # If done is called again, new turn_nr should be 3
        resp = self.client.put('/turn/done')
        self.assertEqual(201, resp.status_code)

        resp = self.client.get('/turn')
        self.assertEqual(3, self.json_body(resp)["id"])


    def test_api_call_for_signing_up_for_event(self):
        data = {
            "signed_up": 2
        }

        resp = self.client.put('/turn/signup/1', data=json.dumps(data))
        self.assertEqual(201, resp.status_code)

        resp = self.client.get('/turn/1')
        self.assertEqual(200, resp.status_code)
        self.assertIn(2, self.json_body(resp)["signed_up"])

    def test_api_call_for_withdrawing_from_signed_up_event(self):
        pass