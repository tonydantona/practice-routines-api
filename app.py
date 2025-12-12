from flask import Flask, jsonify, request
from flask_cors import CORS
from search_by_category import search_by_category
from config import settings
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure CORS based on settings
if settings.CORS_ORIGINS == "*":
    CORS(app)
else:
    # Parse comma-separated origins if provided
    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
    CORS(app, resources={r"/api/*": {"origins": origins}})

@app.route("/api/get-random-routine-by-category-state", methods=["GET"])
def get_random_routine():
    """Get a random practice routine filtered by category and state."""
    try:
        category = request.args.get("category")
        state = request.args.get("state", "not_completed")

        # Validate required parameters
        if not category:
            logger.warning("Request missing required 'category' parameter")
            return jsonify({"error": "Category parameter is required."}), 400

        logger.info(f"Searching for routines: category={category}, state={state}")

        # If state is "all", pass None to search_by_category to get all states
        search_state = None if state == "all" else state
        results = search_by_category(category, search_state)
        routines = results.get("documents", [])

        if not routines:
            logger.info(f"No routines found for category='{category}', state='{state}'")
            return jsonify({"error": "No routines found for this category and state."}), 404

        # Pick a random routine
        idx = random.randint(0, len(routines) - 1)
        routine = routines[idx]

        logger.info(f"Returning random routine from {len(routines)} results")
        return jsonify({"message": routine})

    except Exception as e:
        logger.error(f"Error in get_random_routine: {e}", exc_info=True)
        return jsonify({"error": "Internal server error occurred."}), 500

if __name__ == "__main__":
    app.run(debug=settings.DEBUG, host=settings.FLASK_HOST, port=settings.FLASK_PORT)