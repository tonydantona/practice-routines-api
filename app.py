from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
#CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})
CORS(app)

@app.route("/api/random-routine", methods=["GET"])
def get_random_routine():
    # Placeholder - later you'll query Chroma or load from JSON
     return jsonify({"message": "Play G minor pentatonic with vibrato"})

if __name__ == "__main__":
    app.run(debug=True, port=5050)