FROM python:3.7-buster
WORKDIR /app
COPY . .

RUN pip install -r /app/requirements.txt --no-cache-dir
RUN apt update -y && apt install -y libgl1-mesa-glx

# download paddleocr models
RUN python -c "from paddleocr import PaddleOCR; PaddleOCR(use_angle_cls=False, lang='en')"

CMD chmod +x /app/entrypoint.sh && /app/entrypoint.sh