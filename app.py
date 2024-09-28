import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Secret Key for Flash Messages and Session Management
app.secret_key = os.urandom(24)

# File Upload Settings
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'}

# Initialize MySQL
mysql = MySQL(app)

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Hardcoded admin credentials (for simplicity)
admin_credentials = {
    'username': 'admin',
    'password_hash': generate_password_hash('admin123')  # Password is 'admin123'
}

# Default route to redirect to the login page
@app.route('/')
def home():
    return redirect(url_for('admin_login'))

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check admin credentials
        if username == admin_credentials['username'] and check_password_hash(admin_credentials['password_hash'], password):
            session['admin_logged_in'] = True  # Set a session variable
            flash('Successfully logged in as Admin', 'success')
            return redirect(url_for('upload_file'))  # Redirect to the upload page
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('admin_login.html')

# Route to Upload a New Note
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'admin_logged_in' not in session:
        flash('Access denied! Only admins can upload files. Please log in as admin.', 'danger')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']
        subject = request.form['subject']
        chapter_name = request.form.get('chapter_name')
        file = request.files['file']

        # Check if a file is selected and has an allowed extension
        if file and allowed_file(file.filename):
            try:
                # Secure the filename and save the file to the uploads directory
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Insert the note into the notes table
                cursor = mysql.connection.cursor()
                note_query = """
                    INSERT INTO notes (title, filepath, year, subject)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(note_query, (title, f'static/uploads/{filename}', year, subject))
                mysql.connection.commit()

                # Get the note ID of the newly inserted note
                note_id = cursor.lastrowid

                # Insert chapter details into the chapters table
                if chapter_name:
                    chapter_query = """
                        INSERT INTO chapters (chapter_name, subject, note_id)
                        VALUES (%s, %s, %s)
                    """
                    cursor.execute(chapter_query, (chapter_name, subject, note_id))
                    mysql.connection.commit()

                flash('File uploaded successfully!', 'success')
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error occurred: {str(e)}', 'danger')
            finally:
                cursor.close()

            return redirect(url_for('upload_file'))

    return render_template('upload.html')

# Route to Upload Past Year Question Papers (PYQs)
@app.route('/upload_pyq', methods=['GET', 'POST'])
def upload_pyq():
    if 'admin_logged_in' not in session:
        flash('Access denied! Only admins can upload PYQs. Please log in as admin.', 'danger')
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        serial_no = request.form['pyq_serial_no']  # Updated field for serial number
        pyq_year = request.form['pyq_year']  # Year of the PYQ
        subject = request.form['subject']  # Subject of the PYQ
        file = request.files['file']

        # Check if a file is selected and has an allowed extension
        if file and allowed_file(file.filename):
            try:
                # Secure the filename and save the file to the uploads directory
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Insert the PYQ into the `pyqs` table with relevant fields
                cursor = mysql.connection.cursor()
                pyq_query = """
                    INSERT INTO pyqs (serial_no, filepath, year, subject)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(pyq_query, (serial_no, f'static/uploads/{filename}', pyq_year, subject))
                mysql.connection.commit()

                flash('PYQ uploaded successfully!', 'success')
            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error occurred: {str(e)}', 'danger')
            finally:
                cursor.close()

            return redirect(url_for('upload_pyq'))

    return render_template('upload_pyq.html')

# API route to get cards data (Notes, PYQs, Research Papers)
@app.route('/api/cards', methods=['GET'])
def get_cards():
    try:
        # Fetch cards data from the database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT title AS category, description, link 
            FROM cards_table
        """)
        cards = cursor.fetchall()
        cursor.close()

        # Return data as JSON
        return jsonify(cards), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Admin session end
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)  # Remove the admin session
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/api/search', methods=['GET'])
def search_cards():
    query = request.args.get('query')  # Get the search query from the request
    try:
        cursor = mysql.connection.cursor()
        # Modify the query to perform a search using LIKE
        cursor.execute("""
            SELECT title AS category, description, link 
            FROM cards_table 
            WHERE title LIKE %s OR description LIKE %s
        """, (f'%{query}%', f'%{query}%'))
        results = cursor.fetchall()
        cursor.close()

        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run()


