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


# function to read text from an image file
def ocr_image(file, endpoint, subscription_key):
    image = Image.open(file)
    image_data = image.tobytes()

    response = requests.post(
        url=endpoint + "/vision/v3.1-preview.3/read/analyze",
        headers={
            "Ocp-Apim-Subscription-Key": subscription_key,
            "Content-Type": "application/octet-stream"
        },
        data=image_data
    )

    operation_url = response.headers["Operation-Location"]
    operation_id = operation_url.split("/")[-1]

    # check the read operation status
    while True:
        response = requests.get(
            url=operation_url,
            headers={"Ocp-Apim-Subscription-Key": subscription_key}
        )
        status = response.json()["status"]
        if status == "succeeded":
            break
        elif status == "failed":
            st.error("OCR operation failed")
            return

    # extract the text from the result
    result = response.json()
    text = ""
    for line in result["analyzeResult"]["readResults"][0]["lines"]:
        text += line["text"] + " "
    return text

# function to read text from a PDF file
def ocr_pdf(file, endpoint, subscription_key):
    with open(file, 'rb') as pdf_file:
        pdf_bytes = pdf_file.read()

    response = requests.post(
        url=endpoint + "/vision/v3.1-preview.3/read/analyze",
        headers={
            "Ocp-Apim-Subscription-Key": subscription_key,
            "Content-Type": "application/pdf"
        },
        data=pdf_bytes
    )

    operation_url = response.headers["Operation-Location"]
    operation_id = operation_url.split("/")[-1]

    # check the read operation status
    while True:
        response = requests.get(
            url=operation_url,
            headers={"Ocp-Apim-Subscription-Key": subscription_key}
        )
        status = response.json()["status"]
        if status == "succeeded":
            break
        elif status == "failed":
            st.error("OCR operation failed")
            return

    # extract the text from the result
    result = response.json()
    text = ""
    for page in result["analyzeResult"]["readResults"]:
        for line in page["lines"]:
            text += line["text"] + " "
    return text

# create a file uploader for the user to select an image or PDF
file = st.file_uploader("Upload file", type=["jpg", "jpeg", "png", "pdf"])

# if a file has been uploaded
if file is not None:
    # if the file is an image
    if file.type.split("/")[0] == "image":
        # read the text from the image
        text = ocr_image(file, endpoint, subscription_key)
    # if the file is a PDF
    elif file.type == "application/pdf":
        # read the text from the PDF
        text = ocr_pdf(file, endpoint, subscription_key)
    # if the file is of an unsupported type
    else:
        st.error("Unsupported file type")
        text = ""

    # display the text
    st.write(text)
