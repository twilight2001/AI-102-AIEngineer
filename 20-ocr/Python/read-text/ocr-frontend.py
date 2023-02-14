import os
import requests
from dotenv import load_dotenv
import streamlit as st
# Import namespaces
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

# Define global configuration for the Streamlit app
st.set_page_config(page_title="OCR App", page_icon=":pencil2:", layout="wide")

load_dotenv()
cog_endpoint = os.getenv('COG_SERVICE_ENDPOINT')
cog_key = os.getenv('COG_SERVICE_KEY')

# Authenticate Computer Vision client
credential = CognitiveServicesCredentials(cog_key)
cv_client = ComputerVisionClient(cog_endpoint, credential)

ocr_url = cog_endpoint + "vision/v3.0/ocr"

# Define namespace for Streamlit app
namespace = st.sidebar.text_input("Enter a namespace for your analysis")



def process_image(image_path):
    # Set the headers for the REST API call.
    headers = {'Ocp-Apim-Subscription-Key': cog_key, 'Content-Type': 'application/octet-stream'}
    params = {'language': 'unk', 'detectOrientation': 'true'}
    data = open(image_path, 'rb').read()

    # Call the REST API.
    response = requests.post(ocr_url, headers=headers, params=params, data=data)

    # Get the JSON response.
    response_json = response.json()

    # Extract the text from the JSON response.
    extracted_text = ''
    for region in response_json['regions']:
        for line in region['lines']:
            for word in line['words']:
                extracted_text += ' ' + word['text']

    return extracted_text

# Define the Streamlit app
def app():
    st.title("Azure OCR App")
    st.write("Upload an image or PDF to extract text")

    file = st.file_uploader("Choose a file", type=["jpg", "pdf"])
    if file is not None:
        with open(f"{namespace}.pdf", "wb") as f:
            f.write(file.getbuffer())
        st.write("File uploaded successfully!")

        extracted_text = process_image(f"{namespace}.pdf")

        st.write("Extracted Text:")
        st.write(extracted_text)

# Run the Streamlit app
app()
