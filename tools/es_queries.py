def find_by_item_name_query(name):
    query = {
    "query": {
        "bool": {
            "must": {
                "match_phrase": {
                    "item_name": name
                }
            },
            "filter": {
                "term": {
                    "item_name.keyword": name
                }
            }
        }
    }
}
    return query

def auto_suggest_query(query):
    query = {
        "_source": ["item_name"],
        "size": 15,
        "query": {
            "match_phrase_prefix": {
                "item_name": {
                    "query": query,
                    "max_expansions": 10
                }
            }
        }
    }
    return query

def get_table_orders(tableno):
    query = {
        "query": {
            "term": {
            "table_no": tableno
            }
        }
        }
    return query

def get_table_total_query(tableno):
    query = {
    "query": {
        "term": {
            "table_no": tableno
        }
    },
    "aggs": {
        "table_total": {
            "sum": {
                "field": "item_total"
            }
        }
    }
}
    return query

def get_all_orders_query():
    query = {
        "size": 1000,
        "query": {
            "match_all": {}
        }
        }           
    return query

def update_item_qty(qty,price):
    query = {
            "doc": {
                "qty": qty,
                "item_total":price
            }
        }

    return query

