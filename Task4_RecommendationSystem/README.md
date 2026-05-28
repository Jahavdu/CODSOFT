# Advanced AI Movie Recommendation System

An advanced AI-powered movie recommendation platform built using Python, Machine Learning, and CustomTkinter for the CodSoft Artificial Intelligence Internship.

## Features

* Modern Netflix-style GUI
* Personalized movie recommendations
* Real-time search filtering
* Dynamic user rating system
* Content-based recommendation engine
* Cosine similarity recommendation logic
* Live recommendation updates
* Offline fallback movie database
* TMDB API integration
* Background threaded API fetching
* AI-generated movie poster rendering
* Genre-based recommendation profiling

## Technologies Used

* Python
* CustomTkinter
* Pandas
* NumPy
* Scikit-learn
* Pillow
* Requests
* Cosine Similarity Algorithm

## Machine Learning Logic

The recommendation engine uses:

* Content-Based Filtering
* One-Hot Genre Encoding
* Cosine Similarity

The system mathematically builds a user preference vector based on movie ratings and generates recommendations by comparing similarity scores across the dataset.

## Features Explained

### Content-Based Recommendation System

The AI recommends movies based on genres and previously rated content.

### Live Recommendation Engine

Recommendations update instantly as users change ratings.

### TMDB API Integration

The system can fetch popular movies from The Movie Database (TMDB) API in real time.

### Offline Fallback System

If internet access fails, the system automatically loads a local movie database cache.

### Poster Generation

Custom neon-style movie posters are dynamically generated using Pillow.

## Project Structure

```text id="2p2mvz"
Task4_RecommendationSystem
│
├── recommendation_system.py
├── movies.csv
├── requirements.txt
├── README.md
└── generated_assets
```

## How to Run

### 1. Install Requirements

```bash id="k6sxh1"
pip install -r requirements.txt
```

### 2. Run the Application

```bash id="7o0kww"
python recommendation_system.py
```

## User Features

* Search movies instantly
* Rate movies dynamically
* Generate personalized recommendations
* Switch between online and offline datasets
* View AI-generated recommendation cards

## Internship

This project was created as part of the CodSoft Artificial Intelligence Internship.

## Author

Durvesh Jadhav
