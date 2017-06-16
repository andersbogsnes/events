from flask import Blueprint, jsonify, request

from model import db, Turns

turn_routes = Blueprint('turn_routes', __name__)


@turn_routes.route('/turn/<int:id>', methods=["GET"])
def get_turn(id):
    turn = db.session.query(Turns).filter_by(turn_id=id).first()
    return jsonify(turn.serialize()), 200


@turn_routes.route('/turn', methods=["GET"])
def get_next_turn():
    turn = Turns.next_turn()
    if turn:
        return jsonify(turn.serialize()), 200
    else:
        all_turns = db.session.query(Turns).all()
        for turn in all_turns:
            turn.finished = False
            db.session.add(turn)
        db.session.commit()
        return jsonify(Turns.next_turn().serialize()), 200


@turn_routes.route('/turn/<int:id>', methods=["PUT"])
def modify_turn(id):
    data = request.get_json(force=True)
    if data:
        turn = Turns.query.get(id)
        for key, value in data.items():
            setattr(turn, key, value)
        db.session.add(turn)
        db.session.commit()
        return jsonify(turn.serialize()), 200