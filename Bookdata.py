from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

# Database connection parameters
dbname = "postgres"
user = "postgres"
password = "Itv4312"
host = "localhost"  # or your host if it's different
port = "5432"  # or your port if it's different



# Function to execute SQL query and return results
def execute_query(query, data=None):
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host,
        port=port
    )
    cur = conn.cursor()
    if data:
        cur.execute(query, data)
    else:
        cur.execute(query)
    if cur.description:
        results = cur.fetchall()
    else:
        results = None
    conn.commit()
    cur.close()
    conn.close()
    return results

@app.route('/')
def index():
    return render_template('index.html')

# Function to authenticate user
def authenticate_user(email, password):
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    data = (email, password)
    result = execute_query(query, data)
    return len(result) > 0

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    if authenticate_user(email, password):
        return redirect(url_for('search'))
    else:
        return "Invalid email or password"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        # Insert the user data into the database
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        data = (name, email, password)
        execute_query(query, data)
        return "Signup successful! Please login <a href='/login'>here</a>"
    return render_template('signup.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        # Build SQL query to search for books matching the query
        search_query = (
            "SELECT * FROM books WHERE "
            "isbn ILIKE '%{query}%' OR "
            "title ILIKE '%{query}%' OR "
            "author ILIKE '%{query}%'"
        ).format(query=query)
        results = execute_query(search_query)
        if results:
            return render_template('search_results.html', results=results)  # Pass results to the template
        else:
            return "No results found."
    return render_template('search.html')



@app.route('/book/<isbn>', methods=['GET'])
def book_details(isbn):
    # Fetch book details from the database using the ISBN
    query = "SELECT * FROM books WHERE isbn = '{}';".format(isbn)
    book_details = execute_query(query)
    if book_details:
        # Render template with book details
        return render_template('book_details.html', book=book_details[0])
    else:
        return "Book not found"

@app.route('/save_review/<isbn>', methods=['POST'])
def save_review(isbn):
    review = request.form['review']
    # Update the database with the new review for the book with the given ISBN
    update_query = "UPDATE books SET review = %s WHERE isbn = %s;"
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cur = conn.cursor()
        cur.execute(update_query, (review, isbn))
        conn.commit()  # Commit the transaction
        cur.close()
        conn.close()
    except psycopg2.Error as e:
        error_message = "An error occurred while saving the review: {}".format(str(e))
        return error_message
    return redirect(url_for('book_details', isbn=isbn))  # Redirect to the book details page



if __name__ == '__main__':
    app.run(debug=True)