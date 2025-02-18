FROM python:3.10

WORKDIR /document_loader

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python","document_service.py"]
