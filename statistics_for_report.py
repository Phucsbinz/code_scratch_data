import ast
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "all_jobs_final_analysis_filtered.csv"
REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_JSON = REPORTS_DIR / "jd_statistics_for_report.json"
OUTPUT_MD = REPORTS_DIR / "JD_Statistics_Summary.md"

LIST_COLUMNS = [
    "role_category",
    "experience_level",
    "languages",
    "frameworks",
    "data_ai",
    "databases",
    "cloud",
    "devops_tools",
    "soft_skills",
    "language_requirement",
    "methodology",
    "work_style",
    "education",
]

COUNT_COLUMNS = [
    "source",
    "position",
    "original_level",
]

TOP_N_DEFAULT = 15


def parse_list(value):
    if value is None:
        return []
    value = str(value).strip()
    if not value or value.lower() in {"nan", "none", "null"}:
        return []
    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return [value]
    if isinstance(parsed, list):
        return [str(item).strip() for item in parsed if str(item).strip()]
    return [str(parsed).strip()] if str(parsed).strip() else []


def parse_float(value):
    if value is None:
        return None
    value = str(value).strip()
    if not value or value.lower() in {"nan", "none", "null"}:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    if math.isnan(number):
        return None
    return number


def read_rows(path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader), reader.fieldnames or []


def counter_to_records(counter, total_jobs, top_n=None):
    items = counter.most_common(top_n)
    return [
        {
            "name": name,
            "count": count,
            "percent_of_jobs": round(count / total_jobs * 100, 2) if total_jobs else 0,
        }
        for name, count in items
    ]


def numeric_summary(values):
    values = sorted(v for v in values if v is not None)
    if not values:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
        }
    mid = len(values) // 2
    median = values[mid] if len(values) % 2 else (values[mid - 1] + values[mid]) / 2
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": round(sum(values) / len(values), 2),
        "median": round(median, 2),
    }


def average_years_by_list_item(rows, list_col, min_count=3):
    buckets = defaultdict(list)
    for row in rows:
        years = parse_float(row.get("years_of_exp"))
        if years is None:
            continue
        for item in parse_list(row.get(list_col)):
            buckets[item].append(years)

    result = []
    for item, values in buckets.items():
        if len(values) < min_count:
            continue
        summary = numeric_summary(values)
        result.append(
            {
                "name": item,
                "count": summary["count"],
                "average_years": summary["mean"],
                "median_years": summary["median"],
            }
        )
    return sorted(result, key=lambda item: (-item["average_years"], -item["count"], item["name"]))


def cross_tab_list_by_source(rows, list_col):
    table = defaultdict(Counter)
    for row in rows:
        source = (row.get("source") or "Unknown").strip() or "Unknown"
        for item in parse_list(row.get(list_col)):
            table[source][item] += 1
    return {
        source: counter_to_records(counter, sum(1 for row in rows if (row.get("source") or "Unknown").strip() == source), TOP_N_DEFAULT)
        for source, counter in sorted(table.items())
    }


def build_statistics(rows, columns):
    total_jobs = len(rows)
    source_counter = Counter((row.get("source") or "Unknown").strip() or "Unknown" for row in rows)

    list_counters = {}
    coverage = {}
    for col in LIST_COLUMNS:
        counter = Counter()
        jobs_with_value = 0
        for row in rows:
            items = parse_list(row.get(col))
            if items:
                jobs_with_value += 1
                counter.update(items)
        list_counters[col] = counter
        coverage[col] = {
            "jobs_with_value": jobs_with_value,
            "percent_of_jobs": round(jobs_with_value / total_jobs * 100, 2) if total_jobs else 0,
            "unique_values": len(counter),
        }

    normal_counters = {}
    for col in COUNT_COLUMNS:
        counter = Counter()
        for row in rows:
            value = (row.get(col) or "Unknown").strip() or "Unknown"
            counter[value] += 1
        normal_counters[col] = counter

    years = [parse_float(row.get("years_of_exp")) for row in rows]

    stats = {
        "metadata": {
            "input_file": str(INPUT_CSV.name),
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "total_jobs": total_jobs,
            "columns": columns,
        },
        "overview": {
            "total_jobs": total_jobs,
            "total_columns": len(columns),
            "sources": counter_to_records(source_counter, total_jobs),
            "years_of_exp": numeric_summary(years),
        },
        "coverage": coverage,
        "top_values": {},
        "average_years_by_group": {
            "role_category": average_years_by_list_item(rows, "role_category"),
            "experience_level": average_years_by_list_item(rows, "experience_level"),
            "languages": average_years_by_list_item(rows, "languages", min_count=5),
            "frameworks": average_years_by_list_item(rows, "frameworks", min_count=5),
        },
        "by_source": {
            "role_category": cross_tab_list_by_source(rows, "role_category"),
            "languages": cross_tab_list_by_source(rows, "languages"),
            "frameworks": cross_tab_list_by_source(rows, "frameworks"),
            "soft_skills": cross_tab_list_by_source(rows, "soft_skills"),
        },
    }

    for col, counter in normal_counters.items():
        stats["top_values"][col] = counter_to_records(counter, total_jobs, TOP_N_DEFAULT)
    for col, counter in list_counters.items():
        stats["top_values"][col] = counter_to_records(counter, total_jobs, TOP_N_DEFAULT)

    return stats


def md_table(records, headers):
    if not records:
        return "_Không có dữ liệu._\n"
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for record in records:
        cells = []
        for header in headers:
            value = record.get(header, "")
            cells.append(str(value))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def top_table(stats, key, title, top_n=10):
    records = stats["top_values"].get(key, [])[:top_n]
    normalized = [
        {
            "Hạng mục": item["name"],
            "Số JD": item["count"],
            "% trên tổng JD": item["percent_of_jobs"],
        }
        for item in records
    ]
    return f"### {title}\n\n" + md_table(normalized, ["Hạng mục", "Số JD", "% trên tổng JD"])


def coverage_table(stats):
    rows = []
    for col, item in stats["coverage"].items():
        rows.append(
            {
                "Nhóm dữ liệu": col,
                "JD có dữ liệu": item["jobs_with_value"],
                "% trên tổng JD": item["percent_of_jobs"],
                "Số giá trị khác nhau": item["unique_values"],
            }
        )
    rows.sort(key=lambda item: (-item["% trên tổng JD"], item["Nhóm dữ liệu"]))
    return md_table(rows, ["Nhóm dữ liệu", "JD có dữ liệu", "% trên tổng JD", "Số giá trị khác nhau"])


def avg_years_table(stats, key, title, top_n=10):
    rows = [
        {
            "Hạng mục": item["name"],
            "Số JD có năm KN": item["count"],
            "Năm KN trung bình": item["average_years"],
            "Trung vị": item["median_years"],
        }
        for item in stats["average_years_by_group"].get(key, [])[:top_n]
    ]
    return f"### {title}\n\n" + md_table(rows, ["Hạng mục", "Số JD có năm KN", "Năm KN trung bình", "Trung vị"])


def write_markdown(stats, path):
    overview = stats["overview"]
    years = overview["years_of_exp"]
    content = [
        "# Thống kê dữ liệu JD phục vụ báo cáo",
        "",
        "## 1. Tổng quan bộ dữ liệu",
        "",
        f"- File đầu vào: `{stats['metadata']['input_file']}`",
        f"- Thời điểm tạo thống kê: `{stats['metadata']['generated_at']}`",
        f"- Tổng số JD sau lọc: **{overview['total_jobs']}**",
        f"- Số cột dữ liệu: **{stats['metadata']['total_jobs'] and len(stats['metadata']['columns'])}**",
        f"- Số JD có thông tin năm kinh nghiệm: **{years['count']}**",
        f"- Năm kinh nghiệm trung bình: **{years['mean']}**" if years["mean"] is not None else "- Năm kinh nghiệm trung bình: chưa đủ dữ liệu",
        f"- Trung vị năm kinh nghiệm: **{years['median']}**" if years["median"] is not None else "- Trung vị năm kinh nghiệm: chưa đủ dữ liệu",
        "",
        "### Phân bố nguồn dữ liệu",
        "",
        md_table(
            [
                {"Nguồn": item["name"], "Số JD": item["count"], "% trên tổng JD": item["percent_of_jobs"]}
                for item in overview["sources"]
            ],
            ["Nguồn", "Số JD", "% trên tổng JD"],
        ),
        "## 2. Độ phủ các nhóm thông tin",
        "",
        coverage_table(stats),
        "## 3. Thống kê cần dùng cho báo cáo",
        "",
        top_table(stats, "role_category", "3.1. Top nhóm vị trí tuyển dụng"),
        top_table(stats, "experience_level", "3.2. Nhu cầu theo cấp độ kinh nghiệm"),
        top_table(stats, "education", "3.3. Yêu cầu học vấn/bằng cấp"),
        top_table(stats, "languages", "3.4. Top ngôn ngữ lập trình/nền tảng"),
        top_table(stats, "frameworks", "3.5. Top framework/công nghệ phát triển phần mềm"),
        top_table(stats, "databases", "3.6. Top cơ sở dữ liệu"),
        top_table(stats, "cloud", "3.7. Top nền tảng cloud"),
        top_table(stats, "devops_tools", "3.8. Top công cụ DevOps/Infrastructure"),
        top_table(stats, "data_ai", "3.9. Top kỹ năng Data/AI"),
        top_table(stats, "soft_skills", "3.10. Top kỹ năng mềm"),
        top_table(stats, "language_requirement", "3.11. Yêu cầu ngoại ngữ"),
        top_table(stats, "methodology", "3.12. Phương pháp làm việc"),
        top_table(stats, "work_style", "3.13. Phong cách làm việc/quy trình"),
        "## 4. Năm kinh nghiệm trung bình theo nhóm",
        "",
        avg_years_table(stats, "role_category", "4.1. Theo nhóm vị trí"),
        avg_years_table(stats, "experience_level", "4.2. Theo cấp độ kinh nghiệm"),
        avg_years_table(stats, "languages", "4.3. Theo ngôn ngữ/nền tảng", top_n=15),
        avg_years_table(stats, "frameworks", "4.4. Theo framework", top_n=15),
        "## 5. Gợi ý insight có thể đưa vào báo cáo",
        "",
        "- Dùng `Top nhóm vị trí tuyển dụng` để chứng minh thị trường đang cần nhóm nghề nào nhiều nhất.",
        "- Dùng `Top ngôn ngữ`, `Top framework`, `Database`, `Cloud`, `DevOps` để trả lời sinh viên cần học kỹ năng kỹ thuật nào.",
        "- Dùng `Top kỹ năng mềm`, `Yêu cầu ngoại ngữ`, `Phương pháp làm việc` để phân tích gap ngoài kỹ thuật.",
        "- Dùng `Năm kinh nghiệm trung bình` để chỉ ra doanh nghiệp ưu tiên ứng viên có khả năng làm việc thực tế, đặc biệt ở nhóm senior/middle.",
        "- Dùng `Độ phủ các nhóm thông tin` để giải thích giới hạn dữ liệu: không phải JD nào cũng ghi đầy đủ bằng cấp, cloud, DevOps hoặc năm kinh nghiệm.",
        "",
    ]
    path.write_text("\n".join(content), encoding="utf-8")


def main():
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Không tìm thấy file đầu vào: {INPUT_CSV}")
    REPORTS_DIR.mkdir(exist_ok=True)

    rows, columns = read_rows(INPUT_CSV)
    stats = build_statistics(rows, columns)

    OUTPUT_JSON.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(stats, OUTPUT_MD)

    print(f"Đã đọc {len(rows)} JD từ {INPUT_CSV.name}")
    print(f"Đã tạo JSON: {OUTPUT_JSON}")
    print(f"Đã tạo Markdown: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
