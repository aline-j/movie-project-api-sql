from sqlalchemy import create_engine, text
from pathlib import Path

# Define the database URL
BASE_DIR = Path(__file__).resolve().parents[2]
DB_URL = f"sqlite:///{BASE_DIR / 'data' / 'movies.db'}"

# Create the engine
engine = create_engine(DB_URL)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            year INTEGER NOT NULL,
            rating REAL NOT NULL,
            poster TEXT,
            imdb_id TEXT
        )
    """))
    connection.commit()


def list_movies():
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT title, year, rating, poster, imdb_id FROM movies")
        )
        rows = result.fetchall()

    return {
        title: {
            "year": year,
            "rating": rating,
            "poster": poster,
            "imdb_id": imdb_id
        }
        for title, year, rating, poster, imdb_id in rows
    }


def add_movie(title, year, rating, poster, imdb_id):
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""
                    INSERT INTO movies (title, year, rating, poster, imdb_id)
                    VALUES (:title, :year, :rating, :poster, :imdb_id)
                """),
                {
                    "title": title,
                    "year": int(year),
                    "rating": float(rating),
                    "poster": poster,
                    "imdb_id": imdb_id
                }
            )
            connection.commit()
        except Exception as e:
            print(f"DB error: {e}")
            return False


def delete_movie(title):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("DELETE FROM movies WHERE title = :title"),
                {"title": title},
            )
            connection.commit()
            print(f"Movie {title} deleted successfully.")
        except Exception as e:
            print(f"Error {e}")


def update_movie(title, rating):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text(
                    "UPDATE movies "
                    "SET rating = :rating "
                    "WHERE title = :title"
                ),
                {"title": title, "rating": float(rating)},
            )
            connection.commit()
            print(f"Movie '{title}' updated successfully.")
        except Exception as e:
            print(f"Error: {e}")
