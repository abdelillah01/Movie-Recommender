# Movie Recommender System

A content-based movie recommendation system built with Python, scikit-learn, Django REST Framework, and Next.js.
It recommends similar movies based on the textual similarity of metadata like genres, keywords, cast, and descriptions.


## Overview

This project recommends movies similar to a given title using TF-IDF vectorization and cosine similarity. The system is composed of two main parts:

*   **Machine Learning Model (Offline)** – Builds the similarity model from movie data.
*   **Django Backend API (Online)** – Serves movie recommendations via an HTTP endpoint.
*   **Next.js Frontend (User Interface)**  - allows users to interact with the recommendation system visually.                     
<img width="1669" height="870" alt="Screenshot 2025-10-27 165803" src="https://github.com/user-attachments/assets/8e83b751-97fb-4925-bda7-08b7c42b8a64" />

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [1. Machine Learning Model](#1-machine-learning-model)
- [2. Django Backend API](#2-django-backend-api)
- [3. Next.js Frontend](#3-nextjs-frontend)
- [4. API Usage](#4-api-usage)
- [5. Example Components](#5-example-components)
- [6. Running the Frontend](#6-running-the-frontend)
- [7. Enabling CORS in Django](#7-enabling-cors-in-django)
- [8. Example Interaction](#8-example-interaction)
- [9. Full System Architecture](#9-full-system-architecture)
- [10. Author](#10-author)
- [Future Improvements](#future-improvements)

  
## Project Structure

```
MOVIE-RECOMMENDER/
│
├── ML-model/                 # Machine Learning model & data
│   ├── notebooks/            # Jupyter notebooks for experiments
│   │   └── model_building.ipynb
│   ├── data/
│   │   ├── raw/              # Original datasets
│   │   │   └── movies_metadata.csv
│   │   └── processed/        # Cleaned & merged data
│   │       └── merged_movies.csv
│   ├── model.pkl             # Saved TF-IDF vectorizer + similarity matrix
│   └── utils/                # Helper scripts (optional)
│       └── preprocess.py
│
├── backend/                  # Django REST API
│   ├── backend/              # Django project settings
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── settings.py       # API & CORS settings
│   │   ├── urls.py           # Root URL routes
│   │   └── wsgi.py
│   │
│   ├── recommender_app/      # Core app for recommendations
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py    # Optional (if needed for complex data)
│   │   ├── utils.py          # Loads model.pkl & defines recommend_movies()
│   │   ├── views.py          # Handles API requests
│   │   ├── urls.py           # App-specific routes
│   │   └── tests.py
│   │
│   ├── manage.py
│   ├── requirements.txt      # Django + ML dependencies
│   └── .env                  # Django secret key, debug config, etc.
│
├── frontend/                 # Next.js frontend app
│   ├── app/                  # Next.js App Router directory
│   │   ├── globals.css       # Tailwind base styles
│   │   ├── layout.jsx        # Root layout (if using App Router)
│   │   └── page.jsx          # Home page with search + recommendations
│   │
│   ├── components/           # Reusable UI components
│   │   ├── SearchBar.jsx
│   │   ├── MovieCard.jsx
│   │   └── MovieList.jsx
│   │
│   ├── public/               # Static assets (icons, images, etc.)
│   │   └── favicon.ico
│   │
│   ├── .env.local            # Frontend API base URL (e.g. NEXT_PUBLIC_API_URL)
│   ├── package.json          # Frontend dependencies
│   ├── postcss.config.js     # Tailwind/PostCSS config
│   ├── tailwind.config.js    # Tailwind configuration
│   ├── next.config.js        # Next.js configuration
│   └── README.md             # Frontend-specific documentation
│
├── .gitignore               # Git ignore rules
├── README.md               # Full project documentation (this file)
└── LICENSE                 # MIT license
```


## 1. Machine Learning Model

### Dataset

The dataset contains metadata for thousands of movies, including:

*   Title
*   Genres
*   Overview
*   Cast and Crew
*   Keywords
*   Tagline

All text fields are combined into a single field named `combined`, which is used for feature extraction.

**Example:**
`adventure animation children comedy fantasy jesse buzz lightyear toy cowboy friendship`

## Preprocessing Steps

### Text Cleaning

*   Removed duplicates and missing values.
*   Converted all text to lowercase.
*   Combined multiple textual fields into one `combined` column.

### Feature Extraction with TF-IDF

TF-IDF (Term Frequency-Inverse Document Frequency) transforms text into numerical features representing how important a word is in a document relative to the dataset.
```python
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(max_features=10000, stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies_df['combined'])
```

## Similarity Computation

```python
from sklearn.metrics.pairwise import cosine_similarity

cosine_similarities = cosine_similarity(tfidf_matrix[index], tfidf_matrix).flatten()
similar_indices = cosine_similarities.argsort()[-top_n-1:-1][::-1]
```

## Model Serialization

To avoid recomputing everything on each request, the model is saved as a `.pkl` file:

```python
import pickle

with open("model.pkl", "wb") as f:
    pickle.dump((tfidf_vectorizer, tfidf_matrix, movies_df), f)
```

## How the Algorithm Works (Mathematically)

Each movie is represented as a vector of TF-IDF weights:

**V**<sub>i</sub> = [w<sub>i1</sub>, w<sub>i2</sub>, ..., w<sub>in</sub>]

where w<sub>ij</sub> is the TF-IDF weight of term j in movie i.

The cosine similarity between two movies A and B is defined as:

**similarity(A, B) = (V<sub>A</sub> ⋅ V<sub>B</sub>) / (‖V<sub>A</sub>‖ × ‖V<sub>B</sub>‖)**

This measures the cosine of the angle between their feature vectors — a value close to 1 means the movies are very similar, while 0 means they are unrelated.

Movies with the highest cosine similarity scores to the input movie are returned as recommendations.

## 2. Django Backend API

### Purpose

The backend serves as the bridge between the trained ML model and client applications (like a Next.js frontend). It exposes a REST API endpoint to fetch recommendations for a given movie.

### Core Files

#### `utils.py`

Handles model loading and movie recommendation logic.

```python
from pathlib import Path
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

MODEL_PATH = PROJECT_ROOT / "ML-model" / "model.pkl"
DATA_PATH = PROJECT_ROOT / "ML-model" / "data" / "processed" / "merged_movies.csv"

with open(MODEL_PATH, "rb") as f:
    tfidf_vectorizer, tfidf_matrix, movies_df = pickle.load(f)

title_to_index = {title.lower(): i for i, title in enumerate(movies_df["title"])}

def recommend_movies(movie_title, top_n=10):
    movie_title = movie_title.lower()
    if movie_title not in title_to_index:
        raise ValueError(f"Movie '{movie_title}' not found in dataset")

    idx = title_to_index[movie_title]
    cosine_similarities = cosine_similarity(tfidf_matrix[idx], tfidf_matrix).flatten()
    similar_indices = cosine_similarities.argsort()[-top_n-1:-1][::-1]
    return movies_df.iloc[similar_indices]["title"].tolist()
```

#### `views.py`

Defines the `/api/recommend/` endpoint.

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import recommend_movies

@api_view(["POST"])
def recommend_view(request):
    title = request.data.get("title")
    if not title:
        return Response({"error": "Title is required"}, status=400)

    try:
        recommendations = recommend_movies(title)
        return Response({"recommendations": recommendations})
    except ValueError as e:
        return Response({"error": str(e)}, status=400)
```

#### `urls.py`

```python
from django.urls import path
from .views import recommend_view

urlpatterns = [
    path("recommend/", recommend_view, name="recommend"),
]
```

## 3. API Usage

### Endpoint
```
POST http://127.0.0.1:8000/api/recommend/
```

### Request Body
```json
{
  "title": "Toy Story"
}
```

### Response Example
```json
{
  "recommendations": [
    "Toy Story 2 (1999)",
    "Toy Story 3 (2010)",
    "Cars (2006)",
    "Finding Nemo (2003)",
    "Monsters, Inc. (2001)"
  ]
}
```

## 4. Testing the API

### Using PowerShell (Windows)
```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/recommend/" `
  -Method POST `
  -Body '{"title": "Toy Story"}' `
  -ContentType "application/json"
```

## 5. Running the Backend

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/abdelillah01/Movie-Recommender
   cd movie-recommender/backend
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Django server**
   ```bash
   python manage.py runserver
   ```

The API should now be available at:
```
http://127.0.0.1:8000/api/recommend/
```



## 3. Next.js Frontend

### Overview

The frontend is built with Next.js 14 (App Router) and communicates with the Django backend API. It provides an interactive UI where users can type a movie title, submit it, and instantly view recommended movies.

### Features

- Simple and clean movie search interface  
- Connects to Django REST API
- Error handling for missing or invalid titles


3. **Install dependencies**
   ```bash
   npm install
   npm install axios
   ```


## 6. Running the Frontend

Start the development server:

```bash
npm run dev
```

The app will run on:

 **http://localhost:3000**

Make sure your Django backend is running on `http://127.0.0.1:8000`

## 7. Enabling CORS in Django

If you haven't already, install and configure `django-cors-headers`:

```bash
pip install django-cors-headers
```

Then, add it in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'corsheaders',
    'rest_framework',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOW_ALL_ORIGINS = True  # or specify your frontend origin
```

## 8. Example Interaction

**User Input:**
```
Toy Story
```

**API Response (via Django):**
```json
{
  "recommendations": [
    "Toy Story 2 (1999)",
    "Toy Story 3 (2010)",
    "Cars (2006)",
    "Finding Nemo (2003)",
    "Monsters, Inc. (2001)"
  ]
}
```

**Frontend Output:**
A clean list of recommended movies displayed in the browser.

## 9. Full System Architecture

```
[User]
   ↓
[Next.js Frontend]
   ↓ (POST /api/recommend/)
[Django REST API]
   ↓ (loads model.pkl)
[TF-IDF Model]
   ↓
[Recommendations]
```

## 10. Author

**abdelillah01**

**Technologies:** Python, Django, scikit-learn, Next.js  
**Model Type:** Content Based Filtering using TF-IDF and Cosine Similarity

## Future Improvements

Currently I'm working to improve this project with the following enhancements:

- [ ] **User Authentication** - Allow users to create accounts and save their favorite recommendations
- [ ] **Rating System** - Implement movie ratings to improve recommendation quality
- [ ] **Advanced Filtering** - Add filters by genre, year, or rating
- [ ] **Hybrid Recommendations** - Combine content-based and collaborative filtering
- [ ] **Dockerization** - Containerize the application for easier deployment
- [ ] **Performance Optimization** - Improve recommendation algorithm speed and accuracy




