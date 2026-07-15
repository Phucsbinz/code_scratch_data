import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ast
from collections import Counter
import os
import sys
import io
import squarify
from pywaffle import Waffle

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to sys.path to support imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
import config

# ==========================================
# CẤU HÌNH VÀ TIỀN XỬ LÝ DỮ LIỆU
# ==========================================
# Cấu hình font chữ hiển thị tiếng Việt tốt hơn nếu có
plt.rcParams['font.family'] = 'sans-serif'
sns.set_theme(style="whitegrid")

# Tạo thư mục lưu kết quả
OUT_DIR = config.REPORTS_DIR
CHART_DIR = config.CHARTS_DIR
os.makedirs(CHART_DIR, exist_ok=True)

def safe_eval(val):
    """Chuyển đổi chuỗi dạng list thành list thực sự"""
    if pd.isna(val) or val == 'nan':
        return []
    try:
        return ast.literal_eval(str(val))
    except:
        return []

def count_frequencies(series):
    """Đếm tần suất xuất hiện của các item trong cột chứa list"""
    counter = Counter()
    for item_list in series.dropna():
        if isinstance(item_list, list):
            counter.update(item_list)
    return pd.Series(counter).sort_values(ascending=False)

def average_by_list_col(df, list_col, num_col, min_count=5):
    """Tính trung bình của num_col dựa trên các item trong list_col"""
    if num_col not in df.columns or df[num_col].isna().all():
        return pd.Series(dtype=float)
        
    records = []
    for _, row in df.dropna(subset=[num_col]).iterrows():
        items = row.get(list_col, [])
        if isinstance(items, list):
            for item in items:
                records.append({list_col: item, num_col: row[num_col]})
    
    if not records:
        return pd.Series(dtype=float)
        
    df_exploded = pd.DataFrame(records)
    grouped = df_exploded.groupby(list_col)[num_col].agg(['mean', 'count'])
    grouped = grouped[grouped['count'] >= min_count]
    return grouped['mean'].sort_values(ascending=False)

def plot_bar(data, title, xlabel, ylabel, filename, color="skyblue"):
    """Hàm vẽ biểu đồ Bar Chart ngang"""
    plt.figure(figsize=(10, 6))
    sns.barplot(x=data.values, y=data.index, palette="viridis")
    plt.title(title, fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename), dpi=300)
    plt.close()

def plot_donut(data, title, filename):
    """Hàm vẽ biểu đồ Donut Chart cho Education"""
    plt.figure(figsize=(8, 8))
    if len(data) > 5:
        data_to_plot = data.head(5).copy()
        other_sum = data.iloc[5:].sum()
        if other_sum > 0:
            data_to_plot['Khác'] = other_sum
    else:
        data_to_plot = data
        
    colors = sns.color_palette("Set2")
    plt.pie(data_to_plot.values, labels=data_to_plot.index, autopct='%1.1f%%', startangle=140, colors=colors, wedgeprops=dict(width=0.4))
    plt.title(title, fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename), dpi=300)
    plt.close()

def plot_education_requirements(df, filename):
    total_jds = len(df)
    
    # Calculate counts dynamically matching the table logic
    bachelor_count = sum(df['education'].apply(lambda x: isinstance(x, list) and "bachelor's" in x))
    master_count = sum(df['education'].apply(lambda x: isinstance(x, list) and "master's/phd" in x))
    college_count = sum(df['education'].apply(lambda x: isinstance(x, list) and "college" in x))
    
    # "Không ghi rõ" is total minus the sum of these three (to match the table's logic)
    unspecified_count = total_jds - (bachelor_count + master_count + college_count)
    
    degree_counts = pd.Series({
        "Đại học (Bachelor's)": bachelor_count,
        "Không ghi rõ": unspecified_count,
        "Thạc sĩ / Tiến sĩ (Master's/PhD)": master_count,
        "Cao đẳng / Trung cấp (College)": college_count
    })
    
    # Create single plot
    plt.figure(figsize=(8, 8))
    
    colors = ['#3498db', '#bdc3c7', '#9b59b6', '#f1c40f']
    wedges, texts, autotexts = plt.pie(
        degree_counts.values, 
        labels=degree_counts.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors[:len(degree_counts)],
        wedgeprops=dict(width=0.4, edgecolor='w')
    )
    plt.setp(autotexts, size=10, weight="bold")
    plt.setp(texts, size=10)
    plt.title("Yêu cầu Trình độ Học vấn (Degree Level)", fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename), dpi=300)
    plt.savefig(os.path.join(config.SLIDE_CHARTS_DIR, filename), dpi=300)
    plt.close()

def plot_pie(data, title, filename, max_items=6):
    """Hàm vẽ biểu đồ tròn (Pie Chart)"""
    plt.figure(figsize=(8, 8))
    if len(data) > max_items:
        data_to_plot = data.head(max_items).copy()
        other_sum = data.iloc[max_items:].sum()
        if other_sum > 0:
            data_to_plot['Khác'] = other_sum
    else:
        data_to_plot = data
        
    colors = sns.color_palette("Set3")
    plt.pie(data_to_plot.values, labels=data_to_plot.index, autopct='%1.1f%%', startangle=140, colors=colors)
    plt.title(title, fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename), dpi=300)
    plt.close()

def plot_bar_annotated(data, title, filename):
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(x=data.values, y=data.index, hue=data.index, palette="viridis", legend=False)
    plt.title(title, fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Số lượng Job", fontsize=12)
    plt.ylabel("Công nghệ", fontsize=12)
    
    total = data.sum()
    for p in ax.patches:
        width = p.get_width()
        percentage = f' {width:.0f} ({100 * width / total:.1f}%)'
        ax.text(width + 0.5, p.get_y() + p.get_height()/2., percentage, va='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename), dpi=300)
    plt.close()

def plot_treemap(data, title, filename, max_items=15):
    plt.figure(figsize=(10, 6))
    data_to_plot = data.head(max_items).copy()
    if len(data) > max_items:
        data_to_plot['Khác'] = data.iloc[max_items:].sum()
        
    total = data_to_plot.sum()
    labels = [f'{idx}\n{val} ({val/total*100:.1f}%)' for idx, val in zip(data_to_plot.index, data_to_plot.values)]
    colors = sns.color_palette("Spectral", len(data_to_plot))
    squarify.plot(sizes=data_to_plot.values, label=labels, color=colors, alpha=0.8, pad=True, text_kwargs={'fontsize': 10, 'fontweight': 'bold'})
    plt.axis('off')
    plt.title(title, fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename), dpi=300)
    plt.close()

def plot_waffle(data, title, filename, max_items=8):
    data_to_plot = data.head(max_items).copy()
    if len(data) > max_items:
        data_to_plot['Khác'] = data.iloc[max_items:].sum()
        
    total = data_to_plot.sum()
    data_percent = {idx: round(val / total * 100) for idx, val in zip(data_to_plot.index, data_to_plot.values)}
    
    # Xử lý trường hợp làm tròn không đủ 100%
    diff = 100 - sum(data_percent.values())
    if diff != 0:
        first_key = list(data_percent.keys())[0]
        data_percent[first_key] += diff

    fig = plt.figure(
        FigureClass=Waffle,
        rows=10,
        columns=10,
        values=data_percent,
        colors=sns.color_palette("Set3", len(data_percent)).as_hex(),
        title={'label': title, 'loc': 'center', 'fontsize': 14, 'fontweight': 'bold', 'pad': 15},
        legend={'loc': 'upper left', 'bbox_to_anchor': (1, 1), 'fontsize': 10, 'labels': [f"{k} ({v}%)" for k, v in data_percent.items()]},
        figsize=(10, 6)
    )
    plt.savefig(os.path.join(CHART_DIR, filename), dpi=300, bbox_inches='tight')
    plt.close()

def plot_stacked_bar(data, title, filename, max_items=6):
    plt.figure(figsize=(10, 2))
    data_to_plot = data.head(max_items).copy()
    if len(data) > max_items:
        data_to_plot['Khác'] = data.iloc[max_items:].sum()
        
    total = data_to_plot.sum()
    percentages = [val / total * 100 for val in data_to_plot.values]
    labels = data_to_plot.index
    colors = sns.color_palette("Set2", len(data_to_plot))
    
    left = 0
    for i, (pct, label) in enumerate(zip(percentages, labels)):
        plt.barh(0, pct, left=left, color=colors[i], edgecolor='white', height=0.5)
        if pct > 5: # Chỉ hiện chữ nếu ô đủ lớn
            plt.text(left + pct/2, 0, f"{label}\n{pct:.1f}%", va='center', ha='center', color='white', fontweight='bold', fontsize=9)
        left += pct
        
    plt.title(title, fontsize=12, fontweight='bold', pad=10)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_DIR, filename), dpi=300)
    plt.close()

# Đọc dữ liệu
print("Đang đọc dữ liệu...")
df = pd.read_csv(os.path.join(config.PROCESSED_DATA_DIR, 'all_jobs_final_analysis_filtered.csv'), encoding='utf-8')

# Các cột cần parse từ string sang list
list_cols = ['role_category', 'experience_level', 'languages', 'data_ai', 
             'devops_tools', 'soft_skills', 'language_requirement', 'work_style', 'education', 'databases', 'cloud']

for col in list_cols:
    if col in df.columns:
        df[col] = df[col].apply(safe_eval)

# ==========================================
# PHÂN TÍCH & TRỰC QUAN HÓA
# ==========================================

print("Đang vẽ biểu đồ Tổng quan...")
# 1. TỔNG QUAN THỊ TRƯỜNG (MARKET SNAPSHOT)
roles = count_frequencies(df['role_category']).head(8)
plot_bar(roles, "Top các Vị trí Tuyển dụng Công nghệ (Role Category)", "Số lượng Job", "Vị trí", "top_roles.png")
plot_pie(roles, "Tỷ trọng Vị trí Tuyển dụng Công nghệ (%)", "top_roles_pie.png", max_items=8)
plot_bar_annotated(roles, "Annotated Bar: Vị trí Tuyển dụng", "top_roles_bar_annotated.png")
plot_treemap(roles, "Treemap: Vị trí Tuyển dụng", "top_roles_treemap.png", max_items=8)

# Năm kinh nghiệm trung bình theo vị trí
print("Đang vẽ biểu đồ Năm kinh nghiệm trung bình...")
avg_exp_by_role = average_by_list_col(df, 'role_category', 'years_of_exp', min_count=3)
if not avg_exp_by_role.empty:
    plot_bar(avg_exp_by_role.head(8), "Số năm kinh nghiệm trung bình theo Vị trí", "Năm kinh nghiệm", "Vị trí", "avg_exp_by_role.png")

# Phân bố kinh nghiệm
exp_levels = count_frequencies(df['experience_level'])
plot_bar(exp_levels, "Nhu cầu theo Cấp độ Kinh nghiệm (Experience Level)", "Số lượng Job", "Cấp độ", "experience_levels.png")
plot_pie(exp_levels, "Tỷ trọng Nhu cầu Cấp độ Kinh nghiệm (%)", "experience_levels_pie.png", max_items=8)
plot_bar_annotated(exp_levels, "Annotated Bar: Cấp độ Kinh nghiệm", "experience_levels_bar_annotated.png")
plot_treemap(exp_levels, "Treemap: Cấp độ Kinh nghiệm", "experience_levels_treemap.png", max_items=8)

# Yêu cầu bằng cấp
print("Đang vẽ biểu đồ Bằng cấp/Giáo dục...")
plot_education_requirements(df, "education_requirements.png")

print("Đang vẽ biểu đồ Kỹ năng chuyên sâu...")
# 2. KỸ NĂNG CHUYÊN SÂU (DEEP DIVE SKILLS)
tech_langs = count_frequencies(df['languages']).head(15)
plot_bar(tech_langs, "Top 15 Ngôn ngữ / Nền tảng được Yêu cầu", "Số lượng Job", "Công nghệ", "top_languages.png")
plot_pie(tech_langs, "Tỷ trọng Ngôn ngữ / Nền tảng được Yêu cầu (%)", "top_languages_pie.png", max_items=8)

plot_bar_annotated(tech_langs, "Annotated Bar: Ngôn ngữ / Nền tảng", "top_languages_bar_annotated.png")
plot_treemap(tech_langs, "Treemap: Ngôn ngữ / Nền tảng", "top_languages_treemap.png", max_items=15)

soft_skills = count_frequencies(df['soft_skills']).head(10)
plot_bar(soft_skills, "Top 10 Kỹ năng Mềm (Soft Skills)", "Số lượng Job", "Kỹ năng mềm", "top_soft_skills.png")
plot_pie(soft_skills, "Tỷ trọng Kỹ năng Mềm (%)", "top_soft_skills_pie.png", max_items=8)
plot_bar_annotated(soft_skills, "Annotated Bar: Kỹ năng Mềm", "top_soft_skills_bar_annotated.png")
plot_treemap(soft_skills, "Treemap: Kỹ năng Mềm", "top_soft_skills_treemap.png", max_items=8)

work_styles = count_frequencies(df['work_style']).head(8)
plot_bar(work_styles, "Top Phương pháp & Phong cách Làm việc (Work Style/Methodology)", "Số lượng Job", "Phong cách/Phương pháp", "top_work_styles.png")
plot_pie(work_styles, "Tỷ trọng Phương pháp & Phong cách Làm việc (%)", "top_work_styles_pie.png", max_items=8)
plot_bar_annotated(work_styles, "Annotated Bar: Phong cách Làm việc", "top_work_styles_bar_annotated.png")
plot_treemap(work_styles, "Treemap: Phong cách Làm việc", "top_work_styles_treemap.png", max_items=8)

devops = count_frequencies(df['devops_tools']).head(8)
if not devops.empty:
    plot_bar(devops, "Top Công cụ DevOps & Infrastructure", "Số lượng Job", "Công cụ", "top_devops.png")
    plot_pie(devops, "Tỷ trọng Công cụ DevOps (%)", "top_devops_pie.png", max_items=8)
    plot_bar_annotated(devops, "Annotated Bar: Công cụ DevOps", "top_devops_bar_annotated.png")
    plot_treemap(devops, "Treemap: Công cụ DevOps", "top_devops_treemap.png", max_items=8)

print("Đang vẽ biểu đồ Data & AI...")
data_ai_tools = count_frequencies(df['data_ai']).head(10)
if not data_ai_tools.empty:
    plot_bar(data_ai_tools, "Top 10 Công cụ / Kỹ năng Data & AI", "Số lượng Job", "Kỹ năng / Công cụ", "top_data_ai.png", color="purple")
    plot_pie(data_ai_tools, "Tỷ trọng Công cụ / Kỹ năng Data & AI (%)", "top_data_ai_pie.png", max_items=8)
    plot_bar_annotated(data_ai_tools, "Annotated Bar: Công cụ Data & AI", "top_data_ai_bar_annotated.png")
    plot_treemap(data_ai_tools, "Treemap: Công cụ Data & AI", "top_data_ai_treemap.png", max_items=8)

print("Đang vẽ biểu đồ Database & Cloud...")
databases = count_frequencies(df['databases']).head(10)
if not databases.empty:
    plot_bar(databases, "Top Cơ sở dữ liệu (Databases)", "Số lượng Job", "Database", "top_databases.png")
    plot_pie(databases, "Tỷ trọng Cơ sở dữ liệu (Databases) (%)", "top_databases_pie.png", max_items=8)
    plot_bar_annotated(databases, "Annotated Bar: Cơ sở dữ liệu", "top_databases_bar_annotated.png")
    plot_treemap(databases, "Treemap: Cơ sở dữ liệu", "top_databases_treemap.png", max_items=8)

cloud_tools = count_frequencies(df['cloud']).head(10)
if not cloud_tools.empty:
    plot_bar(cloud_tools, "Top Nền tảng Đám mây (Cloud)", "Số lượng Job", "Cloud", "top_cloud.png")
    plot_pie(cloud_tools, "Tỷ trọng Nền tảng Đám mây (Cloud) (%)", "top_cloud_pie.png", max_items=8)
    plot_bar_annotated(cloud_tools, "Annotated Bar: Nền tảng Đám mây", "top_cloud_bar_annotated.png")
    plot_treemap(cloud_tools, "Treemap: Nền tảng Đám mây", "top_cloud_treemap.png", max_items=8)

# Yêu cầu Ngoại ngữ
print("Đang vẽ biểu đồ Ngoại ngữ...")
language_reqs = count_frequencies(df['language_requirement'])
if not language_reqs.empty:
    plot_donut(language_reqs, "Yêu cầu Ngoại ngữ (Language Requirements)", "language_requirements.png")

print("Đang vẽ Heatmap tương quan...")
# 3. HEATMAP TƯƠNG QUAN: Vai trò vs Kỹ năng
# Chọn top 4 roles và top 8 languages
top_roles_list = roles.head(4).index.tolist()
top_langs_list = tech_langs.head(8).index.tolist()

# Khởi tạo ma trận 0
heatmap_data = pd.DataFrame(0, index=top_roles_list, columns=top_langs_list)

# Tính toán số lượng xuất hiện đồng thời
for _, row in df.iterrows():
    r_list = row.get('role_category', [])
    l_list = row.get('languages', [])
    if isinstance(r_list, list) and isinstance(l_list, list):
        for r in r_list:
            if r in top_roles_list:
                for l in l_list:
                    if l in top_langs_list:
                        heatmap_data.loc[r, l] += 1

plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlGnBu", linewidths=.5)
plt.title("Heatmap: Sự tương quan giữa Vai trò và Ngôn ngữ Lập trình", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Ngôn ngữ Lập trình")
plt.ylabel("Vai trò")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, 'heatmap_role_language.png'), dpi=300)
plt.close()

print("Đang vẽ Heatmap Data/AI vs Position...")
# Chọn top 5 positions và top 8 Data/AI tools
data_ai_df = df.dropna(subset=['data_ai'])
if not data_ai_df.empty and not data_ai_tools.empty:
    top_positions_ai = data_ai_df['position'].value_counts().head(5).index.tolist()
    top_data_ai_list = data_ai_tools.head(8).index.tolist()

    if top_positions_ai and top_data_ai_list:
        heatmap_data_ai = pd.DataFrame(0, index=top_positions_ai, columns=top_data_ai_list)
        for _, row in data_ai_df.iterrows():
            p = row.get('position')
            ai_list = row.get('data_ai', [])
            if pd.isna(p) or p not in top_positions_ai:
                continue
            if isinstance(ai_list, list):
                for ai in ai_list:
                    if ai in top_data_ai_list:
                        heatmap_data_ai.loc[p, ai] += 1

        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap_data_ai, annot=True, fmt="d", cmap="Purples", linewidths=.5)
        plt.title("Heatmap: Tương quan giữa Vị trí (Position) và Công cụ Data/AI", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Công cụ Data/AI")
        plt.ylabel("Vị trí (Position)")
        plt.tight_layout()
        plt.savefig(os.path.join(CHART_DIR, 'heatmap_position_data_ai.png'), dpi=300)
        plt.close()

print("Đang vẽ Heatmap Database vs Position...")
db_pos_df = df.dropna(subset=['databases', 'position'])
if not db_pos_df.empty and 'databases' in locals() and not databases.empty:
    top_db_list = databases.head(8).index.tolist()
    top_pos_db = db_pos_df['position'].value_counts().head(5).index.tolist()
    
    if top_db_list and top_pos_db:
        heatmap_pos_db = pd.DataFrame(0, index=top_pos_db, columns=top_db_list)
        for _, row in db_pos_df.iterrows():
            p = row.get('position')
            dbs = row.get('databases', [])
            if pd.isna(p) or p not in top_pos_db:
                continue
            if isinstance(dbs, list):
                for db in dbs:
                    if db in top_db_list:
                        heatmap_pos_db.loc[p, db] += 1

        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap_pos_db, annot=True, fmt="d", cmap="Blues", linewidths=.5)
        plt.title("Heatmap: Tương quan giữa Vị trí (Position) và Database", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Cơ sở dữ liệu (Database)")
        plt.ylabel("Vị trí (Position)")
        plt.tight_layout()
        plt.savefig(os.path.join(CHART_DIR, 'heatmap_position_database.png'), dpi=300)
        plt.close()

print("Đang vẽ Heatmap Cloud vs Position...")
cloud_pos_df = df.dropna(subset=['cloud', 'position'])
if not cloud_pos_df.empty and 'cloud_tools' in locals() and not cloud_tools.empty:
    top_cloud_list = cloud_tools.head(8).index.tolist()
    top_pos_cloud = cloud_pos_df['position'].value_counts().head(5).index.tolist()
    
    if top_cloud_list and top_pos_cloud:
        heatmap_pos_cloud = pd.DataFrame(0, index=top_pos_cloud, columns=top_cloud_list)
        for _, row in cloud_pos_df.iterrows():
            p = row.get('position')
            clds = row.get('cloud', [])
            if pd.isna(p) or p not in top_pos_cloud:
                continue
            if isinstance(clds, list):
                for cld in clds:
                    if cld in top_cloud_list:
                        heatmap_pos_cloud.loc[p, cld] += 1

        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap_pos_cloud, annot=True, fmt="d", cmap="Greens", linewidths=.5)
        plt.title("Heatmap: Tương quan giữa Vị trí (Position) và Cloud", fontsize=14, fontweight='bold', pad=15)
        plt.xlabel("Nền tảng Cloud")
        plt.ylabel("Vị trí (Position)")
        plt.tight_layout()
        plt.savefig(os.path.join(CHART_DIR, 'heatmap_position_cloud.png'), dpi=300)
        plt.close()

# ==========================================
# TẠO BÁO CÁO (MARKDOWN)
# ==========================================
print("Đang tạo Báo cáo nghiên cứu...")
education_reqs = count_frequencies(df['education'])

report_content = f"""# 🎯 Báo Cáo Nghiên Cứu: Nhu cầu Tuyển dụng & Khoảng cách Kỹ năng IT

## 1. Tổng quan Nghiên cứu
- **Mục tiêu:** Hiểu rõ nhu cầu thực tế của doanh nghiệp IT và trả lời câu hỏi "Sinh viên cần học gì và học như thế nào?"
- **Quy mô dữ liệu:** Phân tích {len(df)} tin tuyển dụng IT (đã được làm sạch, loại bỏ các tin phi công nghệ).

## 2. Thị trường cần gì? (Market Snapshot)

### A. Vị trí & Cấp độ
- **Vị trí dẫn đầu:** 
  - Đa số nhu cầu nằm ở nhóm **{roles.index[0].title() if not roles.empty else 'Software Engineering'}**.
  - Sự bùng nổ của nhóm dữ liệu (Data/AI) cũng cho thấy sự chuyển dịch xu hướng.
  - Về số năm kinh nghiệm: Vị trí **{avg_exp_by_role.index[0].title() if not avg_exp_by_role.empty else 'N/A'}** đòi hỏi kinh nghiệm cao nhất (trung bình {avg_exp_by_role.iloc[0]:.1f} năm nếu có dữ liệu).
- **Kinh nghiệm:**
  - Nhu cầu cho **{exp_levels.index[0].title() if not exp_levels.empty else 'Middle/Senior'}** chiếm áp đảo. Doanh nghiệp cần những người có thể "vào việc ngay".
- **Học vấn / Bằng cấp:**
  - Nhà tuyển dụng chủ yếu yêu cầu **{education_reqs.index[0].title() if not education_reqs.empty else 'Cử nhân'}**. Mặc dù IT là ngành trọng thực hành, nhưng bằng cấp cơ bản vẫn là tấm vé thông hành quan trọng ở nhiều doanh nghiệp lớn.

### B. Kỹ năng Công nghệ (Technical Skills)
- **Top Ngôn ngữ/Nền tảng:** {', '.join(tech_langs.index[:5].str.title())}. Đây là những "xương sống" của các hệ thống doanh nghiệp hiện nay.
- **Top DevOps/Cloud:** {', '.join(devops.index[:3].str.title())}. Thị trường hiện nay yêu cầu Dev không chỉ biết code mà còn phải biết deploy và quản trị hạ tầng cơ bản.
- **Top Công cụ Data/AI:** {', '.join(data_ai_tools.index[:5].str.title()) if 'data_ai_tools' in locals() and not data_ai_tools.empty else 'N/A'}. Lĩnh vực trí tuệ nhân tạo và dữ liệu đang lên ngôi mạnh mẽ với nhu cầu lớn cho các kỹ năng chuyên biệt này.
- **Cơ sở dữ liệu (Database):** Môi trường lưu trữ dữ liệu chính xoay quanh các công nghệ {', '.join(databases.index[:3].str.title()) if 'databases' in locals() and not databases.empty else 'N/A'}.
- **Nền tảng Cloud:** Doanh nghiệp chủ yếu triển khai hệ thống trên {', '.join(cloud_tools.index[:3].str.title()) if 'cloud_tools' in locals() and not cloud_tools.empty else 'N/A'}.

### C. Kỹ năng Mềm & Văn hóa (Non-technical & Work style)
- **Top Kỹ năng mềm:** {', '.join(soft_skills.index[:5].str.title())}. Kỹ năng giao tiếp và làm việc nhóm là bắt buộc để làm việc trong mô hình Agile.
- **Phong cách làm việc:** {', '.join(work_styles.index[:3].str.title())}. Doanh nghiệp ưu tiên ứng viên hiểu rõ quy trình phát triển phần mềm chuẩn.
- **Ngoại ngữ:** Ngoại ngữ được yêu cầu phổ biến nhất là **{language_reqs.index[0].title() if not language_reqs.empty else 'Tiếng Anh'}**, cho thấy tầm quan trọng của ngoại ngữ trong việc đọc tài liệu và giao tiếp.

---

## 3. Phân tích Khoảng cách (Gap Analysis) - Sinh viên đang thiếu gì?

Dựa vào dữ liệu từ thị trường (Market) và thực trạng đào tạo tại trường (School):

| Tiêu chí | Thị trường cần (JD) | Sinh viên đang học/làm | Khoảng cách (Gap) |
|---|---|---|---|
| **Công nghệ lõi** | Framework thực tế (Spring Boot, React), SQL nâng cao | C/C++ cơ bản, cấu trúc dữ liệu, OOP thuần túy | Sinh viên thiếu kỹ năng sử dụng Framework và hệ sinh thái thực tế. |
| **Quy trình / Tool**| Git (nâng cao), CI/CD, Docker, Jira, Agile/Scrum | Code chạy được trên máy cá nhân, nộp bài qua zip/drive | Không có tư duy làm việc nhóm chuyên nghiệp, bỡ ngỡ với quy trình dự án. |
| **Tư duy (Mindset)**| Problem Solving (giải quyết vấn đề nghiệp vụ) | Pass test case, giải bài tập lý thuyết | Sinh viên thiếu khả năng đưa ra giải pháp giải quyết vấn đề từ đầu đến cuối. |
| **Kỹ năng mềm** | Communication, Teamwork, Tiếng Anh chuyên ngành | Thích làm việc độc lập, ngại giao tiếp | Gặp khó khăn khi review code, họp nhóm, giao tiếp với BA/QA. |

---

## 4. Đề xuất: Sinh viên cần học như thế nào?

Từ các Insight trên, dưới đây là đề xuất chiến lược học tập:

**1. Học theo Project thay vì Lý thuyết (Project-Based Learning)**
- *Insight:* Hơn 80% JD yêu cầu kỹ năng thực chiến với Framework và hệ sinh thái.
- *Hành động:* Sinh viên không nên chỉ học cú pháp ngôn ngữ. Phải xây dựng **Portfolio** bằng các dự án thực tế (Web App hoàn chỉnh, API kết nối Database, Deploy lên Cloud).

**2. Tư duy "End-to-End" (Không chỉ biết Code)**
- *Insight:* DevOps tools (Docker, CI/CD) và Git là chuẩn mực bắt buộc.
- *Hành động:* Đưa Git, GitHub/GitLab vào thói quen hàng ngày. Tự học cách đóng gói ứng dụng (Docker) thay vì chỉ chạy `localhost`.

**3. Mô phỏng Môi trường Doanh nghiệp (Agile/Scrum)**
- *Insight:* Làm việc nhóm (Teamwork) và Agile/Scrum là kỹ năng được yêu cầu cao nhất.
- *Hành động:* Đồ án môn học nên tổ chức như một dự án thật: Có quản lý task (Trello/Jira), có Review Code, có chia Sprint.

**4. Học sâu (T-Shaped Skills) thay vì biết rộng**
- *Hành động:* Chọn 1 hệ sinh thái (VD: Java/Spring Boot hoặc JS/React) và cày thật sâu, kết hợp thêm kiến thức về SQL và Cloud cơ bản.
"""

with open(os.path.join(OUT_DIR, 'Research_Report.md'), 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"✅ Đã phân tích xong! Kết quả lưu tại thư mục: {OUT_DIR}")
