import os
import logging
from tqdm import tqdm
from FeatureExtractor import FeatureExtractor
from pymilvus import MilvusClient, DataType

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('embedding.log'), logging.StreamHandler()]
)

def create_collection_if_not_exists(client: MilvusClient):
    """Tạo collection nếu chưa tồn tại"""
    if not client.has_collection("image_embeddings"):
        client.create_collection(
            collection_name="image_embeddings",
            dimension=512,
            auto_id=True,
            vector_field_name="vector",
            metric_type="COSINE"
        )
        logging.info("Đã tạo collection 'image_embeddings'")

def process_all_images(folders):
    extractor = FeatureExtractor("resnet34")
    client = MilvusClient(uri="example.db")

    # Chỉ xóa collection 1 lần duy nhất
    if client.has_collection("image_embeddings"):
        client.drop_collection("image_embeddings")
        logging.info("Đã xoá collection cũ để tránh trùng lặp.")

    create_collection_if_not_exists(client)
    
    batch_data = []
    total_files = 0

    for folder in folders:
        if not os.path.exists(folder):
            logging.warning(f"Thư mục không tồn tại: {folder}")
            continue
        logging.info(f"Bắt đầu xử lý thư mục: {folder}")
        for root, _, files in os.walk(folder):
            for filename in tqdm(files, desc=f"Processing {os.path.basename(root)}"):
                if not filename.lower().endswith(('.jpeg', '.jpg', '.png')) or ':' in filename.lower():
                    continue

                file_path = os.path.join(root, filename)
                
                try:
                    embedding = extractor(file_path)
                    
                    if embedding.shape[0] != 512:
                        logging.warning(f"Vector không hợp lệ: {file_path}")
                        continue
                    
                    # Thêm vào batch
                    batch_data.append({
                        "vector": embedding,
                        "filename": os.path.relpath(file_path, ".").lstrip("./")
                    })

                except Exception as e:
                    logging.error(f"Lỗi xử lý {file_path}: {str(e)}")
                    continue

    if batch_data:
        # Chia batch_data thành các batch nhỏ 100 ảnh để insert
        batch_size = 100
        for i in range(0, len(batch_data), batch_size):
            batch = batch_data[i:i+batch_size]
            client.insert("image_embeddings", batch)
            total_files += len(batch)
            logging.info(f"Đã chèn {total_files} files")
        logging.info(f"Hoàn thành! Tổng file đã xử lý: {total_files}")

if __name__ == "__main__":
    folders = ["./images", "./images/train", "./images/exception", "./images/object", "./images/test"]
    process_all_images(folders)