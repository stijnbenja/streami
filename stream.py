import streamlit as st
import pandas as pd
import io
import requests 
import time
from requests.auth import HTTPBasicAuth
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter, A4, A6
import shutil
import os
#from functions import *
from datetime import datetime, timedelta
import threading


from functions import get, show, label

# VARIABLES --------------------------------------------------------------------

password, pub, priv = st.secrets['pass'], st.secrets["pub"], st.secrets["priv"]

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    
if 'actief' not in st.session_state:
    st.session_state['actief'] = False
    
if 'df' not in st.session_state:
    st.session_state['df'] = 'Click button to retreive orders'
    
if 'df_pak' not in st.session_state:
    st.session_state['df_pak'] = ''    
    

if 'orders' not in st.session_state:
    st.session_state['orders'] = None

# AUTHENITCATION -------------------------------------------------------------------------- 

st.title('Brosmen label systeem')
st.caption('Download openstaande orders and genereer labels')

#Loggin section
if st.session_state['logged_in'] == False:
    pass_input = st.text_input('Password', type="password")
    if pass_input == password:
        st.session_state['logged_in'] = True
        st.write('Succesfully logged in!')        

# BODY -----------------------------------------------------------------------------------
def append_order(orderId):
    global orders
    orders.append(get.return_order_dict(orderId))


if st.session_state['logged_in']:
     
    button_order_download = st.button("Download open orders")
    st.markdown('---')

    if button_order_download:
        
        

        
        # Get order id's of open orders
        get.update_bearer(pub,priv)
        orderId_list = get.get_all_orders_ids()
        
        # Get information of each order and display progress bar
        orders = []
        progress_bar = st.progress(0)
        thread_list = []
        
        for i, orderId in enumerate(orderId_list):
            
            thread = threading.Thread(target=append_order, args=(orderId,))
            thread.start()
            thread_list.append(thread)
            time.sleep(0.05)
            
            if len(orderId_list) > 1:
                progress_bar.progress(round(i/(len(orderId_list)-1),2))
                
        for thread in thread_list:
            thread.join()   
                 
        progress_bar.empty()
        
        st.session_state['orders'] = orders
        
        # Create and display orders dataframe
        try:
            st.session_state['df'] = show.orders_to_df(st.session_state['orders'])
        except:
            st.subheader('Ik ben aan het programmeren')
            st.caption('Vandaar de error hieronder')
            
        st.session_state['df_pak'] = show.orders_to_paklijst(st.session_state['orders'])
        st.session_state['actief'] = True    
        
    st.session_state['df']  
    
    
    if st.session_state['actief'] == True:    
    
    
        col1, col2 = st.columns(2)
        
        with col1:
            
            try:
                st.subheader('Paklijst')
                st.dataframe(data=st.session_state['df_pak'], height=10000)
            except:
                pass
            
            
        with col2:
              
            
            st.subheader('Excel bestanden')
            #orders to excel button    
            try:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    st.session_state['df'].to_excel(writer)
                    writer.save()
                    st.download_button(
                        label="Download orders",
                        data=buffer,
                        file_name="orders.xlsx",
                        mime="application/vnd.ms-excel"
                    )  
            except:
                pass
            
        
            #orders to paklijst button
            try:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    st.session_state['df_pak'].to_excel(writer)
                    writer.save()
                    st.download_button(
                        label="Download paklijst",
                        data=buffer,
                        file_name="paklijst.xlsx",
                        mime="application/vnd.ms-excel"
                    )  
            except:
                pass
        
                    

            st.subheader('Labels')
                
            label.create_labels()
            
            with open('labels.zip', "rb") as fp:
                btn = st.download_button(
                    label="Download als ZIP",
                    data=fp,
                    file_name='labels.zip',
                    mime="application/zip"
                )
            
            merger = label.PdfFileMerger()

            for pdf in sorted(['labels/'+ label for label in os.listdir('labels')]):
                merger.append(open(pdf, 'rb'))
            
            
            date = (datetime.utcnow() + timedelta(hours=1)).strftime('%d-%b-%y %H:%M')
                
            with open(f"labels {date}.pdf", "wb") as fout:
                merger.write(fout)
            
            
            with open(f"labels {date}.pdf", "rb") as fp:
                btn = st.download_button(
                    label="Download als 1 PDF",
                    data=fp,
                    file_name=f'labels {date}.pdf',
                )
            
            
            
        
        
        
        
        



