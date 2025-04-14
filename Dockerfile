FROM jedha/real-time-payments-api-lead-program

COPY . .

# Install pip requirements
RUN pip install -r requirements.txt

CMD gunicorn app:app  --bind 0.0.0.0:$PORT --worker-class uvicorn.workers.UvicornWorker