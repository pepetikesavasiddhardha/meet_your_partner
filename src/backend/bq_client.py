from google.cloud import bigquery
import bq_config

client = bigquery.Client(project=bq_config.PROJECT_ID)

def build_partner_filter(preferences):
    """Dynamically build WHERE clause based on partner preferences."""
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


def fetch_matches(user_traits, partner_prefs):
    """Run BigQuery similarity search for top-5 matches."""

    # Partner preference filters
    where_clause = build_partner_filter(partner_prefs)

    query = f"""
    WITH new_user_data AS (
      SELECT ml_generate_embedding_result
      FROM ML.GENERATE_EMBEDDING(
        MODEL `{bq_config.EMBED_MODEL}`,
        (SELECT "{user_traits['interest_tags']}" AS content),
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

    query_job = client.query(query)
    rows = [dict(row) for row in query_job.result()]
    return rows

def insert_user(user_traits):
    """Insert a new user profile into the main table with embedding."""
    
    # Generate unique integer ID (use FARM_FINGERPRINT on timestamp + interests)
    from datetime import datetime
    import time
    unique_id = abs(hash(str(time.time()) + user_traits["interest_tags"])) % (10**9)

    query = f"""
    CREATE OR REPLACE TABLE `{bq_config.USER_TABLE}` AS
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
      SELECT
        id, gender, sexual_orientation, location_type,
        income_bracket, education_level, content as interest_tags,
        ml_generate_embedding_result
      FROM ML.GENERATE_EMBEDDING(
        MODEL `{bq_config.EMBED_MODEL}`,
        (SELECT id, gender, sexual_orientation, location_type,
        income_bracket, education_level, interest_tags AS content FROM new_user),
        STRUCT(TRUE AS flatten_json_output)
      )
    )
    SELECT * FROM `{bq_config.USER_TABLE}`
    UNION ALL
    SELECT * FROM new_user_embed
    """
    client.query(query).result()
    return unique_id
