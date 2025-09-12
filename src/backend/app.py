import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from bq_client import fetch_matches, insert_user

# ===========================================
# Flask Backend for "Meet Your Partner" App
# -------------------------------------------
# - Serves frontend (HTML, CSS, JS) locally
# - Exposes API endpoints for:
#     1. Searching top 5 similar matches
#     2. Inserting new user data into BigQuery
# - Uses BigQuery (via bq_client.py) to run
#   semantic similarity queries with embeddings
# ===========================================

# Path to the frontend folder (for serving static files)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

# Initialize Flask app
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,   # serve static assets from /frontend
    static_url_path=""            # allow direct URLs (e.g., /style.css)
)

# Allow frontend JS (running in browser) to call backend APIs
CORS(app)


# ==========================
# Routes to Serve Frontend
# ==========================

@app.route("/")
def index():
    """Serves the main landing page (index.html)."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    """Serves static files like CSS, JS, or images when requested."""
    return send_from_directory(FRONTEND_DIR, path)


# ==========================
# API Endpoints
# ==========================

@app.route("/search", methods=["POST"])
def search():
    """
    Endpoint to:
    1. Insert the current user’s traits into BigQuery
    2. Run semantic similarity search against partner preferences
    3. Return top 5 most similar matches
    """
    data = request.json

    # Current user's own traits (mandatory fields)
    user_traits = {
        "gender": data.get("gender"),
        "sexual_orientation": data.get("sexual_orientation"),
        "location_type": data.get("location_type"),
        "income_bracket": data.get("income_bracket"),
        "education_level": data.get("education_level"),
        "interest_tags": data.get("interest_tags"),
    }

    # Partner preference filters (can be partially empty / optional)
    partner_prefs = {
        "gender": data.get("partner_gender"),
        "sexual_orientation": data.get("partner_sexual_orientation"),
        "location_type": data.get("partner_location_type"),
        "income_bracket": data.get("partner_income_bracket"),
        "education_level": data.get("partner_education_level"),
        "interest_tags": data.get("partner_interest_tags"),
    }

    # Insert new user into BigQuery table and get back unique ID
    new_user_id = insert_user(user_traits)

    # Run semantic similarity search for top matches
    results = fetch_matches(user_traits, partner_prefs)

    # Send both new user ID and matches to frontend
    return jsonify({"new_user_id": new_user_id, "matches": results})


# ==========================
# Run Flask Application
# ==========================

if __name__ == "__main__":
    # Running with debug=True enables hot reload + detailed error logs
    app.run(debug=True)
