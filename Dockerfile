FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
USER 65532:65532
EXPOSE 8765
CMD ["python","app.py"]
