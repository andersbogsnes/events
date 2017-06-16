from flask import Blueprint, request, jsonify
from model import User, db

api = Blueprint('api', __name__)


@api.route('/')
def index():
    return "Here will be usage instructions for api"


@api.route("/user", methods=["POST"])
def create_user():
    data = request.get_json(force=True)
    if data:
        user = User.create(**data)
        return jsonify({"success": user.id}), 200
    else:
        return jsonify({"error": "Invalid data"}), 401


@api.route("/user/<int:id>", methods=["GET"])
def get_user(id):
    user = db.session.query(User).filter_by(id=id).first()
    return jsonify(user.serialize()), 200


@api.route("/users", methods=["GET"])
def get_all_users():
    users = db.session.query(User).all()
    users = [user.serialize() for user in users]
    return jsonify(users), 200
