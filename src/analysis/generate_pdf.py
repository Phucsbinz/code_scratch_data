import markdown
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Thêm thư mục gốc dự án vào sys.path để hỗ trợ import
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
import config

# Đường dẫn thư mục
REPORTS_DIR = config.REPORTS_DIR
CHARTS_DIR = config.CHARTS_DIR

def get_img_path(filename):
    # Trả về đường dẫn tuyệt đối dạng D:/... cho xhtml2pdf
    path = os.path.join(CHARTS_DIR, filename).replace('\\', '/')
    return path


# Đọc nội dung Markdown
md_file = os.path.join(REPORTS_DIR, 'Research_Report.md')
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

work_style_caption = """<div style='text-align: left; background: #f8f9fa; padding: 15px; border-left: 4px solid #2980b9; margin: 10px auto; max-width: 600px; font-size: 13px; line-height: 1.6; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>
    <strong style='color: #2c3e50; font-size: 14px;'>Giải thích thuật ngữ (Work Style / Methodology):</strong><br/>
    • <strong>Documentation:</strong> Kỹ năng viết, đọc hiểu và bảo trì tài liệu kỹ thuật.<br/>
    • <strong>Clean Code / SOLID:</strong> Tuân thủ các nguyên tắc viết code sạch, tối ưu, dễ đọc, dễ bảo trì.<br/>
    • <strong>Code Review:</strong> Quy trình kiểm tra chéo mã nguồn giữa các thành viên trong nhóm.<br/>
    • <strong>Agile / Scrum:</strong> Mô hình phát triển phần mềm linh hoạt, chia nhỏ tiến độ theo Sprint.<br/>
    • <strong>REST API / GraphQL:</strong> Tiêu chuẩn thiết kế giao diện lập trình ứng dụng (API).<br/>
    • <strong>TDD / Unit Test:</strong> Viết kịch bản kiểm thử (test case) song song hoặc trước khi viết code.<br/>
    • <strong>OOP:</strong> Tư duy và kỹ năng Lập trình hướng đối tượng.
</div>"""

# Chèn hình ảnh vào Markdown
img_inserts = {
    "### A. Vị trí & Cấp độ": f"### A. Vị trí & Cấp độ\n\n<div class='img-container'><img src='{get_img_path('top_roles.png')}'/><br/><img src='{get_img_path('top_roles_pie.png')}'/><br/><img src='{get_img_path('top_roles_bar_annotated.png')}'/><br/><img src='{get_img_path('top_roles_treemap.png')}'/><br/><img src='{get_img_path('avg_exp_by_role.png')}'/><br/><img src='{get_img_path('experience_levels.png')}'/><br/><img src='{get_img_path('experience_levels_pie.png')}'/><br/><img src='{get_img_path('experience_levels_bar_annotated.png')}'/><br/><img src='{get_img_path('experience_levels_treemap.png')}'/><br/><img src='{get_img_path('education_requirements.png')}'/></div>\n",
    "### B. Kỹ năng Công nghệ (Technical Skills)": f"### B. Kỹ năng Công nghệ (Technical Skills)\n\n<div class='img-container'><img src='{get_img_path('top_languages.png')}'/><br/><img src='{get_img_path('top_languages_pie.png')}'/><br/><img src='{get_img_path('top_languages_bar_annotated.png')}'/><br/><img src='{get_img_path('top_languages_treemap.png')}'/><br/><hr style='margin: 40px 0; border: 1px dashed #ccc;'/><img src='{get_img_path('top_databases.png')}'/><br/><img src='{get_img_path('top_databases_pie.png')}'/><br/><img src='{get_img_path('top_databases_bar_annotated.png')}'/><br/><img src='{get_img_path('top_databases_treemap.png')}'/><br/><hr style='margin: 40px 0; border: 1px dashed #ccc;'/><img src='{get_img_path('top_cloud.png')}'/><br/><img src='{get_img_path('top_cloud_pie.png')}'/><br/><img src='{get_img_path('top_cloud_bar_annotated.png')}'/><br/><img src='{get_img_path('top_cloud_treemap.png')}'/><br/><hr style='margin: 40px 0; border: 1px dashed #ccc;'/><img src='{get_img_path('top_data_ai.png')}'/><br/><img src='{get_img_path('top_data_ai_pie.png')}'/><br/><img src='{get_img_path('top_data_ai_bar_annotated.png')}'/><br/><img src='{get_img_path('top_data_ai_treemap.png')}'/><br/><hr style='margin: 40px 0; border: 1px dashed #ccc;'/><img src='{get_img_path('top_devops.png')}'/><br/><img src='{get_img_path('top_devops_pie.png')}'/><br/><img src='{get_img_path('top_devops_bar_annotated.png')}'/><br/><img src='{get_img_path('top_devops_treemap.png')}'/></div>\n",
    "### C. Kỹ năng Mềm & Văn hóa (Non-technical & Work style)": f"### C. Kỹ năng Mềm & Văn hóa (Non-technical & Work style)\n\n<div class='img-container'><img src='{get_img_path('top_soft_skills.png')}'/><br/><img src='{get_img_path('top_soft_skills_pie.png')}'/><br/><img src='{get_img_path('top_soft_skills_bar_annotated.png')}'/><br/><img src='{get_img_path('top_soft_skills_treemap.png')}'/><br/><img src='{get_img_path('top_work_styles.png')}'/><br/><img src='{get_img_path('top_work_styles_pie.png')}'/><br/><img src='{get_img_path('top_work_styles_bar_annotated.png')}'/><br/><img src='{get_img_path('top_work_styles_treemap.png')}'/><br/>{work_style_caption}<br/><img src='{get_img_path('language_requirements.png')}'/></div>\n",
    "## 3. Phân tích Khoảng cách (Gap Analysis)": f"### D. Tương quan Vai trò và Kỹ năng\n\n<div class='img-container'><img src='{get_img_path('heatmap_role_language.png')}'/><br/><img src='{get_img_path('heatmap_position_data_ai.png')}'/><br/><img src='{get_img_path('heatmap_position_database.png')}'/><br/><img src='{get_img_path('heatmap_position_cloud.png')}'/></div>\n\n## 3. Phân tích Khoảng cách (Gap Analysis)"
}

for k, v in img_inserts.items():
    md_content = md_content.replace(k, v)

# Chuyển đổi Markdown sang HTML (hỗ trợ table)
html_body = markdown.markdown(md_content, extensions=['tables'])

# Wrap HTML body với cấu trúc chuẩn và CSS chuyên nghiệp
html_template = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        font-family: 'Arial', 'Helvetica', sans-serif;
        font-size: 14px;
        line-height: 1.6;
        color: #333;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }}
    h1 {{ color: #2c3e50; text-align: center; font-size: 28px; margin-bottom: 20px; font-family: inherit; }}
    h2 {{ color: #2980b9; border-bottom: 2px solid #2980b9; padding-bottom: 5px; margin-top: 30px; font-size: 22px; font-family: inherit; }}
    h3 {{ color: #16a085; font-size: 18px; margin-top: 20px; font-family: inherit; }}
    p, li, td, th {{ font-family: inherit; }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }}
    th, td {{
        border: 1px solid #bdc3c7;
        padding: 8px;
        text-align: left;
    }}
    th {{
        background-color: #f39c12;
        color: white;
        font-weight: bold;
    }}
    tr:nth-child(even) {{ background-color: #f9f9f9; }}
    .img-container {{
        text-align: center;
        margin: 20px 0;
    }}
    img {{
        width: 500px;
        max-width: 100%;
    }}
    ul, ol {{ margin-bottom: 15px; }}
    li {{ margin-bottom: 5px; }}
</style>
</head>
<body>
    {html_body}
</body>
</html>
"""

# Xuất HTML thay vì cố ép PDF bằng Python
output_html = os.path.join(REPORTS_DIR, 'Research_Report_Visualized.html')

with open(output_html, "w", encoding='utf-8') as result_file:
    result_file.write(html_template)

print(f"Đã tạo file HTML chuyên nghiệp thành công tại: {output_html}")
print("Mẹo: Bạn hãy mở file này bằng Chrome hoặc Edge, sau đó bấm Ctrl + P (Print) và chọn 'Save as PDF' để có bản PDF hoàn hảo 100% không bao giờ lỗi font!")

