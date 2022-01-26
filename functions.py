import requests 
import time
from requests.api import request
from requests.auth import HTTPBasicAuth
import shutil
import os
import streamlit as st
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter, A4, A6
from PyPDF2 import PdfFileMerger

def update_bearer(pub=,priv):

    login_url = 'https://login.bol.com/token?grant_type=client_credentials'
    login_request = requests.post(login_url, auth=HTTPBasicAuth(pub, priv))

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

def orders():
    return getter('orders')

def return_order_dict(orderId):
    
    r = getter(f'orders/{orderId}')
    r2 = r['shipmentDetails']
    ordered_items = r['orderItems']
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

    
def create_labels():
    
    change_slash = lambda name: name.replace('/','|')
    
    #Remove and create labels folder
    shutil.rmtree('labels', ignore_errors=True)
    os.mkdir('labels')
    
    for order in st.session_state['orders']:
            
            label_width, label_height = A6[1], A6[0]
            canvas = Canvas(f"labels/{change_slash(order['ref'])}-{order['orderId']}.pdf", pagesize=(label_width, label_height))

            #Parameters
            logo_file = 'postnl.jpg'
            logo_ratio = 1.84957627119
            logo_height = 70
            logo_width = logo_height * logo_ratio

            line_distance = 1.2
            
            font_name = 'Helvetica'
            font_name_bold = 'Helvetica-Bold'
            font_size_normal = 8
            font_size_small = 5
            line_height_normal = font_size_normal * line_distance
            line_height_small =  font_size_small * line_distance
            
            eigen_adres = "The BrosMen, Boadreef 2, 3563 EP Utrecht"
            
            label_padding = 10
            top_margin = 170
            left_margin = 160
            
            # Set standard font
            canvas.setFont(font_name, font_size_normal)
            
            # Eigen adres
            canvas.drawString(label_padding, label_height-line_height_normal*2, eigen_adres)
            
            # Main Text
            
            # 1. Naam
            canvas.drawString(left_margin, top_margin, f"{order['voornaam']} {order['achternaam']}")
            # 2. Straat & huisnummer
            canvas.drawString(left_margin, top_margin-line_height_normal*1, f"{order['straat']} {order['huisnummer']}")
            # 4. Land
            canvas.drawString(left_margin, top_margin-line_height_normal*3, f"{order['land']}")
            # 3. Postcode & stad
            canvas.setFont(font_name_bold, font_size_normal)
            canvas.drawString(left_margin, top_margin-line_height_normal*2, f"{order['postcode']} {order['stad']}")
            
            # Side Text
            canvas.setFont(font_name, font_size_small)
            canvas.drawString(label_padding, top_margin-line_height_small*3, order['orderId'])
            canvas.drawString(label_padding, top_margin-line_height_small*4, change_slash(order['ref']))
            
            # Post nl logo
            canvas.drawImage(logo_file, 360-logo_height, 350-logo_width, mask='auto', width=logo_width,height=logo_height)
            
            canvas.save()
            
    shutil.make_archive('labels', 'zip', 'labels')