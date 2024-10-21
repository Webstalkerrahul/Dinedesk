import pandas as pd

def read_csv():
    df = pd.read_csv(r'./menus/menu.csv')
    return df