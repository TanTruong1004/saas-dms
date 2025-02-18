**preconfigure:** Sửa network trong docker-compose file.

Đầu tiên chúng a cần build một Docker Image từ code, để build Docker Image chúng ta chạy câu lệnh:

```docker build -t dms_document_loader . ```

Sau đó để chạy Docker Image vừa build chúng ta chạy câu lệnh:

```docker-compose -f docker-compose-processing.yml up```
