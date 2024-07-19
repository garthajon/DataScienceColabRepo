FROM python:3.12

EXPOSE 8082

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["streamlit", "run", "team106.py", "--server.port=8082", "--server.address=0.0.0.0"]
