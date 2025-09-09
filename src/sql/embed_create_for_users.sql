-- Create a column named id
CREATE OR REPLACE TABLE `siddudev.meet_your_partner.matching_app_user_data` AS
SELECT
  ROW_NUMBER() OVER() AS id,
  t.*
FROM `siddudev.meet_your_partner.matching_app_user_data` t;

-- create embeddings for users in database based on their interest tags
CREATE OR REPLACE TABLE `siddudev.meet_your_partner.matching_app_user_data_embed` AS
SELECT 
    id,
    gender,
    sexual_orientation,
    location_type,
    income_bracket,
    education_level,
    content as interest_tags,
    ml_generate_embedding_result
FROM
    ML.GENERATE_EMBEDDING(
        MODEL `meet_your_partner.siddu_txt_embed_model`,
        (
            SELECT 
              id,
              gender,
              sexual_orientation,
              location_type,
              income_bracket,
              education_level,
              interest_tags as content,
            FROM `siddudev.meet_your_partner.matching_app_user_data`
        ),
        STRUCT(TRUE AS flatten_json_output)
    );


-- Delete the original table which we don't need now
DROP TABLE `siddudev.meet_your_partner.matching_app_user_data`;

-- Perform vector search for finding top-5 similar users
WITH new_user_data AS (
    SELECT ml_generate_embedding_result
    FROM
        ML.GENERATE_EMBEDDING(
            MODEL `siddudev.meet_your_partner.siddu_txt_embed_model`,
            (
                SELECT 
                    "Spirituality,travel,food,sports" 
                    AS content
            ),
            STRUCT(TRUE AS flatten_json_output)
        )
)
SELECT
    base.gender,
    base.sexual_orientation,
    base.location_type,
    base.income_bracket,
    base.education_level,
    base.interest_tags,
    distance
FROM
    VECTOR_SEARCH(
        (
            SELECT *
            FROM `siddudev.meet_your_partner.matching_app_user_data_embed`
            WHERE gender = "Female"
            AND sexual_orientation = "Straight"
            and location_type = "Urban"
            and income_bracket = "High"
            and education_level = "MBA"
        ),
        "ml_generate_embedding_result",
        (SELECT ml_generate_embedding_result FROM new_user_data),
        "ml_generate_embedding_result",
        distance_type=>"COSINE",
        top_k=>5
    )
ORDER BY distance;
