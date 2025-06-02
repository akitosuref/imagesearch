---
title: "📚 Báo cáo Giữa Kỳ: Ứng dụng phân tán với Milvus – Tìm kiếm sản phẩm tương tự"
date: "2025-06-02"
updated: "2025-06-02"
categories:
  - "distributed-system"
  - "milvus"
  - "fastapi"
  - "docker"
coverImage: "https://thafd.bing.com/th/id/OIP.tt7SLo-YeIPvOzQRuKh38gAAAA?rs=1&pid=ImgDetMain"
coverWidth: 16
coverHeight: 9
excerpt: Tổng quan, mục tiêu, kiến trúc và kế hoạch triển khai hệ thống tìm kiếm sản phẩm tương tự sử dụng Milvus, FastAPI, Docker, AI.
---

### 📚 Tổng quan & Mục tiêu Dự án

#### 💡 Mục đích của hệ thống
Xây dựng hệ thống tìm kiếm sản phẩm tương tự dựa trên ảnh, ứng dụng Milvus (vector database), FastAPI, Docker, AI. Hệ thống cho phép upload ảnh, trích xuất đặc trưng, lưu trữ và tìm kiếm ảnh tương tự trong tập dữ liệu lớn.

---

### 🏗️ Giải thích các thành phần chính trong hệ thống

#### 1. Máy chủ ứng dụng (FastAPI)
- **Vai trò:** Nhận yêu cầu từ người dùng (upload ảnh, tìm kiếm), trích xuất đặc trưng ảnh, truy vấn Milvus, trả về kết quả.
- **Cách hoạt động:** Khi người dùng upload ảnh, FastAPI sử dụng mô hình ResNet34 để trích xuất vector đặc trưng, sau đó gửi truy vấn tìm kiếm đến Milvus để lấy các ảnh tương tự nhất.

#### 2. Cơ sở dữ liệu vector (Milvus Lite)
- **Vai trò:** Lưu trữ các vector đặc trưng của ảnh và tên file ảnh.
- **Cách hoạt động:** Khi nhận truy vấn từ FastAPI, Milvus sử dụng thuật toán Approximate Nearest Neighbor (ANN) với metric cosine similarity để tìm ra các vector gần nhất trong không gian vector.
- **Replication:** Nếu dùng Milvus cluster (project hiện tại dùng Milvus Lite), dữ liệu sẽ được sao chép giữa các node theo cấu hình `MILVUS_REPLICA_NUMBER`. Khi một node gặp sự cố, node khác vẫn giữ dữ liệu mới nhất.
- **Sharding:** Trong [`MilvusCollection.py`](MilvusCollection.py:1), có cấu hình sharding theo trường `uploader` (partition_key_field). Nếu triển khai cluster, dữ liệu sẽ được phân chia giữa các node dựa trên giá trị trường này, giúp tăng khả năng mở rộng và tối ưu truy vấn.

#### 3. Reverse Proxy & Load Balancer (Nginx)
- **Vai trò:** Phân phối đều các request từ client đến nhiều instance FastAPI, đảm bảo hệ thống chịu tải tốt và sẵn sàng cao.
- **Cách hoạt động:** Nginx nhận request HTTP từ người dùng, chuyển tiếp đến một trong các container FastAPI (fastapi1, fastapi2, fastapi3) theo thuật toán round-robin.

#### 4. Docker Compose & Multi-container
- **Vai trò:** Quản lý vòng đời các service (FastAPI, Milvus, Nginx, MinIO, Etcd), hỗ trợ mở rộng, tự động khởi động lại khi lỗi.
- **Cách hoạt động:** Chỉ cần một lệnh `docker-compose up`, toàn bộ hệ thống sẽ được khởi động đồng bộ, các service liên kết với nhau qua mạng nội bộ Docker.

#### 5. Giao diện người dùng (HTML/Jinja2)
- **Vai trò:** Cho phép người dùng upload ảnh, xem kết quả tìm kiếm trực quan.
- **Cách hoạt động:** Khi người dùng upload ảnh, giao diện gửi request đến API `/search`, nhận kết quả và hiển thị các ảnh tương tự.

#### 6. Kiểm thử tải (stress_test.sh)
- **Vai trò:** Mô phỏng nhiều client gửi request đồng thời để kiểm tra khả năng chịu tải của hệ thống.
- **Cách hoạt động:** Script chạy nhiều tiến trình, mỗi tiến trình gửi nhiều request upload ảnh đến API `/search` qua Nginx.

---

### 🔗 Giao thức giao tiếp giữa các thành phần

- **HTTP/REST:** Giao tiếp giữa client (trình duyệt) và FastAPI, giữa Nginx và các node FastAPI đều dùng HTTP.
- **gRPC/Thư viện nội bộ:** Milvus Lite được truy cập qua thư viện Python, không dùng giao thức mạng ngoài (nếu dùng Milvus cluster sẽ dùng gRPC).
- **Docker network:** Các container giao tiếp nội bộ qua mạng Docker.

---

### ⚙️ Logic hoạt động & thuật toán

- **Trích xuất đặc trưng:** Sử dụng ResNet34 pretrained (timm, torch), ảnh được chuyển thành vector 512 chiều, chuẩn hóa L2.
- **Tìm kiếm gần đúng (ANN):** Milvus sử dụng thuật toán Approximate Nearest Neighbor (ANN) với cosine similarity để tìm top-k vector gần nhất.
- **Replication:** Nếu dùng cluster, Milvus sẽ đồng bộ dữ liệu giữa các node replica. Khi ghi dữ liệu, node primary sẽ gửi bản sao đến các node replica, đảm bảo tính nhất quán và sẵn sàng.
- **Sharding:** Nếu bật partition_key_field, dữ liệu sẽ được chia nhỏ giữa các node dựa trên giá trị trường này (ví dụ uploader), giúp cân bằng tải lưu trữ và truy vấn.
- **Load balancing:** Nginx sử dụng thuật toán round-robin để phân phối request đến các node FastAPI.

---

### 🧰 Thư viện sử dụng trong project

| Thư viện        | Mục đích sử dụng                                    |
| --------------- | --------------------------------------------------- |
| `milvus`        | Lưu trữ và tìm kiếm vector nhanh chóng              |
| `torch`         | Trích đặc trưng ảnh bằng mô hình ResNet             |
| `timm`          | Tiện ích mô hình pretrained cho trích xuất ảnh      |
| `fastapi`       | Xây dựng API tìm kiếm, upload ảnh                   |
| `docker`        | Đóng gói, triển khai hệ thống phân tán              |
| `nginx`         | Reverse proxy, cân bằng tải                         |
| `jinja2`        | Template cho giao diện web                          |
| `requests`      | Giao tiếp HTTP nội bộ giữa các node                 |

---

### 🚫 Những thành phần KHÔNG có trong project

- Không có xử lý mô tả văn bản, không có vector hóa văn bản (TF-IDF, Word2Vec)
- Không có Flask, flask-jsonrpc, pika, kombu, aio-pika, message queue, RPC
- Không có hệ thống gợi ý dựa trên nhiều thuộc tính (chỉ dựa vào ảnh)
- Không có clustering nâng cao, không có retry logic tự động

---

### 📝 Kết luận

Dự án đã vận dụng thành công các nguyên lý của hệ thống phân tán: mở rộng linh hoạt, chịu lỗi, sẵn sàng cao, đảm bảo nhất quán dữ liệu và trải nghiệm người dùng liền mạch. Các thành phần như Milvus, FastAPI, Nginx, Docker Compose phối hợp chặt chẽ, minh họa rõ nét cho kiến trúc ứng dụng phân tán hiện đại.

**Tác giả:** Vương Quang Quý & Hoàng Cẩm Tú  

