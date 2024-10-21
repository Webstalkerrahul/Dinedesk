from connect import es_conn,create_index
import csv_help
from elasticsearch.helpers import bulk

conn = es_conn()
df = csv_help.read_csv()

temp = create_index(conn,"test")
try:
    for i, row in df.iterrows():
        doc ={
            "hotel_name":"hotel1",
            "hotel_id":1,
            "item_name":row['name'],
            "item_price":row['price']
        }
        conn.index(index="test", id=i, document=doc)
        print("Data inserted successfully in Elastic search")

except Exception as e:
    print(f"Error while inserting documents due to :\n{e}")




