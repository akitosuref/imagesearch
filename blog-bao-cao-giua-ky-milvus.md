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

### 🏗️ Tổng quan kiến trúc & thành phần dự án

#### 1. Kiến trúc tổng thể

- **Milvus Lite**: Vector database lưu trữ embedding ảnh, hỗ trợ tìm kiếm gần đúng (ANN) với cosine similarity.
- **FastAPI**: API server xử lý upload, tìm kiếm ảnh, log, health check.
- **Nginx**: Reverse proxy, cân bằng tải giữa nhiều node FastAPI.
- **Docker Compose**: Quản lý toàn bộ vòng đời service, hỗ trợ mở rộng, chịu lỗi, triển khai đa máy.
- **MinIO & Etcd**: Lưu trữ đối tượng và quản lý cluster cho Milvus (cấu hình sẵn, nhưng project dùng Milvus Lite).

#### 2. Pipeline xử lý dữ liệu

- **Trích xuất đặc trưng ảnh**:  
  Sử dụng [`FeatureExtractor.py`](FeatureExtractor.py:1) với mô hình ResNet34 (timm, torch), ảnh được chuyển thành vector 512 chiều, chuẩn hóa L2.
- **Nạp dữ liệu vào Milvus**:  
  Script [`embeddings_to_milvus.py`](embeddings_to_milvus.py:1) duyệt thư mục ảnh, trích xuất vector và insert vào Milvus theo batch.
- **Lưu trữ & truy vấn vector**:  
  Milvus lưu vector, tên file, hỗ trợ sharding theo uploader ([`MilvusCollection.py`](MilvusCollection.py:1)). API `/search` nhận ảnh upload, truy vấn top-10 ảnh gần nhất theo cosine similarity.
- **Giao diện người dùng**:  
  Giao diện web hiện đại ([`templates/index.html`](templates/index.html:1)), upload ảnh, xem kết quả trực quan.

#### 3. Kiểm thử tải & khả năng chịu lỗi

- Script [`stress_test.sh`](stress_test.sh:1) mô phỏng nhiều client gửi request đồng thời đến API `/search` qua Nginx.
- FastAPI ghi log chi tiết, có endpoint `/log` để xem nhanh log hệ thống.
- Docker Compose cấu hình `restart: always`, các service tự động khởi động lại khi gặp sự cố.

#### 4. Cân bằng tải, mở rộng & tính sẵn sàng

- Nginx reverse proxy ([`nginx.conf`](nginx.conf:1)) cân bằng tải giữa các node FastAPI.
- Milvus bật cluster, replication (`MILVUS_CLUSTER_ENABLED=true`, `MILVUS_REPLICA_NUMBER=2`), leader election với etcd (cấu hình sẵn, project thực tế dùng Milvus Lite).
- Hệ thống hỗ trợ triển khai đa máy vật lý qua Docker network overlay.

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

### 🚀 Ứng dụng thực tế của hệ thống

- 🔍 Tìm kiếm sản phẩm tương tự dựa trên ảnh


---

### 🔎 Đánh giá tiêu chí hệ thống phân tán

- **Scalability:** Thêm nhiều node FastAPI, Milvus dễ dàng qua Docker Compose.
- **Fault Tolerance:** Milvus replication (nếu dùng cluster), nhiều instance FastAPI, Nginx tự động chuyển request khi node lỗi.
- **Availability:** Nginx reverse proxy đảm bảo dịch vụ luôn online, Docker tự động restart container khi lỗi.
- **Transparency:** Người dùng chỉ tương tác qua API/giao diện web, không cần biết bên dưới có bao nhiêu node.
- **Concurrency & Parallelism:** FastAPI xử lý đồng thời nhiều request, script stress test mô phỏng nhiều client truy cập cùng lúc.
- **Replication:** Milvus cluster đồng bộ dữ liệu giữa các node (nếu dùng cluster), đảm bảo không mất mát khi một node gặp sự cố.
- **Load Balancer:** Nginx phân phối đều request đến các node FastAPI.
- **Leader Election:** Milvus sử dụng etcd để tự động bầu chọn leader (nếu dùng cluster).

---

### 📝 Kết luận

Dự án đã vận dụng thành công các nguyên lý của hệ thống phân tán: mở rộng linh hoạt, chịu lỗi, sẵn sàng cao, đảm bảo nhất quán dữ liệu và trải nghiệm người dùng liền mạch. Các thành phần như Milvus, FastAPI, Nginx, Docker Compose phối hợp chặt chẽ, minh họa rõ nét cho kiến trúc ứng dụng phân tán hiện đại.

**Tác giả:** Vương Quang Quý & Hoàng Cẩm Tú  
