import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
app.secret_key = "secret_key_here"  # Simple secret key (not recommended for production)

# Initialize the database
def init_db():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        # Create clothes stock table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clothes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                size TEXT NOT NULL,
                quantity INTEGER NOT NULL
            );
        """)
    conn.close()

init_db()

# Register endpoint
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username and password required"}), 400

    try:
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Username already exists"}), 409

# Login endpoint
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()

    if result and result[0] == password:
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid username or password"}), 401

# Create a new clothing item
@app.route("/stock", methods=["POST"])
def add_clothing_item():
    data = request.get_json()
    name = data.get("name")
    size = data.get("size")
    quantity = data.get("quantity")

    if not name or not size or quantity is None:
        return jsonify({"message": "Name, size, and quantity are required"}), 400

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clothes (name, size, quantity) VALUES (?, ?, ?)", (name, size, quantity))
        conn.commit()

    return jsonify({"message": "Clothing item added"}), 201

# Read all clothing items
@app.route("/stock", methods=["GET"])
def get_clothing_items():
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clothes")
        rows = cursor.fetchall()

    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "name": row[1],
            "size": row[2],
            "quantity": row[3]
        })
    return jsonify(items), 200

# Read a single clothing item by ID
@app.route("/stock/<int:item_id>", methods=["GET"])
def get_clothing_item(item_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clothes WHERE id = ?", (item_id,))
        row = cursor.fetchone()

    if row:
        item = {
            "id": row[0],
            "name": row[1],
            "size": row[2],
            "quantity": row[3]
        }
        return jsonify(item), 200
    return jsonify({"message": "Item not found"}), 404

# Update a clothing item
@app.route("/stock/<int:item_id>", methods=["PUT"])
def update_clothing_item(item_id):
    data = request.get_json()
    name = data.get("name")
    size = data.get("size")
    quantity = data.get("quantity")

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clothes WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"message": "Item not found"}), 404

        cursor.execute("""
            UPDATE clothes 
            SET name = ?, size = ?, quantity = ?
            WHERE id = ?
        """, (name, size, quantity, item_id))
        conn.commit()

    return jsonify({"message": "Clothing item updated"}), 200

# Delete a clothing item
@app.route("/stock/<int:item_id>", methods=["DELETE"])
def delete_clothing_item(item_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clothes WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"message": "Item not found"}), 404

        cursor.execute("DELETE FROM clothes WHERE id = ?", (item_id,))
        conn.commit()

    return jsonify({"message": "Clothing item deleted"}), 200

if __name__ == "__main__":
    app.run(debug=True)
