from PIL import Image
import base64
from io import BytesIO
import requests
import json
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="image path", default="captcha.png", required=False)
ap.add_argument("-p", "--port", help="api port", default="5000", required=False)
args = ap.parse_args()

def pil_to_bs64(image):
    buffered = BytesIO()
    image = image.convert("RGB")
    image.save(buffered, format="jpeg")
    return base64.b64encode(buffered.getvalue()).decode()

pil_image = Image.open(args.image)
bs64_image = pil_to_bs64(pil_image)

result = requests.post("http://localhost:{}/captcha-solver".format(args.port), data=json.dumps({"image": bs64_image}))
print(result.text)