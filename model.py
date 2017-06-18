from flask_sqlalchemy import SQLAlchemy
import datetime as dt

db = SQLAlchemy()

signup_association = db.Table('signups',
                              db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                              db.Column('turn_id', db.Integer, db.ForeignKey('turns.turn_id')))


class EventSignupException(Exception):
    pass


def swap_turn(user1, user2):
    """
    Takes two users and swaps their turns
    :param user1: db.Model.User
    :param user2: db.Model.User
    :return: None
    """

    user2.turn, user1.turn = user1.turn, user2.turn
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.Integer)

    created_date = db.Column(db.DateTime, default=dt.datetime.today())
    last_updated = db.Column(db.DateTime, default=dt.datetime.today(), onupdate=dt.datetime.today())

    signed_up_for = db.relationship("Turns", secondary=signup_association, back_populates="signed_up")

    def __init__(self, name, email, phone=None):
        self.name = name
        self.email = email
        self.phone = phone

    def __repr__(self):
        return f"<User {self.name}>"

    @classmethod
    def create(cls, name, email, phone):
        user = cls(name=name, email=email, phone=phone)
        user.turn = Turns(finished=False)

        db.session.add(user)
        db.session.commit()
        return user

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "created": self.created_date,
            "turn": self.turn.turn_id,
            "finished": self.turn.finished
        }


class Turns(db.Model):
    __tablename__ = 'turns'

    turn_id = db.Column(db.Integer, primary_key=True)
    finished = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship("User", backref=db.backref("turn", cascade="all, delete-orphan", uselist=False))
    signed_up = db.relationship("User", secondary=signup_association, back_populates="signed_up_for")

    @classmethod
    def next_turn(cls):
        return cls.query.filter_by(finished=False).first()

    @classmethod
    def pop(cls):
        turn = Turns.next_turn()
        user = turn.user
        user.turn = cls(finished=False)
        db.session.add(user)
        db.session.commit()

    def signup(self, user):
        if user not in self.signed_up:
            self.signed_up.append(user)
            db.session.add(self)
            db.session.commit()
        else:
            raise EventSignupException("User already signed up")

    def withdraw(self, user):
        try:
            self.signed_up.remove(user)
            db.session.add(self)
            db.session.commit()
        except ValueError:
            raise EventSignupException("User is not signed up")

    def serialize(self):
        return {
            "id": self.turn_id,
            "finished": self.finished,
            "name": self.user.name,
            "phone": self.user.phone,
            "email": self.user.email,
            "signed_up": [user.name for user in self.signed_up]
        }
