from flask import Blueprint, jsonify, render_template, redirect, url_for, request
from tools import sql_main
# import es_conn, create_index, delete_index, find_item_by_name
from tools.elasticsearch import es_main,es_queries

payments = Blueprint('payments',__name__)

@payments.route("/show_all")
def show_all():
    bills, bill_sums = sql_main.get_bills()
    bill_sums = list(bill_sums)
    total_online = bill_sums[0] if bill_sums[0] is not None else 0
    total_cash = bill_sums[1] if bill_sums[1] is not None else 0
    total = bill_sums[2] if bill_sums[0] is not None else 0
    return render_template(
        'payments.html',
        data = bills,
        total_online = total_online, 
        total_cash = total_cash, 
        total = total,)

@payments.route("/insert_payment", methods=['POST'])
def insert_payment():
    bill_no = request.form.get("bill_no")
    online = request.form.get("online")
    cash = request.form.get("cash")

    if cash == None or cash == '':
        cash = 0
    if online == None or online == '':
        online = 0

    res = sql_main.add_payment(bill_no, online, cash)
    return redirect(url_for('payments.show_all'))
    

