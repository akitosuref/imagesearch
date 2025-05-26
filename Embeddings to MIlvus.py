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

def process_images(root_folder: str, batch_size: int = 100):
    """Xử lý và chèn ảnh vào Milvus theo batch"""
    
    # Khởi tạo components
    extractor = FeatureExtractor("resnet34")
    client = MilvusClient(uri="example.db")  # Sử dụng Milvus Lite
    
    # Đảm bảo collection tồn tại
    create_collection_if_not_exists(client)
    
    # Batch processing
    batch_data = []
    total_files = 0
    
    # Duyệt qua tất cả file ảnh
    for root, _, files in os.walk(root_folder):
        for filename in tqdm(files, desc=f"Processing {os.path.basename(root)}"):
            # Kiểm tra định dạng file
            if not filename.lower().endswith(('.jpeg', '.jpg', '.png')):
                continue
                
            file_path = os.path.join(root, filename)
            
            try:
                # Trích xuất embedding
                embedding = extractor(file_path)
                
                # Validate embedding
                if embedding.shape[0] != 512:
                    logging.warning(f"Vector không hợp lệ: {file_path}")
                    continue
                
               
                # Thêm vào batch
                batch_data.append({
                    "vector": embedding,
                    "filename": os.path.relpath(file_path, ".").lstrip("./")
                })

                
                # Chèn khi đủ batch size
                if len(batch_data) >= batch_size:
                    client.insert("image_embeddings", batch_data)
                    total_files += len(batch_data)
                    batch_data.clear()
                    logging.info(f"Đã chèn {total_files} files")
                    
            except Exception as e:
                logging.error(f"Lỗi xử lý {file_path}: {str(e)}")
                continue
            
    
    # Chèn phần dữ liệu còn lại
    if batch_data:
        client.insert("image_embeddings", batch_data)
        total_files += len(batch_data)
        logging.info(f"Hoàn thành! Tổng file đã xử lý: {total_files}")

if __name__ == "__main__":
    # Xử lý tất cả thư mục
    folders = [
        "./exception",
        "./object", 
        "./test",
        "./train"
    ]
    
    for folder in folders:
        if os.path.exists(folder):
            logging.info(f"Bắt đầu xử lý thư mục: {folder}")
            process_images(folder)
        else:
            logging.warning(f"Thư mục không tồn tại: {folder}")