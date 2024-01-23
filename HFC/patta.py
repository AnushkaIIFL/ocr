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

patta = Blueprint('patta', __name__)

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"
openai.api_version = "2023-05-15"

translator = Translator()


deployment_name = os.getenv("DEPLOYMENT2")

deployment_name = os.getenv("DEPLOYMENT2")
def is_english(text):
    return all(ord(char) < 128 for char in text)

def translate_ocr(extracted_text,lang):
    
    # prompt = f"""this data is from patta document (land ownership related document): {extracted_text}. Analyze the data Then from the text extract appropriate values for  following fields in english and answer in key:value pair format for eg.(key1:value1\nkey2:value2)  *****************IN JSON FORMAT***********:
    # - Name of the land owner, name of his/her mother/father/husband and residential address.
    # - Patta no.
    # - Boundaries
    # - Property Address 
    # - Property Area
    # - District
    # - Tehsildaar
    # If any value in {lang} languge please translate or transliterate it into english"""
    prompt = f"""Extracted data from the land ownership document Patta:

    The data provided has been extracted using OCR. Due to the document's structure and the likelihood of data being in a columnar format, the sentences may not be complete. OCR tends to read data row-wise, so it's essential to differentiate and map the sentences/data accordingly. 

    {extracted_text}

    Please analyze the given data and extract only the following fields in English in key:value pair format (JSON FORMAT):
        - In Favour of  [Note: This is the name of the person holding this document or on whose behalf the document is held]
        - By 
        - Registration/Reference No. 
        - Date of document in DD/MM/YYYY format 
    If any field is not present then you can set "NOT AVAILABLE" as a value for that field
  
    If any word is in {lang} language , please translate or transliterate it into English."""

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

@patta.route('/api/patta_upload', methods=["POST"])
def ror_ocr():
    file = request.files["file"]
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
  

#   - Name of the land owner, name of his/her mother/father/husband and residential address.
#     - Patta no.
#     - Boundaries
#     - Property Address 
#     - Property Area
#     - District
#     - Tehsildaar
