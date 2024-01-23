from flask import Flask
from HFC.deed import deed
from HFC.patta import patta
from HFC.ror import ror
from HFC.common import common
from udyam import udyam
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    
    return "HFC OCR"
# app.register_blueprint(deed)
# app.register_blueprint(patta)
# app.register_blueprint(ror)
# app.register_blueprint(common)
app.register_blueprint(udyam)
if __name__ == '__main__':
    app.run(debug=True)
    