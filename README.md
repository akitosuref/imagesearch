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

## Chạy stress_test.sh trên Docker
 chạy stress test bằng lệnh:

```bash
docker run --rm -it -v "$(pwd)":/app -w /app python:3 bash stress_test.sh
```

Script sẽ truy cập được file ảnh mẫu trong thư mục project khi chạy trong container.
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
## Đánh giá các tiêu chí hệ thống phân tán

1. **Fault Tolerance**  
   - Milvus bật replication (`MILVUS_REPLICA_NUMBER=2`) trong [`docker-compose.yml`](docker-compose.yml:1).
   - Có nhiều container FastAPI (`fastapi1`, `fastapi2`, `fastapi3`).
   - Nếu 1 node FastAPI hoặc Milvus chết, Nginx vẫn chuyển request đến node còn lại, dữ liệu không mất.

2. **Distributed Communication**  
   - Nginx reverse proxy ([`nginx.conf`](nginx.conf:3)) chuyển tiếp HTTP đến các container FastAPI.
   - Các node giao tiếp qua HTTP, có thể mở rộng ra nhiều máy nếu cấu hình Docker network overlay.

3. **Replication**
   - Dự án sử dụng Milvus với chế độ cluster và replication (`MILVUS_CLUSTER_ENABLED=true`, `MILVUS_REPLICA_NUMBER=2` trong [`docker-compose.yml`](docker-compose.yml:1)).
   - Khi một node Milvus gặp sự cố, node còn lại vẫn lưu trữ dữ liệu, đảm bảo không mất mát.
   - Hiện tại chưa triển khai sharding (phân mảnh dữ liệu theo khóa). Nếu có thời gian, nhóm sẽ nghiên cứu thêm về sharding để tăng khả năng mở rộng và tối ưu truy vấn.

4. **Simple Monitoring/Logging**
   - FastAPI ghi log chi tiết ra file `embedding.log` (ghi lại các thao tác embedding, lỗi, truy vấn...).
   - Có endpoint `/log` để xem nhanh log hệ thống qua API.
   - Nginx và Milvus cũng có log riêng, có thể xem bằng lệnh `docker logs <container_name>`.
   - Nếu có thời gian, nhóm sẽ bổ sung dashboard giám sát trực quan (sử dụng Grafana, Prometheus hoặc custom web UI) để theo dõi trạng thái các node, số lượng request, lỗi, tài nguyên...


5. **Basic Stress Test**  
   - Script [`stress_test.sh`](stress_test.sh:1) mô phỏng nhiều client gửi request đồng thời đến endpoint `/search` qua Nginx, giúp kiểm tra tải và quan sát log hệ thống.

6. **System Recovery**
   - Dự án đã cấu hình `restart: always` cho tất cả các service trong [`docker-compose.yml`](docker-compose.yml:1). Khi một container FastAPI, Milvus, Nginx hoặc MinIO bị lỗi hoặc dừng bất ngờ, Docker Compose sẽ tự động khởi động lại container đó.
   - Milvus cluster sử dụng etcd để lưu trạng thái cluster. Khi node Milvus khởi động lại, nó sẽ tự động join lại cluster mà không cần thao tác thủ công.
   - FastAPI khi khởi động lại sẽ tự động kết nối lại Milvus và tiếp tục phục vụ request từ Nginx.
7. **Load Balancing**
   - Dự án đã triển khai Nginx reverse proxy với upstream gồm nhiều container FastAPI (xem [`nginx.conf`](nginx.conf:4)). Nginx sẽ tự động phân phối đều các request đến các node FastAPI, giúp tận dụng tài nguyên và tăng khả năng chịu tải.

8. **Consistency Guarantees**
    - Milvus replication đảm bảo dữ liệu nhất quán giữa các node Milvus: mọi thao tác ghi (insert, update, delete) đều được đồng bộ sang các node replica.
    - Quá trình đồng bộ này diễn ra tự động: khi có thao tác ghi lên node primary, dữ liệu sẽ được sao chép sang các node replica trong cluster Milvus. Điều này giúp mọi node đều có cùng trạng thái dữ liệu mới nhất.
    - Khi một node gặp sự cố, node còn lại vẫn giữ dữ liệu mới nhất, đảm bảo không mất mát và không có trạng thái "split-brain".
    - Việc đồng bộ này giúp hệ thống của dự án luôn đảm bảo tính nhất quán dữ liệu, tăng khả năng chịu lỗi và sẵn sàng cao cho các truy vấn tìm kiếm ảnh.
    - Hiện tại chưa có cảnh báo tự động khi mất đồng bộ, nếu có thời gian nhóm sẽ bổ sung kiểm tra định kỳ và cảnh báo khi phát hiện bất nhất dữ liệu.

9. **Leader Election**
   - Milvus sử dụng etcd để quản lý cluster, tự động bầu chọn (election) leader trong các node Milvus.
   - Khi node leader gặp sự cố hoặc bị dừng, etcd sẽ tự động chọn một node khác làm leader mới, đảm bảo cluster luôn có node điều phối chính, không bị gián đoạn dịch vụ.
   - Nếu có thời gian, nhóm sẽ bổ sung dashboard hoặc API hiển thị trạng thái leader, các node follower và lịch sử chuyển đổi leader để dễ giám sát, debug.

11. **Hoạt động đa máy**
    - Dự án hỗ trợ triển khai trên nhiều máy vật lý bằng cách sử dụng Docker 
    - Khi triển khai thực tế, chỉ cần các máy cùng tham gia vào một mạng Docker overlay , các container FastAPI, Milvus, Nginx sẽ tự động nhận diện và giao tiếp qua HTTP.s
    - Điều này giúp mở rộng hệ thống dễ dàng, tăng khả năng chịu tải và đảm bảo tính sẵn sàng cao.
    - Nếu có thời gian, nhóm sẽ xây dựng tài liệu hướng dẫn chi tiết triển khai đa máy và kịch bản kiểm thử thực tế trên nhiều node vật lý.