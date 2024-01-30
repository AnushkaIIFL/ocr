import os
import json
from dotenv import load_dotenv
from flask import Blueprint, Flask, request
from googletrans import Translator
import openai
from ocr import extract_text
from logger import logger_msg

load_dotenv()

udyam = Blueprint('udyam', __name__)

openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_type = "azure"
openai.api_version = "2023-05-15"

translator = Translator()

deployment_name = os.getenv("DEPLOYMENT2")

def translate_ocr(prompt):
    completion = openai.ChatCompletion.create(
        engine=deployment_name,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return completion.choices[0].message.content

@udyam.route('/api/udyam/upload', methods=["POST"])
def udyam_ocr():
    logger_msg("Inside udyam_ocr")
    try:
        file = request.files["file"]
        file_name = file.filename
        if not file_name:
            logger_msg("No document sent in API")
            return {"error": "No document sent in API"}, 409
        logger_msg(f"File name: {file_name}")

        extracted_text = extract_text(file, file_name, lang="eng")
        analyze_data = f"""The given data is supposed to be from udyam aadhar a business document. 

{extracted_text}, 
        
Please analyze the data and extract only the following fields in key:value pair (JSON format)
- udyam_registration_number
- name_of_enterprise
- type_of_enterprise
- social_category_of_enterpreneur
- date_of_incorporation_registration_of_enterprise
- date_of_commencement_of_production_business
- date_of_udyam_registration
- national_industry_clasification_codes #nic(s) 2 digit code with activity, #nic(s) 4 digit code with activity, #nic(s) 5 digit code with activity, #and Activity
- pin_code

If value is not available please return NOT AVAILABLE
"""

        if "error" in extracted_text:
            return extracted_text, 409

        logger_msg("Text is extracted")
        # logger_msg(f"Extracted Text: {extracted_text}")
        response = translate_ocr(analyze_data)
        logger_msg(f"Response from GPT: {response}")

        json_data = json.loads(response)
        if json_data["udyam_registration_number"] == "NOT AVAILABLE":
            logger_msg("Document uploaded is not a udyam aadhar document")
            return {"error": "Please check if the document uploaded is UDYAM"}, 409

        return json_data, 200
    except Exception as e:
        logger_msg(f"Error in udyam_ocr: {str(e)}")
        return {"error": str(e)}, 500
