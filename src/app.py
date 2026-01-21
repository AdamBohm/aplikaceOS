import os
import logging
from datetime import datetime
import pyodbc
from flask import Flask, render_template, request, redirect, url_for, session

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-insecure-secret')

# Helper to get or set default session keys
def get_session(key, default=''):
    return session.get(key, default)

@app.route('/')
def index():
    return redirect(url_for('page1'))

# Step 1: osobní údaje
@app.route('/page1', methods=['GET', 'POST'])
def page1():
    if request.method == 'POST':
        session['name'] = request.form.get('name', '').strip()
        session['email'] = request.form.get('email', '').strip()
        return redirect(url_for('page2'))
    return render_template('page1.html', name=get_session('name'), email=get_session('email'))

# Step 2: volba workshopu / tracku
@app.route('/page2', methods=['GET', 'POST'])
def page2():
    tracks = [
        {'id': 'beginner', 'title': 'Začátečníci', 'desc': 'Základy, praktické cvičení.'},
        {'id': 'intermediate', 'title': 'Středně pokročilí', 'desc': 'Rozšířené techniky a best practices.'},
        {'id': 'advanced', 'title': 'Pokročilí', 'desc': 'Deep-dive, případové studie.'}
    ]
    if request.method == 'POST':
        session['track'] = request.form.get('track', '')
        session['experience'] = request.form.get('experience', '')
        return redirect(url_for('page3'))
    return render_template('page2.html', tracks=tracks, selected_track=get_session('track'), experience=get_session('experience'))

# Step 3: volba termínu a poznámka
@app.route('/page3', methods=['GET', 'POST'])
def page3():
    dates = [
        '2026-02-20',
        '2026-03-05',
        '2026-03-19'
    ]
    if request.method == 'POST':
        session['date'] = request.form.get('date', '')
        session['notes'] = request.form.get('notes', '').strip()
        return redirect(url_for('summary'))
    return render_template('page3.html', dates=dates, date=get_session('date'), notes=get_session('notes'))

# Souhrn
@app.route('/summary', methods=['GET'])
def summary():
    data = {
        'name': get_session('name'),
        'email': get_session('email'),
        'track': get_session('track'),
        'experience': get_session('experience'),
        'date': get_session('date'),
        'notes': get_session('notes')
    }
    # Try to save to SQL Server if configuration is provided
    try:
        save_registration(data)
    except Exception as e:
        logging.exception('Failed to save registration to DB: %s', e)
    return render_template('summary.html', data=data)


def get_db_connection():
    host = os.environ.get('DB_HOST')
    if not host:
        return None
    driver = os.environ.get('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
    port = os.environ.get('DB_PORT', '1433')
    database = os.environ.get('DB_NAME', '')
    user = os.environ.get('DB_USER', '')
    password = os.environ.get('DB_PASSWORD', '')

    server = f"{host},{port}" if port else host
    conn_str = (
        f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={user};PWD={password}"
    )
    return pyodbc.connect(conn_str, timeout=5)


def ensure_table(conn):
    create_sql = """
    IF OBJECT_ID('dbo.registrations', 'U') IS NULL
    CREATE TABLE dbo.registrations (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(200),
        email NVARCHAR(200),
        track NVARCHAR(100),
        experience NVARCHAR(100),
        event_date DATE,
        notes NVARCHAR(MAX),
        created_at DATETIME
    )
    """
    with conn.cursor() as cur:
        cur.execute(create_sql)
        conn.commit()


def save_registration(data: dict):
    conn = get_db_connection()
    if conn is None:
        logging.info('DB not configured; skipping save.')
        return
    try:
        ensure_table(conn)
        insert_sql = (
            "INSERT INTO dbo.registrations (name, email, track, experience, event_date, notes, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)"
        )
        event_date = None
        if data.get('date'):
            try:
                event_date = datetime.fromisoformat(data.get('date')).date()
            except Exception:
                event_date = None
        params = (
            data.get('name'),
            data.get('email'),
            data.get('track'),
            data.get('experience'),
            event_date,
            data.get('notes'),
            datetime.utcnow(),
        )
        with conn.cursor() as cur:
            cur.execute(insert_sql, params)
            conn.commit()
        logging.info('Saved registration for %s', data.get('email'))
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
