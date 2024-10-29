from flask import Flask, render_template, request, url_for, redirect, session, g, jsonify
from functools import wraps
from flask_cors import CORS # type: ignore


from api.billing.billing_api import billing
from api.payments.payment_api import payments
from api.expenses.expenses_api import expenses
# from api import test.test

app = Flask(__name__)
CORS(app)
app.secret_key = 'aa'

users = {
    'admin': 'password'
}

app.register_blueprint(billing,url_prefix='/billing')
app.register_blueprint(payments,url_prefix='/payments')
app.register_blueprint(expenses,url_prefix='/expenses')

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

@app.route("/login", methods=["GET", "POST", "POST"])
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
    
@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/start_table',methods=["GET", "POST"])
def start_table():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True, use_reloader=True)
