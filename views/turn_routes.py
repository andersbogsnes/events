from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from model import db, Turns, User

turn_routes = Blueprint('turn_routes', __name__)


@turn_routes.route('/turn', methods=["GET"])
def get_next_turn():
    turn = Turns.next_turn()
    return jsonify(turn.serialize()), 200

@turn_routes.route('/turn/<int:id>', methods=["GET"])
def get_turn(id):
    turn = db.session.query(Turns).filter_by(turn_id=id).first()
    return jsonify(turn.serialize()), 200


@turn_routes.route('/turn/swap/<int:id>', methods=["PUT"])
def modify_turn(id):

    try:
        data = request.get_json(force=True)
        turn = Turns.query.get(id)
        for key, value in data.items():
            setattr(turn, key, value)
        db.session.add(turn)
        db.session.commit()
        return jsonify(turn.serialize()), 200
    except BadRequest:
        return jsonify({""})


@turn_routes.route('/turn/signup/<int:id>', methods=["PUT"])
def signup_to_turn(id):
    try:
        data = request.get_json(force=True)
        user = User.query.get(data["user_id"])
        turn = Turns.query.get(id)
        if user:
            turn.sign_up.append(user)
    except:
        pass
