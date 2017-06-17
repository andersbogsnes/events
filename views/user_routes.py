from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from model import User, db

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
