from flask import Flask, render_template, request, url_for, redirect, session, g
from tools import execute_workflows
from functools import wraps

app = Flask(__name__)
app.secret_key = 'aa'

users = {
    'admin': 'password'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def load_user():
    g.user = session.get('user')

@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        first_name = request.form.get("username")
        print(first_name)
    return render_template('registration.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
            session['user'] = username
            print("logged in")
            return redirect(url_for('home'))
        else:
            error = "Invalid username or password"
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route("/")
@app.route("/home")
@login_required
def home():
    # res = await execute_workflows.start_dashboard_workflow("test")
    return render_template('dashboard.html', name=g.user)

@app.route("/analysis")
@login_required
def analysis():
    # res = await execute_workflows.start_dashboard_workflow("test")
    return render_template('dashboard.html', name=g.user)

@app.route('/test')
def index():
    return render_template('test.html')

@app.route('/billing')
def billing():
    return render_template('billing.html')

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True, use_reloader=True)
