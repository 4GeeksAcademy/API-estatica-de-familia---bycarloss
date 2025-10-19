"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# Create the jackson family object
jackson_family = FamilyStructure("Jackson")

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def get_members():
    members = jackson_family.get_all_members()
    return jsonify(members), 200

@app.route('/members/<int:member_id>', methods=['GET'])
def get_one_member(member_id):
    member = jackson_family.get_member(member_id)
    if not member:
        return jsonify({"msg": "Member not found"}), 404
    return jsonify(member), 200

@app.route('/members', methods=['POST'])
def create_member():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"msg": "Invalid JSON body"}), 400
    required = ("first_name", "age")
    if any(k not in data for k in required):
        return jsonify({"msg": "Missing fields"}), 400
    try:
        created = jackson_family.add_member(data)
    except Exception:
        return jsonify({"msg": "Invalid payload"}), 400
    return jsonify(created), 200

@app.route('/members/<int:member_id>', methods=['DELETE'])
def remove_member(member_id):
    deleted = jackson_family.delete_member(member_id)
    if not deleted:
        return jsonify({"msg": "Member not found"}), 404
    return jsonify({"done": True}), 200

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)