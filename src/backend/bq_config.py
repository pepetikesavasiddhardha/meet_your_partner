# ==========================
# BigQuery Configuration
# ==========================

# Project where all BigQuery resources live
PROJECT_ID = "siddudev"

# Dataset that stores the user tables and ML model
DATASET = "meet_your_partner"

# Pre-trained embedding model for generating vector representations of text
# (used to turn user interest tags into semantic embeddings)
EMBED_MODEL = f"{PROJECT_ID}.{DATASET}.siddu_txt_embed_model"

# Main table storing user profiles along with their embeddings
USER_TABLE = f"{PROJECT_ID}.{DATASET}.matching_app_user_data_embed"
