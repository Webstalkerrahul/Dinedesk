from flask import Blueprint, jsonify, render_template, redirect, url_for, request
from tools import sql_main
# import es_conn, create_index, delete_index, find_item_by_name
from tools.elasticsearch import es_main,es_queries

expenses = Blueprint('expenses',__name__)

@expenses.route("/show_all")
def show_all():
    expenses, expenses_sums, totals_bill = sql_main.get_expenses()
    expenses_sums = list(expenses_sums)
    
    total = expenses_sums[2] if expenses_sums[2] is not None else 0
    total_online = expenses_sums[0] if expenses_sums[0] is not None else 0
    total_cash = expenses_sums[1] if expenses_sums[1] is not None else 0

    print(totals_bill)

    totals_bill[2] = totals_bill[2] - total
    total_online = expenses_sums[0] - totals_bill[1]
    total_cash = expenses_sums[1] - totals_bill[0]

    return render_template(
        'expenses.html',
        data =expenses,
        total = total,
        totals_bill = totals_bill[2],
        online = total_online,
        cash = total_cash
        )

@expenses.route("/insert_expenses", methods=["POST"])
def insert_expenses():
    item = request.form.get("item_name")
    rate = request.form.get("rate")
    cash = request.form.get("cash")
    online = request.form.get("online")
    

    res = sql_main.add_expenses(item, rate, cash, online)
    return redirect(url_for('expenses.show_all'))