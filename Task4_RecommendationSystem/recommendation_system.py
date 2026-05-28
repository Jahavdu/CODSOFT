import os
import pandas as pd
import numpy as np
import customtkinter as ctk
from PIL import Image, ImageDraw
import requests
import threading
from sklearn.metrics.pairwise import cosine_similarity

# --- CONFIGURATION & FALLBACK DATASETS ---
MOVIES_CSV = "movies.csv"
TMDB_API_KEY = "978cbe6fa487dfbcbf2ca66cd86325ca"

TMDB_GENRE_MAP = {
    28: "Action", 12: "Adventure", 35: "Comedy", 878: "Sci-Fi",
    27: "Horror", 14: "Fantasy", 53: "Thriller", 18: "Drama",
    80: "Crime", 10749: "Romance", 16: "Animation", 9648: "Mystery"
}


def bootstrap_local_fallback():
    """Ensures a baseline library exists instantly on launch so the UI never waits for the network."""
    if not os.path.exists(MOVIES_CSV):
        data = {
            "movie_id": list(range(1, 16)),
            "title": [
                "John Wick: Chapter 4", "Mad Max: Fury Road", "Avengers: Endgame",
                "The Hangover", "Superbad", "Step Brothers",
                "Interstellar", "Inception", "The Matrix",
                "The Conjuring", "Insidious", "IT Chapter Two",
                "The Lord of the Rings", "The Hobbit", "Harry Potter"
            ],
            "genre": [
                "Action", "Action", "Action", "Comedy", "Comedy", "Comedy",
                "Sci-Fi", "Sci-Fi", "Sci-Fi", "Horror", "Horror", "Horror",
                "Fantasy", "Fantasy", "Fantasy"
            ]
        }
        pd.DataFrame(data).to_csv(MOVIES_CSV, index=False)


bootstrap_local_fallback()


# --- NATIVE NEON POSTER GENERATOR ENGINE ---
def generate_native_poster(title, genre):
    """Generates a premium dark-neon minimalist movie poster completely offline."""
    width, height = 180, 135
    img = Image.new("RGB", (width, height), "#18181B")
    draw = ImageDraw.Draw(img)

    accent_colors = {
        "Action": "#EF4444", "Adventure": "#F59E0B", "Comedy": "#10B981",
        "Sci-Fi": "#06B6D4", "Horror": "#8B5CF6", "Fantasy": "#EC4899",
        "Thriller": "#3B82F6", "Drama": "#6366F1", "Crime": "#14B8A6"
    }
    accent = accent_colors.get(genre, "#6B7280")

    draw.rectangle([0, 0, width, height], fill="#141417")
    draw.rectangle([0, height - 6, width, height], fill=accent)

    draw.rectangle([20, 25, 45, 40], outline=accent, width=2)
    draw.line([20, 32, 45, 32], fill=accent, width=1)

    display_title = title if len(title) <= 22 else f"{title[:19]}..."
    draw.text((25, 60), display_title, fill="#FFFFFF")
    draw.text((25, 80), genre.upper(), fill=accent)

    return ctk.CTkImage(light_image=img, dark_image=img, size=(180, 135))


# --- ADVANCED CONTENT-BASED PROFILE ML SYSTEM ---
class ContentBasedRecommender:
    def __init__(self):
        self.reload_dataframe()

    def reload_dataframe(self):
        """Reloads the local dataframe when background API updates occur."""
        self.movies_df = pd.read_csv(MOVIES_CSV)
        self.genre_matrix = pd.get_dummies(self.movies_df["genre"])

    def compute_recommendations(self, user_ratings_dict, num_rec=4):
        """Builds a preference profile vector to mathematically score and rank catalog elements."""
        if not user_ratings_dict:
            return self.movies_df.sample(min(num_rec, len(self.movies_df)))

        user_vector = np.zeros(len(self.genre_matrix.columns))
        genre_cols = list(self.genre_matrix.columns)

        for movie_title, rating in user_ratings_dict.items():
            movie_row = self.movies_df[self.movies_df["title"] == movie_title]
            if not movie_row.empty:
                genre = movie_row.iloc[0]["genre"]
                if genre in genre_cols:
                    idx = genre_cols.index(genre)
                    user_vector[idx] += (rating - 2.5)

        scores = cosine_similarity([user_vector], self.genre_matrix.values)[0]

        results_df = self.movies_df.copy()
        results_df["score"] = scores

        unrated_df = results_df[~results_df["title"].isin(user_ratings_dict.keys())]

        if unrated_df.empty:
            unrated_df = results_df

        final_rec = unrated_df.sort_values(ascending=False, by="score")
        return final_rec.head(num_rec)


# --- INDUSTRIAL SEARCH-ENABLED APP ENGINE ---
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.ml_engine = ContentBasedRecommender()
        self.active_user_ratings = {}

        ctk.set_appearance_mode("dark")
        self.title("AI Search & Recommendation Pipeline")
        self.geometry("1150x720")
        self.resizable(False, False)
        self.configure(fg_color="#09090B")

        # --- LEFT PANEL: PROFILE GENERATOR + SEARCH SYSTEM ---
        self.left_panel = ctk.CTkFrame(self, width=450, fg_color="#141417", corner_radius=0)
        self.left_panel.pack(side="left", fill="y")
        self.left_panel.pack_propagate(False)

        self.panel_title = ctk.CTkLabel(self.left_panel, text="PROFILE SEARCH ENGINE", font=("Helvetica", 18, "bold"),
                                        text_color="#F4F4F5")
        self.panel_title.pack(pady=(25, 5), padx=20, anchor="w")

        # Real-time Input Field
        self.search_entry = ctk.CTkEntry(
            self.left_panel,
            placeholder_text="🔍 Type movie name to isolate and rate instantly...",
            height=35,
            fg_color="#1C1C21",
            border_color="#27272A",
            text_color="#FFFFFF"
        )
        self.search_entry.pack(fill="x", padx=20, pady=(10, 5))
        self.search_entry.bind("<KeyRelease>", self._execute_live_search_filter)

        # Status indicator showing whether data is local or fetching live from API
        self.status_lbl = ctk.CTkLabel(self.left_panel, text="Sync Status: Operational (Using Local Database Cache)",
                                       font=("Helvetica", 11), text_color="#71717A")
        self.status_lbl.pack(padx=20, pady=(0, 10), anchor="w")

        self.rating_scroller = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.rating_scroller.pack(fill="both", expand=True, padx=10, pady=5)

        self._populate_rating_inputs()

        # --- RIGHT PANEL: OUTPUT PIPELINE CAROUSEL ---
        self.viewport = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.viewport.pack(side="right", fill="both", expand=True, padx=35, pady=25)

        self.view_title = ctk.CTkLabel(self.viewport, text="Personalized Discoveries", font=("Helvetica", 26, "bold"),
                                       text_color="#FFFFFF")
        self.view_title.pack(anchor="w", pady=(10, 5))

        self.view_subtitle = ctk.CTkLabel(self.viewport, text="Real-time mathematical processing results",
                                          font=("Helvetica", 13), text_color="#71717A")
        self.view_subtitle.pack(anchor="w", pady=(0, 30))

        self.rec_cards_frame = ctk.CTkFrame(self.viewport, fg_color="transparent")
        self.rec_cards_frame.pack(fill="x", pady=5)

        self.update_live_recommendations()

        # Kick off background API fetching worker safely
        threading.Thread(target=self._async_fetch_tmdb_movies, daemon=True).start()

    def _async_fetch_tmdb_movies(self):
        """Queries TMDB endpoints on a separate background thread to completely eliminate connection hangs."""
        self.after(0, lambda: self.status_lbl.configure(text="Sync Status: Querying live TMDB database matrix...",
                                                        text_color="#F59E0B"))
        movie_list = []
        seen_titles = set()

        try:
            for page in range(1, 5):
                url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
                response = requests.get(url, timeout=4).json()

                if "results" in response:
                    for movie in response["results"]:
                        title = movie.get("title")
                        genre_ids = movie.get("genre_ids")

                        if title and genre_ids and title not in seen_titles:
                            primary_genre = TMDB_GENRE_MAP.get(genre_ids[0], "Drama")
                            movie_list.append({
                                "movie_id": len(movie_list) + 1,
                                "title": title,
                                "genre": primary_genre
                            })
                            seen_titles.add(title)

            if movie_list:
                # Update database file on successful call completion
                pd.DataFrame(movie_list).to_csv(MOVIES_CSV, index=False)

                # Push updates safely back to the main UI display loop thread
                self.after(0, self._handle_successful_api_sync)
                return

        except Exception:
            # Catching connection loss silently to keep user session uninterrupted
            self.after(0, lambda: self.status_lbl.configure(
                text="Sync Status: Offline mode active (Fallback cache loaded)", text_color="#EF4444"))

    def _handle_successful_api_sync(self):
        """Refreshes the operational datasets smoothly once the background API worker delivers data."""
        self.status_lbl.configure(text="Sync Status: Connected Live (Database updated with top 80 current releases)",
                                  text_color="#10B981")
        self.ml_engine.reload_dataframe()
        self._populate_rating_inputs(self.search_entry.get())
        self.update_live_recommendations()

    def _populate_rating_inputs(self, search_query=""):
        """Clears and builds rating cards dynamically, preserving active selections."""
        for widget in self.rating_scroller.winfo_children():
            widget.destroy()

        sorted_movies = self.ml_engine.movies_df.sort_values(by=["genre", "title"])
        query = search_query.strip().lower()

        for _, row in sorted_movies.iterrows():
            title = row["title"]
            genre = row["genre"]

            if query and query not in title.lower():
                continue

            item_frame = ctk.CTkFrame(self.rating_scroller, fg_color="#1C1C21", height=52, corner_radius=6)
            item_frame.pack(fill="x", pady=4, padx=5)
            item_frame.pack_propagate(False)

            display_lbl = title if len(title) <= 22 else f"{title[:19]}..."
            label = ctk.CTkLabel(item_frame, text=f"{display_lbl}\n({genre})", font=("Helvetica", 11, "bold"),
                                 text_color="#E4E4E7", justify="left")
            label.pack(side="left", padx=12)

            rating_menu = ctk.CTkSegmentedButton(
                item_frame,
                values=["Unrated", "1★", "2★", "3★", "4★", "5★"],
                font=("Helvetica", 10),
                height=26,
                width=190,
                selected_color="#27272A",
                text_color="#FFFFFF",
                command=lambda val, t=title: self._register_rating_change(t, val)
            )
            rating_menu.pack(side="right", padx=12)

            current_saved_score = self.active_user_ratings.get(title)
            if current_saved_score:
                rating_menu.set(f"{current_saved_score}★")
            else:
                rating_menu.set("Unrated")

    def _execute_live_search_filter(self, event):
        """Triggers fluid text-matching filter updates on the selection pane."""
        current_query = self.search_entry.get()
        self._populate_rating_inputs(current_query)

    def _register_rating_change(self, movie_title, value):
        """Updates model profile coefficients based on live ratings adjustments."""
        if value == "Unrated":
            if movie_title in self.active_user_ratings:
                del self.active_user_ratings[movie_title]
        else:
            numeric_rating = int(value[0])
            self.active_user_ratings[movie_title] = numeric_rating

        self.update_live_recommendations()

    def update_live_recommendations(self):
        """Clears active display grids to re-render fresh matrix matching selections."""
        for widget in self.rec_cards_frame.winfo_children():
            widget.destroy()

        recommended_slice = self.ml_engine.compute_recommendations(self.active_user_ratings, num_rec=4)

        for _, row in recommended_slice.iterrows():
            card = ctk.CTkFrame(self.rec_cards_frame, width=180, height=235, fg_color="#141417", corner_radius=10,
                                border_color="#232326", border_width=1)
            card.pack(side="left", padx=(0, 16))
            card.pack_propagate(False)

            poster_image = generate_native_poster(row["title"], row["genre"])
            poster_canvas = ctk.CTkLabel(card, image=poster_image, text="")
            poster_canvas.pack(fill="x", padx=4, pady=4)

            meta_title = ctk.CTkLabel(card, text=row["title"], font=("Helvetica", 13, "bold"), text_color="#FFFFFF",
                                      wraplength=160, justify="center")
            meta_title.pack(pady=(12, 2), padx=6)

            meta_genre = ctk.CTkLabel(card, text=row["genre"], font=("Helvetica", 11), text_color="#71717A")
            meta_genre.pack()


if __name__ == "__main__":
    app = App()
    app.mainloop()