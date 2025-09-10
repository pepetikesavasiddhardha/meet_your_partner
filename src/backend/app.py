import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from bq_client import fetch_matches, insert_user

# ==========================
# Flask App Configuration
# ==========================

# Absolute path to frontend folder
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))

# Create Flask app instance
app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

# Enable CORS so frontend JS can call backend
CORS(app)

# ==========================
# Routes to Serve Frontend
# ==========================

@app.route("/")
def index():
    """Serve index.html when visiting root."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    """Serve static files like CSS, JS, images."""
    return send_from_directory(FRONTEND_DIR, path)

# ==========================
# API Endpoints
# ==========================

@app.route("/search", methods=["POST"])
def search():
    data = request.json

    user_traits = {
        "gender": data.get("gender"),
        "sexual_orientation": data.get("sexual_orientation"),
        "location_type": data.get("location_type"),
        "income_bracket": data.get("income_bracket"),
        "education_level": data.get("education_level"),
        "interest_tags": data.get("interest_tags"),
    }

    partner_prefs = {
        "gender": data.get("partner_gender"),
        "sexual_orientation": data.get("partner_sexual_orientation"),
        "location_type": data.get("partner_location_type"),
        "income_bracket": data.get("partner_income_bracket"),
        "education_level": data.get("partner_education_level"),
        "interest_tags": data.get("partner_interest_tags"),  # ✅ now included
    }

    new_user_id = insert_user(user_traits)
    results = fetch_matches(user_traits, partner_prefs)

    return jsonify({"new_user_id": new_user_id, "matches": results})

# ==========================
# Run Flask Application
# ==========================

if __name__ == "__main__":
    app.run(debug=True)
