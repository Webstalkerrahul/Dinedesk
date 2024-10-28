from tools import csv_help
from tools.elasticsearch import es_queries
from utils import connect
from flask import request
import time
es_conn = connect.es_connect()

def create_index(name):
    try: 
        res = es_conn.indices.create(index=f"{name}")
        return 201 #this is for created
    except Exception as e: 
        return 409 #this is for conflic index already exists

def delete_index(name):
    try: 
        res = es_conn.indices.delete(index=f"{name}",ignore=[400, 404])
        return 201 #this is for created
    except Exception as e: 
        return 409 #this is for conflic index already exists
    
def find_item_by_name(name,table,qty):
    try:
        query = es_queries.find_by_item_name_query(name)
        item_result = es_conn.search(index="test", body=query)
        item_details = item_result['hits']['hits'][0]['_source']
        item_details.update({'table_no':int(table),'qty':int(qty),'item_total':int(item_details['item_price'])*int(qty)})
        return item_details
    except Exception as e:
        return False

def insert_into_index_df():
    df = csv_help.read_csv()
    try:
        for i, row in df.iterrows():
            doc ={
                "hotel_name":"hotel1",
                "hotel_id":i,
                "item_name":row['NAME'],
                "item_price":row['PRICE']
            }
            es_conn.index(index="test", id=i, document=doc)

    except Exception as e:
        print(f"Error while inserting documents due to :\n{e}")

def insert_into_index_orders(item_details):
    try:
        tno = item_details["table_no"]
        item_name = item_details["item_name"]
        item_qty = item_details["qty"]
        item_price = item_details["item_price"]
        result = get_table_orders(tno)
        
        if result:
            for res in result:
                if tno == res['_source']['table_no'] and item_name == res['_source']['item_name']:
                    qty = res['_source']['qty']+item_qty
                    price = qty * item_price
                    doc_id = res['_id']
                    query = es_queries.update_item_qty(qty,price)
                    es_conn.update(index="orders",id = doc_id,body=query)
                    return True
                
        es_conn.index(index="orders", document=item_details)
        es_conn.indices.refresh(index="orders")
       
        return True

    except Exception as e:
        print(f"Error while inserting documents due to :\n{e}")

def get_table_orders(tableno):
    try:
        query=es_queries.get_table_orders(tableno)
        result = es_conn.search(index="orders", body=query)
        table_orders = result['hits']['hits']
        return table_orders

    except Exception as e:
        print(f"Error while fetching orders due to :\n{e}")

def get_table_total(tableno):
    try:
        query=es_queries.get_table_total_query(tableno)
        result = es_conn.search(index="orders", body=query)
        total = result['aggregations']['table_total']['value']
        return total

    except Exception as e:
        print(f"Error while fetching orders due to :\n{e}")


def get_all_orders():
    try:
        es_conn.indices.refresh(index="orders")
        query=es_queries.get_all_orders_query()
        all_orders = es_conn.search(index="orders", body=query)
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

def update_qty(qty):
    try:
        query = es_queries.update_item_qty(qty)
        response = es_conn.update_by_query(index="orders", body=query)
    except Exception as e:
        print(f"Error while updataing qty due to :\n{e}")

def auto_suggest(query):
    
    payload = es_queries.auto_suggest_query(query)
    resp = es_conn.search(index="test", body=payload)
    result = [result['_source']['item_name'] for result in resp['hits']['hits']]
    return result

def delete_item(item_id):
    try:
        print(item_id)
        res= es_conn.delete(index="orders", id=item_id)
        es_conn.indices.refresh(index="orders")

        print(res)
    except:
        print("Cannot r")