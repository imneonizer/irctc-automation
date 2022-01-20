from PIL import Image
import base64
from io import BytesIO
import requests
import json
import os

class OCR:
    def __init__(self, api_url=None):
        # http://localhost:5000/captcha-solver
        self.api_url = api_url or os.environ.get('OCR_API', "http://localhost:8210/captcha-solver")
    
    def pil_to_bs64(self, image):
        buffered = BytesIO()
        image = image.convert("RGB")
        image.save(buffered, format="jpeg")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def predict(self, pil_image):
        try:
            bs64_image = self.pil_to_bs64(pil_image)
            result = requests.post(self.api_url, data=json.dumps({"image": bs64_image}))
            return self.clean(result.text)
        except:
            return ""
    
    def clean(self, text):
        text = text.replace("Typeintheboxbelow", "")
        text = text.replace(":", "")
        return text.strip()

ocr = OCR()