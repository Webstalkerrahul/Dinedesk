import pandas as pd

def read_csv():
    df = pd.read_csv(r'./menus/test_menu.csv')
    return df