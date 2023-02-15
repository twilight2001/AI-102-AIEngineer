from dotenv import load_dotenv
import os
import time
from PIL import Image, ImageDraw 
from glob import glob
from os import path
import streamlit as st

# Import namespaces
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials


def main():

    st.title("Azure Read API OCR")

    global cv_client

    try:
        # Get Configuration Settings
        load_dotenv()
        cog_endpoint = os.getenv('COG_SERVICE_ENDPOINT')
        cog_key = os.getenv('COG_SERVICE_KEY')


    # Authenticate Computer Vision client
        credential = CognitiveServicesCredentials(cog_key)
        cv_client = ComputerVisionClient(cog_endpoint, credential)

        # Menu for text reading functions
        # Get the file path
        image_file = st.text_input("Enter the filename (including extension) of the image or PDF to read: ")
        image_file = os.path.join('.\images',image_file)
        GetTextRead(image_file)
        
    except Exception as ex:
        print(ex)

def GetTextRead(image_file):
    st.write('Extracting text in {}\n'.format(image_file))
    # Use Read API to read text in image
    with open(image_file, mode="rb") as image_data:
        read_op = cv_client.read_in_stream(image_data, raw=True)

        # Get the async operation ID so we can check for the results
        operation_location = read_op.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]

    # Wait for the asynchronous operation to complete
    while True:
        read_results = cv_client.get_read_result(operation_id)
        if read_results.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
            break
        time.sleep(1)

    # If the operation was successfully, process the text line by line
    if read_results.status == OperationStatusCodes.succeeded:
        for page in read_results.analyze_result.read_results:
            for line in page.lines:
                st.write(line.text)
                # Uncomment the following line if you'd like to see the bounding box 
                # print(line.bounding_box
     
if __name__ == "__main__":
    main()