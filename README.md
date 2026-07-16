# Phân tích Dữ liệu Tuyển dụng IT (IT Job Market Analysis)

Dự án này thực hiện việc thu thập dữ liệu từ các trang tuyển dụng IT hàng đầu tại Việt Nam (VietnamWorks, ITviec, TopDev), tiến hành làm sạch, trích xuất thông tin chuyên sâu (Ngôn ngữ, Cấp độ, Học vấn, Cơ sở dữ liệu, DevOps, Cloud, Kỹ năng mềm...), xử lý trùng lặp, trực quan hóa dữ liệu và xuất bản báo cáo phân tích xu hướng thị trường cùng khoảng cách kỹ năng (Education Gap).

---

## 📂 Cấu trúc Thư mục Dự án Tiêu chuẩn

Dự án được tái cấu trúc theo bố cục phân lớp chuyên nghiệp dành cho các dự án Dữ liệu:

```text
code scratch data/
├── config.py                 # Cấu hình đường dẫn tuyệt đối động (Centralized Paths)
├── main.py                   # Entrypoint điều hướng pipeline chính (Clean & Extract)
├── requirements.txt          # Các thư viện phụ thuộc của dự án
├── README.md                 # Hướng dẫn dự án này
│
├── data/                     # Quản lý dữ liệu dự án
│   ├── raw/                  # Chứa các file CSV thô ban đầu thu thập từ Scrapers
│   │   ├── jobs_dev_top_final.csv
│   │   ├── jobs_itviec_final.csv
│   │   ├── jobs_vietnamworks.csv
│   │   └── jobs_vietnamworks_async_parallel.csv
│   │
│   └── processed/            # Chứa dữ liệu sạch và kết quả phân tích sau xử lý
│       ├── ... (các tệp trung gian đã làm sạch & trích xuất kỹ năng)
│       ├── all_jobs_final_analysis.csv
│       ├── all_jobs_rows_filtered.csv
│       └── all_jobs_final_analysis_filtered.csv  # Bộ dữ liệu 837 JD chuẩn
│
├── src/                      # Mã nguồn (Source Code) của dự án
│   ├── crawlers/             # Chứa tập lệnh scraper/crawler dữ liệu
│   │   ├── scratch_itviec.py
│   │   ├── scratch_topdev.py
│   │   ├── vietnamworks_sync.py
│   │   └── vietnamworks_async.py
│   │
│   └── analysis/             # Chứa mã nguồn xử lý, phân tích và vẽ biểu đồ
│       ├── data_cleaning.py
│       ├── data_processing.py
│       ├── data_visualization.py
│       ├── generate_pdf.py
│       ├── statistics_for_report.py
│       └── analyze_csv_content.py
│
└── reports/                  # Thư mục chứa kết quả phân tích & báo cáo đầu ra
    ├── csv_analysis_result.json
    ├── jd_statistics_for_report.json
    ├── JD_Statistics_Summary.md
    ├── Research_Report.md
    ├── Research_Report_Visualized.html
    └── charts/               # Lưu 46 biểu đồ PNG sắc nét phục vụ báo cáo
```

---

## Cài đặt Môi trường

1. **Cài đặt các thư viện Python phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Cài đặt các trình duyệt hỗ trợ Playwright (cho việc cào dữ liệu động):**
   ```bash
   playwright install
   ```

---

## Hướng dẫn Sử dụng & Vận hành

Dự án cung cấp cấu hình đường dẫn tập trung động trong `config.py`. Tất cả các script trong `src/` có khả năng tự phát hiện thư mục gốc của dự án để chạy độc lập hoặc chạy qua pipeline.

### 1. Quy trình Xử lý & Làm sạch Dữ liệu
Để chạy pipeline gộp dữ liệu từ 4 nguồn thô, làm sạch ký tự đặc biệt, dịch thuật cấp độ, trích xuất từ khóa kỹ thuật và gộp trùng lặp (VietnamWorks) thành bộ dữ liệu 837 JD:
```bash
py main.py
```
*Kết quả:* Bộ dữ liệu chuẩn cuối cùng sẽ được lưu tại `data/processed/all_jobs_final_analysis_filtered.csv`.

### 2. Vẽ biểu đồ & Tạo báo cáo Markdown
Để chạy vẽ 46 biểu đồ trực quan (bao gồm biểu đồ trình độ học vấn đơn lẻ theo yêu cầu) và tạo báo cáo `Research_Report.md`:
```bash
py src/analysis/data_visualization.py
```
*Lưu ý:* Biểu đồ `education_requirements.png` cũng được tự động đồng bộ hóa sang thư mục `slide_charts/` ở thư mục cha của dự án.

### 3. Xuất bản báo cáo HTML trực quan
Để biên dịch báo cáo markdown sang tệp HTML trực quan chuyên nghiệp có nhúng các biểu đồ:
```bash
py src/analysis/generate_pdf.py
```
*Mẹo:* Mở tệp `reports/Research_Report_Visualized.html` bằng trình duyệt Chrome hoặc Edge, nhấn `Ctrl + P` (Print) và chọn **Save as PDF** để nhận file PDF báo cáo hoàn hảo không lỗi font.

### 4. Tập lệnh phân tích & thống kê bổ trợ
- Để xuất thống kê chi tiết dạng JSON và Markdown phục vụ báo cáo:
  ```bash
  py src/analysis/statistics_for_report.py
  ```
- Để quét mã Unicode các ký tự đặc biệt và đếm từ khóa biến thể công nghệ trên các tệp dữ liệu gốc:
  ```bash
  py src/analysis/analyze_csv_content.py
  ```
