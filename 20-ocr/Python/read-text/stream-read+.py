from dotenv import load_dotenv
import os
import re 
import time
from PIL import Image, ImageDraw 
from glob import glob
from os import path
import streamlit as st
st.set_page_config(layout="wide")

# Import namespaces
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

from dotenv import load_dotenv
import os
import time
from PIL import Image, ImageDraw 
from glob import glob
from os import path
import streamlit as st
#st.set_page_config(layout="wide")

# Import namespaces
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials

def display_results(response): 
    if response.status_code != 200: 
        st.error("Error: {}".format(response.json())) 
        return 
    result = response.json() 
    if len(result["analyzeResult"]["readResults"]) == 0: 
        st.warning("No text found in the image.") 
        return 
    for page in result["analyzeResult"]["readResults"]: 
        st.write("Page No.{}".format(page["page"])) 
        for line in page["lines"]: 
            line = re.sub(r'\d+', '<span style="color:red">{}</span>'.format(r'\g<0>'), line["text"]) # color red before Arabic numbers 
            st.write(line, unsafe_allow_html=True) 
            st.write('<hr style="border: 1px solid red">') # add a colored line 
 

def main(image_file):
    st.write('Extracting text in {}\n'.format(image_file))
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
    page = [] 
    # Use Read API to read text in image
    with open(image_file, mode="rb") as f:
        image_data = f.read()
    try:
        #call API to read binary data
        read_op = cv_client.read_in_stream(image_data, raw=True)
        # Get the operation ID (URL with an ID at the end) from response
        operation_location = read_op.headers["Operation-Location"]
        operation_id = operation_location.split("/")[-1]
        # Wait for the asynchronous operation to complete
        while True:
            read_results = cv_client.get_read_result(operation_id)
            if read_results.status not in [OperationStatusCodes.running, OperationStatusCodes.not_started]:
                break
            time.sleep(1)
        # If the operation was successfully, print detected text line by line
        if read_results.status == OperationStatusCodes.succeeded:
            for page in read_results.analyze_result.read_results:
                for line in page.lines:
                    page.append(line.text)
                    # Uncomment the following line if you'd like to see the bounding box 
                    # print(line.bounding_box
    except Exception as e:
        print("No text detected in the image.\n")
        print(e) 

    display_results(page) 
 


def on_file_upload(): 
    uploaded_file = st.file_uploader("Upload an image file", type=["jpg", "jpeg", "png"]) 

    if uploaded_file is not None: 
        image_file = "temp.jpg" 
        with open(image_file, "wb") as f: 
            f.write(uploaded_file.getbuffer()) 
        # Call main function with image file as argument 
        main(image_file)

    

if __name__ == "__main__":
    st.title("Azure Read API OCR")
    on_file_upload() 