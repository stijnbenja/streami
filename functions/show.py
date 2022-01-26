import pandas as pd

# 1. orders to df
# 2. orders to paklijst

def orders_to_df(orders):
    df = pd.DataFrame(orders)
    df = df.explode('items')
    df = pd.concat([
        df.reset_index(drop=True), 
        pd.DataFrame(df['items'].tolist())
        ], 
                   axis=1).drop('items', axis = 1).sort_values('ref').reindex(
                        ['ref','quantity','ean','orderId','voornaam','achternaam','straat','huisnummer','postcode','stad','land'], 
                        axis=1).reset_index(drop=True)
    return df  

def orders_to_paklijst(orders):
    return orders_to_df(orders).groupby('ref').agg({'quantity':'sum'})

