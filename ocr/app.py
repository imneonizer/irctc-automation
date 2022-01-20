from PIL import Image
from io import BytesIO
import base64

import numpy as np
from paddleocr import PaddleOCR
from flask import Flask, request


class OCR:
    def __init__(self):
        self.model = PaddleOCR(use_angle_cls=False, lang='en')

    def predict(self, img):
        if isinstance(img, str):
            img = Image.open(img).convert("RGB")
        
        try:
            return self.model.ocr(np.array(img), rec=True, cls=False, det=False)[0][0].replace(" ", "")
        except:
            return ''

ocr = OCR()
app = Flask("paddleocr")

@app.route("/captcha-solver", methods=["POST"])
def index():
    bs64_image = request.get_json(force=True).get("image")
    pil_image = Image.open(BytesIO(base64.b64decode(bs64_image)))
    return ocr.predict(pil_image)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)