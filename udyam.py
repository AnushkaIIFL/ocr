import openai
import os
from googletrans import Translator
from dotenv import load_dotenv
from flask import Flask, request, Blueprint
import json
import sys
from logger import logger_msg

# sys.path.append('..') 
# from document_ocr import extract_text
from ocr import extract_text
load_dotenv()

udyam = Blueprint('udyam', __name__)
# app = Flask(__name__)

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"
openai.api_version = "2023-05-15"

translator = Translator()


deployment_name = os.getenv("DEPLOYMENT2")

def translate_ocr(extracted_text,lang="eng"):
    
    prompt = f"""The given data is from udyam aadhar a business document. 
     
       {extracted_text}, 
       
       Please analyze the data and extract only the following fields in key:value pair (JSON format)
       

     -UDYAM REGISTRATION NUMBER
     -NAME OF ENTERPRISE
     -TYPE OF ENTERPRISE
     -SOCIAL CATEGORY OF ENTERPRENEUR
     -DATE OF INCORPORATION/ REGISTRATION OF ENTERPRISE
     -DATE OF COMMENCEMENT OF PRODUCTION/BUSINESS
     -DATE OF UDYAM REGISTRATION
     -NATIONAL INDUSTRY CLASIFICATION CODE(s) #nic(s) 2 digit code with activity, #nic(s) 4 digit code with activity, #nic(s) 5 digit code with activity, #and Activity
     -PIN CODE

     If value is not available please return NOT AVAILABLE
    """	

      	


    completion = openai.ChatCompletion.create(
        engine=deployment_name,
        temperature=0.2,
        messages=[{ "role": "user", "content": prompt}],
        max_tokens=500
      )
    answer=completion.choices[0].message.content
    return answer



@udyam.route('/api/udyam/upload', methods=["POST"])
def udyam_ocr():
    logger_msg("Inside udyam_ocr")
    try:
        file = request.files["file"]
        # lang = request.form['lang']
        # print("lang = ",lang)
        file_name = file.filename
        logger_msg(f"File name: {file_name}")
        extracted_text=extract_text(file,file_name,lang="eng")
        logger_msg("Text is extracted")
        # logger_msg(f"Extracted Text: {extracted_text}")
        response=translate_ocr(extracted_text,lang="eng")
        logger_msg(f"Response from gpt: {response}")
        
    
    
        if response:
            json_data = json.loads(response)
            return json_data
        else :
            return ("Invalid output format")
    except Exception as e:
         logger_msg(f"Error in udyam_ocr: {str(e)}")
# if __name__ == '__main__':
#     app.run(debug=True)

