# Meet Your Partner

**Approach-2: Semantic Detective**

A prototype system built using **Google BigQuery**, **Embeddings**, and **Vector Search** to recommend **ideal partners** based on shared interests and preferences.
The system demonstrates how older adults—or anyone seeking companionship—can discover matches that align closely with their expectations.

---

## 📌 Problem Statement

In countries such as **Japan** and **South Korea**, where the aging population is significantly higher, loneliness has become a growing concern.
Many older adults want companionship but struggle to find suitable partners due to social isolation, limited mobility, or lack of platforms tailored to their needs.

---

## 🎯 Objective

To build a **semantic match-finding system** that:

* Identifies partners whose **interests align** with a user’s stated preferences.
* Returns the **top-5 most similar matches** from an existing database.
* Stores new user profiles (with embeddings) so they can also appear in future searches.

---

## 💡 Business Impact

* **Reduces loneliness** → Helps older adults connect with compatible partners.
* **Market expansion** → While the prototype focuses on older people, the approach can easily be extended to all age groups.
* **Revenue opportunities** → Similar to other dating platforms, monetization can be achieved through premium subscriptions, targeted recommendations, or regional matchmaking features.
* **Global usability** → Supports **multilingual inputs** (e.g., Japanese, Korean), making it relevant across diverse regions and not restricted to English speakers.

---

## 🧠 Approach Overview

This solution is a simple extension of SQL, enhanced with BigQuery’s built-in machine learning capabilities. By combining embeddings and vector search directly within SQL queries, the system provides an efficient and scalable way to solve the partner-matching problem without requiring external ML pipelines.

### 1. Dataset

* Used the **Dating App Behavior Dataset 2025** from Kaggle:
  👉 [https://www.kaggle.com/datasets/keyushnisar/dating-app-behavior-dataset/data](https://www.kaggle.com/datasets/keyushnisar/dating-app-behavior-dataset/data)
* Dataset size: **50,000 rows**
* Selected 6 key features for matching:

  * `gender`
  * `sexual_orientation`
  * `location_type`
  * `income_bracket`
  * `education_level`
  * `interest_tags`
* Added a **unique ID column** for user identification.
* Other app-usage features were excluded since they were not relevant for matchmaking.

---

### 2. Data Preparation

* Downloaded dataset from Kaggle and uploaded it to **BigQuery**.
* Retained only the 6 matching-related features.
* Created a **user ID column** to uniquely identify each profile.

---

### 3. Embeddings

* Generated **semantic embeddings** for `interest_tags` using:

  * **`ML.GENERATE_EMBEDDING`** in BigQuery.
  * **Model Used** → `text-multilingual-embedding-002`.
* This allows the system to handle **non-English inputs**—essential for regions where users may describe interests in their native language.

---

### 4. Similarity Search

When a new user provides their partner preferences:

1. Generate embeddings for the **entered interest\_tags**.
2. Perform **`VECTOR_SEARCH`** on the database to retrieve **Top-5 closest matches**.
3. Store the new user’s profile (with embedding) in the database for future queries.

---

### 5. Results Display

* Users are shown matches **one at a time**.
* Each profile includes basic details (gender, orientation, income, education, interests).
* Users can click **“Interested”** or **“Not Interested.”**
* As the dataset lacks real names/photos, a **default avatar** and **user ID** are displayed.

---

### 6. Vector Indexing (Note)

* Not used in this prototype since the dataset is relatively small (\~50k).
* Per BigQuery documentation, **vector indexing** is recommended only for datasets ≥ 1M records.
* Future improvements may include indexing, richer user metadata, and multilingual personalization.

---

## ⚙️ How to Run Locally

setup:
prerequisites:
\- Python 3.13 or later
\- Google Cloud SDK (for BigQuery access)
\- BigQuery project with required permissions
\- Internet connection for installing dependencies

steps:
\- step: Clone the repository
commands:
\- `git clone https://github.com/pepetikesavasiddhardha/meet_your_partner.git`
\- `cd meet_your_partner`
\- step: Install uv package manager
description: >
uv is used to manage Python environments and dependencies.
commands:
\- `curl -LsSf https://astral.sh/uv/install.sh | sh`
\- step: Install project dependencies
commands:
\- `uv sync`
\- step: Run the backend server
description: >
Start the Flask backend to serve the app.
commands:
\- `python src/backend/app.py`
\- step: Open the application in browser
url: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

notes:

* Enable required **BigQuery APIs** in your project.
* Ensure proper **Google credentials** are available for query execution.
* The app requires **embedding models** created in BigQuery ML beforehand.
* If using free-tier credits, keep dataset usage minimal to avoid charges.

success\_message: >
🎉 Setup complete! Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser
and start using the **Meet Your Partner** system locally.