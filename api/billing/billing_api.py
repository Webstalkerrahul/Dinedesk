from flask import Blueprint
from elasticsearch import Elasticsearch # type: ignore
import time
from tools.elasticsearch import es_queries
from tools import sql_main
# import es_conn, create_index, delete_index, find_item_by_name
from tools.elasticsearch import es_main,es_queries
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS # type: ignore


billing = Blueprint('billing',__name__)

def get_combine_totals(all_orders_list):
    tables=[]
    for orders in all_orders_list:
        tables.append(orders.get('table_no'))
    tables=list(set(tables))
    new = []
    for a in tables:
        n=es_main.get_table_total(a)
        new.append({'table_no':a,'table_total':n})
    return new

@billing.route('/show_tables', methods=["GET","POST"])
async def show_tables():
    if request.method == "POST":
        table = request.form.get("table-no")
        name = request.form.get("search-suggest")
        qty = request.form.get("item-quantity")
        item_details = es_main.find_item_by_name(name,table,qty)
        a = es_main.insert_into_index_orders(item_details)
        if a:
            # time.sleep(2)
            all_orders_list = es_main.get_all_orders()
            new= get_combine_totals(all_orders_list)
            return render_template('billing.html', items=all_orders_list, totals=new)
        
    all_orders_list = es_main.get_all_orders()
    new= get_combine_totals(all_orders_list)
    return render_template('billing.html', items=all_orders_list, totals=new)

@billing.route("/search")
def search_autocomplete():
    query = request.args["q"].lower()
    result  = es_main.auto_suggest(query)
    return jsonify(result)

@billing.route('/delete-item/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        es_main.delete_item(item_id)
        all_orders_list = es_main.get_all_orders()
       
        new = get_combine_totals(all_orders_list)
        return jsonify({
            'success': True,
            'items': all_orders_list,
            'totals': new
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@billing.route('/add_order_to_db/<table_no>',methods=["GET", "POST"])
def addorder(table_no):
    tabel_orders=es_main.get_table_orders(table_no)
    new= es_main.get_table_total(table_no)
    sql_main.print_bill(tabel_orders,new,table_no)
    return jsonify({
            'success': True
        })