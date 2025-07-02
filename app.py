from flask import Flask, jsonify, request
from flask_cors import CORS
from search_by_category import search_by_category
import random

app = Flask(__name__)
#CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})
CORS(app)

@app.route("/api/random-routine", methods=["GET"])
def get_random_routine():
    category = request.args.get("category")
    # set up the default state with "not_completed
    state = request.args.get("state", "not_completed")
    if not category:
        return jsonify({"message": "Category parameter is required."}), 400
    results = search_by_category(category, state)
    routines = results.get("documents", [])
    if not routines:
        return jsonify({"message": "No routines found for this category and state."}), 404
    # Pick a random routine
    idx = random.randint(0, len(routines) - 1)
    routine = routines[idx]
    return jsonify({"message": routine})

if __name__ == "__main__":
    app.run(debug=True, port=5050)