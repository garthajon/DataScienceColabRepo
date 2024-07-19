FROM python:3.12

EXPOSE 8080

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["streamlit", "run", "team106.py", "--server.port=8080", "--server.address=0.0.0.0"]
