FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY FeatureExtractor.py .
COPY MilvusCollection.py .
COPY embeddings_to_milvus.py .
COPY templates/ ./templates/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]