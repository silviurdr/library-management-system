import database_common


@database_common.connection_handler
def get_all_books(cursor):
    cursor.execute("""
    SELECT * from book
    ORDER BY book_id;
    """)
    all_books = cursor.fetchall()
    return all_books


# @database_common.connection_handler
# def get_book_id(cursor, book_id):
#     cursor.execute(f"""
#     SELECT book_id from book
#     WHERE book_id={book_id};
#     """)


@database_common.connection_handler
def add_new_member_to_database(cursor, member):
    cursor.execute("""
    INSERT INTO member (full_name, city, email, password, username) VALUES('{0}', '{1}', '{2}', '{3}', '{4}');
    """.format(member['full_name'], member['city'], member['email'], member['password'], member['username']))


@database_common.connection_handler
def check_registered_user(cursor, username):
    cursor.execute("""
    SELECT * FROM member
    WHERE username = '{0}'
    """.format(username))

    login_member = cursor.fetchall()
    return login_member


@database_common.connection_handler
def get_user_info(cursor, selected_member_id):
    cursor.execute("""
    SELECT * FROM member
    WHERE member_id = '{0}'
    """.format(selected_member_id))
    user_info = cursor.fetchall()
    return user_info


@database_common.connection_handler
def get_user_full_name(cursor, username):
    cursor.execute("""
        SELECT full_name FROM member
        WHERE username = '{0}'
        """.format(username))

    full_name = cursor.fetchall()
    return full_name


@database_common.connection_handler
def get_copies(cursor, selected_book_id):
    cursor.execute("""
    SELECT copies FROM book
    WHERE book_id={0}
    """.format(selected_book_id))
    copies = cursor.fetchone()
    return copies



@database_common.connection_handler
def get_member_id_by_username(cursor, username_session):
    cursor.execute("""
    SELECT member_id FROM member
    WHERE username='{0}' """.format(username_session))
    member_id = cursor.fetchone()
    return member_id


@database_common.connection_handler
def get_member_id_by_username_from_review(cursor, reviewer_member_id):
    cursor.execute("""
    SELECT member_id FROM review
    WHERE member_id='{0}'""".format(reviewer_member_id))
    member_id = cursor.fetchone()
    return member_id


@database_common.connection_handler
def rent_book_database(cursor, book_id, member_id):
    cursor.execute("""
    UPDATE book
    SET copies = copies - 1
    WHERE book_id = {0}
    """.format(book_id))
    cursor.execute("""
    INSERT INTO rented (member_id, book_id, date_rented, date_due, date_returned) VALUES('{0}', '{1}', CURRENT_DATE, CURRENT_DATE + INTERVAL '14 DAYS', CURRENT_DATE + INTERVAL '100 DAYS')
    """.format(member_id['member_id'], book_id))


@database_common.connection_handler
def get_book_by_id(cursor, book_id):
    cursor.execute(f"""
        SELECT book_id from book
        WHERE book_id = {book_id}
    """)
    selected_book_id = cursor.fetchone()
    return selected_book_id


@database_common.connection_handler
def get_books_for_member(cursor, username_session):
    cursor.execute("""
    SELECT r.rented_id, b.book_id, title, author, published_date, isbn, date_due - CURRENT_DATE as remaining_days FROM book b
    INNER JOIN rented r ON (b.book_id = r.book_id)
    INNER JOIN member m ON (m.member_id=r.member_id)
    WHERE m.username='{0}' and r.returned=False
    """.format(username_session))
    rented_books_for_member = cursor.fetchall()
    return rented_books_for_member


@database_common.connection_handler
def get_rented_id(cursor, selected_book_id, session_username):
    cursor.execute("""
    SELECT rented_id FROM rented r
    JOIN member m ON (r.member_id = m.member_id)
    WHERE username='{0}' AND book_id={1};
    """.format(session_username, selected_book_id))
    rented_id = cursor.fetchone()
    return rented_id


@database_common.connection_handler
def get_rented_book(cursor, selected_book_id, session_username):
    cursor.execute("""
    SELECT * FROM rented r
    JOIN member m ON (r.member_id = m.member_id)
    WHERE username='{0}' AND book_id={1};
    """.format(session_username, selected_book_id))
    rented_id = cursor.fetchone()
    return rented_id


@database_common.connection_handler
def return_book_database(cursor, selected_book_id, username_session, selected_rented_id):
    cursor.execute("""
    UPDATE book b
    SET copies = copies + 1
    WHERE book_id={0};
    """.format(selected_book_id))

@database_common.connection_handler
def get_day_diff(cursor, selected_rented_id):
    cursor.execute(f"""
    SELECT CURRENT_DATE - date_due as date_diff from rented
    WHERE rented_id={selected_rented_id['rented_id']} 
    """)
    day_diff = cursor.fetchone()
    return day_diff



@database_common.connection_handler
def delete_returned_book_database(cursor, selected_rented_id):
    cursor.execute(f"""
    DELETE from rented r
    WHERE rented_id={selected_rented_id['rented_id']}
    """)
  

@database_common.connection_handler
def add_review_to_database(cursor, reviewed_book_id, reviewer_member_id, review, filename):
    cursor.execute(f"""
    INSERT INTO review
    (member_id, book_id, review_date, review_rating, message, subject, image)
    VALUES ({reviewer_member_id}, {reviewed_book_id}, CURRENT_DATE, {review['rating']},
     '{review['message']}', '{review['subject']}', '{filename}')
    """)


@database_common.connection_handler
def get_book_reviews(cursor, selected_book_id):
    cursor.execute(f"""
    SELECT r.review_date, r.member_id, r.review_rating, r.review_id, r.votes_up, r.votes_down,
    r.image, r.message, r.subject, m.username from review r
    INNER JOIN member m
    ON(m.member_id = r.member_id)
    WHERE book_id={selected_book_id}
    ORDER by r.review_date DESC;
    """)
    reviews = cursor.fetchall()
    return reviews

@database_common.connection_handler
def get_reviewers_for_book(cursor, selected_book_id):
    cursor.execute(f"""
    SELECT member_id from review
    WHERE book_id={selected_book_id}
    """)
    reviewers_for_book = cursor.fetchall()
    return reviewers_for_book 


@database_common.connection_handler
def get_all_info_for_selected_book(cursor, selected_book_id):
    cursor.execute(f"""
    SELECT book_id, title, author, published_date, isbn, copies, image, about, votes_up, votes_down, votes_up + votes_down as total_votes
    from book
    WHERE book_id={selected_book_id}
    """)
    all_book_info = cursor.fetchone()
    return all_book_info


@database_common.connection_handler
def vote_book_up(cursor, selected_book_id):
    cursor.execute(f"""
    UPDATE book
    SET votes_up = votes_up + 1
    WHERE book_id={selected_book_id}
    """)

@database_common.connection_handler
def vote_book_down(cursor, selected_book_id):
    cursor.execute(f"""
    UPDATE book
    SET votes_down = votes_down + 1
    WHERE book_id={selected_book_id}
    """)

@database_common.connection_handler
def register_vote_for_member(cursor, username_session, book_id, index):
    cursor.execute(f"""
    UPDATE member
    SET voted_books[{index}]={book_id}
    WHERE username='{username_session}'
    """)

@database_common.connection_handler
def register_vote_review_for_member(cursor, username_session, review_id, index):
    cursor.execute(f"""
    UPDATE member
    SET voted_reviews[{index}]={review_id}
    WHERE username='{username_session}'
    """)

@database_common.connection_handler
def get_voted_books_for_member(cursor, username_session):
    cursor.execute(f"""
    SELECT voted_books from member
    WHERE username='{username_session}'
    """)
    all_voted_books = cursor.fetchone()
    return all_voted_books

@database_common.connection_handler
def get_voted_reviews_for_member(cursor, username_session):
    cursor.execute(f"""
    SELECT voted_reviews from member
    WHERE username='{username_session}'
    """)
    all_reviews_voted = cursor.fetchone()
    return all_reviews_voted


@database_common.connection_handler
def get_book_id_by_review_id(cursor, selected_review_id):
    cursor.execute(f"""
    SELECT book_id from review
    WHERE review_id={selected_review_id}
    """)
    book_id_for_review = cursor.fetchone()
    return book_id_for_review


@database_common.connection_handler
def vote_review_up(cursor, selected_review_id):
    cursor.execute(f"""
    UPDATE review
    SET votes_up = votes_up + 1
    WHERE review_id={selected_review_id}
    """)


@database_common.connection_handler
def vote_review_down(cursor, selected_review_id):
    cursor.execute(f"""
    UPDATE review
    SET votes_down = votes_up + 1
    WHERE review_id={selected_review_id}
    """)


@database_common.connection_handler
def get_info_for_review(cursor, selected_review_id):
    cursor.execute(f"""
    SELECT message, image, subject, review_rating
    FROM review
    WHERE review_id={selected_review_id}
    """)
    info_for_review = cursor.fetchone()
    return info_for_review


@database_common.connection_handler
def edit_review_database(cursor, selected_review_id, review_to_edit, filename):
    cursor.execute(f"""
    UPDATE review
    SET message='{review_to_edit["message"]}', subject='{review_to_edit["subject"]}',
    image='{filename}', review_rating={review_to_edit["review_rating"]}
    WHERE review_id={selected_review_id}
    """)


@database_common.connection_handler
def get_user_reviews(cursor, selected_member_id):
    cursor.execute(f"""
    SELECT r.review_date, r.message, r.image, r.subject, r.review_rating,
    r.votes_up, r.votes_down, b.book_id, b.title, b.image as book_image from review r
    INNER JOIN book b ON (b.book_id=r.book_id)
    WHERE member_id={selected_member_id}
    ORDER BY r.review_date DESC;
    """)
    reviews_for_user = cursor.fetchall()
    return reviews_for_user

@database_common.connection_handler
def get_reviews_count_for_user(cursor, selected_member_id):
    cursor.execute(f"""
    SELECT COUNT(review_id) FROM review
    WHERE member_id={selected_member_id};
    """)
    reviews_count = cursor.fetchone()
    return reviews_count


@database_common.connection_handler
def get_role_for_user(cursor, session_username):
    cursor.execute(f"""
    SELECT role from member
    WHERE username='{session_username}'
    """)
    user_role = cursor.fetchone()
    return user_role