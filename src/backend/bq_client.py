from google.cloud import bigquery
import bq_config

# Create BigQuery client (re-used across functions)
client = bigquery.Client(project=bq_config.PROJECT_ID)


# ==========================
# Helper: Partner Filter Builder
# ==========================

def build_partner_filter(preferences):
    """
    Dynamically build WHERE clause for partner preferences.
    - Only adds filters for fields that are provided
    - If no preferences given, defaults to TRUE (no filtering)
    """
    filters = []
    if preferences.get("gender"):
        filters.append(f'gender = "{preferences["gender"]}"')
    if preferences.get("sexual_orientation"):
        filters.append(f'sexual_orientation = "{preferences["sexual_orientation"]}"')
    if preferences.get("location_type"):
        filters.append(f'location_type = "{preferences["location_type"]}"')
    if preferences.get("income_bracket"):
        filters.append(f'income_bracket = "{preferences["income_bracket"]}"')
    if preferences.get("education_level"):
        filters.append(f'education_level = "{preferences["education_level"]}"')

    return " AND ".join(filters) if filters else "TRUE"


# ==========================
# Fetch Matches (Vector Search)
# ==========================

def fetch_matches(user_traits, partner_prefs):
    """
    Run BigQuery semantic similarity search to return top-5 matches.

    Steps:
    1. Generate embedding for current user's interest tags (new_user_data CTE)
    2. Search against stored embeddings in USER_TABLE (with partner preference filters applied)
    3. Use VECTOR_SEARCH with COSINE distance to retrieve nearest neighbors
    """
    where_clause = build_partner_filter(partner_prefs)

    query = f"""
    WITH new_user_data AS (
      -- Generate embedding for input user’s interest tags
      SELECT ml_generate_embedding_result
      FROM ML.GENERATE_EMBEDDING(
        MODEL `{bq_config.EMBED_MODEL}`,
        (SELECT "{partner_prefs['interest_tags']}" AS content),
        STRUCT(TRUE AS flatten_json_output)
      )
    )
    SELECT
      base.id,
      base.gender,
      base.sexual_orientation,
      base.location_type,
      base.income_bracket,
      base.education_level,
      base.interest_tags,
      distance
    FROM VECTOR_SEARCH(
      (
        -- Candidate pool: all existing users filtered by partner prefs
        SELECT id, gender, sexual_orientation, location_type,
               income_bracket, education_level, interest_tags, ml_generate_embedding_result
        FROM `{bq_config.USER_TABLE}`
        WHERE {where_clause}
      ),
      "ml_generate_embedding_result",
      (SELECT ml_generate_embedding_result FROM new_user_data),
      "ml_generate_embedding_result",
      distance_type => "COSINE",
      top_k => 5
    )
    ORDER BY distance
    """

    # Execute query and return results as list of dicts
    query_job = client.query(query)
    rows = [dict(row) for row in query_job.result()]
    return rows


# ==========================
# Insert New User
# ==========================

def insert_user(user_traits):
    """
    Insert a new user into USER_TABLE with embeddings.
    
    Steps:
    1. Generate a unique integer ID for the new user
    2. Build a CTE with the raw user traits
    3. Generate embedding using ML.GENERATE_EMBEDDING
    4. Insert the row (traits + embedding) into BigQuery table
    """
    import time
    # Unique ID derived from timestamp + interest tags hash
    unique_id = abs(hash(str(time.time()) + user_traits["interest_tags"])) % (10**9)

    query = f"""
    INSERT INTO `{bq_config.USER_TABLE}` (id, gender, sexual_orientation, location_type,
        income_bracket, education_level, interest_tags, ml_generate_embedding_result)
    WITH new_user AS (
      SELECT
        {unique_id} AS id,
        "{user_traits['gender']}" AS gender,
        "{user_traits['sexual_orientation']}" AS sexual_orientation,
        "{user_traits['location_type']}" AS location_type,
        "{user_traits['income_bracket']}" AS income_bracket,
        "{user_traits['education_level']}" AS education_level,
        "{user_traits['interest_tags']}" AS interest_tags
    ),
    new_user_embed AS (
      -- Generate embedding for this new user's interests
      SELECT
        id, gender, sexual_orientation, location_type,
        income_bracket, education_level, content as interest_tags,
        ml_generate_embedding_result
      FROM ML.GENERATE_EMBEDDING(
        MODEL `{bq_config.EMBED_MODEL}`,
        (
          SELECT id, gender, sexual_orientation, location_type,
                 income_bracket, education_level, interest_tags AS content
          FROM new_user
        ),
        STRUCT(TRUE AS flatten_json_output)
      )
    )
    SELECT * FROM new_user_embed
    """

    # Run insertion query
    client.query(query).result()
    return unique_id
