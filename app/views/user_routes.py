from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest

from app.model import User, db

user_route = Blueprint('api', __name__)


@user_route.route("/user", methods=["POST"])
def create_user():
    try:
        data = request.get_json(force=True)
        user = User.create(**data)
        return jsonify({"success": user.id}), 200
    except BadRequest:
        return jsonify({"error": "Invalid data"}), 401


@user_route.route("/user/<int:id>", methods=["GET"])
def get_user(id):
    user = User.query.get(id)
    return jsonify(user.serialize()), 200


@user_route.route("/users", methods=["GET"])
def get_all_users():
    users = db.session.query(User).all()
    users = [user.serialize() for user in users]
    return jsonify(users), 200


@user_route.route('/user/swap', methods=["PUT"])
def swap_users():
    try:
        data = request.get_json(force=True)
        user_id, user2_id = data["swap"]
        user = User.query.get(user_id)
        user2 = User.query.get(user2_id)
        if user and user2:
            user.swap_turn(user2)
            return jsonify({"success":
                                f"User {user.id} now has turn {user.turn.turn_id}. "
                                f"User {user2.id} now has turn {user2.turn.turn_id}"}), 201
        else:
            return jsonify({"error": f"User {user_id} or User {user2_id} not found"}), 404

    except BadRequest:
        return jsonify({"error": "Couldn't read request"}), 401
