#Automated Movie Recommendation System

A production-style Content-Based Movie Recommendation System built using Natural Language Processing (NLP) and Cosine Similarity.
The application recommends the Top 5 most similar movies based on user selection and dynamically fetches movie posters via TMDb API.


#Project Overview

This project demonstrates practical implementation of:

Text vectorization using NLP

Similarity computation using cosine similarity

Precomputed similarity matrix optimization

Interactive web deployment using Streamlit

API integration for real-time poster fetching

The system analyzes movie metadata and returns highly relevant recommendations instantly.


#Recommendation Architecture
- Data Processing Pipeline

Combine movie metadata (genres, keywords, cast, crew, overview)

Apply NLP preprocessing (tokenization, stemming, cleaning)

Convert text into vectors

Compute cosine similarity matrix

Store similarity matrix using pickle for fast retrieval


#Recommendation Logic
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_indices = sorted(list(enumerate(distances)),
                           reverse=True,
                           key=lambda x: x[1])[1:6]
✔ Retrieves movie index
✔ Sorts similarity scores
✔ Returns Top 5 similar movies


#Application Features

Interactive movie selection dropdown

Top 5 real-time recommendations

Dynamic movie posters via TMDb API

Clickable recommendation cards

Overview display for selected movie

Clean responsive UI with custom CSS styling

Optimized similarity lookup using precomputed matrix


#Tech Stack
Category	Technology
Language	Python
Frontend	Streamlit
NLP	Text Vectorization
Similarity Metric	Cosine Similarity
Data Storage	Pickle
API Integration	TMDb API


#📂 Project Structure
├── app.py
├── movies.pkl
├── similarity.pkl
├── notebook.ipynb
├── requirements.txt
└── README.md


#How to Run Locally
1️ Clone Repository
[git clone https://github.com/yourusername/movie-recommendation-system.git
cd movie-recommendation-system]

2.Install Dependencies
[pip install -r requirements.txt]

3.Run Application
[streamlit run app.py]

#TMDb API Setup

Create an account at The Movie Database (TMDb)

Generate API Key

Replace in app.py:  TMDB_API_KEY = "YOUR_TMDB_API_KEY"


#Key Highlights

Implemented end-to-end NLP-based recommendation engine

Optimized performance using precomputed similarity matrix

Integrated third-party API for real-time poster retrieval

Built interactive frontend using Streamlit

Demonstrates strong understanding of:

Text processing

Vector space modeling

Similarity metrics

Deployment-ready ML applications


#Future Enhancements

Add collaborative filtering

Deploy on Streamlit Cloud / AWS

Replace cosine similarity with advanced embeddings (Word2Vec / BERT)

Add user login & personalized history

Integrate movie trailer API


#Author

Affan Ahmad
Machine Learning & AI Enthusiast

#Show Your Support

If you found this project useful, consider giving it a ⭐ on GitHub.
