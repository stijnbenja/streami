import requests 
import time
from requests.auth import HTTPBasicAuth

# 1. update bearer
# 2. getter
# 3. get all orders [id only] (list)
# 4. get single order [all info] (dict)
# 5. Append order to list

def update_bearer(pub,priv):

    login_request = requests.post(
        url = 'https://login.bol.com/token?grant_type=client_credentials', 
        auth = HTTPBasicAuth(pub, priv)
        )

    global bearer
    bearer = login_request.json()['access_token']
    print(f'login succesful at {time.strftime("%H:%M", time.localtime())}' if str(login_request) == '<Response [200]>' else 'Problem occured')
  

def getter(sub, params=None):

    header = {
        'Authorization': 'Bearer {}'.format(bearer),
        'Accept': 'application/vnd.retailer.v5+json'
    }
    
    base = 'https://api.bol.com/retailer/'
    return requests.get(base+sub, headers=header, params=params).json()  
  
     
def get_all_orders_ids():
    orders = []
    for page_nr in range(1,10):
        try:
            orders += getter(f'orders?page={page_nr}')['orders']
        except:
            break
        
    orderId_list = [order['orderId'] for order in orders]
    return orderId_list     


def return_order_dict(orderId):
    
    r = getter(f'orders/{orderId}')
    r2 = r['shipmentDetails']
    ordered_items = r['orderItems']
    ordered_items = [item for item in ordered_items if item['fulfilment']['distributionParty']!='BOL']
    
    order_dict = {
        'orderId': r['orderId'],
        
        'items':[
            {
            'ref': order['offer']['reference'],
            'ean': order['product']['ean'],
            'quantity': order['quantity']
        } 
            for order in ordered_items],
        
        'voornaam': r2['firstName'], 
        'achternaam': r2['surname'], 
        'straat': r2['streetName'], 
        'huisnummer': r2['houseNumber'],
        'postcode':r2['zipCode'],
        'stad':r2['city'], 
        'land':r2['countryCode']
    }
    
    return order_dict


def append_order(orderId):
    global orders
    orders.append(return_order_dict(orderId))
    