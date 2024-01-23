import openai
import os
from googletrans import Translator
from dotenv import load_dotenv
from flask import Flask, request, Blueprint
import json
import sys

sys.path.append('..') 
from document_ocr import extract_text
load_dotenv()

ror = Blueprint('ror', __name__)

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"
openai.api_version = "2023-05-15"

translator = Translator()


deployment_name = os.getenv("DEPLOYMENT2")
def is_english(text):
    return all(ord(char) < 128 for char in text)
def translate_ocr(extracted_text,lang):
    
    prompt =  f"""this data is from ROR document (land ownership related document) in '{lang}' language: 

    "{extracted_text}"

    The data provided has been extracted using OCR.Due to the document's structure and sometimes the likelihood of data being in a columnar format, the sentences may not be complete. OCR tends to read data row-wise,so it's essential to consider, understand, differentiate and map the sentences/data accordingly. 

    Please analyze the given data and accurately extract only the following fields in English key:value pair format (JSON FORMAT):
       
    the fields are:
    - Names of document holder(s)
    - Registeration Number
    - Registration Date
    
If any field is not present then you can set "NOT AVAILABLE" as a value for that field


    
   """
    
    completion = openai.ChatCompletion.create(
        engine=deployment_name,
        temperature=0.2,
        messages=[{ "role": "user", "content": prompt}],
        max_tokens=500
      )
    answer=completion.choices[0].message.content
    return answer

def final_call(res,lang):
    
    prompt = f"""The given data is in {lang} language. Please transliterate this data into english and give json format:

    {res}

    """
  


    completion = openai.ChatCompletion.create(
        engine=deployment_name,
        temperature=0.1,
        messages=[{ "role": "user", "content": prompt}],
        max_tokens=500
      )
    answer=completion.choices[0].message.content
    return answer

@ror.route('/api/ror_upload', methods=["POST"])
def ror_ocr():
    file = request.files["file"]
    print("got the file")
    lang = request.form['lang']
    print("lang = ",lang)
    file_name = file.filename
    extracted_text=extract_text(file,file_name,lang)
    print("Extracted Text: ",extracted_text)
    # translated_text = translator.translate(extracted_text, dest='en')
    response=translate_ocr(extracted_text,lang)
    print(response)
    eng_res = is_english(response)
    if not eng_res:
        print(eng_res)
        response = final_call(response,lang)
        print(response)
    try:
        json_data = json.loads(response)
        return json_data
    except :
        return ("Invalid output format")
  
# DATA TO BE EXTRACTED
    # - Type of land portion (survey number/block number)
    # - Plot number (in case of block)
    # - Area
    # - Name of the land owner
    # - Name of his/her mother/father/husband 
    # - Residential address
    # - Each landowner's share
    # - Encumbrance/Charges
    # - Remarks (usually in the last column)