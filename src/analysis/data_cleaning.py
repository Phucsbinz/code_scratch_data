"""
data_cleaning.py - Module chứa các hàm xử lý dữ liệu CSV.

Sử dụng:
    from data_cleaning import clean_dataframe

    df = pd.read_csv('file.csv')
    df_cleaned = clean_dataframe(df, no_translate_cols=['job_name', 'position', 'skills'])
"""

import pandas as pd
import re
import os
import json
import unicodedata
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# 1. SPECIAL CHARACTERS MAP → replace with space
# ============================================================
SPECIAL_CHARS_MAP = {
    '\u2013': ' ', '\u2014': ' ', '\u2011': ' ', '\u2010': ' ',   # dashes
    '\u2019': ' ', '\u2018': ' ', '\u201C': ' ', '\u201D': ' ',   # quotes
    '\u2026': ' ',                                                  # ellipsis
    '\u2022': ' ', '\u25CF': ' ', '\u25E6': ' ',                   # bullets
    '\u2192': ' ', '\u27A1': ' ',                                   # arrows
    '\u2265': ' ',                                                  # >=
    '\u00B7': ' ',                                                  # middle dot
    '\u3001': ' ', '\u3002': ' ',                                   # JP comma/period
    '\uFF1A': ' ', '\uFF0C': ' ', '\uFF0F': ' ', '\uFF09': ' ',   # fullwidth
    '\uFF0B': ' ', '\u30FB': ' ',
    '\u200B': '',  '\uFE0F': '',                                    # zero-width
    '\U0001F31E': '', '\U0001F4B2': '',                             # emoji
}

# ============================================================
# 2. TECH TERM NORMALIZATION (variant → canonical lowercase)
# ============================================================
# Canonical mapping: variant → normalized form
# Sorted longest-first to avoid partial matches
_RAW_TECH_MAP = {
    # C++ variants
    'CPP': 'c++', 'cpp': 'c++', 'C++': 'c++',
    # JavaScript
    'JavaScript': 'javascript', 'Javascript': 'javascript', 'javascript': 'javascript',
    # TypeScript
    'TypeScript': 'typescript', 'Typescript': 'typescript', 'typescript': 'typescript',
    # Python
    'Python': 'python', 'python': 'python', 'PYTHON': 'python',
    # Node.js
    'Node.js': 'node.js', 'NodeJS': 'node.js', 'Nodejs': 'node.js',
    'nodejs': 'node.js', 'Node.JS': 'node.js', 'NODEJS': 'node.js',
    # React
    'ReactJS': 'react', 'React.js': 'react', 'reactjs': 'react', 'react.js': 'react',
    # Angular
    'AngularJS': 'angular', 'Angular.js': 'angular', 'angularjs': 'angular',
    # Vue
    'Vue.js': 'vue.js', 'VueJS': 'vue.js', 'Vuejs': 'vue.js', 'vuejs': 'vue.js',
    # .NET
    'ASP.NET': '.net', 'asp.net': '.net', 'dotnet': '.net', 'DotNet': '.net',
    # PostgreSQL
    'Postgres': 'postgresql', 'postgres': 'postgresql', 'PostgreSql': 'postgresql',
    # SQL Server
    'MSSQL': 'mssql', 'mssql': 'mssql',
    # Java
    'JAVA': 'java', 'java': 'java',
    # PHP
    'Php': 'php', 'php': 'php',
    # Go
    'Golang': 'golang', 'golang': 'golang',
    # React Native
    'React-Native': 'react native', 'ReactNative': 'react native',
    'react-native': 'react native',
    # Docker
    'docker': 'docker', 'DOCKER': 'docker',
    # Kubernetes
    'K8s': 'kubernetes', 'k8s': 'kubernetes', 'kubernetes': 'kubernetes',
    # AWS
    'Amazon Web Services': 'aws', 'aws': 'aws',
    # Azure
    'azure': 'azure', 'AZURE': 'azure',
    # GCP
    'Google Cloud': 'gcp', 'google cloud': 'gcp', 'gcp': 'gcp',
    # CI/CD
    'CICD': 'ci/cd', 'CI CD': 'ci/cd', 'cicd': 'ci/cd', 'ci/cd': 'ci/cd',
    # DevOps
    'Devops': 'devops', 'devops': 'devops', 'DEVOPS': 'devops',
    # Machine Learning
    'Machine learning': 'machine learning', 'machine learning': 'machine learning',
    'Machine Learning': 'machine learning', 'ML': 'machine learning',
    # AI
    'Artificial Intelligence': 'ai', 'artificial intelligence': 'ai',
    # Agile
    'agile': 'agile', 'AGILE': 'agile',
    # Scrum
    'scrum': 'scrum',
    # HTML/CSS
    'HTML5': 'html', 'html': 'html', 'CSS3': 'css', 'css': 'css',
    # Git
    'GIT': 'git', 'git': 'git',
    # MongoDB
    'mongodb': 'mongodb', 'MongoDb': 'mongodb',
    # Redis
    'redis': 'redis', 'REDIS': 'redis',
    # Elasticsearch
    'ElasticSearch': 'elasticsearch', 'Elastic Search': 'elasticsearch',
    'elasticsearch': 'elasticsearch',
    # Spring
    'SpringBoot': 'spring boot', 'spring boot': 'spring boot',
    # Next.js
    'NextJS': 'next.js', 'Nextjs': 'next.js', 'nextjs': 'next.js',
    # Linux
    'linux': 'linux', 'LINUX': 'linux',
    # OOP
    'Object-Oriented': 'oop', 'object-oriented': 'oop', 'Object Oriented': 'oop',
    # REST/API
    'RESTful': 'restful', 'APIs': 'api',
}

# Build compiled regex patterns (longer patterns first to avoid partial matches)
TECH_PATTERNS = []
for variant, canonical in sorted(_RAW_TECH_MAP.items(), key=lambda x: -len(x[0])):
    try:
        pat = re.compile(r'\b' + re.escape(variant) + r'\b')
        TECH_PATTERNS.append((pat, canonical))
    except re.error:
        pass

# ============================================================
# 3. TRANSLATION (EN → VI)
# ============================================================
try:
    from deep_translator import GoogleTranslator
    _TRANSLATOR_AVAILABLE = True
except ImportError:
    _TRANSLATOR_AVAILABLE = False

try:
    from langdetect import detect, LangDetectException
    _LANGDETECT_AVAILABLE = True
except ImportError:
    _LANGDETECT_AVAILABLE = False


def _is_english(text):
    if not _LANGDETECT_AVAILABLE or not text or len(str(text).strip()) < 20:
        return False
    try:
        return detect(str(text)) == 'en'
    except Exception:
        return False


# Danh sách thuật ngữ cần bảo vệ khi dịch (không dịch)
PROTECTED_TERMS = [
    # Languages
    'c#', 'c++', 'javascript', 'typescript', 'python', 'java', 'php',
    'golang', 'kotlin', 'swift', 'ruby', 'dart', 'rust', 'scala', 'r',
    'html', 'css', 'sql', 'mysql', 'postgresql', 'mssql', 'nosql',
    # Frameworks / Libraries
    'node.js', 'react', 'angular', 'vue.js', '.net', 'asp.net',
    'spring', 'spring boot', 'django', 'flask', 'laravel', 'express',
    'next.js', 'nuxt.js', 'flutter', 'react native', 'electron',
    'fastapi', 'nestjs', 'rails', 'ruby on rails', 'symfony',
    # Tools / Platforms
    'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'github',
    'gitlab', 'jenkins', 'terraform', 'ansible', 'nginx', 'apache',
    'kafka', 'rabbitmq', 'redis', 'mongodb', 'elasticsearch',
    'graphql', 'rest', 'restful', 'api', 'ci/cd', 'devops',
    'linux', 'ubuntu', 'windows', 'macos',
    # Concepts
    'machine learning', 'deep learning', 'ai', 'nlp', 'llm',
    'computer vision', 'data science', 'big data', 'oop',
    'microservices', 'agile', 'scrum', 'kanban',
    'blockchain', 'iot', 'saas', 'paas', 'iaas',
    'frontend', 'backend', 'fullstack', 'full-stack',
    'etl', 'data warehouse', 'power bi', 'tableau',
    'tensorflow', 'pytorch', 'pandas', 'numpy', 'spark',
    'hadoop', 'airflow', 'mlops', 'databricks', 'snowflake',
]
# Sort dài trước để tránh match ngắn trước (vd: "spring boot" trước "spring")
PROTECTED_TERMS.sort(key=len, reverse=True)


def _protect_terms(text):
    """Thay thuật ngữ bằng placeholder trước khi dịch."""
    mapping = {}
    for i, term in enumerate(PROTECTED_TERMS):
        pat = re.compile(re.escape(term), re.IGNORECASE)
        placeholder = f'__TERM{i}__'
        if pat.search(text):
            mapping[placeholder] = term
            text = pat.sub(placeholder, text)
    return text, mapping


def _restore_terms(text, mapping):
    """Khôi phục thuật ngữ từ placeholder sau khi dịch."""
    for placeholder, term in mapping.items():
        text = text.replace(placeholder, term)
    return text


def _translate_chunk(text):
    """Dịch 1 đoạn text (đã protect terms)."""
    try:
        r = GoogleTranslator(source='en', target='vi').translate(text)
        time.sleep(0.2)
        return r or text
    except Exception:
        return text


def _translate_cell(text):
    """Dịch 1 cell từ EN → VI. Giữ nguyên thuật ngữ chuyên ngành."""
    if pd.isna(text):
        return text
    text = str(text).strip()
    if not text or len(text) < 10 or not _is_english(text):
        return text

    # Bảo vệ thuật ngữ
    text, mapping = _protect_terms(text)

    # Dịch (chia chunk nếu quá dài)
    if len(text) > 4500:
        parts = re.split(r'(?<=[.!?])\s+', text)
        results = []
        chunk = ''
        for p in parts:
            if len(chunk) + len(p) > 4500:
                if chunk:
                    results.append(_translate_chunk(chunk))
                chunk = p
            else:
                chunk = (chunk + ' ' + p) if chunk else p
        if chunk:
            results.append(_translate_chunk(chunk))
        translated = ' '.join(results)
    else:
        translated = _translate_chunk(text)

    # Khôi phục thuật ngữ
    return _restore_terms(translated, mapping)


# ============================================================
# 4. PUBLIC FUNCTIONS - Dùng trong main.py
# ============================================================

def clean_special_chars(df):
    """
    Thay ký tự đặc biệt (Unicode) bằng dấu cách cho TẤT CẢ các cột.
    Input/Output: DataFrame
    """
    df = df.copy()
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x if pd.isna(x) else
                                unicodedata.normalize('NFC', str(x)))
        df[col] = df[col].apply(lambda x: _replace_chars(x))
    return df


def clean_tech_terms(df):
    """
    Chuẩn hóa biến thể thuật ngữ công nghệ về 1 dạng duy nhất cho TẤT CẢ các cột.
    Input/Output: DataFrame
    """
    df = df.copy()
    for col in df.columns:
        df[col] = df[col].apply(lambda x: _normalize_terms(x))
    return df


def clean_translate(df, no_translate_cols=None):
    """
    Dịch nội dung tiếng Anh → tiếng Việt, TRỪ các cột trong no_translate_cols.
    Giữ nguyên thuật ngữ chuyên ngành.
    Input/Output: DataFrame
    """
    if not _TRANSLATOR_AVAILABLE:
        print("⚠️  deep_translator chưa cài. Chạy: pip install deep-translator")
        return df

    if no_translate_cols is None:
        no_translate_cols = []

    df = df.copy()
    translate_cols = [c for c in df.columns if c not in no_translate_cols]
    for col in translate_cols:
        non_null = df[col].notna().sum()
        print(f"  Đang dịch [{col}] ({non_null} giá trị)...")
        count = 0
        for idx in df.index:
            val = df.at[idx, col]
            if pd.notna(val) and isinstance(val, str) and len(val.strip()) >= 10:
                original = val
                df.at[idx, col] = _translate_cell(val)
                if df.at[idx, col] != original:
                    count += 1
        print(f"    → Đã dịch {count} cells")
    return df


def clean_lowercase(df):
    """
    Chuyển tất cả nội dung về lowercase cho TẤT CẢ các cột.
    Input/Output: DataFrame
    """
    df = df.copy()
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x if pd.isna(x) else str(x).lower())
    return df


def clean_dataframe(df, no_translate_cols=None, translate=True):
    """
    Hàm tổng hợp: chạy toàn bộ pipeline cleaning trên 1 DataFrame.

    Pipeline:
        1. Chuyển về lowercase
        2. Unicode NFC + thay ký tự đặc biệt (bảo vệ thuật ngữ có . /)
        3. Chuẩn hóa biến thể thuật ngữ công nghệ
        4. Dịch EN → VI (trừ các cột chỉ định, bảo vệ thuật ngữ)

    Args:
        df: DataFrame cần xử lý
        no_translate_cols: list các cột KHÔNG dịch (job_name, position, skills...)
        translate: True/False - có dịch hay không (mặc định True)

    Returns:
        DataFrame đã cleaned
    """
    if no_translate_cols is None:
        no_translate_cols = []

    print("  [1/4] Chuyển về lowercase...")
    df = clean_lowercase(df)

    print("  [2/4] Xử lý ký tự đặc biệt...")
    df = clean_special_chars(df)

    print("  [3/4] Chuẩn hóa thuật ngữ công nghệ...")
    df = clean_tech_terms(df)

    if translate:
        print("  [4/4] Dịch EN → VI (giữ nguyên thuật ngữ)...")
        df = clean_translate(df, no_translate_cols=no_translate_cols)
    else:
        print("  [4/4] Bỏ qua dịch thuật.")

    print("  ✅ Hoàn tất!")
    return df


# ============================================================
# PRIVATE HELPERS
# ============================================================

# Thuật ngữ chứa . hoặc / cần bảo vệ khi xóa dấu . /
_TERMS_WITH_DOT_SLASH = [
    'node.js', 'vue.js', 'next.js', 'nuxt.js', 'react.js', 'angular.js',
    '.net', 'asp.net', 'express.js', 'd3.js', 'three.js', 'nest.js',
    'ci/cd', 'i/o', 'c/c++',
]
_TERMS_WITH_DOT_SLASH.sort(key=len, reverse=True)

# Pre-compile patterns (tối ưu: không compile lại mỗi cell)
_COMPILED_DOT_SLASH = [
    (re.compile(re.escape(term), re.IGNORECASE), f'XPROTECTX{i}X')
    for i, term in enumerate(_TERMS_WITH_DOT_SLASH)
]

# Pre-compile tech normalization: gộp 120+ patterns thành 1 regex duy nhất
_TECH_LOOKUP = {v.lower(): c for v, c in _RAW_TECH_MAP.items()}
_ALL_TECH_RE = re.compile(
    '|'.join(r'\b' + re.escape(v) + r'\b'
             for v in sorted(_RAW_TECH_MAP.keys(), key=len, reverse=True)),
    re.IGNORECASE
)


def _replace_chars(text):
    if pd.isna(text):
        return text
    text = str(text)

    # 1) Bảo vệ thuật ngữ chứa . hoặc / (dùng pre-compiled patterns)
    dot_slash_map = {}
    for pat, placeholder in _COMPILED_DOT_SLASH:
        m = pat.search(text)
        if m:
            dot_slash_map[placeholder] = m.group(0)  # giữ nguyên dạng gốc
            text = pat.sub(placeholder, text)

    # 2) Xóa ký tự đặc biệt Unicode
    for char, repl in SPECIAL_CHARS_MAP.items():
        text = text.replace(char, repl)

    # 3) Xóa dấu . / _ , : ; - ( ) "
    text = text.replace('.', '')
    text = text.replace('/', '')
    text = text.replace('_', ' ')
    text = text.replace(',', ' ')
    text = text.replace(':', ' ')
    text = text.replace(';', ' ')
    text = text.replace('-', ' ')
    text = text.replace('(', ' ')
    text = text.replace(')', ' ')
    text = text.replace('"', ' ')

    # 4) Khôi phục thuật ngữ
    for placeholder, original in dot_slash_map.items():
        text = text.replace(placeholder, original)

    text = re.sub(r'\s+', ' ', text).strip()
    return text


def _normalize_terms(text):
    """Chuẩn hóa biến thể thuật ngữ công nghệ về 1 dạng duy nhất (dùng single regex)."""
    if pd.isna(text):
        return text
    return _ALL_TECH_RE.sub(
        lambda m: _TECH_LOOKUP.get(m.group(0).lower(), m.group(0)),
        str(text)
    )
