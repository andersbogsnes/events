from flask_sqlalchemy import SQLAlchemy
import datetime as dt

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.Integer)

    created_date = db.Column(db.DateTime, default=dt.datetime.today())
    last_updated = db.Column(db.DateTime, default=dt.datetime.today(), onupdate=dt.datetime.today())



    def __init__(self, name, email, phone=None):
        self.name = name
        self.email = email
        self.phone = phone

    def __repr__(self):
        return f"<User {self.name}>"

    @classmethod
    def create(cls, name, email, phone):
        user = cls(name=name, email=email, phone=phone)
        user.turn.append(Turns(finished=False))

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

    # TODO: Implement as queue
    turn_id = db.Column(db.Integer, primary_key=True)
    finished = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship("User", backref=db.backref("turn", lazy='dynamic'))

    @classmethod
    def next_turn(cls):
        return cls.query.filter_by(finished=False).first()

    @classmethod
    def pop(cls, user_id):
        user = User.query.get(user_id)
        user.turn.finished = True
        user.turn = cls(finished=False)
        db.session.add(user)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.turn_id,
            "finished": self.finished,
            "name": self.user.name,
            "phone": self.user.phone,
            "email": self.user.email
        }


