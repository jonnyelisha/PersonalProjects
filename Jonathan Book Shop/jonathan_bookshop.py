import tkinter as tk
import psycopg2
from datetime import datetime
import shutil

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="Library",
    user="postgres",
    password="Appleipod123"
)
c = conn.cursor()

# Create the users table
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT, password TEXT)''')

# Create the books table
c.execute('''CREATE TABLE IF NOT EXISTS books
             (book_title TEXT, author TEXT, borrower_name TEXT, borrow_date TEXT, contact_info TEXT)''')

# Create the activity logs table
c.execute('''CREATE TABLE IF NOT EXISTS activity_logs
             (username TEXT, action TEXT, book_title TEXT, date TIMESTAMP)''')

# Create the notifications table
c.execute('''CREATE TABLE IF NOT EXISTS notifications
             (username TEXT, message TEXT, date TIMESTAMP)''')

# Insert the books into the database
books = [
    ("Harry Potter and the Philosopher's Stone", "J.K. Rowling"),
    ("1984", "George Orwell"),
    ("Beloved", "Toni Morrison"),
    ("The Old Man and the Sea", "Ernest Hemingway"),
    ("Pride and Prejudice", "Jane Austen"),
    ("The Wind-Up Bird Chronicle", "Haruki Murakami"),
    ("I Know Why the Caged Bird Sings", "Maya Angelou"),
    ("One Hundred Years of Solitude", "Gabriel García Márquez"),
    ("The Handmaid's Tale", "Margaret Atwood"),
    ("The Kite Runner", "Khaled Hosseini")
]

for book, author in books:
    c.execute("INSERT INTO books (book_title, author) VALUES (%s, %s)", (book, author))
conn.commit()

current_user = None

# Function to log activity
def log_activity(user, action, book_title):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO activity_logs (username, action, book_title, date) VALUES (%s, %s, %s, %s)", (user, action, book_title, date))
    conn.commit()

# Function to backup the database
def backup_database():
    shutil.copyfile('path/to/your/database', 'path/to/backup/location/backup.db')
    print("Database backup created successfully.")

# Function to restore the database
def restore_database():
    shutil.copyfile('path/to/backup/location/backup.db', 'path/to/your/database')
    print("Database restored successfully.")

# Function to login or create a new account
def login():
    global current_user
    username = username_entry.get()
    password = password_entry.get()
    c.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = c.fetchone()
    if user:
        current_user = username
        print(f"J, {username}!")
        login_window.withdraw()
        if username == "admin":  # Assuming 'admin' is the admin username
            admin_options_window.deiconify()
        else:
            user_options_window.deiconify()
    else:
        print("Invalid username or password.")

# Function to create a new account
def create_new_account(username, password):
    c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
    conn.commit()

# Function to borrow a book
def borrow_book():
    book_title = book_title_entry.get()
    c.execute("SELECT borrower_name FROM books WHERE book_title = %s", (book_title,))
    borrower = c.fetchone()
    if borrower and borrower[0]:
        print(f"Sorry, the book '{book_title}' is already borrowed by {borrower[0]}.")
    else:
        contact_info = contact_entry.get()
        borrow_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("SELECT author FROM books WHERE book_title = %s", (book_title,))
        author = c.fetchone()[0]
        c.execute("UPDATE books SET borrower_name = %s, borrow_date = %s, contact_info = %s WHERE book_title = %s", (current_user, borrow_date, contact_info, book_title))
        conn.commit()
        log_activity(current_user, 'borrow', book_title)
        print(f"You have borrowed the book '{book_title}' by {author}. The borrow date is {borrow_date}.")

# Function to return a book
def return_book():
    book_title = book_title_entry.get()
    c.execute("SELECT borrower_name FROM books WHERE book_title = %s", (book_title,))
    borrower = c.fetchone()
    if borrower and borrower[0] == current_user:
        c.execute("UPDATE books SET borrower_name = NULL, borrow_date = NULL, contact_info = NULL WHERE book_title = %s", (book_title,))
        conn.commit()
        log_activity(current_user, 'return', book_title)
        print(f"You have returned the book '{book_title}'.")
    else:
        print(f"The book '{book_title}' is not borrowed by you.")

# Function to show book status
def show_book_status():
    c.execute("SELECT book_title, author FROM books WHERE borrower_name IS NULL")
    available_books = c.fetchall()
    print("Available books to borrow:")
    for book, author in available_books:
        print(f"- {book} by {author}")

# Function to view borrowed books
def view_borrowed_books():
    c.execute("SELECT book_title, author FROM books WHERE borrower_name = %s", (current_user,))
    borrowed_books = c.fetchall()
    borrowed_books_window = tk.Toplevel(user_options_window)
    borrowed_books_window.title("Borrowed Books")
    borrowed_books_label = tk.Label(borrowed_books_window, text="Books you have borrowed:")
    borrowed_books_label.pack()
    for book, author in borrowed_books:
        book_label = tk.Label(borrowed_books_window, text=f"{book} by {author}")
        book_label.pack()

# Function to search for books
def search_books():
    search_query = search_entry.get()
    c.execute("SELECT book_title, author FROM books WHERE book_title ILIKE %s OR author ILIKE %s", (f"%{search_query}%", f"%{search_query}%"))
    search_results = c.fetchall()
    search_results_window = tk.Toplevel(user_options_window)
    search_results_window.title("Search Results")
    search_results_label = tk.Label(search_results_window, text="Search results:")
    search_results_label.pack()
    for book, author in search_results:
        result_label = tk.Label(search_results_window, text=f"{book} by {author}")
        result_label.pack()

# Function to add a new book
def add_book():
    book_title = add_book_title_entry.get()
    author = add_book_author_entry.get()
    c.execute("INSERT INTO books (book_title, author) VALUES (%s, %s)", (book_title, author))
    conn.commit()
    print(f"The book '{book_title}' by {author} has been added to the library.")

# Function to remove a book
def remove_book():
    book_title = remove_book_title_entry.get()
    c.execute("DELETE FROM books WHERE book_title = %s", (book_title,))
    conn.commit()
    print(f"The book '{book_title}' has been removed from the library.")

# Function to view borrow history
def view_borrow_history():
    borrow_history_window = tk.Toplevel(user_options_window)
    borrow_history_window.title("Borrow History")
    c.execute("SELECT book_title, action, date FROM activity_logs WHERE username = %s", (current_user,))
    history = c.fetchall()
    history_label = tk.Label(borrow_history_window, text="Your borrow history:")
    history_label.pack()
    for book, action, date in history:
        history_item_label = tk.Label(borrow_history_window, text=f"{date}: {action} '{book}'")
        history_item_label.pack()

# Function to execute an SQL query
def execute_sql_query():
    sql_query_window = tk.Toplevel(admin_options_window)
    sql_query_window.title("Execute SQL Query")
    query_label = tk.Label(sql_query_window, text="SQL Query:")
    query_label.pack()
    query_entry = tk.Entry(sql_query_window, width=100)
    query_entry.pack()
    def execute_query():
        query = query_entry.get()
        try:
            c.execute(query)
            results = c.fetchall()
            results_window = tk.Toplevel(sql_query_window)
            results_window.title("Query Results")
            for result in results:
                result_label = tk.Label(results_window, text=str(result))
                result_label.pack()
        except Exception as e:
            error_label = tk.Label(sql_query_window, text=f"Error: {e}")
            error_label.pack()
    execute_button = tk.Button(sql_query_window, text="Execute", command=execute_query)
    execute_button.pack()

# Function to show statistics
def show_statistics():
    statistics_window = tk.Toplevel(admin_options_window)
    statistics_window.title("Statistics")
    def fetch_statistics():
        c.execute("SELECT COUNT(*) FROM books")
        total_books = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM books WHERE borrower_name IS NOT NULL")
        borrowed_books = c.fetchone()[0]
        stats_label = tk.Label(statistics_window, text=f"Total Books: {total_books}\nTotal Users: {total_users}\nBorrowed Books: {borrowed_books}")
        stats_label.pack()
    show_stats_button = tk.Button(statistics_window, text="Show Statistics", command=fetch_statistics)
    show_stats_button.pack()

# Function to search with filters
def search_with_filters():
    filters_window = tk.Toplevel(user_options_window)
    filters_window.title("Advanced Search")
    title_label = tk.Label(filters_window, text="Title:")
    title_label.pack()
    title_entry = tk.Entry(filters_window)
    title_entry.pack()
    author_label = tk.Label(filters_window, text="Author:")
    author_label.pack()
    author_entry = tk.Entry(filters_window)
    author_entry.pack()
    year_label = tk.Label(filters_window, text="Year of Publication:")
    year_label.pack()
    year_entry = tk.Entry(filters_window)
    year_entry.pack()
    def perform_search():
        title = title_entry.get()
        author = author_entry.get()
        year = year_entry.get()
        query = "SELECT book_title, author FROM books WHERE 1=1"
        if title:
            query += f" AND book_title ILIKE '%{title}%'"
        if author:
            query += f" AND author ILIKE '%{author}%'"
        if year:
            query += f" AND EXTRACT(YEAR FROM borrow_date) = {year}"
        c.execute(query)
        search_results = c.fetchall()
        results_window = tk.Toplevel(filters_window)
        results_window.title("Search Results")
        for book, author in search_results:
            result_label = tk.Label(results_window, text=f"{book} by {author}")
            result_label.pack()
    search_button = tk.Button(filters_window, text="Search", command=perform_search)
    search_button.pack()

# Create the login window
login_window = tk.Tk()
login_window.title("Jonathan's Book Shop - Login")

username_label = tk.Label(login_window, text="Username:")
username_label.pack()
username_entry = tk.Entry(login_window)
username_entry.pack()

password_label = tk.Label(login_window, text="Password:")
password_label.pack()
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()

login_button = tk.Button(login_window, text="Login", command=login)
login_button.pack()

# Create the admin options window
admin_options_window = tk.Tk()
admin_options_window.title("Admin Options")
admin_options_window.withdraw()

sql_query_button = tk.Button(admin_options_window, text="Execute SQL Query", command=execute_sql_query)
sql_query_button.pack()

statistics_button = tk.Button(admin_options_window, text="View Statistics", command=show_statistics)
statistics_button.pack()

backup_button = tk.Button(admin_options_window, text="Backup Database", command=backup_database)
backup_button.pack()

restore_button = tk.Button(admin_options_window, text="Restore Database", command=restore_database)
restore_button.pack()

# Create the user options window
user_options_window = tk.Tk()
user_options_window.title("User Options")
user_options_window.withdraw()

book_title_label = tk.Label(user_options_window, text="Book Title:")
book_title_label.pack()
book_title_entry = tk.Entry(user_options_window)
book_title_entry.pack()

contact_label = tk.Label(user_options_window, text="Contact Information:")
contact_label.pack()
contact_entry = tk.Entry(user_options_window)
contact_entry.pack()

borrow_button = tk.Button(user_options_window, text="Borrow", command=borrow_book)
borrow_button.pack()

return_button = tk.Button(user_options_window, text="Return", command=return_book)
return_button.pack()

status_button = tk.Button(user_options_window, text="Check Status", command=show_book_status)
status_button.pack()

view_borrowed_button = tk.Button(user_options_window, text="View Borrowed Books", command=view_borrowed_books)
view_borrowed_button.pack()

search_button = tk.Button(user_options_window, text="Search Books", command=search_books)
search_button.pack()

add_book_label = tk.Label(user_options_window, text="Add Book - Title:")
add_book_label.pack()
add_book_title_entry = tk.Entry(user_options_window)
add_book_title_entry.pack()
add_book_author_label = tk.Label(user_options_window, text="Add Book - Author:")
add_book_author_label.pack()
add_book_author_entry = tk.Entry(user_options_window)
add_book_author_entry.pack()
add_book_button = tk.Button(user_options_window, text="Add Book", command=add_book)
add_book_button.pack()

remove_book_label = tk.Label(user_options_window, text="Remove Book - Title:")
remove_book_label.pack()
remove_book_title_entry = tk.Entry(user_options_window)
remove_book_title_entry.pack()
remove_book_button = tk.Button(user_options_window, text="Remove Book", command=remove_book)
remove_book_button.pack()

borrow_history_button = tk.Button(user_options_window, text="View Borrow History", command=view_borrow_history)
borrow_history_button.pack()

advanced_search_button = tk.Button(user_options_window, text="Advanced Search", command=search_with_filters)
advanced_search_button.pack()

exit_button = tk.Button(user_options_window, text="Exit", command=user_options_window.quit)
exit_button.pack()

login_window.mainloop()
conn.close()
