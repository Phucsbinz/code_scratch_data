# Phân tích Dữ liệu Tuyển dụng IT (IT Job Market Analysis)

Dự án này thu thập dữ liệu từ các trang tuyển dụng IT tại Việt Nam (VietnamWorks, ITviec, TopDev...), sau đó tiến hành làm sạch, phân tích và trực quan hóa dữ liệu để xuất ra báo cáo (HTML/PDF) về xu hướng thị trường, yêu cầu kỹ năng, và vị trí công việc.

## 🛠 Cài đặt môi trường

1. Clone repository về máy.
2. Cài đặt các thư viện Python cần thiết:
   ```bash
   pip install -r requirements.txt
   ```
3. Cài đặt các trình duyệt cho Playwright (được dùng để cào dữ liệu web động):
   ```bash
   playwright install
   ```

## 🚀 Cách chạy dự án

### Cách 1: Chạy toàn bộ quy trình (Pipeline)
Bạn chỉ cần chạy file `main.py` để hệ thống tự động làm sạch dữ liệu, lọc các cột rác, phân tích và gọi script tạo biểu đồ:
```bash
python main.py
```

### Cách 2: Chỉ chạy phần Trực quan hóa (Visualization)
Nếu bạn đã có sẵn file CSV đầu ra (`all_jobs_final_analysis_filtered.csv`) và chỉ muốn chỉnh sửa biểu đồ/báo cáo:
```bash
# 1. Vẽ các biểu đồ (Bar, Pie, Treemap, Waffle...)
python data_visualization.py

# 2. Ghép hình ảnh vào báo cáo Markdown và xuất ra HTML
python generate_pdf.py
```

## 📁 Cấu trúc thư mục chính
- `VietNamWork_async` / `Scratch_...`: Các script dùng Playwright/BeautifulSoup để cào dữ liệu.
- `data_cleaning.py` / `data_processing.py`: Xử lý, chuẩn hóa từ khóa (skills, databases, tools) và gộp dữ liệu.
- `data_visualization.py`: Logic vẽ biểu đồ bằng `matplotlib`, `seaborn`, `squarify`, `pywaffle`.
- `generate_pdf.py`: Render báo cáo từ Markdown sang HTML.
- `reports/`: Chứa file báo cáo cuối cùng `Research_Report_Visualized.html` và thư mục hình ảnh `charts/`.

*(Lưu ý: Các file `.csv` chứa hàng ngàn dòng dữ liệu đã được cấu hình ẩn khỏi Git để tránh làm nặng repository)*
