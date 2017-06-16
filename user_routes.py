from flask import Blueprint, request, jsonify
from model import User, db

user_route = Blueprint('api', __name__)

@user_route.route('/')
def index():
    return "Here will be usage instructions for api"


@user_route.route("/user", methods=["POST"])
def create_user():
    data = request.get_json(force=True)
    if data:
        user = User.create(**data)
        return jsonify({"success": user.id}), 200
    else:
        return jsonify({"error": "Invalid data"}), 401


@user_route.route("/user/<int:id>", methods=["GET"])
def get_user(id):
    user = db.session.query(User).filter_by(id=id).first()
    return jsonify(user.serialize()), 200


@user_route.route("/users", methods=["GET"])
def get_all_users():
    users = db.session.query(User).all()
    users = [user.serialize() for user in users]
    return jsonify(users), 200
