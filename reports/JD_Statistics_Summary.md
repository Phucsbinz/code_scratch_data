# Thống kê dữ liệu JD phục vụ báo cáo

## 1. Tổng quan bộ dữ liệu

- File đầu vào: `all_jobs_final_analysis_filtered.csv`
- Thời điểm tạo thống kê: `2026-07-15T17:41:52`
- Tổng số JD sau lọc: **837**
- Số cột dữ liệu: **18**
- Số JD có thông tin năm kinh nghiệm: **691**
- Năm kinh nghiệm trung bình: **4.23**
- Trung vị năm kinh nghiệm: **4.0**

### Phân bố nguồn dữ liệu

| Nguồn | Số JD | % trên tổng JD |
|---|---|---|
| VietnamWorks_sync + VietnamWorks_async | 373 | 44.56 |
| ITviec | 299 | 35.72 |
| VietnamWorks_async | 81 | 9.68 |
| VietnamWorks_sync | 56 | 6.69 |
| TopDev | 28 | 3.35 |

## 2. Độ phủ các nhóm thông tin

| Nhóm dữ liệu | JD có dữ liệu | % trên tổng JD | Số giá trị khác nhau |
|---|---|---|---|
| Nhóm vị trí công việc (role_category) | 813 | 97.13 | 12 |
| Kỹ năng mềm (soft_skills) | 773 | 92.35 | 15 |
| Ngôn ngữ lập trình / Nền tảng (languages) | 735 | 87.81 | 19 |
| Cấp độ kinh nghiệm (experience_level) | 680 | 81.24 | 8 |
| Yêu cầu học vấn / Bằng cấp (education) | 600 | 71.68 | 4 |
| Quy trình / Phong cách làm việc (work_style) | 500 | 59.74 | 14 |
| Yêu cầu ngoại ngữ (language_requirement) | 495 | 59.14 | 5 |
| Công cụ DevOps & Hạ tầng (devops_tools) | 339 | 40.5 | 10 |
| Kỹ năng & Công cụ Data/AI (data_ai) | 327 | 39.07 | 23 |
| Cơ sở dữ liệu (databases) | 238 | 28.43 | 13 |
| Framework & Thư viện (frameworks) | 237 | 28.32 | 18 |
| Phương pháp phát triển (methodology) | 236 | 28.2 | 9 |
| Nền tảng đám mây (cloud) | 205 | 24.49 | 3 |

## 3. Thống kê cần dùng cho báo cáo

### 3.1. Top nhóm vị trí tuyển dụng

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| software engineering | 396 | 47.31 |
| ai/ml engineering | 233 | 27.84 |
| quality assurance | 220 | 26.28 |
| data engineering | 189 | 22.58 |
| business analysis | 159 | 19.0 |
| data science | 133 | 15.89 |
| data analysis | 96 | 11.47 |
| cybersecurity | 91 | 10.87 |
| embedded system | 62 | 7.41 |
| devops/sre | 60 | 7.17 |

### 3.2. Nhu cầu theo cấp độ kinh nghiệm

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| senior | 377 | 45.04 |
| manager | 323 | 38.59 |
| middle | 229 | 27.36 |
| lead/principal | 182 | 21.74 |
| junior | 69 | 8.24 |
| fresher | 55 | 6.57 |
| director | 32 | 3.82 |
| intern | 19 | 2.27 |

### 3.3. Yêu cầu học vấn/bằng cấp

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| bachelor's | 522 | 62.37 |
| computer science | 442 | 52.81 |
| master's/phd | 77 | 9.2 |
| college | 26 | 3.11 |

### 3.4. Top ngôn ngữ lập trình/nền tảng

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| python | 365 | 43.61 |
| sql | 307 | 36.68 |
| java | 146 | 17.44 |
| c++ | 104 | 12.43 |
| golang | 99 | 11.83 |
| javascript | 78 | 9.32 |
| c# | 76 | 9.08 |
| html/css | 63 | 7.53 |
| typescript | 53 | 6.33 |
| r | 42 | 5.02 |

### 3.5. Top framework/công nghệ phát triển phần mềm

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| react | 76 | 9.08 |
| .net | 72 | 8.6 |
| node.js | 45 | 5.38 |
| langchain | 42 | 5.02 |
| spring boot | 39 | 4.66 |
| angular | 29 | 3.46 |
| spring | 26 | 3.11 |
| langgraph | 25 | 2.99 |
| fastapi | 23 | 2.75 |
| vue.js | 23 | 2.75 |

### 3.6. Top cơ sở dữ liệu

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| oracle | 95 | 11.35 |
| postgresql | 90 | 10.75 |
| mysql | 67 | 8.0 |
| sql server | 59 | 7.05 |
| mongodb | 55 | 6.57 |
| redis | 42 | 5.02 |
| elasticsearch | 22 | 2.63 |
| firebase | 12 | 1.43 |
| milvus | 9 | 1.08 |
| pinecone | 7 | 0.84 |

### 3.7. Top nền tảng cloud

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| aws | 163 | 19.47 |
| azure | 113 | 13.5 |
| gcp | 81 | 9.68 |

### 3.8. Top công cụ DevOps/Infrastructure

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| ci/cd | 188 | 22.46 |
| docker | 133 | 15.89 |
| microservices | 93 | 11.11 |
| kubernetes | 91 | 10.87 |
| linux | 82 | 9.8 |
| kafka | 64 | 7.65 |
| jenkins | 28 | 3.35 |
| terraform | 19 | 2.27 |
| rabbitmq | 17 | 2.03 |
| nginx | 5 | 0.6 |

### 3.9. Top kỹ năng Data/AI

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| machine learning | 140 | 16.73 |
| llm | 103 | 12.31 |
| power bi | 90 | 10.75 |
| rag | 65 | 7.77 |
| tensorflow | 60 | 7.17 |
| pytorch | 56 | 6.69 |
| nlp | 52 | 6.21 |
| tableau | 51 | 6.09 |
| etl | 48 | 5.73 |
| deep learning | 47 | 5.62 |

### 3.10. Top kỹ năng mềm

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| communication | 459 | 54.84 |
| analytical | 398 | 47.55 |
| teamwork | 369 | 44.09 |
| mentoring | 334 | 39.9 |
| work independently | 278 | 33.21 |
| responsibility | 259 | 30.94 |
| problem solving | 240 | 28.67 |
| leadership | 193 | 23.06 |
| adaptability | 157 | 18.76 |
| creativity | 131 | 15.65 |

### 3.11. Yêu cầu ngoại ngữ

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| english | 472 | 56.39 |
| japanese | 40 | 4.78 |
| chinese | 27 | 3.23 |
| korean | 13 | 1.55 |
| french | 2 | 0.24 |

### 3.12. Phương pháp làm việc

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| devops | 115 | 13.74 |
| agile | 101 | 12.07 |
| sdlc | 44 | 5.26 |
| scrum | 36 | 4.3 |
| safe | 16 | 1.91 |
| ddd | 9 | 1.08 |
| waterfall | 9 | 1.08 |
| kanban | 3 | 0.36 |
| lean | 1 | 0.12 |

### 3.13. Phong cách làm việc/quy trình

| Hạng mục | Số JD | % trên tổng JD |
|---|---|---|
| documentation | 294 | 35.13 |
| solid | 129 | 15.41 |
| rest api | 86 | 10.27 |
| system design | 64 | 7.65 |
| remote/hybrid | 57 | 6.81 |
| oop | 47 | 5.62 |
| unit test | 36 | 4.3 |
| code review | 27 | 3.23 |
| graphql | 23 | 2.75 |
| clean code | 17 | 2.03 |

## 4. Năm kinh nghiệm trung bình theo nhóm

### 4.1. Theo nhóm vị trí

| Hạng mục | Số JD có năm KN | Năm KN trung bình | Trung vị |
|---|---|---|---|
| data science | 113 | 5.08 | 4.0 |
| ai/ml engineering | 201 | 4.65 | 4.0 |
| product management | 20 | 4.55 | 5.0 |
| embedded system | 51 | 4.47 | 3.0 |
| data engineering | 156 | 4.35 | 4.0 |
| cybersecurity | 68 | 4.35 | 5.0 |
| business analysis | 143 | 4.31 | 4.0 |
| software engineering | 308 | 4.17 | 3.0 |
| devops/sre | 56 | 4.12 | 4.0 |
| project management | 35 | 4.0 | 5.0 |

### 4.2. Theo cấp độ kinh nghiệm

| Hạng mục | Số JD có năm KN | Năm KN trung bình | Trung vị |
|---|---|---|---|
| lead/principal | 170 | 6.03 | 5.0 |
| director | 31 | 5.52 | 5.0 |
| senior | 342 | 5.19 | 5.0 |
| manager | 281 | 4.32 | 4.0 |
| middle | 220 | 4.27 | 3.0 |
| junior | 51 | 3.78 | 3.0 |
| fresher | 26 | 1.77 | 2.0 |
| intern | 7 | 1.43 | 1.0 |

### 4.3. Theo ngôn ngữ/nền tảng

| Hạng mục | Số JD có năm KN | Năm KN trung bình | Trung vị |
|---|---|---|---|
| r | 35 | 5.89 | 3.0 |
| typescript | 45 | 5.4 | 4.0 |
| java | 118 | 4.59 | 4.0 |
| python | 295 | 4.5 | 4.0 |
| javascript | 60 | 4.05 | 3.0 |
| sql | 263 | 3.92 | 3.0 |
| golang | 82 | 3.91 | 4.0 |
| html/css | 53 | 3.81 | 3.0 |
| shell/bash | 13 | 3.77 | 5.0 |
| scala | 10 | 3.7 | 3.0 |
| c++ | 80 | 3.58 | 3.0 |
| php | 13 | 3.46 | 3.0 |
| kotlin | 8 | 3.25 | 2.5 |
| c# | 61 | 3.23 | 3.0 |
| dart | 5 | 3.2 | 3.0 |

### 4.4. Theo framework

| Hạng mục | Số JD có năm KN | Năm KN trung bình | Trung vị |
|---|---|---|---|
| next.js | 16 | 8.12 | 5.0 |
| langchain | 36 | 5.78 | 5.0 |
| nest.js | 11 | 5.55 | 4.0 |
| react | 64 | 5.06 | 5.0 |
| express | 5 | 4.8 | 4.0 |
| langgraph | 20 | 4.6 | 4.5 |
| node.js | 36 | 4.44 | 4.0 |
| spring boot | 36 | 4.42 | 4.0 |
| .net | 55 | 4.04 | 5.0 |
| angular | 25 | 3.76 | 4.0 |
| vue.js | 21 | 3.71 | 4.0 |
| spring | 19 | 3.53 | 3.0 |
| fastapi | 22 | 3.32 | 4.0 |
| react native | 10 | 3.3 | 3.0 |
| flutter | 14 | 3.14 | 2.5 |

## 5. Gợi ý insight có thể đưa vào báo cáo

- Dùng `Top nhóm vị trí tuyển dụng` để chứng minh thị trường đang cần nhóm nghề nào nhiều nhất.
- Dùng `Top ngôn ngữ`, `Top framework`, `Database`, `Cloud`, `DevOps` để trả lời sinh viên cần học kỹ năng kỹ thuật nào.
- Dùng `Top kỹ năng mềm`, `Yêu cầu ngoại ngữ`, `Phương pháp làm việc` để phân tích gap ngoài kỹ thuật.
- Dùng `Năm kinh nghiệm trung bình` để chỉ ra doanh nghiệp ưu tiên ứng viên có khả năng làm việc thực tế, đặc biệt ở nhóm senior/middle.
- Dùng `Độ phủ các nhóm thông tin` để giải thích giới hạn dữ liệu: không phải JD nào cũng ghi đầy đủ bằng cấp, cloud, DevOps hoặc năm kinh nghiệm.
