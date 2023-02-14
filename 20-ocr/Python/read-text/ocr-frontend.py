from dotenv import load_dotenv 
import time
from PIL import Image, ImageDraw 
from glob import glob
import os
from os import path  
import sys 
import streamlit as st 
import json
import requests 

# Import namespaces
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

# Get Configuration Settings
load_dotenv()
cog_endpoint = os.getenv('COG_SERVICE_ENDPOINT')
cog_key = os.getenv('COG_SERVICE_KEY')

# Authenticate Computer Vision client
credential = CognitiveServicesCredentials(cog_key)
cv_client = ComputerVisionClient(cog_endpoint, credential)


def read_text(file):
    # set up the REST API endpoint and headers
    url = endpoint + '/formrecognizer/v2.1/layout/analyze'
    headers = {
        'Content-Type': 'application/pdf',
        'Ocp-Apim-Subscription-Key': subscription_key
    }

    # read the file data and set up the request body
    file_data = file.read()
    data = file_data

    # send the request to the Form Recognizer service
    response = requests.post(url, headers=headers, data=data)

    # check if the request was successful
    if response.status_code != 202:
        raise ValueError('Failed to submit the request. Expected 202, got {} ({})'.format(response.status_code, response.json()))

    # get the operation location from the response headers
    operation_location = response.headers['Operation-Location']

    # poll the service until the operation is complete
    while True:
        response = requests.get(operation_location, headers=headers)
        if response.status_code != 200:
            raise ValueError('Failed to fetch the result. Expected 200, got {} ({})'.format(response.status_code, response.json()))
        response_json = response.json()
        if response_json['status'] in ['succeeded', 'failed']:
            break

    # check if the operation was successful
    if response_json['status'] == 'failed':
        raise ValueError('The operation failed: {}'.format(response_json['analyzeResult']['errors']))

    # extract the text from the response
    text = ''
    pages = response_json['analyzeResult']['pageResults']
    for page in pages:
        for line in page['lines']:
            for word in line['words']:
                text += word['text'] + ' '

    # return both the extracted text and the full JSON output
    return text, response_json

# create a Streamlit app with a file upload widget
st.title('Azure Form Recognizer Demo')
file = st.file_uploader('Upload a PDF file')

# when the user submits the file, extract the text and JSON output
if file is not None:
    text, json_output = read_text(file)
    st.write('Extracted text:', text)
    st.write('JSON output:', json_output)
