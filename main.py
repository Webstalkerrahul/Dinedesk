from flask import Flask, render_template, request, url_for, redirect, session, g, jsonify
from tools import connect, es_queries
# import es_conn, create_index, delete_index, find_item_by_name
from tools import execute_workflows
from functools import wraps
from flask_cors import CORS # type: ignore
from elasticsearch import Elasticsearch # type: ignore
import time

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

def get_combine_totals(es,all_orders_list):
    tables=[]
    for orders in all_orders_list:
        tables.append(orders.get('table_no'))
    tables=list(set(tables))
    new = []
    for a in tables:
        n=connect.get_table_total(es,a)
        new.append({'table_no':a,'table_total':n})
    return new


@app.route('/billing', methods=["GET","POST"])
async def billing():
    es = connect.es_conn()
    if request.method == "POST":
        table = request.form.get("table-no")
        name = request.form.get("search-suggest")
        qty = request.form.get("item-quantity")
        item_details = connect.find_item_by_name(es,name,table,qty)
        a = connect.insert_into_index_orders(es, item_details)
        if a:
            time.sleep(2)
            all_orders_list = connect.get_all_orders(es)
            new= get_combine_totals(es,all_orders_list)
            return render_template('billing.html', items=all_orders_list, totals=new)
        
    all_orders_list = connect.get_all_orders(es)
    new= get_combine_totals(es,all_orders_list)
    return render_template('billing.html', items=all_orders_list, totals=new)
    
@app.route('/test')
def test():
    return render_template('test.html')

@app.route("/search")
def search_autocomplete():
    es = connect.es_conn()
    print(f"Connected to ElasticSearch cluster {es.info().body['cluster_name']}")

    query = request.args["q"].lower()
    
    payload = es_queries.auto_suggest_query(query)

    resp = es.search(index="test", body=payload)
    result = [result['_source']['item_name'] for result in resp['hits']['hits']]
    return jsonify(result)

@app.route('/delete-item/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        es = connect.es_conn()
        es.delete(index="orders", id=item_id)
        all_orders_list = connect.get_all_orders(es)
        new= get_combine_totals(es,all_orders_list)
        return jsonify({
            'success': True,
            'items': all_orders_list,
            'totals': new
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_order_to_db/<table_no>',methods=["GET", "POST"])
def addorder(table_no):
    print("before")
    es = connect.es_conn()
    tabel_orders=connect.get_table_orders(es,table_no)
    new= connect.get_table_total(es,table_no)
    connect.print_bill(tabel_orders,new,table_no)
    print("after")
    return jsonify({
            'success': True
        })

@app.route('/start_table',methods=["GET", "POST"])
def start_table():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True, use_reloader=True)
