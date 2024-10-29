from utils import connect
import psycopg2
from datetime import datetime, timedelta

es = connect.es_connect()
connection = connect.db_connect()
# connection = psycopg2.connect(database="Dinedesk", user="postgres", password="admin", host="localhost", port="5432")
cursor = connection.cursor()

def print_bill(tabel_orders,new,table_no):
    items = []
    item_qty = []
    items_price = []
    items_price_total = []

    for order in tabel_orders:   
        items.append(order['_source']['item_name'])
        items_price.append(order['_source']['item_price'])
        item_qty.append(order['_source']['qty'])
        items_price_total.append(order['_source']['item_total'])

    insert_query = """
    INSERT INTO bills (table_no, products, qty, price, total_price, total_bill, online, cash)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(insert_query, (table_no, items, item_qty, items_price, items_price_total, new, 0, 0))

    connection.commit()
    # connection.close()

    # Fetch and print the records from the bills table
    # cursor.execute("SELECT * FROM bills;")
    # record = cursor.fetchall()

    # for row in record:
    #     print(row)
    for order in tabel_orders:   
        item_id=order['_id']
        es.delete(index="orders", id=item_id)

def get_bills():
    try:
        
        connection.rollback()
        start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1, hours=6)

        cursor.execute(
            "SELECT * FROM bills WHERE time >= %s AND time < %s ORDER BY time DESC;",
            (start_time, end_time)
        )
        records = cursor.fetchall() 

        cursor.execute("SELECT SUM(online) AS total_online, SUM(cash) AS total_cash, SUM(total_bill) AS total_sum FROM bills WHERE time >= %s AND time < %s", (start_time, end_time))
        totals = cursor.fetchone() 
        totals = [float(value) if value is not None else 0 for value in totals]
        return records, totals 
    except psycopg2.Error as e:
        connection.rollback()
        print(f"Database error occurred: {e}")
        raise

    finally:
        connection.commit()

def add_payment(bill_no, online, cash):
    try:
        cursor.execute("SELECT cash,online FROM bills WHERE id = %s;", (bill_no,))
        result = cursor.fetchone()

        if cash == 0:
            cash = result[0]
        if online == 0:
            online = result[1]

        query = "UPDATE bills SET online = %s, cash = %s WHERE id = %s;"
        cursor.execute(query, (online, cash, bill_no))
        connection.commit()
        return 200
    except Exception as e:
        print(f"Error due to {e}")
        return 404

def get_expenses():
    try:
        
        connection.rollback()
        start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1, hours=6)

        cursor.execute(
            "SELECT * FROM expenses WHERE time >= %s AND time < %s ORDER BY time DESC;",
            (start_time, end_time)
        )
        records = cursor.fetchall() 

        cursor.execute("SELECT SUM(online) AS total_online, SUM(cash) AS total_cash, SUM(rate) AS total_sum FROM expenses WHERE time >= %s AND time < %s", (start_time, end_time))
        totals = cursor.fetchone()

        cursor.execute("SELECT SUM(online) AS total_online, SUM(cash) AS total_cash, SUM(total_bill) AS total_sum FROM bills WHERE time >= %s AND time < %s", (start_time, end_time))
        totals_bill = cursor.fetchone()

        totals = [float(value) if value is not None else 0 for value in totals]
        totals_bill = [float(value) if value is not None else 0 for value in totals_bill]
        return records, totals, totals_bill
    
    except psycopg2.Error as e:
        connection.rollback()
        print(f"Database error occurred: {e}")
        raise

    finally:
        connection.commit()

def add_expenses(item, rate, cash, online):
    try:
        if cash == '' or cash == None:
            cash = 0 
        
        if online == '' or online == None:
            online = 0

        query = "INSERT INTO expenses (item, rate, cash, online) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (item, rate, cash, online))
        connection.commit()
        return 200
    except Exception as e:
        print(f"Error due to {e}")
        return 404