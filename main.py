import streamlit as st
import pandas as pd
import sqlite3
import base64
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="SAD Library System", page_icon="📚", layout="wide")

# Database setup
def init_db():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Create books table
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (book_id TEXT PRIMARY KEY,
                  title TEXT NOT NULL,
                  author TEXT NOT NULL,
                  isbn TEXT,
                  category TEXT,
                  quantity INTEGER,
                  available INTEGER,
                  status TEXT)''')
    
    # Create borrowed_books table
    c.execute('''CREATE TABLE IF NOT EXISTS borrowed_books
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  book_id TEXT,
                  title TEXT,
                  borrower_name TEXT,
                  borrower_id TEXT,
                  borrow_date DATE,
                  due_date DATE,
                  status TEXT)''')
    
    # Check if tables are empty and add sample data
    c.execute("SELECT COUNT(*) FROM books")
    if c.fetchone()[0] == 0:
        sample_books = [
            ('B001', 'Python Programming', 'John Smith', '978-1234567890', 'Programming', 5, 5, 'Available'),
            ('B002', 'Data Science Handbook', 'Jane Doe', '978-0987654321', 'Data Science', 3, 3, 'Available'),
            ('B003', 'Web Development Guide', 'Mike Johnson', '978-1122334455', 'Web Development', 7, 7, 'Available')
        ]
        c.executemany("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_books)
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Database functions
def get_all_books():
    conn = sqlite3.connect('library.db')
    df = pd.read_sql_query("SELECT * FROM books", conn)
    conn.close()
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
    df['available'] = pd.to_numeric(df['available'], errors='coerce').fillna(0).astype(int)
    return df

def get_borrowed_books():
    conn = sqlite3.connect('library.db')
    df = pd.read_sql_query("SELECT * FROM borrowed_books", conn)
    conn.close()
    return df

def add_book(book_id, title, author, isbn, category, quantity, available, status):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (book_id, title, author, isbn, category, quantity, available, status))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def update_book_availability(book_id, available, status):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("UPDATE books SET available = ?, status = ? WHERE book_id = ?",
              (available, status, book_id))
    conn.commit()
    conn.close()

def add_borrowed_book(book_id, title, borrower_name, borrower_id, borrow_date, due_date, status):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("INSERT INTO borrowed_books (book_id, title, borrower_name, borrower_id, borrow_date, due_date, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (book_id, title, borrower_name, borrower_id, borrow_date, due_date, status))
    conn.commit()
    conn.close()

def update_borrowed_book_status(book_id, borrower_id, status):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("UPDATE borrowed_books SET status = ? WHERE book_id = ? AND borrower_id = ? AND status = 'Borrowed'",
              (status, book_id, borrower_id))
    conn.commit()
    conn.close()

# Function to convert image to base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Try to load background image
img_base64 = get_base64_image("static/LIBRARY ROOM.jpg")

# Custom CSS for background
if img_base64:
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: -1;
        }}
        
        h1, h2, h3, p, label, .stMarkdown {{
            color: white !important;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
        }}
        
        .stButton>button {{
            background-color: rgba(139, 92, 46, 0.9);
            color: white;
            font-weight: bold;
        }}
        
        .stTextInput>div>div>input, .stSelectbox>div>div>select, .stNumberInput>div>div>input {{
            background-color: rgba(255, 255, 255, 0.9);
        }}
        </style>
    """, unsafe_allow_html=True)

# Title
st.title("📚 SAD Library Inventory Management System")
st.caption("💾 Now with SQLite Database - Your data is saved!")

# Sidebar navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["Dashboard", "Add Book", "Search Books", "Borrow Book", "Return Book", "Borrowed Books", "View All Books"])

# Dashboard
if menu == "Dashboard":
    st.header("📊 Dashboard")
    
    books_df = get_all_books()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div style='background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color: #f0ad4e; margin: 0;'>Total Books</h3>
                <h1 style='color: white; margin: 10px 0;'>{}</h1>
            </div>
        """.format(len(books_df)), unsafe_allow_html=True)
    
    with col2:
        total_quantity = books_df['quantity'].sum()
        st.markdown("""
            <div style='background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color: #5bc0de; margin: 0;'>Total Copies</h3>
                <h1 style='color: white; margin: 10px 0;'>{}</h1>
            </div>
        """.format(total_quantity), unsafe_allow_html=True)
    
    with col3:
        available_books = books_df['available'].sum()
        st.markdown("""
            <div style='background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color: #5cb85c; margin: 0;'>Available Copies</h3>
                <h1 style='color: white; margin: 10px 0;'>{}</h1>
            </div>
        """.format(available_books), unsafe_allow_html=True)
    
    with col4:
        borrowed = total_quantity - available_books
        st.markdown("""
            <div style='background: rgba(0,0,0,0.8); padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color: #d9534f; margin: 0;'>Books Borrowed</h3>
                <h1 style='color: white; margin: 10px 0;'>{}</h1>
            </div>
        """.format(borrowed), unsafe_allow_html=True)
    
    st.subheader("📖 Recent Books")
    st.dataframe(books_df.head(5), use_container_width=True)
    
    st.subheader("📂 Books by Category")
    if not books_df.empty:
        category_counts = books_df['category'].value_counts()
        st.bar_chart(category_counts)

# Add Book
elif menu == "Add Book":
    st.header("➕ Add New Book")
    
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            book_id = st.text_input("Book ID *", placeholder="e.g., B004")
            title = st.text_input("Book Title *", placeholder="e.g., Machine Learning Basics")
            author = st.text_input("Author *", placeholder="e.g., Sarah Williams")
            isbn = st.text_input("ISBN", placeholder="e.g., 978-1234567890")
        
        with col2:
            category = st.selectbox("Category *", ["Programming", "Data Science", "Web Development", "Database", "Networking", "Other"])
            quantity = st.number_input("Quantity *", min_value=1, value=1)
            available = st.number_input("Available Copies *", min_value=1, value=1)
            status = st.selectbox("Status", ["Available", "Out of Stock"])
        
        submit = st.form_submit_button("Add Book")
        
        if submit:
            if book_id and title and author and category:
                if add_book(book_id, title, author, isbn, category, quantity, available, status):
                    st.success(f"✅ Book '{title}' added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Book ID already exists!")
            else:
                st.error("❌ Please fill all required fields (*)")

# Search Books
elif menu == "Search Books":
    st.header("🔍 Search Books")
    
    books_df = get_all_books()
    
    search_option = st.radio("Search by:", ["Title", "Author", "Category", "Book ID"])
    search_query = st.text_input(f"Enter {search_option}")
    
    if search_query:
        if search_option == "Title":
            results = books_df[books_df['title'].str.contains(search_query, case=False, na=False)]
        elif search_option == "Author":
            results = books_df[books_df['author'].str.contains(search_query, case=False, na=False)]
        elif search_option == "Category":
            results = books_df[books_df['category'].str.contains(search_query, case=False, na=False)]
        else:
            results = books_df[books_df['book_id'].str.contains(search_query, case=False, na=False)]
        
        if not results.empty:
            st.success(f"Found {len(results)} result(s)")
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("No books found matching your search.")

# Borrow Book
elif menu == "Borrow Book":
    st.header("📤 Borrow Book")
    
    books_df = get_all_books()
    available_books = books_df[books_df['available'] > 0]
    
    if available_books.empty:
        st.warning("No books available for borrowing at the moment.")
    else:
        with st.form("borrow_form"):
            book_id = st.selectbox("Select Book ID", available_books['book_id'].tolist())
            
            if book_id:
                selected_book = books_df[books_df['book_id'] == book_id].iloc[0]
                st.info(f"**Title:** {selected_book['title']}\n\n**Author:** {selected_book['author']}\n\n**Available:** {selected_book['available']}")
            
            borrower_name = st.text_input("Borrower Name *")
            borrower_id = st.text_input("Borrower ID *", placeholder="e.g., STU001")
            
            borrow_date = st.date_input("Borrow Date", value=datetime.now())
            due_date = st.date_input("Due Date", value=datetime.now() + timedelta(days=14))
            
            submit = st.form_submit_button("Borrow Book")
            
            if submit:
                if borrower_name and borrower_id:
                    # Update book availability
                    new_available = selected_book['available'] - 1
                    new_status = 'Out of Stock' if new_available == 0 else 'Available'
                    update_book_availability(book_id, new_available, new_status)
                    
                    # Add to borrowed books
                    add_borrowed_book(book_id, selected_book['title'], borrower_name, borrower_id, 
                                    borrow_date, due_date, 'Borrowed')
                    
                    st.success(f"✅ Book borrowed successfully by {borrower_name}!")
                    st.rerun()
                else:
                    st.error("❌ Please fill all required fields!")

# Return Book
elif menu == "Return Book":
    st.header("📥 Return Book")
    
    borrowed_df = get_borrowed_books()
    borrowed_books = borrowed_df[borrowed_df['status'] == 'Borrowed']
    
    if borrowed_books.empty:
        st.warning("No books currently borrowed.")
    else:
        with st.form("return_form"):
            borrower_id = st.selectbox("Select Borrower ID", borrowed_books['borrower_id'].unique().tolist())
            
            if borrower_id:
                borrower_books = borrowed_books[borrowed_books['borrower_id'] == borrower_id]
                book_id = st.selectbox("Select Book to Return", borrower_books['book_id'].tolist())
                
                submit = st.form_submit_button("Return Book")
                
                if submit:
                    books_df = get_all_books()
                    selected_book = books_df[books_df['book_id'] == book_id].iloc[0]
                    
                    # Update book availability
                    new_available = selected_book['available'] + 1
                    update_book_availability(book_id, new_available, 'Available')
                    
                    # Update borrowed books status
                    update_borrowed_book_status(book_id, borrower_id, 'Returned')
                    
                    st.success(f"✅ Book returned successfully!")
                    st.rerun()

# Borrowed Books
elif menu == "Borrowed Books":
    st.header("📋 Currently Borrowed Books")
    
    borrowed_df = get_borrowed_books()
    borrowed = borrowed_df[borrowed_df['status'] == 'Borrowed']
    
    if borrowed.empty:
        st.info("No books are currently borrowed.")
    else:
        st.dataframe(borrowed, use_container_width=True)
        
        # Check for overdue books
        today = pd.to_datetime(datetime.now().date())
        borrowed['due_date'] = pd.to_datetime(borrowed['due_date'])
        overdue = borrowed[borrowed['due_date'] < today]
        
        if not overdue.empty:
            st.warning(f"⚠️ {len(overdue)} overdue book(s)!")
            st.dataframe(overdue, use_container_width=True)

# View All Books
elif menu == "View All Books":
    st.header("📚 All Books in Library")
    
    books_df = get_all_books()
    
    if books_df.empty:
        st.info("No books in the library yet.")
    else:
        st.dataframe(books_df, use_container_width=True)
        
        # Download as CSV
        csv = books_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="library_inventory.csv",
            mime="text/csv"
        )

# Footer
st.sidebar.markdown("---")

st.sidebar.info("📚 SAD Library System v2.0 - SQLite Edition")
