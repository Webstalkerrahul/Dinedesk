from tools import get_config, es_queries, csv_help
from elasticsearch import Elasticsearch # type: ignore
import psycopg2 # type: ignore

con = get_config.get_es_config()

def es_conn():
    es_user=con['es_user']
    es_pass=con['es_pass']
    es_host_1=con['es_host_1']
    es_ca_certs=con['es_ca_certs']
    client = Elasticsearch(
        hosts=es_host_1,
        ca_certs=es_ca_certs,
        basic_auth=(es_user, es_pass)
    )
    # print(client.info())
    return client

def create_index(conn,name):
    try: 
        res = conn.indices.create(index=f"{name}")
        return 201 #this is for created
    except Exception as e: 
        return 409 #this is for conflic index already exists

def delete_index(conn,name):
    try: 
        res = conn.indices.delete(index=f"{name}",ignore=[400, 404])
        return 201 #this is for created
    except Exception as e: 
        return 409 #this is for conflic index already exists
    
def find_item_by_name(conn,name,table,qty):
    try:
        query = es_queries.find_by_item_name_query(name)
        item_result = conn.search(index="test", body=query)
        item_details = item_result['hits']['hits'][0]['_source']
        item_details.update({'table_no':int(table),'qty':int(qty),'item_total':int(item_details['item_price'])*int(qty)})
        return item_details
    except Exception as e:
        return False

def insert_into_index_df(conn):
    df = csv_help.read_csv()
    try:
        for i, row in df.iterrows():
            doc ={
                "hotel_name":"hotel1",
                "hotel_id":i,
                "item_name":row['NAME'],
                "item_price":row['PRICE']
            }
            conn.index(index="test", id=i, document=doc)
        print("Data inserted successfully in Elastic search")

    except Exception as e:
        print(f"Error while inserting documents due to :\n{e}")

def insert_into_index_orders(conn,item_details):
    try:
        tno = item_details["table_no"]
        item_name = item_details["item_name"]
        item_qty = item_details["qty"]
        item_price = item_details["item_price"]
        result = get_table_orders(conn, tno)
        
        if result:
            for res in result:
                if tno == res['_source']['table_no'] and item_name == res['_source']['item_name']:
                    qty = res['_source']['qty']+item_qty
                    price = qty * item_price
                    doc_id = res['_id']
                    query = es_queries.update_item_qty(qty,price)
                    conn.update(index="orders",id = doc_id,body=query)
                    print("Data updated ")
                    return True
                
        conn.index(index="orders", document=item_details)
        print("Data inserted")
       
        return True

    except Exception as e:
        print(f"Error while inserting documents due to :\n{e}")

def get_table_orders(conn,tableno):
    try:
        query=es_queries.get_table_orders(tableno)
        result = conn.search(index="orders", body=query)
        table_orders = result['hits']['hits']
        return table_orders

    except Exception as e:
        print(f"Error while fetching orders due to :\n{e}")

def get_table_total(conn,tableno):
    try:
        query=es_queries.get_table_total_query(tableno)
        result = conn.search(index="orders", body=query)
        total = result['aggregations']['table_total']['value']
        return total

    except Exception as e:
        print(f"Error while fetching orders due to :\n{e}")


def get_all_orders(conn):
    try:
        query=es_queries.get_all_orders_query()
        all_orders = conn.search(index="orders", body=query)
        orders_with_id=[]
        all_orders = [hit for hit in all_orders['hits']['hits']]
        for order in all_orders:
            result = {
                    '_id': order['_id'],
                    'hotel_name': order['_source']['hotel_name'],
                    'hotel_id': order['_source']['hotel_id'],
                    'item_name': order['_source']['item_name'],
                    'item_price': order['_source']['item_price'],
                    'table_no': order['_source']['table_no'],
                    'qty': order['_source']['qty'],
                    'item_total': order['_source']['item_total']
                }
            orders_with_id.append(result)
        return orders_with_id

    except Exception as e:
        print(f"Error while fetching orders due to :\n{e}")

def update_qty(conn,qty):
    try:
        query = es_queries.update_item_qty(qty)
        response = conn.update_by_query(index="orders", body=query)
        print(response)
    except Exception as e:
        print(f"Error while updataing qty due to :\n{e}")

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

    print("total:", new)

    connection = psycopg2.connect(database="Dinedesk", user="postgres", password="admin", host="localhost", port="5432")
    cursor = connection.cursor()

    insert_query = """
    INSERT INTO bills (table_no, products, qty, price, total_price, total_bill)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(insert_query, (table_no, items, item_qty, items_price, items_price_total, new))

    connection.commit()
    cursor.close()
    connection.close()

    # Fetch and print the records from the bills table
    # cursor.execute("SELECT * FROM bills;")
    # record = cursor.fetchall()

    # for row in record:
    #     print(row)
    es = es_conn()
    for order in tabel_orders:   
        item_id=order['_id']
        es.delete(index="orders", id=item_id)
    print("item deleted")

