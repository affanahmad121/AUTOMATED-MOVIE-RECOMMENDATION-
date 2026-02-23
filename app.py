import streamlit as st
import pickle
import requests
import urllib.parse

# --- Configuration ---
TMDB_API_KEY = "d4ab109228e3e30f5f39870ce41eabe5"
TMDB_BASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500/"
PLACEHOLDER_IMAGE_URL = "https://placehold.co/150x225/cccccc/333333?text=No+Image"

# --- Define fixed image and card dimensions ---
IMAGE_WIDTH = "150px"  # Fixed width for consistency
IMAGE_HEIGHT = "225px"  # Standard poster aspect ratio 1:1.5 (150x225)
# Calculate card height: Image height + padding + text area min-height + some buffer
# Re-evaluate CARD_HEIGHT: 225 (img) + 20 (card padding) + 8 (text margin-top) + ~40 (for 2 lines of text) = 293px
CARD_HEIGHT = "295px"  # Adjusted for a snug fit. Fine-tune if text wraps differently.

# --- Streamlit Page Configuration (MUST BE FIRST) ---
st.set_page_config(page_title="Movie Recommendation System", layout="centered")

# --- Inject Custom CSS for consistent sizing, hover effects, and spacing ---
st.markdown(f"""
<style>
/* Remove default padding from Streamlit's main content wrapper if it causes unwanted outer gaps */
/* Use data-testid selector for robustness */
div[data-testid="stVerticalBlock"] > div:first-child {{ /* Target the main content area */
    padding-left: 0rem;
    padding-right: 0rem;
}}

/* Ensure Streamlit columns have no internal padding and manage their content */
/* Use data-testid selector for robustness */
div[data-testid="column"] {{
    padding-left: 0rem !important;
    padding-right: 0rem !important;
    display: flex; /* Make columns flex containers */
    justify-content: center; /* Center content (your movie cards) horizontally within columns */
    align-items: flex-start; /* Align content to the top within columns */
}}

/* Style for the clickable movie card container */
.movie-card-container {{
    border: 1px solid #333; /* A subtle border */
    border-radius: 8px; /* Rounded corners */
    padding: 10px;
    margin: 0 5px; /* <--- KEY CHANGE: Added horizontal margin here */
    text-align: center;
    cursor: pointer;
    background-color: #1a1a1a; /* Dark background for the card */
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    width: {IMAGE_WIDTH}; /* Fixed width for the entire card */
    height: {CARD_HEIGHT}; /* Fixed height for the entire card */
    display: flex; /* Use flexbox for internal layout */
    flex-direction: column; /* Stack image and text vertically */
    justify-content: space-between; /* Push image to top, text to bottom */
    align-items: center; /* Center content horizontally */
    overflow: hidden; /* Hide anything that overflows the fixed height */
    box-sizing: border-box; /* Include padding and border in the element's total width and height */
}}

/* Hover effect for the movie card container */
.movie-card-container:hover {{
    transform: translateY(-5px); /* Lift effect */
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4); /* More pronounced shadow */
}}

/* Style for the movie title text */
.movie-title-text {{
    font-weight: bold;
    font-size: 0.95em;
    margin-top: 8px; /* Space between image and text */
    margin-bottom: 0;
    flex-grow: 1; /* Allow text to take available space */
    display: flex; /* Use flexbox for text alignment */
    align-items: center; /* Center text vertically */
    justify-content: center; /* Center text horizontally */
    color: #eee; /* Light color for text */
    overflow: hidden; /* Hide overflow */
    text-overflow: ellipsis; /* Add ellipsis for overflowing text */
    display: -webkit-box; /* For multi-line ellipsis */
    -webkit-line-clamp: 2; /* Limit text to 2 lines */
    -webkit-box-orient: vertical;
    word-break: break-word; /* Break long words */
    padding: 0 2px; /* Small horizontal padding for text within its box */
    text-align: center; /* Ensure text is centered horizontally */
}}

/* Style for the movie poster image */
.movie-poster-image {{
    width: {IMAGE_WIDTH}; /* Fixed width */
    height: {IMAGE_HEIGHT}; /* Fixed height */
    object-fit: cover; /* Ensures images cover the area without distortion */
    border-radius: 4px; /* Slightly rounded image corners */
    flex-shrink: 0; /* Prevent image from shrinking */
}}
</style>
""", unsafe_allow_html=True)


# --- Helper function to fetch poster URL from TMDb API ---
def fetch_poster(movie_id, api_key):
    """
    Fetches the poster path for a given movie ID from the TMDb API.
    """
    if not api_key or api_key == "YOUR_TMDB_API_KEY":
        st.warning(
            "Please replace 'YOUR_TMDB_API_KEY' in the code with your actual TMDb API key to fetch movie posters.")
        return PLACEHOLDER_IMAGE_URL

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return TMDB_BASE_IMAGE_URL + poster_path
        else:
            return PLACEHOLDER_IMAGE_URL
    except requests.exceptions.Timeout:
        st.error(
            f"Timeout error: Could not connect to TMDb API for movie ID {movie_id}. Please check your internet connection or try again later.")
        return PLACEHOLDER_IMAGE_URL
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster for movie ID {movie_id}: {e}")
        return PLACEHOLDER_IMAGE_URL
    except ValueError:
        st.error(f"Error decoding JSON response for movie ID {movie_id}.")
        return PLACEHOLDER_IMAGE_URL


# --- Load data ---
try:
    movies = pickle.load(open('movies.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    st.error(
        "Error: 'movies.pkl' or 'similarity.pkl' not found. Please ensure these files are in the same directory as the script.")
    st.stop()

st.title("🎬 Movie Recommendation System")
st.write("Get personalized movie recommendations based on your favorite movie!")

# Initialize session state for selected_movie if not already set
if 'selected_movie' not in st.session_state:
    st.session_state.selected_movie = None

movie_list = movies['title'].values

# --- Check for clicked movie from URL query parameters ---
if "movie_clicked" in st.query_params:
    clicked_movie_title = st.query_params["movie_clicked"]
    if isinstance(clicked_movie_title, list):
        clicked_movie_title = clicked_movie_title[0]

    clicked_movie_title = urllib.parse.unquote(clicked_movie_title)

    if clicked_movie_title != st.session_state.selected_movie:
        st.session_state.selected_movie = clicked_movie_title
        st.query_params.clear()
        st.rerun()

# Dropdown for initial movie selection or to change selection
initial_selected_movie_from_dropdown = st.selectbox(
    "Select a movie you like:",
    movie_list,
    key="dropdown_movie_selector",
    index=list(movie_list).index(
        st.session_state.selected_movie) if st.session_state.selected_movie in movie_list else 0
)

# If the dropdown selection changes, update the session state and rerun
if initial_selected_movie_from_dropdown != st.session_state.selected_movie:
    st.session_state.selected_movie = initial_selected_movie_from_dropdown
    st.query_params.clear()
    st.rerun()


# --- Recommend function ---
def recommend(movie):
    """
    Recommends movies based on similarity and fetches their posters.
    """
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        st.error(f"Movie '{movie}' not found in the dataset. Please select another movie.")
        return [], [], []

    distances = similarity[index]
    movie_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_movie_ids = []

    for i in movie_indices:
        movie_row = movies.iloc[i[0]]
        recommended_movies.append(movie_row.title)
        recommended_movie_ids.append(movie_row.id)
        poster_url = fetch_poster(movie_row.id, TMDB_API_KEY)
        recommended_posters.append(poster_url)

    return recommended_movies, recommended_posters, recommended_movie_ids


# --- Streamlit UI for Recommendation ---
if st.button("Recommend", key="main_recommend_button") or st.session_state.selected_movie:
    if TMDB_API_KEY == "YOUR_TMDB_API_KEY":
        st.warning("Please update the `TMDB_API_KEY` in the script to fetch actual movie posters.")

    if st.session_state.selected_movie:
        with st.spinner(f"Fetching recommendations for '{st.session_state.selected_movie}'..."):
            recommendations, posters, _ = recommend(st.session_state.selected_movie)

        if recommendations:
            st.markdown("---")
            st.subheader("Recommended Movies:")

            # Using gap="small" on st.columns helps control overall column spacing
            cols = st.columns(5, gap="medium")

            for idx, col in enumerate(cols):
                with col:
                    encoded_movie_title = urllib.parse.quote(recommendations[idx])

                    movie_card_html = f"""
                    <a href="?movie_clicked={encoded_movie_title}" style="text-decoration: none; color: inherit;">
                        <div class="movie-card-container" style="margin-left:0,margin-right:10px">
                            <img src="{posters[idx]}" alt="{recommendations[idx]} poster" class="movie-poster-image">
                            <p class="movie-title-text">{recommendations[idx]}</p>
                        </div>
                    </a>
                    """
                    st.markdown(movie_card_html, unsafe_allow_html=True)
        else:
            st.info("No recommendations found for the selected movie or an error occurred.")

        # --- About section for the currently selected movie ---
        st.markdown("---")
        st.subheader(f"About '{st.session_state.selected_movie}'")
        movie_info = movies[movies['title'] == st.session_state.selected_movie].iloc[0]

        selected_movie_poster_url = fetch_poster(movie_info.id, TMDB_API_KEY)
        st.image(selected_movie_poster_url, width=150)

        if 'overview' in movie_info and movie_info['overview']:
            st.write("**Overview:**", movie_info['overview'])
        elif 'tags' in movie_info and movie_info['tags']:
            st.write("**Tags:**", movie_info['tags'])
        else:
            st.write("No overview or tags available for this movie.")
    else:
        st.info("Please select a movie from the dropdown or click 'Recommend' to get started.")

# --- Sidebar About Section ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/744/744922.png", width=80)
st.sidebar.title("About")
st.sidebar.markdown(
    """
    **Movie Recommendation System**  
    This app suggests movies based on your favorite selection using content-based filtering.  
    - Built with TMDb 5000 Movie Dataset  
    - Uses NLP and cosine similarity  
    - Movie posters fetched from **The Movie Database (TMDb) API**
    - Created by **AFFAN**
    """
)
st.sidebar.markdown("---")
st.sidebar.caption("© 2025 AFFAN. All rights reserved.")