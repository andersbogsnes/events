from flask import Blueprint, jsonify, request
from werkzeug.exceptions import BadRequest

from app.model import db, Turns, User

turn_routes = Blueprint('turn_routes', __name__)


@turn_routes.route('/turn', methods=["GET"])
def get_next_turn():
    turn = Turns.next_turn()
    return jsonify(turn.serialize()), 200


@turn_routes.route('/turns', methods=["GET"])
def get_all_turns():
    turns = Turns.query.all()
    return jsonify([turn.serialize() for turn in turns]), 200


@turn_routes.route('/turn/<int:id>', methods=["GET"])
def get_turn(id):
    turn = db.session.query(Turns).filter_by(turn_id=id).first()
    if turn:
        return jsonify(turn.serialize()), 200
    else:
        return jsonify({"error": "turn_id doesn't exist"}), 404


@turn_routes.route('/turn/done', methods=["PUT"])
def pop_turn():
    turn = Turns.pop()
    return jsonify(turn.serialize()), 201


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
def signup_for_turn(id):
    try:
        data = request.get_json(force=True)
        user = User.query.get(data["signed_up"])
        turn = Turns.query.get(id)
        if user:
            turn.signup(user)
            return jsonify({"success": f"{user.name} signed up for turn {turn.turn_id}"}), 201
        else:
            return jsonify({"error": f"User {data['signed_up']} not found"}), 404
    except BadRequest:
        return jsonify({"error": "Couldn't read request"}), 401


@turn_routes.route('/turn/withdraw/<int:id>', methods=["PUT"])
def withdraw_from_turn(id):
    try:
        data = request.get_json(force=True)
        user = User.query.get(data["withdraw"])
        turn = Turns.query.get(id)
        if user:
            turn.withdraw(user)
            return jsonify({"success": f"{user.name} withdrew from turn {turn.turn_id}"}), 201
        else:
            return jsonify({"error": f"User {data['withdraw']} not found"}), 404


    except BadRequest:
        return jsonify({"error": "Couldn't read request"}), 401
