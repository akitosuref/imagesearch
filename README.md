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

## Cài đặt
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng
```bash
uvicorn app:app --reload
```

## Đóng góp
- Chuẩn hóa tên file theo PEP8.
- Đảm bảo cập nhật requirements.txt khi thêm thư viện mới.
- Viết code rõ ràng, có chú thích.

## Liên hệ
- Tác giả:Vương Quang Quý & Hoàng Cẩm Tú