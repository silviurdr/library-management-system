
from flask import Flask, session, request, render_template, flash, redirect, url_for
from markupsafe import escape
import os
from werkzeug.utils import secure_filename
import connection as con
import util as utl


UPLOAD_FOLDER = 'static/'

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = b'-5#y2Y"F4Q8*\n\xec]/'


@app.route('/', methods=['POST', 'GET'])
def index():
    member_page = False
    if 'username' in session:
        login_username = session['username']
        member_page = True
        member_to_login = con.check_registered_user(session['username'])
        print(member_to_login)
        member_full_name = con.get_user_full_name(session['username'])
        return render_template('index.html',
                               member_page=member_page,
                               member_full_name=member_full_name,
                               member_to_login=member_to_login,
                               login_username=login_username)
    else:
        return render_template('index.html',
                               member_page=member_page)


@app.route('/books')
def books():
    BOOKS_HEADINGS = ['ID', 'Title', 'Author',
                      'Published Date', 'ISBN', 'Copies', 'Votes Up', 'Votes Down', 'Status']

    all_books = con.get_all_books()
    member_page = False

    if 'username' in session:
        login_username = session['username']
        utl.get_list_of_titles_rented_per_member(session)
        member_to_login = con.check_registered_user(session['username'])
        member_full_name = con.get_user_full_name(session['username'])
        member_page = True

        titles = utl.get_list_of_titles_rented_per_member(session)

        return render_template('books.html',
                               all_books=all_books,
                               books_headings=BOOKS_HEADINGS,
                               member_to_login=member_to_login,
                               member_page=member_page,
                               member_full_name=member_full_name,
                               titles=titles,
                               login_username=login_username)

    return render_template('books.html',
                           all_books=all_books,
                           books_headings=BOOKS_HEADINGS,
                           member_page=member_page)


@app.route('/books/<book_id>/info')
def get_book_info(book_id: int):

    voting_enabled = True
    reviewers_ids = []
    selected_book_id = con.get_book_by_id(book_id)['book_id']
    reviewers_for_book = con.get_reviewers_for_book(selected_book_id)
    for reviewer in reviewers_for_book:
        reviewers_ids.append(reviewer['member_id'])
    member_page = False
    reviews = con.get_book_reviews(book_id)
    selected_book = con.get_all_info_for_selected_book(book_id)
    positive_reviews = utl.calculate_vote_percentage(selected_book['votes_up'], selected_book['votes_down'])
    if 'username' in session:
        login_username = session['username']
        member_id = con.get_member_id_by_username(login_username)['member_id']
        reviewer_member_id = con.get_member_id_by_username_from_review(member_id)['member_id']
        member_to_login = con.check_registered_user(session['username'])
        member_page = True
        member_full_name = con.get_user_full_name(session['username'])

        return render_template('book-info.html',
                               selected_book=selected_book,
                               member_page=member_page,
                               member_full_name=member_full_name,
                               member_to_login=member_to_login,
                               reviewers_ids=reviewers_ids,
                               positive_reviews=positive_reviews,
                               reviews=reviews,
                               login_username=login_username,
                               reviewer_member_id=reviewer_member_id)
    else:
        return render_template('book-info.html',
                               reviews=reviews,
                               selected_book=selected_book,
                               positive_reviews=positive_reviews,
                               member_page=member_page)


@app.route('/registration', methods=['POST', 'GET'])
def register_new_member():

    new_member = {}
    if request.method == "POST":
        new_member['full_name'] = request.form['full-name']
        new_member['email'] = request.form['email']
        new_member['username'] = request.form['username']
        new_member['city'] = request.form['city']
        new_member['password'] = utl.hash_password(request.form['password'])
        con.add_new_member_to_database(new_member)
        return redirect('/')
    return render_template('registration.html', new_member=new_member)


@app.route('/login.html', methods=['POST', 'GET'])
def login():

    BOOKS_HEADINGS = ['ID', 'Title', 'Author',
                      'Published Date', 'ISBN', 'Copies', 'Status']
    all_books = con.get_all_books()
    member_page = False
    is_member = False

    if request.method == 'POST':
        member_to_login = con.check_registered_user(request.form['username'])

        if len(member_to_login) > 0:
            is_member = utl.verify_password(
                request.form['password'], member_to_login[0]['password'])
            if is_member:
                member_page = True
                session['username'] = request.form['username']
                member_full_name = con.get_user_full_name(session['username'])
                return render_template('books.html',
                                       member_to_login=member_to_login,
                                       books_headings=BOOKS_HEADINGS,
                                       all_books=all_books,
                                       member_page=member_page,
                                       member_full_name=member_full_name)
            else:
                return render_template('login.html', is_member=is_member)
        else:
            return render_template('login.html', is_member=is_member)

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/rent-book/<book_id>')
def rent_book(book_id: int):

    copies = con.get_copies(book_id)['copies']
    if copies > 0:
        username = session['username']
        member_id = con.get_member_id_by_username(username)
        con.rent_book_database(book_id, member_id)
        return redirect('/books')
    else:
        return redirect('/books')

@app.route('/my-books')
def show_my_books():

    utl.get_list_of_titles_rented_per_member(session)

    BOOKS_HEADINGS = ['Rented ID', 'Book ID', 'Title', 'Author',
                      'Published Date', 'ISBN', 'To Return In', 'Return Book']

    if 'username' in session:
        login_username = session['username']
        member_to_login = con.check_registered_user(session['username'])
        member_page = True
        member_full_name = con.get_user_full_name(session['username'])

        username = session['username']
        books_for_member = con.get_books_for_member(username)
        return render_template('my-books.html',
                        books_for_member=books_for_member,
                        books_headings=BOOKS_HEADINGS,
                        member_to_login=member_to_login,
                        member_page=member_page,
                        member_full_name=member_full_name,
                        login_username = session['username'])

@app.route('/return-book/<book_id>')
def return_book(book_id):

    session_username = session['username']
    rented_book_id = con.get_rented_id(book_id, session_username)
    rented_book = con.get_rented_book(book_id, session_username)
    day_diff = con.get_day_diff(rented_book_id)['date_diff']
    fine_amount = utl.calculate_fine(day_diff)
    con.return_book_database(book_id, session_username, rented_book_id)
    con.delete_returned_book_database(rented_book_id)

    return redirect('/my-books')

@app.route('/books/<book_id>/review', methods=['get', 'post'])
def write_review(book_id):
    reviews = con.get_book_reviews(book_id)
    selected_book_id = con.get_book_by_id(book_id)['book_id']
    session_username = session['username']
    reviewer_member_id = con.get_member_id_by_username(session_username)['member_id']
    reviewed_book_id = book_id
    if request.method == 'POST':
        filename = "no image"
        file = request.files['file']
        if file and utl.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        review = request.form
        con.add_review_to_database(reviewed_book_id, reviewer_member_id, review, filename)
        return redirect(url_for('get_book_info', book_id=book_id))

    return render_template('review.html', selected_book_id=selected_book_id,
                                          reviews=reviews)


@app.route('/books/<book_id>/vote-up')
def vote_book_up(book_id):
    
    username = session['username']
    all_votes = con.get_voted_books_for_member(username)['voted_books']
    if all_votes is None:
        next_all_votes_index = 0
        con.register_vote_for_member(username, book_id, next_all_votes_index)
        con.vote_book_up(book_id)
    elif int(book_id) not in all_votes:
        next_all_votes_index = len(all_votes)
        con.register_vote_for_member(username, book_id, next_all_votes_index)
        con.vote_book_up(book_id)
    return redirect(f'/books/{book_id}/info')


@app.route('/books/<book_id>/vote-down')
def vote_book_down(book_id):
    
    username = session['username']
    all_votes = con.get_voted_books_for_member(username)['voted_books']
    if all_votes is None:
        next_all_votes_index = 0
        con.register_vote_for_member(username, book_id, next_all_votes_index)
        con.vote_book_down(book_id)
    elif int(book_id) not in all_votes:
        next_all_votes_index = len(all_votes)
        con.register_vote_for_member(username, book_id, next_all_votes_index)
        con.vote_book_down(book_id)

    return redirect(f'/books/{book_id}/info')


@app.route('/review/<review_id>/vote-up')
def vote_review_up(review_id):

    book_id_for_review = con.get_book_id_by_review_id(review_id)['book_id']

    username = session['username']
    all_reviews_voted = con.get_voted_reviews_for_member(username)['voted_reviews']
    if all_reviews_voted is None:
        next_all_votes_index = 0
        con.register_vote_review_for_member(username, review_id, next_all_votes_index)
        con.vote_review_up(review_id)
    elif int(review_id) not in all_reviews_voted:
        next_all_votes_index = len(all_reviews_voted)
        con.register_vote_review_for_member(username, review_id, next_all_votes_index)
        con.vote_review_up(review_id)
    return redirect(f'/books/{book_id_for_review}/info')


@app.route('/review/<review_id>/vote-down')
def vote_review_down(review_id):

    book_id_for_review = con.get_book_id_by_review_id(review_id)['book_id']

    username = session['username']
    all_reviews_voted = con.get_voted_reviews_for_member(username)['voted_reviews']
    if all_reviews_voted is None:
        next_all_votes_index = 0
        con.register_vote_review_for_member(username, review_id, next_all_votes_index)
        con.vote_review_down(review_id)
    elif int(review_id) not in all_reviews_voted:
        next_all_votes_index = len(all_reviews_voted)
        con.register_vote_review_for_member(username, review_id, next_all_votes_index)
        con.vote_review_down(review_id)
    return redirect(f'/books/{book_id_for_review}/info')


@app.route('/review/<review_id>/edit', methods=['POST', 'GET'])
def edit_review(review_id):

    review_to_edit = con.get_info_for_review(review_id)
    book_id = con.get_book_id_by_review_id(review_id)['book_id']
    
    if request.method == "POST":
        review_to_edit['subject'] = request.form['subject']
        review_to_edit['message'] = request.form['message']
        filename = review_to_edit['image']
        if 'rating' in request.form.keys():
            review_to_edit['review_rating'] = request.form['rating']
        if 'file' in request.files.keys():
            file = request.files['file']
            if file and utl.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                con.edit_review_database(review_id, review_to_edit, filename)
        con.edit_review_database(review_id, review_to_edit, filename)
        return redirect(f'/books/{book_id}/info')

    return render_template('edit_review.html', review_to_edit=review_to_edit)


@app.route('/member/<member_id>')
def user_page(member_id):
    user_info = con.get_user_info(member_id)

    user_reviews = con.get_user_reviews(member_id)
    reviews_count = con.get_reviews_count_for_user(member_id)['count']
    
    return render_template('member-page.html',
                    user_info=user_info,
                    user_reviews=user_reviews,
                    reviews_count=reviews_count)




if __name__ == '__main__':

    app.run(debug=True,
            port=5000)
