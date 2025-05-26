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
templates = Jinja2Templates(directory="templates") # Đã sửa đường dẫn templates
app.mount("/train", StaticFiles(directory="train"), name="train")
app.mount("/test", StaticFiles(directory="test"), name="test")
app.mount("/object", StaticFiles(directory="object"), name="object")
app.mount("/exception", StaticFiles(directory="exception"), name="exception")
# Chi tiết kết nối Milvus (được chuyển thành hằng số để dễ sửa đổi)
MILVUS_URI = "example.db"  # Sử dụng Milvus Lite

def get_milvus_client():

    global _milvus_client
    if '_milvus_client' not in globals():
        try:
            _milvus_client = MilvusClient(uri=MILVUS_URI)
        except Exception as e:
            logging.error(f"Lỗi kết nối đến Milvus: {e}")
            raise  # Re-raise ngoại lệ để ngăn ứng dụng chạy với kết nối bị lỗi
    return _milvus_client

def create_milvus_collection():
    # """
    # Tạo collection Milvus nếu nó chưa tồn tại.
    # """
    client = get_milvus_client()
    try:
        if not client.has_collection("image_embeddings"):
            client.create_collection(
                collection_name="image_embeddings",
                dimension=512,
                auto_id=True,
                vector_field_name="vector",
                metric_type="COSINE"
            )
            logging.info("Đã tạo collection Milvus: 'image_embeddings'")
        else:
            logging.info("Collection Milvus 'image_embeddings' đã tồn tại.")
    except Exception as e:
        logging.error(f"Lỗi tạo collection Milvus: {e}")
        raise

def process_and_insert_images(root_folder: str, batch_size: int = 100):
    # """
    # Xử lý ảnh từ một thư mục, trích xuất các embedding của chúng và chèn
    # chúng vào Milvus theo lô.
    # """
    extractor = FeatureExtractor("resnet34")
    client = get_milvus_client()
    create_milvus_collection()  # Đảm bảo collection tồn tại

    batch_data = []
    total_files = 0

    for root, _, files in os.walk(root_folder):
        for filename in tqdm(files, desc=f"Đang xử lý {os.path.basename(root)}"):
            if not filename.lower().endswith(('.jpeg', '.jpg', '.png')):
                continue

            file_path = os.path.join(root, filename)
            try:
                embedding = extractor(file_path)
                if embedding.shape[0] != 512:
                    logging.warning(f"Vector không hợp lệ cho {file_path}")
                    continue

                batch_data.append({
                    "vector": embedding,
                    "filename": os.path.relpath(file_path, ".")  # Sửa ở đây
                })

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
    logging.info(f"Đã hoàn thành xử lý ảnh từ {root_folder}. Tổng số ảnh đã xử lý: {total_files}")



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

def initialize_milvus():
    """
    Khởi tạo Milvus. Hàm này được gọi khi ứng dụng khởi động.
    """
    try:
        create_milvus_collection()  # Tạo collection nếu cần
    except Exception as e:
        logging.critical(f"Không thể khởi tạo Milvus: {e}")
        #  Consider sys.exit(1) here if Milvus is critical to the app's operation
        raise  # Re-raise to prevent app from running
    
if __name__ == "__main__":
    import uvicorn
    # Initialize Milvus before starting the FastAPI app
    initialize_milvus()

    # Populate Milvus with embeddings (this should only happen once, not on every app start unless you want to re-index)
    folders_to_process = ["./exception", "./object", "./test", "./train"]  # Correct folder paths
    for folder in folders_to_process:
        if os.path.exists(folder):
            logging.info(f"Processing images from folder: {folder}")
            process_and_insert_images(folder)
        else:
            logging.warning(f"Folder not found: {folder}")
    
    # Start the FastAPI application using uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
