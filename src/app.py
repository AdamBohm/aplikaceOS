import os
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-insecure-secret')

@app.route('/')
def index():
    return redirect(url_for('page1'))

@app.route('/page1', methods=['GET', 'POST'])
def page1():
    if request.method == 'POST':
        session['name'] = request.form.get('name', '').strip()
        session['email'] = request.form.get('email', '').strip()
        return redirect(url_for('page2'))
    return render_template('page1.html', name=session.get('name', ''), email=session.get('email', ''))

@app.route('/page2', methods=['GET', 'POST'])
def page2():
    if request.method == 'POST':
        session['age'] = request.form.get('age', '').strip()
        session['comment'] = request.form.get('comment', '').strip()
        return redirect(url_for('summary'))
    return render_template('page2.html', age=session.get('age', ''), comment=session.get('comment', ''))

@app.route('/summary')
def summary():
    name = session.get('name', '')
    email = session.get('email', '')
    age = session.get('age', '')
    comment = session.get('comment', '')
    return render_template('summary.html', name=name, email=email, age=age, comment=comment)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
