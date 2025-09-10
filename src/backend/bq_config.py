# Configuration for BigQuery project & resources

PROJECT_ID = "siddudev"
DATASET = "meet_your_partner"

# Embedding model for text -> vector
EMBED_MODEL = f"{PROJECT_ID}.{DATASET}.siddu_txt_embed_model"

# Main user table with embeddings
USER_TABLE = f"{PROJECT_ID}.{DATASET}.matching_app_user_data_embed"
