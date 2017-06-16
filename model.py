from flask_sqlalchemy import SQLAlchemy
import datetime as dt

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    phone = db.Column(db.Integer)
    turn_id = db.Column(db.Integer, db.ForeignKey('turns.turn_id'))
    created_date = db.Column(db.DateTime, default=dt.datetime.today())
    last_updated = db.Column(db.DateTime, default=dt.datetime.today(), onupdate=dt.datetime.today())

    turn = db.relationship("Turns", backref=db.backref("user", uselist=False))

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

    @classmethod
    def next_turn(cls):
        return db.session.query(Turns).filter_by(finished=False).first()


