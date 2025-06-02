# Milvus Image Search Project

## Mô tả
Ứng dụng tìm kiếm ảnh sử dụng Milvus, FastAPI và các mô hình trích xuất đặc trưng ảnh.

## Cấu trúc thư mục
- `app.py`: API chính (FastAPI)
- `FeatureExtractor.py`: Trích xuất đặc trưng ảnh
- `MilvusCollection.py`: Quản lý kết nối và thao tác với Milvus
- `embeddings_to_milvus.py`: Đưa vector nhúng vào Milvus
- `stress_test.sh`: Script kiểm thử hiệu năng
- `images/`: Thư mục chứa ảnh mẫu
- `templates/`: Giao diện web (HTML)
- `requirements.txt`: Danh sách thư viện Python cần thiết

## Hướng dẫn thêm dữ liệu train

Để thêm nhanh toàn bộ dữ liệu train cho các tập train1; train2 và train3, sử dụng lệnh sau trong terminal:
```bash
cp -r images/train images/train2
cp -r images/train images/train2 && cp -r images/train images/train3
```
Lệnh này sẽ sao chép toàn bộ thư mục `images/train` sang `images/train1` ;`images/train2` và `images/train3`.

## Cài đặt các thư viện cần thiết 
```bash
pip install -r requirements.txt
```
## Chạy file embeddings_to_milvus.py 
```bash
python3 embedding_to_milvus.py

```
## Chạy ứng dụng
```bash
uvicorn app:app --reload
```

## Chạy bằng Docker

**Lưu ý:**
Trước khi chạy Docker, bạn cần chạy lệnh embedding để nạp dữ liệu vào Milvus:
```bash
python3 embeddings_to_milvus.py
```

```bash
# Build và khởi động toàn bộ hệ thống (Milvus, FastAPI, Nginx)
docker-compose up --build

# Nếu muốn chạy nền 
docker-compose up -d

# Kiểm tra trạng thái các container
docker-compose ps

# Dừng toàn bộ hệ thống
docker-compose down
```
## Khả năng chịu lỗi (Fault Tolerance)

- **Milvus**: Đã bật chế độ cluster và replication (`MILVUS_CLUSTER_ENABLED=true`, `MILVUS_REPLICA_NUMBER=2`) trong `docker-compose.yml`. Nếu một node Milvus gặp sự cố, dữ liệu vẫn còn trên node khác.
- **FastAPI**: Chạy nhiều instance FastAPI (`fastapi1`, `fastapi2`). Nếu một container chết, container còn lại vẫn phục vụ được.
- **Nginx**: Đóng vai trò reverse proxy, phân phối request đến các instance FastAPI, đảm bảo tính sẵn sàng cao.

**Lưu ý:**  
- Để kiểm tra hoặc thay đổi số lượng replica của Milvus, chỉnh sửa biến môi trường `MILVUS_REPLICA_NUMBER` trong file `docker-compose.yml`.
- Có thể mở rộng thêm instance FastAPI bằng cách khai báo thêm service tương tự trong `docker-compose.yml`.



## Liên hệ
- Tác giả:Vương Quang Quý & Hoàng Cẩm Tú