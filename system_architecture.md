# 1. Sơ đồ kiến trúc hệ thống

![System Architecture](1.jpg)

---

# 2. Mô tả chi tiết các thành phần

- **User/Web**: Giao diện web cho phép người dùng upload và tìm kiếm ảnh.
- **FastAPI Node(s)**: Máy chủ API xử lý upload, trích xuất đặc trưng, truy vấn Milvus, trả kết quả cho người dùng. Có thể mở rộng nhiều node, giao tiếp qua Docker network.
- **Milvus Lite**: Cơ sở dữ liệu vector lưu trữ embedding ảnh, hỗ trợ truy vấn tương tự.
- **Images Folder**: Lưu trữ file ảnh gốc.
- **Docker Network**: Kết nối các container (FastAPI, Milvus) giúp giao tiếp nội bộ an toàn, hiệu quả.

**Luồng hoạt động:**
1. Người dùng upload/tìm kiếm ảnh qua web/API.
2. FastAPI nhận ảnh, trích xuất vector, lưu/truy vấn Milvus.
3. Milvus trả về kết quả, FastAPI trả kết quả cho người dùng.

---

# 3. Công nghệ và thư viện sử dụng

- **FastAPI**: Xây dựng API hiệu suất cao, dễ mở rộng.
- **Milvus Lite**: Lưu trữ và truy vấn vector ảnh, tối ưu cho tìm kiếm tương tự.
- **Docker Compose**: Quản lý, triển khai các thành phần hệ thống dạng container.
- **Jinja2**: Tạo giao diện web động.
- **pymilvus**: Thư viện Python kết nối Milvus.
- **FeatureExtractor (ResNet34)**: Trích xuất đặc trưng ảnh.
- **tqdm, logging**: Theo dõi tiến trình, ghi log hệ thống.

**Lý do chọn:**  
Các công nghệ đều phổ biến, dễ mở rộng, hỗ trợ tốt cho xử lý ảnh và triển khai phân tán.

---

# 4. Mô hình dữ liệu (Database Model)

- **Collection:** `image_embeddings`
  - `id` (auto_id)
  - `vector` (float[512])
  - `filename` (string): Đường dẫn ảnh gốc

---

# 5. Chiến lược triển khai và cấu hình hệ thống

- **Triển khai:** Sử dụng Docker Compose để chạy các container FastAPI, Milvus, đảm bảo dễ mở rộng và quản lý.
- **Cấu hình:**  
  - Mỗi node FastAPI có thể giao tiếp với node khác qua Docker network.
  - Milvus Lite lưu trữ dữ liệu cục bộ, có thể mở rộng sang Milvus cluster nếu cần.
  - Thư mục ảnh mount vào container để chia sẻ dữ liệu.
- **Sharding/Replication:**  
  - Hiện tại hệ thống chưa phân mảnh (sharding) hoặc sao chép (replication) dữ liệu. Nếu mở rộng, có thể dùng sharding theo hash filename hoặc replication giữa các node Milvus.

---