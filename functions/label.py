import os 
import shutil
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter, A4, A6
from PyPDF2 import PdfFileMerger
import streamlit as st
from PyPDF2 import PdfFileMerger

def create_labels():
    
    change_slash = lambda name: name.replace('/','|')
    
    #Remove and create labels folder
    shutil.rmtree('labels', ignore_errors=True)
    os.mkdir('labels')
    
    for order in st.session_state['orders']:
            
            label_width, label_height = A6[1], A6[0]
            
            file_name = f"{change_slash(order['items'][0]['ref'])}-{order['orderId']}"
            canvas = Canvas(f"labels/{file_name}.pdf", pagesize=(label_width, label_height))
            
            logo_file = 'postnl.jpg'
            logo_ratio = 1.84957627119
            logo_height = 90
            logo_width = logo_height * logo_ratio

            line_distance = 1.2
            
            font_name = 'Helvetica'
            font_name_bold = 'Helvetica-Bold'
            font_size_normal = 10
            font_size_small = 7
            line_height_normal = font_size_normal * line_distance
            line_height_small =  font_size_small * line_distance
            
            
            eigen_adres = st.secrets['adres']
            
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
            
            canvas.drawString(label_padding, top_margin-line_height_small*(1), f"Order {order['orderId']}")
            
            for i, item in enumerate(order['items']):
                canvas.drawString(label_padding, top_margin-line_height_small*(3 + i*4), str(item['quantity']))
                canvas.drawString(label_padding, top_margin-line_height_small*(4 + i*4), change_slash(item['ref']))
                #canvas.drawString(label_padding, top_margin-line_height_small*(5 + i*4), str(item['ean']))
                        
            # Post nl logo
            canvas.drawImage(logo_file, label_width-label_padding-logo_width+5, label_height-label_padding-logo_height+5, mask='auto', width=logo_width,height=logo_height)
            
            canvas.save()
            
    shutil.make_archive('labels', 'zip', 'labels')