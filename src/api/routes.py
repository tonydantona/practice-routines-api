"""
Flask API routes for practice routines.
"""

import logging
from flask import Blueprint, jsonify, request
from src.services.routine_service import RoutineService

logger = logging.getLogger(__name__)

# Create blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')

# This will be injected by the app factory
_routine_service: RoutineService = None


def init_routes(routine_service: RoutineService):
    """
    Initialize routes with dependencies.

    Args:
        routine_service: The routine service instance.
    """
    global _routine_service
    _routine_service = routine_service


@api_bp.route("/get-random-routine-by-category-state", methods=["GET"])
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

        # If state is "all", pass None to get all states
        search_state = None if state == "all" else state

        # Get random routine using service
        routine = _routine_service.get_random_routine_by_category(category, search_state)

        if not routine:
            logger.info(f"No routines found for category='{category}', state='{state}'")
            return jsonify({"error": "No routines found for this category and state."}), 404

        logger.info(f"Returning random routine")
        return jsonify({"message": routine.text})

    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error in get_random_routine: {e}", exc_info=True)
        return jsonify({"error": "Internal server error occurred."}), 500


@api_bp.route("/routines", methods=["GET"])
def get_all_routines():
    """Get all practice routines."""
    try:
        category = request.args.get("category")
        state = request.args.get("state")

        if category:
            logger.info(f"Getting routines by category: {category}, state: {state}")
            routines = _routine_service.get_routines_by_category(category, state)
        elif state:
            if state == "not_completed":
                logger.info("Getting not-completed routines")
                routines = _routine_service.get_not_completed_routines()
            else:
                logger.info(f"Getting routines by state: {state}")
                # This would need a new service method
                return jsonify({"error": "State filter without category not yet supported"}), 400
        else:
            logger.info("Getting all routines")
            routines = _routine_service.get_all_routines()

        return jsonify({
            "count": len(routines),
            "routines": [r.to_dict() for r in routines]
        })

    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error getting routines: {e}", exc_info=True)
        return jsonify({"error": "Internal server error occurred."}), 500


@api_bp.route("/routines/search", methods=["GET"])
def search_routines():
    """Semantic search for routines."""
    try:
        query = request.args.get("query")
        top_n = request.args.get("top_n", 5, type=int)
        min_score = request.args.get("min_score", 0.3, type=float)

        if not query:
            logger.warning("Request missing required 'query' parameter")
            return jsonify({"error": "Query parameter is required."}), 400

        logger.info(f"Searching routines: query='{query}', top_n={top_n}, min_score={min_score}")

        routines = _routine_service.search_routines(query, top_n, min_score)

        return jsonify({
            "query": query,
            "count": len(routines),
            "routines": [r.to_dict() for r in routines]
        })

    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error searching routines: {e}", exc_info=True)
        return jsonify({"error": "Internal server error occurred."}), 500


@api_bp.route("/routines/<routine_id>/complete", methods=["PUT"])
def mark_routine_completed(routine_id):
    """Mark a routine as completed."""
    try:
        logger.info(f"Marking routine {routine_id} as completed")
        _routine_service.mark_routine_completed(routine_id)

        return jsonify({"message": f"Routine {routine_id} marked as completed"})

    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error marking routine completed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error occurred."}), 500


@api_bp.route("/routines/<routine_id>/uncomplete", methods=["PUT"])
def mark_routine_not_completed(routine_id):
    """Mark a routine as not completed."""
    try:
        logger.info(f"Marking routine {routine_id} as not completed")
        _routine_service.mark_routine_not_completed(routine_id)

        return jsonify({"message": f"Routine {routine_id} marked as not completed"})

    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error marking routine not completed: {e}", exc_info=True)
        return jsonify({"error": "Internal server error occurred."}), 500
