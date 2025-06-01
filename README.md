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
## Khả năng chịu lỗi (Fault Tolerance)

- **Milvus**: Đã bật chế độ cluster và replication (`MILVUS_CLUSTER_ENABLED=true`, `MILVUS_REPLICA_NUMBER=2`) trong `docker-compose.yml`. Nếu một node Milvus gặp sự cố, dữ liệu vẫn còn trên node khác.
- **FastAPI**: Chạy nhiều instance FastAPI (`fastapi1`, `fastapi2`). Nếu một container chết, container còn lại vẫn phục vụ được.
- **Nginx**: Đóng vai trò reverse proxy, phân phối request đến các instance FastAPI, đảm bảo tính sẵn sàng cao.

**Lưu ý:**  
- Để kiểm tra hoặc thay đổi số lượng replica của Milvus, chỉnh sửa biến môi trường `MILVUS_REPLICA_NUMBER` trong file `docker-compose.yml`.
- Có thể mở rộng thêm instance FastAPI bằng cách khai báo thêm service tương tự trong `docker-compose.yml`.



## Liên hệ
- Tác giả:Vương Quang Quý & Hoàng Cẩm Tú