from app.model import db, User, Turns, EventSignupException
from tests.utils import BaseTestClass


class TestDataModel(BaseTestClass):
    def test_user_repr_is_as_expected(self):
        with self.app.app_context():
            user = User.query.get(1)
            self.assertEqual("<User Test Mctesterson>", user.__repr__())

    def test_turn_nr_is_initialized_on_user(self):
        with self.app.app_context():
            user = User.query.get(1)
            self.assertEqual(1, user.turn.turn_id)

    def test_turn_is_incremented_correctly(self):
        with self.app.app_context():
            users = db.session.query(User).all()
            turns = db.session.query(Turns).all()
            self.assertEqual(1, users[0].turn.turn_id)
            self.assertEqual(2, users[1].turn.turn_id)
            self.assertEqual(self.test_users[0]["name"], turns[0].user.name)
            self.assertEqual(self.test_users[1]["phone"], turns[1].user.phone)

    def test_get_next_turn(self):
        # TODO: Change finished Boolean to simple .first selection
        with self.app.app_context():
            next_turn = Turns.next_turn()
            self.assertEqual(self.test_users[0]["name"], next_turn.user.name)

    def test_that_turn_pop_sets_old_turn_as_finished_and_adds_new(self):
        with self.app.app_context():
            user = User.query.get(1)
            self.assertEqual(1, user.turn.turn_id)

            Turns.pop()
            user = User.query.get(1)
            self.assertEqual(4, user.turn.turn_id)

            turns = Turns.query.filter(Turns.user_id == user.id).all()
            self.assertTrue(1, len(turns))
            self.assertFalse(turns[0].finished)
            self.assertEqual(1, turns[0].user.id)

    def test_swapping_turns_between_users_works_as_expected(self):
        with self.app.app_context():
            user = User.query.get(1)
            self.assertFalse(user.turn.finished)
            user2 = User.query.get(2)
            self.assertFalse(user2.turn.finished)

            turn1_id = user.turn.turn_id
            turn2_id = user2.turn.turn_id

            user.swap_turn(user2)

            user = User.query.get(1)
            self.assertEqual(turn2_id, user.turn.turn_id)
            self.assertEqual(turn1_id, user2.turn.turn_id)

            turn1 = Turns.query.get(turn1_id)
            self.assertEqual(user2.id, turn1.user.id)
            turn2 = Turns.query.get(turn2_id)
            self.assertEqual(user.id, turn2.user.id)

    def test_signing_up_for_event_works_as_expected(self):
        # TODO: Block turns user from signing up to own turn
        with self.app.app_context():
            user2 = User.query.get(2)
            this_turn = Turns.next_turn()

            this_turn.signup(user2)

            this_turn = Turns.next_turn()
            self.assertIn(user2, this_turn.signed_up)
            self.assertEqual(user2.id, this_turn.signed_up[0].id)

            user2 = User.query.get(2)
            self.assertIn(this_turn, user2.signed_up_for)

    def test_change_signup_status_after_signup(self):
        # Sign up user2 for user1's event
        with self.app.app_context():
            user2 = User.query.get(2)
            current_turn = Turns.next_turn()

            current_turn.signup(user2)
            db.session.add(current_turn)
            db.session.commit()
            self.assertIn(current_turn, user2.signed_up_for)

            # Withdraw from signed up event
            current_turn.withdraw(user2)

            self.assertNotIn(current_turn, user2.signed_up_for)
            self.assertEqual(0, len(current_turn.signed_up))

    def test_sign_up_for_already_signed_up_event(self):
        with self.app.app_context():
            user2 = User.query.get(2)
            current_turn = Turns.next_turn()
            current_turn.signup(user2)
            self.assertIn(user2, current_turn.signed_up)

            self.assertRaises(EventSignupException, current_turn.signup, user2)

            self.assertIn(user2, current_turn.signed_up)
            self.assertEqual(1, len(current_turn.signed_up))

    def test_change_signup_status_when_user_not_already_signed_up(self):
        with self.app.app_context():
            user2 = User.query.get(2)
            current_turn = Turns.next_turn()

            # Make sure user not signed_up
            self.assertNotIn(user2, current_turn.signed_up)

            # Try to withdraw from event that user is not signed up for - should raise exception
            self.assertRaises(EventSignupException, current_turn.withdraw, user2)

            # User is still not signed up
            self.assertNotIn(user2, current_turn.signed_up)
