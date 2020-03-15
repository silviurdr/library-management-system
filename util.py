import connection as con

import bcrypt


def get_selected_book(book_id):
    all_books = con.get_all_books()
    for book in all_books:
        if int(book['book_id']) == int(book_id):
            selected_book = book
            return selected_book

    return None


def hash_password(plain_text_password):
    # By using bcrypt, the salt is saved into the hash itself
    hashed_bytes = bcrypt.hashpw(
        plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


def get_list_of_titles_rented_per_member(active_session):
    username = active_session['username']
    all_books = con.get_books_for_member(username)
    titles = []
    for book in all_books:
        titles.append(book['title'])
    return titles


def calculate_fine(return_days_delay):

    if return_days_delay <= 0:
        fine_amount = 0
    elif 0 < return_days_delay < 7:
        fine_amount = 5
    elif 7 < return_days_delay < 31:
        fine_amount = 10
    elif return_days_delay > 30:
        fine_amount = 20

    return fine_amount


def calculate_vote_percentage(votes_up, votes_down):
    try:
        positive_reviews = round(votes_up /(votes_up + votes_down)   * 100)
        return positive_reviews
    except ZeroDivisionError:
        return 0
