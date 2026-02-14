import random    # for random selection of a movie, (menu: 6. Random movie)
import statistics    # for median
import sys    # for exit application
from rapidfuzz import process, fuzz    # for search
from storage import movie_storage_sql as storage
from services.fetch_data import fetch_movie_from_api
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
STATIC_DIR = BASE_DIR / "static"


def print_empty_line():
    """
    print an empty line for a better display in the console
    """
    print()


def show_movie_menu_title():
    """
    title of the application,
    only displayed when opening the application on the first time
    """
    print('********** My Movies Database **********\n')


def show_movie_menu_content():
    """
    display the main menu of the application
    """
    print('Menu:')
    print(' 0. Exit')
    print(' 1. List movies')
    print(' 2. Add movie')
    print(' 3. Delete movie')
    print(' 4. Update movie')
    print(' 5. Stats')
    print(' 6. Random movie')
    print(' 7. Search movie')
    print(' 8. Movies sorted by rating')
    print(' 9. Movies sorted by year')
    print('10. Filter movies')
    print('11. Generate website')
    print_empty_line()
    movie_menu_user_choice()


def continue_next_choice():
    """
    ask the user if they want to return to the menu to perform a new action
    """
    print_empty_line()
    enter_for_continue = input('Press enter to continue')
    print_empty_line()

    if enter_for_continue == "":
        show_movie_menu_content()


def movie_menu_user_choice():
    """
    processes user input for menu options
    """

    dispatch = {
        '0': exit_application,
        '1': list_movies,
        '2': add_movie,
        '3': delete_movie,
        '4': update_movie_rating,
        '5': stats_movies,
        '6': random_movie,
        '7': search_movie,
        '8': movies_sorted_by_rating,
        '9': movies_sorted_by_year,
        '10': filter_movies,
        '11': generate_website,
    }

    while True:
        user_choice = input('Enter choice (0-10): ').strip()
        print_empty_line()

        if not user_choice:
            continue

        if user_choice in dispatch:
            dispatch[user_choice]()
        else:
            print('Please select a valid number for an action.\n')


def exit_application():
    """
    ends the application and prints bye
    """
    print('Bye!')
    sys.exit()


def list_movies():
    """
    lists all movies in the database,
    prints title, year and rating
    """
    # Get the data from the JSON file
    movies = storage.list_movies()

    print(f'{len(movies)} movies in total')
    print_empty_line()

    for movie, info in movies.items():
        print(f"{movie} ({info['year']}), Rating: {info['rating']}")

    continue_next_choice()


def add_movie():
    """
    adds a new movie with year and rating to the database
    """
    # Get the data from the JSON file
    movies = storage.list_movies()

    # Movie title input
    while True:
        movie_title = input('Enter new movie name '
                            '(or "q" to show the menu again): ').strip()

        if not movie_title:
            print('Movie name cannot be empty. Please try again.')
        # input 'q' exit the function and show the menu
        elif movie_title.lower() == 'q':
            print_empty_line()
            print("Action cancelled.")
            print_empty_line()
            continue_next_choice()
        elif movie_title in movies:
            print(f'Movie "{movie_title}" is already in the database.')
        else:
            break

    try:
        movie_data = fetch_movie_from_api(movie_title)
    except ConnectionError:
        print("Error: OMDb API not reachable.")
        continue_next_choice()
        return
    except RuntimeError:
        print(RuntimeError)
        continue_next_choice()
        return

    if movie_data is None:
        print(f'Data for movie "{movie_title}" not found.')
        continue_next_choice()
        return

    raw_rating = movie_data.get("imdbRating")

    if raw_rating == "N/A":
        print("Movie has no IMDb rating. Setting rating to 0.0")
        rating = 0.0
    else:
        rating = float(raw_rating)

    storage.add_movie(
        movie_data["Title"],
        int(movie_data["Year"]),
        rating,
        movie_data["Poster"],
        movie_data["imdbID"]
    )

    print(f'Movie "{movie_data["Title"]}" (Year: {movie_data["Year"]},'
          f'Rating: {rating}) '
          f'successfully added.')

    continue_next_choice()


def delete_movie():
    """
    deletes an existing movie from the database
    """
    # Get the data from the JSON file
    movies = storage.list_movies()

    # Movie title input
    while True:
        movie_title_to_delete = input('Enter movie name to delete: (or "q" '
                                      'to show the menu again): ').strip()

        if not movie_title_to_delete:
            print('Movie name cannot be empty. Please try again.')
        # input 'q' exit the function and show the menu
        elif movie_title_to_delete.lower() == 'q':
            print_empty_line()
            print("Action cancelled.")
            print_empty_line()
            continue_next_choice()
        elif movie_title_to_delete not in movies:
            print(f'Cannot find the movie "{movie_title_to_delete}" '
                  f'in the database. Please try again.')
        else:
            movies.pop(movie_title_to_delete)
            print(f'Movie {movie_title_to_delete} successfully deleted')
            break

    # Delete the movie and save the data to the JSON file
    storage.delete_movie(movie_title_to_delete)
    continue_next_choice()


def update_movie_rating():
    """
    updates the rating of a movie
    """
    # Get the data from the JSON file
    movies = storage.list_movies()

    # Movie title input
    while True:
        movie_title_to_update = input('Enter movie name (or "q" '
                                      'to show the menu again): ').strip()

        if not movie_title_to_update:
            print('Movie name cannot be empty. Please try again.')
        # input 'q' exit the function and show the menu
        elif movie_title_to_update.lower() == 'q':
            print_empty_line()
            print("Action cancelled.")
            print_empty_line()
            continue_next_choice()
        elif movie_title_to_update not in movies:
            print(f'Cannot find the movie "{movie_title_to_update}" '
                  f'in the database. Please try again.')
        else:
            break

    # New rating input
    while True:
        try:
            new_movie_rating = float(input('Enter new rating (0-10): '))
            if 0 <= new_movie_rating <= 10:
                movies[movie_title_to_update]['rating'] = new_movie_rating
                print(f'Updated Movie {movie_title_to_update}.')
                # Update rating of movie and save the data to the JSON file
                storage.update_movie(movie_title_to_update,
                                     new_movie_rating)
                break
        except ValueError:
            print('Invalid input: Rating must be between 0-10.')
            continue

    continue_next_choice()


def stats_movies():
    """
    shows statistics (average, median, best rating, worst rating)
    """
    # Get the data from the JSON file
    movies = storage.list_movies()

    all_ratings_list = []
    sum_ratings = 0

    for info in movies.values():
        rating = info['rating']
        all_ratings_list.append(rating)
        sum_ratings += rating

    # show the average rating
    average_rating = sum_ratings / len(movies)
    print(f'Average rating: {average_rating:.1f}')

    # show the median rating
    sorted_ratings = sorted(all_ratings_list)
    median_rating = statistics.median(sorted_ratings)
    print(f'Median rating: {median_rating:.1f}')

    # show the best movie
    max_rating = max(all_ratings_list)
    for movie, info in movies.items():
        if info['rating'] == max_rating:
            print(f"Best movie: {movie}, {info['rating']}")

    # show the worst movie
    min_rating = min(all_ratings_list)
    for movie, info in movies.items():
        if info['rating'] == min_rating:
            print(f"Worst movie: {movie}, {info['rating']}")

    continue_next_choice()


def random_movie():
    """
    selects a movie at random from the list
    """
    # Get the data from the JSON file
    movies = storage.list_movies()

    movie, info = random.choice(list(movies.items()))
    print(f"Your movie for tonight: {movie} ({info['year']}), "
          f"it's rated {info['rating']}")

    continue_next_choice()


def search_movie():
    """
    search for movies
    """
    # Get the data from the JSON file
    movies = storage.list_movies()

    # Movie title input
    while True:
        search_term = input('Enter part of movie name '
                            '(or "q" to show the menu again): ').strip()

        if not search_term:
            print('Movie name cannot be empty. Please try again.')
            continue
        # input 'q' exit the function and show the menu
        if search_term.lower() == 'q':
            print_empty_line()
            print("Action cancelled.")
            print_empty_line()
            continue_next_choice()
        break

    matches = process.extract(search_term, movies.keys(),
                              scorer=fuzz.WRatio, limit=5)

    good_matches = [match for match in matches if match[1] >= 60]

    if good_matches:
        exact_match = next((
            m for m in good_matches
            if m[0].casefold() == search_term.casefold()), None
        )

        if exact_match:
            info = movies[exact_match[0]]
            year, rating = info['year'], info['rating']
            print(f"{exact_match[0]} ({year}), rating {rating}")
        else:
            print(f'\nThe movie "{search_term}" does not exist. Did you mean:')
            for title, _, _ in good_matches:
                info = movies[title]
                year, rating = info['year'], info['rating']
                print(title)

    continue_next_choice()


def movies_sorted_by_rating():
    """
    displays movies sorted by rating (top rated movie first, then descending)
    """
    # Get the data from the JSON file
    movies = storage.list_movies()

    sorted_movies_by_rating = dict(sorted(movies.items(),
                                          key=lambda item: item[1]['rating'],
                                          reverse=True))

    for movie, info in sorted_movies_by_rating.items():
        print(f"{movie} ({info['year']}): {info['rating']}")

    continue_next_choice()


def movies_sorted_by_year():
    """
    displays movies sorted by year
    Users can choose whether to sort the films by release year in
    ascending ("up") or descending ("down") order.
    """
    # Get the data from the JSON file
    movies = storage.list_movies()

    while True:
        sorting_years_option = input('Do you want to sort ascending '
                                     '(enter "up") or descending '
                                     '(enter "down")? ').strip().lower()

        if sorting_years_option == 'up':
            reverse_order = False
            break
        if sorting_years_option == 'down':
            reverse_order = True
            break

        print('Invalid input. Please enter "up" or "down".')

    sorted_movies_by_year = dict(
        sorted(
            movies.items(),
            key=lambda item: item[1]['year'],
            reverse=reverse_order
        )
    )

    for movie, info in sorted_movies_by_year.items():
        print(f"{movie} ({info['year']})")

    continue_next_choice()


def filter_movies():
    """
    Prompt the user to input the minimum rating, start year, and end year.
    Filter the list of movies based on the provided criteria.
    If the user leaves an entry blank, this will be considered as
    no minimum rating, no start year or no end year.
    """
    movies = storage.list_movies()

    # minimum rating
    minimum_rating = input('Enter minimum rating '
                           '(leave blank for no min rating): ').strip()

    if minimum_rating:
        minimum_rating = float(minimum_rating)
    else:
        minimum_rating = None

    # start year
    start_year = input('Enter start year '
                       '(leave blank for no start year): ').strip()

    if start_year:
        start_year = int(start_year)
    else:
        start_year = None

    # end year
    end_year = input('Enter end year '
                     '(leave blank for no end year): ').strip()

    if end_year:
        end_year = int(end_year)
    else:
        end_year = None

    # Filter logic
    filtered_movies = {
        title: info for title, info in movies.items()
        if (
            minimum_rating is None or info['rating'] >= minimum_rating
        ) and (
            start_year is None or info['year'] >= start_year
        ) and (
            end_year is None or info['year'] <= end_year)
    }

    if not filtered_movies:
        print('No movies match your filters.')
    else:
        print_empty_line()
        print('Filtered Movies:')
        for title, info in filtered_movies.items():
            print(f"{title} ({info['year']}): {info['rating']}")

    continue_next_choice()


def generate_website():
    """
    Generates a website (generated-website.html) using the template
    and movies from the DB
    """
    # Load all movies from DB
    movies = storage.list_movies()
    movie_items = ""

    for title, info in movies.items():
        poster = info.get("poster", "")
        imdb_id = info.get("imdb_id")
        imdb_url = (
            f"https://www.imdb.com/title/{imdb_id}/"
            if imdb_id else "#"
        )
        movie_items += (
            f'<li>\n'
            f'    <div class="movie">\n'
            f'      <a href="{imdb_url}" target="_blank">\n'
            f'          <img class="movie-poster" src="{poster}">\n'
            f'      </a>\n'
            f'      <div class="movie-title">{title}</div>\n'
            f'      <div class="movie-year">{info["year"]}</div>\n'
            f'    </div>\n'
            f'</li>\n'
        )

    with open(STATIC_DIR / "index_template.html") as f:
        template = f.read()

    html = template.replace("__TEMPLATE_TITLE__", "My Movie App")
    html = html.replace("__TEMPLATE_MOVIE_GRID__", movie_items)

    with open(STATIC_DIR / "generated-website.html", "w") as f:
        f.write(html)

    print("Website was generated successfully.")


def main():
    """
    Starting point of the application
    """
    # Show title and menu of the application
    show_movie_menu_title()
    show_movie_menu_content()


if __name__ == '__main__':
    main()
