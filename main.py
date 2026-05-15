"""
main.py - Pipeline xử lý 4 file CSV:
  1. Cleaning (data_cleaning.py)
  2. Advanced Information Extraction (data_processing.py)
"""

import pandas as pd
import os
import sys
import io
import time
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from data_cleaning import clean_dataframe
from data_processing import extract_keywords

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# Cấu hình 4 file CSV
# ============================================================
FILES = [
    {
        'input': 'jobs_dev_top_final.csv',
        'output_cleaned': 'jobs_dev_top_final_cleaned.csv',
        'output_keywords': 'jobs_dev_top_final_extracted.csv',
        'source': 'TopDev',
        'rename_cols': {},
        'no_translate_cols': ['job_name', 'position', 'level'],
    },
    {
        'input': 'jobs_itviec_final.csv',
        'output_cleaned': 'jobs_itviec_final_cleaned.csv',
        'output_keywords': 'jobs_itviec_final_extracted.csv',
        'source': 'ITviec',
        'rename_cols': {},
        'no_translate_cols': ['job_name', 'position', 'skills'],
    },
    {
        'input': 'jobs_vietnamworks.csv',
        'output_cleaned': 'jobs_vietnamworks_cleaned.csv',
        'output_keywords': 'jobs_vietnamworks_extracted.csv',
        'source': 'VietnamWorks_sync',
        'rename_cols': {'Job Title': 'job_name', 'Position': 'position'},
        'no_translate_cols': ['job_name', 'position', 'Skills', 'Level'],
    },
    {
        'input': 'jobs_vietnamworks_async_parallel.csv',
        'output_cleaned': 'jobs_vietnamworks_async_parallel_cleaned.csv',
        'output_keywords': 'jobs_vietnamworks_async_parallel_extracted.csv',
        'source': 'VietnamWorks_async',
        'rename_cols': {'Job Title': 'job_name', 'Position': 'position'},
        'no_translate_cols': ['job_name', 'position', 'Skills', 'Level'],
    },
]


def save_csv(df, path, label):
    """Lưu CSV, tự đổi tên nếu file bị lock."""
    saved = False
    save_path = path
    for attempt in range(5):
        try:
            df.to_csv(save_path, index=False, encoding='utf-8-sig')
            saved = True
            break
        except PermissionError:
            base, ext = os.path.splitext(path)
            save_path = f"{base}_v{attempt+2}{ext}"
            print(f"  ⚠️ File bị lock, thử lưu: {os.path.basename(save_path)}")

    if saved:
        size_kb = os.path.getsize(save_path) / 1024
        print(f"  💾 {label}: {os.path.basename(save_path)} ({size_kb:.1f} KB)")
    else:
        print(f"  ❌ Không thể lưu {label}! Đóng file rồi chạy lại.")

def filter_empty_rows(df):
    """
    Bước 1: Xóa các dòng mà languages, databases, cloud, devops_tools đều trống.
    """
    before_rows = len(df)
    tech_check_cols = ['languages', 'databases', 'cloud', 'devops_tools']

    mask_all_empty = True
    for col in tech_check_cols:
        if col in df.columns:
            is_empty = df[col].isna() | (df[col].astype(str).str.strip().isin(['', 'nan', 'None', '[]']))
            mask_all_empty = mask_all_empty & is_empty

    df = df[~mask_all_empty].reset_index(drop=True)
    dropped = before_rows - len(df)
    print(f"  🗑️ Xóa {dropped} dòng phi tech ({before_rows} → {len(df)})")
    return df


def filter_sparse_cols(df, threshold=0.80):
    """
    Bước 2: Xóa các cột có dữ liệu trống trên threshold (mặc định 80%).
    """
    cols_to_drop = []
    for col in df.columns:
        null_rate = df[col].isna().sum() / len(df)
        empty_rate = (df[col].astype(str).str.strip().isin(['', 'nan', 'None', '[]'])).sum() / len(df)
        total_empty = null_rate + empty_rate - (null_rate * empty_rate)
        if total_empty > threshold:
            cols_to_drop.append((col, total_empty))

    if cols_to_drop:
        print(f"  🗑️ Xóa {len(cols_to_drop)} cột trống > {threshold*100:.0f}%:")
        for col, rate in cols_to_drop:
            print(f"      - {col} ({rate*100:.1f}% trống)")
        df = df.drop(columns=[c for c, _ in cols_to_drop])
    else:
        print(f"  ✅ Không có cột nào trống > {threshold*100:.0f}%")

    print(f"  📊 Kết quả: {df.shape[0]} dòng x {df.shape[1]} cột")
    return df


def handle_duplicate_jobs(df):
    """
    Bước 3: Xử lý các dòng JD có tên công việc trùng nhau (case-insensitive).
    - Chỉ gộp trùng đối với các nguồn: VietnamWorks_sync và VietnamWorks_async.
    - Các cột dạng list "['A', 'B']" (bao gồm cả kỹ năng mềm) sẽ được gộp (union) lại.
    - Các cột source sẽ được nối lại bằng dấu '+'.
    - Các cột khác ưu tiên giá trị dài nhất hoặc giá trị đầu tiên.
    """
    before_rows = len(df)
    if 'job_name' not in df.columns:
        return df

    # Chỉ lọc trùng cho VietnamWorks_sync và VietnamWorks_async
    vw_sources = ['VietnamWorks_sync', 'VietnamWorks_async']
    if 'source' in df.columns:
        mask = df['source'].isin(vw_sources)
        df_to_dedup = df[mask].copy()
        df_keep = df[~mask].copy()
    else:
        df_to_dedup = df.copy()
        df_keep = pd.DataFrame()

    if df_to_dedup.empty:
        return df

    # Chuẩn hóa để so sánh
    df_to_dedup['_key'] = df_to_dedup['job_name'].astype(str).str.lower().str.strip()

    def merge_series(series):
        valid = series.dropna()
        if len(valid) == 0:
            return np.nan
        
        col_name = series.name
        if col_name == 'source':
            return ' + '.join(valid.astype(str).unique())
            
        first_str = str(valid.iloc[0]).strip()
        if first_str.startswith('[') and first_str.endswith(']'):
            # Là dạng list string (Bao gồm cả Tech Skills và Soft Skills)
            import ast
            combined = []
            for val in valid:
                val_str = str(val).strip()
                if val_str.startswith('[') and val_str.endswith(']'):
                    try:
                        lst = ast.literal_eval(val_str)
                        if isinstance(lst, list):
                            combined.extend(lst)
                    except:
                        pass
            # Trả về list dạng chuỗi, duy nhất
            unique_vals = []
            for x in combined:
                if x not in unique_vals:
                    unique_vals.append(x)
            if not unique_vals:
                return np.nan
            return str(unique_vals)
            
        if series.dtype == object:
            # Ưu tiên chuỗi dài nhất
            return max(valid, key=lambda x: len(str(x)))
            
        return valid.iloc[0]

    # Bỏ qua cột _key khi trả về
    agg_dict = {col: merge_series for col in df_to_dedup.columns if col != '_key'}
    df_dedup = df_to_dedup.groupby('_key').agg(agg_dict).reset_index(drop=True)

    # Gộp lại với các dữ liệu không cần lọc trùng
    df_final = pd.concat([df_keep, df_dedup], ignore_index=True)

    dropped = before_rows - len(df_final)
    print(f"  🔄 Gộp trùng tên (VietnamWorks): Xóa {dropped} dòng ({before_rows} → {len(df_final)})")
    
    return df_final


def main():
    start_all = time.time()
    all_results = []

    for i, cfg in enumerate(FILES, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/4] {cfg['source']}: {cfg['input']}")
        print(f"{'='*60}")

        input_path = os.path.join(BASE_DIR, cfg['input'])

        # Đọc CSV
        df = pd.read_csv(input_path, encoding='utf-8')
        
        # 0. Chuẩn hóa tên cột ngay từ đầu
        if cfg['rename_cols']:
            df = df.rename(columns=cfg['rename_cols'])

        # 0.1 Xóa các dòng lỗi (chỉ có position, các cột khác đều null)
        content_cols = [c for c in df.columns if c not in ['position', 'job_name']]
        before = len(df)
        df = df.dropna(subset=content_cols, how='all')
        dropped = before - len(df)
        if dropped > 0:
            print(f"  ⚠️ Xóa {dropped} dòng lỗi (không có dữ liệu)")
            df = df.reset_index(drop=True)
            
        print(f"  Đã đọc: {df.shape[0]} dòng x {df.shape[1]} cột")

        # === STEP 1: Cleaning ===
        start = time.time()
        df_cleaned = clean_dataframe(
            df,
            no_translate_cols=cfg['no_translate_cols'],
            translate=False,
        )
        t_clean = time.time() - start

        # Lưu file cleaned
        save_csv(df_cleaned,
                 os.path.join(BASE_DIR, cfg['output_cleaned']),
                 f"Cleaned [{t_clean:.1f}s]")

        # === STEP 2: Advanced Extraction ===
        start = time.time()
        print(f"\n  📊 Đang phân tích nội dung chuyên sâu...")
        df_ext = extract_keywords(df_cleaned)

        # Chèn các thông tin cơ bản vào đầu df mới
        df_ext.insert(0, 'source', cfg['source'])
        df_ext.insert(1, 'job_name', df_cleaned['job_name'])
        df_ext.insert(2, 'position', df_cleaned.get('position', pd.Series(dtype=str)))
        
        # Giữ lại cột level gốc để tham chiếu
        if 'level' in df_cleaned.columns:
            df_ext.insert(3, 'original_level', df_cleaned['level'])
        elif 'Level' in df_cleaned.columns:
            df_ext.insert(3, 'original_level', df_cleaned['Level'])

        t_ext = time.time() - start

        # Lưu file extracted cho từng file
        save_csv(df_ext,
                 os.path.join(BASE_DIR, cfg['output_keywords']),
                 f"Extracted [{t_ext:.1f}s]")

        all_results.append(df_ext)

    # === STEP 3: Merge tất cả kết quả thành 1 file ===
    print(f"\n{'='*60}")
    print("Gộp tất cả dữ liệu đã phân tích thành 1 file...")
    df_all = pd.concat(all_results, ignore_index=True)
    
    save_csv(df_all,
             os.path.join(BASE_DIR, 'all_jobs_final_analysis.csv'),
             "FINAL ANALYSIS merged")

    # === STEP 4: Lọc dữ liệu — xóa dòng phi tech + cột trống + xử lý trùng lặp ===
    print(f"\n{'='*60}")
    print("Lọc dữ liệu: xóa dòng phi tech + cột trống > 80% + xử lý trùng tên...")
    print(f"{'='*60}")
    df_filtered = filter_empty_rows(df_all)
    df_filtered = filter_sparse_cols(df_filtered)
    df_filtered = handle_duplicate_jobs(df_filtered)

    save_csv(df_filtered,
             os.path.join(BASE_DIR, 'all_jobs_final_analysis_filtered.csv'),
             "FINAL FILTERED")

    total = time.time() - start_all
    print(f"\n{'='*60}")
    print(f"🎉 Hoàn tất! Tổng thời gian: {total:.1f}s")
    print(f"{'='*60}")
    print(f"  📄 all_jobs_final_analysis.csv ({df_all.shape[0]} jobs, {df_all.shape[1]} cột)")
    print(f"  📄 all_jobs_final_analysis_filtered.csv ({df_filtered.shape[0]} jobs, {df_filtered.shape[1]} cột)")


def main2():
    """Chỉ lọc dữ liệu từ file all_jobs_final_analysis.csv có sẵn."""
    input_path = os.path.join(BASE_DIR, 'all_jobs_final_analysis.csv')
    print(f"Đọc file: {os.path.basename(input_path)}")
    df = pd.read_csv(input_path, encoding='utf-8')
    print(f"  📄 {df.shape[0]} dòng x {df.shape[1]} cột")

    # Bước 1: Xóa dòng phi tech
    print(f"\n{'='*60}")
    print("BƯỚC 1: Xóa dòng không có dữ liệu tech")
    print(f"{'='*60}")
    df = filter_empty_rows(df)
    save_csv(df,
             os.path.join(BASE_DIR, 'all_jobs_rows_filtered.csv'),
             "ROWS FILTERED")

    # Bước 2: Xóa cột trống > 80%
    print(f"\n{'='*60}")
    print("BƯỚC 2: Xóa cột trống > 80%")
    print(f"{'='*60}")
    df = filter_sparse_cols(df)

    # Bước 3: Xử lý trùng lặp
    print(f"\n{'='*60}")
    print("BƯỚC 3: Xử lý các dòng JD trùng tên (Deduplicate)")
    print(f"{'='*60}")
    df = handle_duplicate_jobs(df)

    save_csv(df,
             os.path.join(BASE_DIR, 'all_jobs_final_analysis_filtered.csv'),
             "FINAL FILTERED")


if __name__ == '__main__':
    main2()
