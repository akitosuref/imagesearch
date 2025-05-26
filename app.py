import os
import logging
import tempfile
from tqdm import tqdm
from FeatureExtractor import FeatureExtractor
from pymilvus import MilvusClient
from fastapi import FastAPI, UploadFile, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('embedding.log'), logging.StreamHandler()]
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/images", StaticFiles(directory="./images"), name="images")

MILVUS_URI = "example.db"
COLLECTION_NAME = "image_embeddings"
IMAGE_FOLDER = "./images"

# ------------------- Milvus -------------------

def get_milvus_client():
    global _milvus_client
    if '_milvus_client' not in globals():
        try:
            _milvus_client = MilvusClient(uri=MILVUS_URI)
        except Exception as e:
            logging.error(f"Lỗi kết nối đến Milvus: {e}")
            raise
    return _milvus_client

def reset_milvus_collection():
    client = get_milvus_client()
    if client.has_collection(COLLECTION_NAME):
        client.drop_collection(COLLECTION_NAME)
        logging.info(f"Đã xóa collection cũ: '{COLLECTION_NAME}'")
    client.create_collection(
        collection_name=COLLECTION_NAME,
        dimension=512,
        auto_id=True,
        vector_field_name="vector",
        metric_type="COSINE"
    )
    logging.info(f"Đã tạo collection Milvus: '{COLLECTION_NAME}'")

# ------------------- Xử lý ảnh -------------------

def process_and_insert_images(folder: str, batch_size: int = 100):
    extractor = FeatureExtractor("resnet34")
    client = get_milvus_client()
    reset_milvus_collection()

    batch_data = []
    total = 0

    for root, _, files in os.walk(folder):
        for filename in tqdm(files, desc=f"Đang xử lý {os.path.basename(root)}"):
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')) or ':' in filename:
                continue

            file_path = os.path.join(root, filename)
            try:
                embedding = extractor(file_path)
                if embedding.shape[0] != 512:
                    logging.warning(f"Vector không hợp lệ: {file_path}")
                    continue

                rel_path = os.path.relpath(file_path, start=".")
                if not rel_path.startswith("images/"):
                    rel_path = os.path.join("images", os.path.basename(file_path))

                batch_data.append({"vector": embedding, "filename": rel_path})

                if len(batch_data) >= batch_size:
                    client.insert(COLLECTION_NAME, batch_data)
                    total += len(batch_data)
                    batch_data.clear()

            except Exception as e:
                logging.error(f"Lỗi khi xử lý {file_path}: {str(e)}")

    if batch_data:
        client.insert(COLLECTION_NAME, batch_data)
        total += len(batch_data)

    logging.info(f"Đã chèn {total} ảnh vào Milvus.")

# ------------------- API -------------------

@app.post("/search")
async def search_image(file: UploadFile):
    client = get_milvus_client()
    extractor = FeatureExtractor("resnet34")

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        try:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

            embedding = extractor(tmp_path)
            results = client.search(
                collection_name=COLLECTION_NAME,
                data=[embedding],
                output_fields=["filename"],
                limit=20
            )

            seen = set()
            very_similar = []
            somewhat_similar = []

            for hit in results[0]:
                fname = hit.entity.get("filename")
                score = hit.score

                if fname and os.path.exists(fname) and fname not in seen:
                    if score > 0.75:
                        very_similar.append(fname)
                    elif score > 0.6:
                        somewhat_similar.append(fname)
                    seen.add(fname)

            return {
                "very_similar": very_similar,
                "somewhat_similar": somewhat_similar
            }

        except Exception as e:
            logging.error(f"Lỗi trong khi tìm kiếm: {e}")
            return {"error": str(e)}, 500
        finally:
            os.unlink(tmp_path)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ------------------- Khởi chạy -------------------

if __name__ == "__main__":
    import uvicorn

    if os.path.exists(IMAGE_FOLDER):
        logging.info(f"Xử lý thư mục: {IMAGE_FOLDER}")
        process_and_insert_images(IMAGE_FOLDER)
    else:
        logging.warning(f"Thư mục không tồn tại: {IMAGE_FOLDER}")

    uvicorn.run(app, host="0.0.0.0", port=8000)
