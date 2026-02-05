import os
import certifi
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId

# Load environment variables
load_dotenv()
connection_string = os.getenv("COSMOS_DB_CONNECTION_STRING")

# Connect to Cosmos DB with MongoDB API
client = MongoClient(connection_string, tls=True, tlsCAFile=certifi.where())
database: Database = client.get_database("bookstore")
collection: Collection = database.get_collection("books")

# Flask application
app = Flask(__name__)

# Home Page
@app.route('/')
def index():
    """Home page - displays all books"""
    books = list(collection.find())
    for book in books:
        book["_id"] = str(book["_id"])
    return render_template("index.html", books=books)

# Crud Operations

# CREATE - Add new book
@app.route('/books', methods=['POST'])
def add_book():
    """Add a new book to the database"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['isbn', 'title', 'year', 'price', 'page', 'category']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"'{field}' is required"}), 400
    
    # Check if book with ISBN already exists
    if collection.find_one({'isbn': data['isbn']}):
        return jsonify({'error': 'A book with this ISBN already exists.'}), 400
    
    # Create new book document
    new_book = {
        "isbn": data['isbn'],
        "title": data['title'],
        "year": data.get('year'),
        "price": data.get('price'),
        "page": data.get('page'),
        "category": data.get('category'),
        "coverPhoto": data.get('coverPhoto', ''),
        "publisher": data.get('publisher', {}),
        "author": data.get('author', {})
    }
    
    result = collection.insert_one(new_book)
    new_book['_id'] = str(result.inserted_id)
    
    return jsonify({"message": f"Book '{data['title']}' has been added.", "book": new_book}), 201

# READ - Get all books
@app.route('/books', methods=['GET'])
def get_books():
    """Get all books from database"""
    books = list(collection.find())
    books_list = []
    
    for book in books:
        book['_id'] = str(book['_id'])
        books_list.append({
            'id': book['_id'],
            'isbn': book.get('isbn', ''),
            'title': book.get('title', ''),
            'year': book.get('year', ''),
            'price': book.get('price', ''),
            'page': book.get('page', ''),
            'category': book.get('category', ''),
            'coverPhoto': book.get('coverPhoto', ''),
            'publisher': book.get('publisher', {}),
            'author': book.get('author', {})
        })
    
    # Check if request wants JSON or HTML
    if request.headers.get('Accept') == 'application/json':
        return jsonify(books_list), 200
    
    return render_template('index.html', books=books_list)

# READ - Get single book by ISBN
@app.route('/books/isbn/<book_isbn>', methods=['GET'])
def get_book_by_isbn(book_isbn):
    """Get a single book by ISBN"""
    book = collection.find_one({'isbn': book_isbn})
    
    if book:
        book['_id'] = str(book['_id'])
        return jsonify(book), 200
    else:
        return jsonify({'error': 'Book not found'}), 404

# READ - Get single book by ID
@app.route('/books/<string:book_id>', methods=['GET'])
def get_book_by_id(book_id):
    """Get a single book by MongoDB ID"""
    try:
        book = collection.find_one({'_id': ObjectId(book_id)})
        if book:
            book['_id'] = str(book['_id'])
            return jsonify(book), 200
        else:
            return jsonify({'error': 'Book not found'}), 404
    except:
        return jsonify({'error': 'Invalid book ID'}), 400

# UPDATE - Update book by ID
@app.route('/books/<string:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update a book by ID"""
    data = request.get_json()
    
    # Build update fields
    update_fields = {}
    allowed_fields = ['title', 'year', 'price', 'page', 'category', 'coverPhoto', 'publisher', 'author']
    
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]
    
    if not update_fields:
        return jsonify({'error': 'No valid fields to update.'}), 400
    
    try:
        updated_book = collection.find_one_and_update(
            {'_id': ObjectId(book_id)},
            {'$set': update_fields},
            return_document=True
        )
        
        if updated_book:
            updated_book['_id'] = str(updated_book['_id'])
            return jsonify({"message": "Book updated successfully.", "book": updated_book}), 200
        else:
            return jsonify({'error': 'Book not found'}), 404
    except:
        return jsonify({'error': 'Invalid book ID'}), 400

# UPDATE - Update book by ISBN
@app.route('/books/isbn/<book_isbn>', methods=['PUT'])
def update_book_by_isbn(book_isbn):
    """Update a book by ISBN"""
    data = request.get_json()
    
    update_fields = {}
    allowed_fields = ['title', 'year', 'price', 'page', 'category', 'coverPhoto', 'publisher', 'author']
    
    for field in allowed_fields:
        if field in data:
            update_fields[field] = data[field]
    
    if not update_fields:
        return jsonify({'error': 'No valid fields to update.'}), 400
    
    result = collection.update_one({'isbn': book_isbn}, {'$set': update_fields})
    
    if result.matched_count:
        updated_book = collection.find_one({'isbn': book_isbn})
        updated_book['_id'] = str(updated_book['_id'])
        return jsonify({"message": "Book updated successfully.", "book": updated_book}), 200
    else:
        return jsonify({'error': 'Book not found'}), 404

# DELETE - Delete book by ID
@app.route('/books/<string:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book by ID"""
    try:
        result = collection.delete_one({'_id': ObjectId(book_id)})
        
        if result.deleted_count:
            return jsonify({'message': 'Book deleted successfully.'}), 200
        else:
            return jsonify({'error': 'Book not found'}), 404
    except:
        return jsonify({'error': 'Invalid book ID'}), 400

# DELETE - Delete book by ISBN
@app.route('/books/isbn/<book_isbn>', methods=['DELETE'])
def delete_book_by_isbn(book_isbn):
    """Delete a book by ISBN"""
    result = collection.delete_one({'isbn': book_isbn})
    
    if result.deleted_count:
        return jsonify({'message': 'Book deleted successfully.'}), 200
    else:
        return jsonify({'error': 'Book not found'}), 404

# Filter Operations

@app.route('/books/category/<category>', methods=['GET'])
def get_books_by_category(category):
    """Get books by category"""
    books = list(collection.find({'category': {'$regex': category, '$options': 'i'}}))
    
    for book in books:
        book['_id'] = str(book['_id'])
    
    return jsonify(books), 200

@app.route('/books/author/<author_name>', methods=['GET'])
def get_books_by_author(author_name):
    """Get books by author name"""
    books = list(collection.find({
        '$or': [
            {'author.firstName': {'$regex': author_name, '$options': 'i'}},
            {'author.lastName': {'$regex': author_name, '$options': 'i'}}
        ]
    }))
    
    for book in books:
        book['_id'] = str(book['_id'])
    
    return jsonify(books), 200

# Health Check

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Kubernetes"""
    try:
        # Try to ping the database
        client.admin.command('ping')
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 500

# API Info

@app.route('/api', methods=['GET'])
def api_info():
    """API documentation endpoint"""
    return jsonify({
        'name': 'Bookstore API',
        'version': '1.0',
        'author': 'AIN3003 Project',
        'endpoints': {
            'GET /': 'Home page with book list',
            'GET /books': 'Get all books',
            'GET /books/<id>': 'Get book by ID',
            'GET /books/isbn/<isbn>': 'Get book by ISBN',
            'POST /books': 'Add new book',
            'PUT /books/<id>': 'Update book by ID',
            'PUT /books/isbn/<isbn>': 'Update book by ISBN',
            'DELETE /books/<id>': 'Delete book by ID',
            'DELETE /books/isbn/<isbn>': 'Delete book by ISBN',
            'GET /books/category/<category>': 'Filter by category',
            'GET /books/author/<name>': 'Filter by author',
            'GET /health': 'Health check',
            'GET /api': 'API documentation'
        }
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
