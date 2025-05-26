import os
import logging
from tqdm import tqdm
from FeatureExtractor import FeatureExtractor
from pymilvus import MilvusClient
from fastapi import FastAPI, UploadFile, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

import tempfile

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('embedding.log'), logging.StreamHandler()]
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/train", StaticFiles(directory="./images/train"), name="train")

MILVUS_URI = "example.db"  # Sử dụng Milvus Lite

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
            raise  # Re-raise ngoại lệ để ngăn ứng dụng chạy với kết nối bị lỗi
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
    total_files = 0

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

                batch_data.append({
                    "vector": embedding,
                    "filename": os.path.relpath(file_path, ".")
                })
                rel_path = os.path.relpath(file_path, start=".")
                if not rel_path.startswith("images/"):
                    rel_path = os.path.join("images", os.path.basename(file_path))

                batch_data.append({"vector": embedding, "filename": rel_path})


                if len(batch_data) >= batch_size:
                    client.insert("image_embeddings", batch_data)
                    total_files += len(batch_data)
                    batch_data.clear()
                    logging.info(f"Đã chèn {total_files} ảnh")

            except Exception as e:
                logging.error(f"Lỗi xử lý {file_path}: {str(e)}")

    if batch_data:
        client.insert("image_embeddings", batch_data)
        total_files += len(batch_data)
        logging.info(f"Đã chèn {total_files} ảnh còn lại")
  



@app.post("/search")
async def search_image(file: UploadFile):
    """
    Xử lý các yêu cầu tìm kiếm ảnh.
    """
    client = get_milvus_client()
    extractor = FeatureExtractor("resnet34")

    # Sử dụng trình quản lý ngữ cảnh để xử lý tệp tạm thời
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        try:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name  # Lấy tên *trước khi* nó bị đóng

            embedding = extractor(tmp_path)
            results = client.search(
                collection_name="image_embeddings",
                data=[embedding],
                output_fields=["filename"],
                limit=10
            )

            valid_results = [
                hit.entity.get("filename")
                for hit in results[0]
                if hit.entity.get("filename") and os.path.exists(hit.entity.get("filename")) # Kiểm tra xem file có tồn tại không
            ]
            return {"results": valid_results}
        except Exception as e:
            logging.error(f"Lỗi trong quá trình tìm kiếm: {e}")
            return {"error": str(e)}, 500  # Trả về phản hồi lỗi phù hợp
        finally:
            # Đảm bảo tệp tạm thời bị xóa *sau khi* chúng ta dùng xong
            os.unlink(tmp_path)

@app.get("/")
async def main(request: Request):
    """
    Xử lý yêu cầu trang chính.
    """
    return templates.TemplateResponse("index.html", {"request": request})

def create_milvus_collection():
    raise NotImplementedError

def initialize_milvus():
    try:
        create_milvus_collection()  # Tạo collection nếu cần
    except Exception as e:
        logging.critical(f"Không thể khởi tạo Milvus: {e}")
        raise
    
if __name__ == "__main__":
    import uvicorn
    # Khởi động Milvus trước khi ứng dụng FastAPI bắt đầu
    initialize_milvus()
    
    # Start the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
