from flask_sqlalchemy import SQLAlchemy
import datetime as dt

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.Integer)
    created_date = dt.datetime.today()
    last_updated = dt.datetime.today()

    turns = db.relationship("turns", backref="user", uselist=False)

    def __init__(self, name, email, phone=None, turn=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.turn = turn

    def __repr__(self):
        return f"<User {self.name}>"

    @classmethod
    def create(cls, name, email, phone):
        user = cls(name=name, email=email, phone=phone)
        db.session.add(user)
        user.turns = Turns(finished=False)

        db.session.commit()
        return user

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "created": self.created_date,
            "turn": self.turn
        }


class Turns(db.Model):
    __tablename__ = 'turns'

    turn_id = db.Column(db.Integer, primary_key=True)
    finished = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    accepted = db.relationship("User", backref="accept")
