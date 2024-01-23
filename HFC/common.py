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



common = Blueprint('common', __name__)

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"
openai.api_version=os.getenv("AZURE_API_VERSION")

translator = Translator()


deployment_name = os.getenv("DEPLOYMENT2")

def is_english(text):
    return all(ord(char) < 128 for char in text)

def translate_ocr(extracted_text,lang,document):
    

    prompt = f"""
    Extracted text from a {document} document:

    {extracted_text}

    The text above is extracted from a land ownership document using OCR technology. The document could be one of several types, including 7/12, Jamalbandi, Khasra, Khatauni, A Khata, B Khata, Khata Extract, Khata Certificate, Sale Deed, Agreement Deed, or Conveyance Deed. These documents may contain information in a columnar or mixed format and could be in {lang} language.

    Based on the document type and its structure, please analyze the given data and extract the following fields in English in key:value pair format (JSON FORMAT):

    - By: [Party 1: The name of the other party involved in the document, if applicable.]
    - In Favour of: [Party 2: The name(s) of the person(s) holding this document or on whose behalf the document is held. If multiple names are present, list all.]
    - Registration/Reference No.: [The unique number identifying the document.]
    - Date of Document: [The date when the document was created, in DD/MM/YYYY format.]

    Please note:
    - If any field is not present in the document, set "NOT AVAILABLE" as a value for that field.
    - If any word is in {lang} language, translate or transliterate it into English.
`    - Ensure accuracy in capturing names, especially where multiple names are listed.
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

@common.route('/api/ocr/document/upload', methods=["POST"])
def common_ocr():
    print("************************************************************************************")
    file = request.files["file"]
    lang = request.form['lang']
    document = request.form["document"]
    
    print("lang = ",lang)
    file_name = file.filename
    
    extracted_text=extract_text(file,file_name,lang)
    print("Extracted Text: ",extracted_text, "length: ",len(extracted_text))
    if len(extracted_text) > 14000:
        # Split the text into two parts
        half_length = len(extracted_text) // 2
        first_half = extracted_text[:half_length]
        second_half = extracted_text[half_length:]

        # Get responses for each half
        response1 = translate_ocr(first_half, lang)
        response2 = translate_ocr(second_half, lang)

        # Combine the responses into a single JSON object
        data1 = json.loads(response1)
        data2 = json.loads(response2)

        combined_data = {**data1, **data2}  # Merge the dictionaries

        return json.dumps(combined_data)
    # translated_text = translator.translate(extracted_text, dest='en')
    response=translate_ocr(extracted_text,lang,document)
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
  
   
   

