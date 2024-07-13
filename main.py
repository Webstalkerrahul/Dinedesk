from flask import Flask, render_template, request, url_for, redirect, session, g, jsonify
import requests
from tools import execute_workflows
from functools import wraps
from flask_cors import CORS
from elasticsearch import Elasticsearch

app = Flask(__name__)
CORS(app)
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

@app.route("/search")
def search_autocomplete():
    es = Elasticsearch(
    hosts=["https://127.0.0.1:9200"],
    basic_auth=('elastic', 'Nm5gG8=-lJB1pQl0eWXd'),
    ca_certs="E:\\Software\\elastic\\elasticsearch-8.13.0\\config\\certs\\http_ca.crt"
)
    print(f"Connected to ElasticSearch cluster {es.info().body['cluster_name']}")

    query = request.args["q"].lower()
    
    payload = {
        "_source": ["item_name"],
        "size": 15,
        "query": {
            "bool": {
                "must": [
                    {
                        "wildcard": {
                            "item_name": {
                                "value": f"{query}*"
                            }
                        }
                    }
                ]
            }
        },
        "aggs": {
            "auto_complete": {
                "terms": {
                    "field": "item_name.keyword",
                    "order": {
                        "_count": "desc"
                    },
                    "size": 25
                }
            }
        }
    }

    resp = es.search(index="test", body=payload)
    result = [result['_source']['item_name'] for result in resp['hits']['hits']]
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True, use_reloader=True)
