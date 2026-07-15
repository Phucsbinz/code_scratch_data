"""
data_processing.py - Công cụ trích xuất thông tin chuyên sâu (Keywords, Salary, Experience).
Sử dụng kết hợp Dictionary-Based và Regex.

v2 - Sửa lỗi nhận diện:
  - Word boundary cho TẤT CẢ patterns (fix false positive: 'scala' ← 'scalable')
  - experience_level chỉ quét từ cột level + job_name (fix career-path pollution)
  - role_category chỉ quét job_name + position + role_responsibilities
  - Thêm 7 dictionaries: DATA_AI, LANGUAGE_REQUIREMENT, METHODOLOGY, WORK_STYLE, EDUCATION, CERTIFICATIONS
  - Tách CLOUD vs DEVOPS, VERSION_CONTROL vs PM_TOOLS
  - Mở rộng SOFT_SKILLS, LANGUAGES
"""

import pandas as pd
import re
import numpy as np

# 1. DANH MỤC TỪ KHÓA MỞ RỘNG
# Định dạng: 'canonical': [(pattern, is_regex), ...]
# Tất cả patterns sẽ được wrap trong word boundary khi matching

ROLE_CATEGORY = {
    'software engineering': [
        ('software engineer', False), ('software developer', False),
        ('lập trình viên', False), ('phát triển phần mềm', False),
        ('kỹ sư phần mềm', False), ('web developer', False),
        ('fullstack', False), ('full stack', False),
        ('frontend developer', False), ('backend developer', False),
        ('mobile developer', False), ('android developer', False),
        ('ios developer', False),
    ],
    'data engineering': [
        ('data engineer', False), ('kỹ sư dữ liệu', False),
        ('big data', False), ('data pipeline', False),
        ('data architect', False), ('data platform', False),
    ],
    'data science': [
        ('data science', False), ('data scientist', False),
        ('khoa học dữ liệu', False),
    ],
    'ai/ml engineering': [
        ('ai engineer', False), ('ml engineer', False),
        ('machine learning engineer', False), ('deep learning engineer', False),
        ('nlp engineer', False), ('trí tuệ nhân tạo', False),
        ('ai software engineer', False),
    ],
    'data analysis': [
        ('data analyst', False), ('phân tích dữ liệu', False),
        ('bi analyst', False), ('business intelligence', False),
    ],
    'business analysis': [
        ('business analyst', False), ('phân tích nghiệp vụ', False),
        ('business development', False),
        (r'\bba\b', True),
    ],
    'quality assurance': [
        ('quality assurance', False), ('quality control', False),
        ('tester', False), ('kiểm thử', False),
        ('automation test', False), ('manual test', False),
        ('test engineer', False), ('qa engineer', False),
        ('qc engineer', False),
        (r'\bqa\b', True), (r'\bqc\b', True), (r'\bqaqc\b', True),
    ],
    'cybersecurity': [
        ('bảo mật', False), ('an ninh mạng', False),
        ('an toàn thông tin', False),
        ('security engineer', False), ('security analyst', False),
        ('pentest', False), ('soc analyst', False),
        ('data security', False), ('information security', False),
        ('quản trị hệ thống', False),
    ],
    'devops/sre': [
        ('devops', False), (r'\bsre\b', True),
        ('cloud engineer', False), ('infrastructure engineer', False),
    ],
    'embedded system': [
        ('embedded', False), ('nhúng', False), ('firmware', False),
        (r'\biot\b', True),
    ],
    'product management': [
        ('product manager', False), ('product owner', False),
    ],
    'project management': [
        ('project manager', False), ('quản lý dự án', False),
        (r'\bpm\b', True),
    ],
}

EXPERIENCE_LEVEL = {
    'intern': [('intern', False), ('thực tập', False), ('internship', False), ('sinh viên', False)],
    'fresher': [
        ('fresher', False), ('mới tốt nghiệp', False), ('entry level', False),
        ('fresh graduate', False), ('mới ra trường', False), ('0 1 year', False),
        ('không yêu cầu kinh nghiệm', False), ('no experience required', False),
    ],
    'junior': [('junior', False), (r'1\s*[-–]\s*2\s*(?:năm|year)', True), (r'dưới 2 năm', True)],
    'middle': [
        ('middle', False), ('mid level', False), ('mid senior', False),
        ('intermediate', False), (r'2\s*[-–]\s*5\s*(?:năm|year)', True),
        (r'3\+?\s*(?:năm|year)', True),
    ],
    'senior': [
        ('senior', False), ('chuyên viên cao cấp', False), ('chuyên gia', False),
        (r'5\+?\s*(?:năm|year)', True), (r'trên 5 năm', True),
    ],
    'lead/principal': [
        ('lead', False), ('principal', False), ('trưởng nhóm', False),
        ('techlead', False), ('tech lead', False), ('team lead', False),
        ('staff engineer', False),
    ],
    'director': [('director', False), ('giám đốc', False), ('phó giám đốc', False)],
    'manager': [('manager', False), ('trưởng phòng', False), ('phó phòng', False), ('quản lý', False)],
}

LANGUAGES = {
    'python': [('python', False)],
    'java': [(r'\bjava\b', True)],
    'javascript': [('javascript', False)],
    'typescript': [('typescript', False)],
    'c#': [(r'c#', True), ('c sharp', False)],
    'c++': [(r'c\+\+', True), (r'\bcpp\b', True), (r'c/c\+\+', True)],
    'php': [(r'\bphp\b', True)],
    'golang': [('golang', False), (r'\bgo\b(?!\s*to\b)', True)],
    'ruby': [(r'\bruby\b', True)],
    'swift': [(r'swift\s+(?:programming|language|developer|ios)', True)],
    'kotlin': [('kotlin', False)],
    'sql': [(r'\bsql\b', True)],
    'rust': [(r'\brust\b', True)],
    'r': [(r'\br\b(?=\s*[,\s])', True), (r'python\s*[,/]\s*r\b', True), (r'\br\s*[,/]\s*(?:python|sql)', True)],
    'scala': [(r'\bscala\b', True)],
    'dart': [(r'\bdart\b', True)],
    'html/css': [('html', False), ('css', False), ('htmlcss', False)],
    'shell/bash': [('powershell', False), ('bash', False), ('shell script', False)],
    'apex': [(r'\bapex\b', True)],
}

FRAMEWORKS = {
    'react': [(r'\breact\b', True), ('reactjs', False)],
    'react native': [('react native', False), ('react-native', False)],
    'angular': [('angular', False)],
    'vue.js': [('vue', False), ('vuejs', False), (r'vue\.js', True)],
    'next.js': [('nextjs', False), (r'next\.js', True)],
    'node.js': [(r'\bnodejs\b', True), (r'node\.js', True)],
    'nest.js': [('nestjs', False), (r'nest\.js', True)],
    'spring boot': [('spring boot', False), ('springboot', False)],
    'spring': [(r'\bspring\b(?!\s*boot)', True)],
    '.net': [(r'\.net\b', True), ('dotnet', False), (r'asp\.net', True)],
    'django': [('django', False)],
    'flask': [(r'\bflask\b', True)],
    'fastapi': [('fastapi', False)],
    'laravel': [('laravel', False)],
    'flutter': [('flutter', False)],
    'express': [(r'\bexpress\b', True), ('expressjs', False)],
    'langchain': [('langchain', False)],
    'langgraph': [('langgraph', False)],
}

DATA_AI = {
    'machine learning': [('machine learning', False)],
    'deep learning': [('deep learning', False)],
    'nlp': [(r'\bnlp\b', True), ('natural language processing', False)],
    'computer vision': [('computer vision', False)],
    'llm': [(r'\bllm\b', True), ('large language model', False)],
    'transformer': [(r'\btransformer\b', True)],
    'tensorflow': [('tensorflow', False)],
    'pytorch': [('pytorch', False)],
    'scikit-learn': [('scikit-learn', False), ('scikit learn', False), ('sklearn', False)],
    'keras': [(r'\bkeras\b', True)],
    'hugging face': [('hugging face', False), ('huggingface', False)],
    'langchain': [('langchain', False)],
    'llamaindex': [('llamaindex', False), ('llama index', False)],
    'mlops': [('mlops', False)],
    'rag': [(r'\brag\b', True), ('retrieval augmented generation', False)],
    'power bi': [('power bi', False)],
    'tableau': [('tableau', False)],
    'spark': [(r'\bspark\b', True)],
    'airflow': [('airflow', False)],
    'data warehouse': [('data warehouse', False), ('data warehousing', False)],
    'etl': [(r'\betl\b', True)],
    'dbt': [(r'\bdbt\b', True)],
    'ocr': [(r'\bocr\b', True)],
}

DATABASES = {
    'mysql': [('mysql', False)],
    'postgresql': [('postgres', False), ('postgresql', False)],
    'mongodb': [('mongo', False), ('mongodb', False)],
    'redis': [('redis', False)],
    'oracle': [(r'\boracle\b', True)],
    'sql server': [('sql server', False), ('mssql', False)],
    'elasticsearch': [('elasticsearch', False), ('elastic search', False)],
    'firebase': [('firebase', False)],
    'pinecone': [('pinecone', False)],
    'milvus': [('milvus', False)],
    'weaviate': [('weaviate', False)],
    'qdrant': [('qdrant', False)],
    'dataverse': [('dataverse', False)],
}

CLOUD = {
    'aws': [(r'\baws\b', True)],
    'azure': [('azure', False)],
    'gcp': [(r'\bgcp\b', True), ('google cloud', False)],
}

DEVOPS_TOOLS = {
    'docker': [('docker', False)],
    'kubernetes': [('kubernetes', False), (r'\bk8s\b', True)],
    'jenkins': [('jenkins', False)],
    'ci/cd': [('ci/cd', False), ('cicd', False)],
    'terraform': [('terraform', False)],
    'linux': [('linux', False)],
    'nginx': [('nginx', False)],
    'microservices': [('microservices', False)],
    'rabbitmq': [('rabbitmq', False)],
    'kafka': [(r'\bkafka\b', True)],
}

VERSION_CONTROL = {
    'git': [(r'\bgit\b(?!hub|lab)', True)],
    'github': [('github', False)],
    'gitlab': [('gitlab', False)],
    'bitbucket': [('bitbucket', False)],
    'svn': [(r'\bsvn\b', True), ('subversion', False)],
}

PM_TOOLS = {
    'jira': [('jira', False)],
    'confluence': [('confluence', False)],
    'trello': [('trello', False)],
    'notion': [(r'\bnotion\b', True)],
    'asana': [('asana', False)],
}

SOFT_SKILLS = {
    'communication': [
        ('communication', False), ('giao tiếp', False),
        ('trao đổi thông tin', False), ('kỹ năng truyền đạt', False),
    ],
    'teamwork': [
        ('teamwork', False), ('làm việc nhóm', False),
        ('team work', False), ('phối hợp', False), ('collaboration', False),
        ('cooperat', False),
    ],
    'problem solving': [
        ('problem solving', False), ('giải quyết vấn đề', False),
        ('xử lý vấn đề', False), ('xử lý tình huống', False),
    ],
    'critical thinking': [
        ('critical thinking', False), ('tư duy phản biện', False),
        ('tư duy hệ thống', False), ('systematic think', False),
    ],
    'time management': [
        ('time management', False), ('quản lý thời gian', False),
        ('sắp xếp công việc', False), ('lập kế hoạch', False),
    ],
    'leadership': [
        ('leadership', False), ('lãnh đạo', False), ('dẫn dắt', False),
        ('people management', False), ('quản lý đội nhóm', False),
        ('điều phối', False),
    ],
    'presentation': [
        ('presentation', False), ('thuyết trình', False), ('trình bày', False),
        ('diễn giải', False), ('trình bày vấn đề', False),
    ],
    'analytical': [
        ('analytical', False), ('phân tích', False), ('tư duy logic', False),
        ('logical thinking', False), ('tư duy phân tích', False),
        ('detail oriented', False), ('tỉ mỉ', False), ('chú ý chi tiết', False),
        ('attention to detail', False),
    ],
    'creativity': [
        ('creativity', False), ('sáng tạo', False),
        ('creative', False), ('innovation', False),
    ],
    'mentoring': [
        ('mentoring', False), ('đào tạo', False), ('coaching', False),
        ('hướng dẫn', False), ('chia sẻ kiến thức', False),
        ('knowledge sharing', False), ('training', False),
    ],
    'negotiation': [
        ('negotiation', False), ('đàm phán', False),
        ('thương lượng', False),
    ],
    'adaptability': [
        ('adaptability', False), ('thích nghi', False), ('linh hoạt', False),
        ('flexible', False), ('adapt', False), ('học hỏi', False),
        ('willingness to learn', False), ('tinh thần học hỏi', False),
    ],
    'work independently': [
        ('work independently', False), ('làm việc độc lập', False),
        ('tự chủ', False), ('autonomy', False), ('self driven', False),
        ('chủ động', False), ('proactive', False),
    ],
    'work under pressure': [
        ('work under pressure', False), ('chịu áp lực', False),
        ('chịu được áp lực', False), ('áp lực cao', False),
    ],
    'responsibility': [
        ('responsibility', False), ('trách nhiệm', False),
        ('tinh thần trách nhiệm', False), ('ownership', False),
    ],
}

LANGUAGE_REQUIREMENT = {
    'english': [
        ('english', False), ('tiếng anh', False),
        (r'\btoeic\b', True), (r'\bielts\b', True), (r'\btoefl\b', True),
        ('english communication', False), ('english proficiency', False),
        ('giao tiếp tiếng anh', False), ('đọc hiểu tiếng anh', False),
        ('sử dụng tiếng anh', False),
    ],
    'japanese': [
        ('japanese', False), ('tiếng nhật', False),
        (r'\bjlpt\b', True), (r'\bn[1-5]\b', True),
        ('nihongo', False),
    ],
    'korean': [
        ('korean', False), ('tiếng hàn', False),
        (r'\btopik\b', True),
    ],
    'chinese': [
        ('chinese', False), ('tiếng trung', False), ('tiếng hoa', False),
        (r'\bhsk\b', True), ('mandarin', False),
    ],
    'french': [('french', False), ('tiếng pháp', False)],
}

METHODOLOGY = {
    'agile': [('agile', False)],
    'scrum': [('scrum', False)],
    'kanban': [('kanban', False)],
    'waterfall': [('waterfall', False)],
    'devops': [('devops', False), ('devsecops', False)],
    'lean': [(r'\blean\b', True)],
    'safe': [(r'\bsafe\b', True), ('scaled agile', False)],
    'sdlc': [(r'\bsdlc\b', True), ('software development life cycle', False), ('vòng đời phát triển', False)],
    'ddd': [(r'\bddd\b', True), ('domain driven design', False)],
}

WORK_STYLE = {
    'code review': [('code review', False)],
    'rest api': [('restful', False), ('rest api', False), ('restful api', False)],
    'graphql': [('graphql', False)],
    'solid': [(r'\bsolid\b', True)],
    'clean code': [('clean code', False), ('code clean', False)],
    'documentation': [('documentation', False), ('tài liệu', False), ('viết tài liệu', False)],
    'pair programming': [('pair programming', False)],
    'tdd': [(r'\btdd\b', True), ('test driven', False)],
    'bdd': [(r'\bbdd\b', True), ('behavior driven', False)],
    'design patterns': [('design pattern', False), ('mô hình thiết kế', False)],
    'oop': [(r'\boop\b', True), ('object oriented', False), ('hướng đối tượng', False)],
    'unit test': [('unit test', False)],
    'system design': [('system design', False), ('thiết kế hệ thống', False)],
    'remote/hybrid': [('remote', False), ('hybrid', False), ('work from home', False), ('làm việc từ xa', False)],
}

EDUCATION = {
    "bachelor's": [
        ("bachelor", False), ('đại học', False), ('university', False),
        ('tốt nghiệp đại học', False), ('trình độ đại học', False),
        ('bằng đại học', False), ('cử nhân', False),
    ],
    'college': [
        ('college', False), ('cao đẳng', False),
        ('trung cấp', False), ('vocational', False),
    ],
    "master's/phd": [
        ("master", False), ('thạc sĩ', False), ('tiến sĩ', False),
        (r'\bphd\b', True), ('postgraduate', False), ('sau đại học', False),
    ],
    'computer science': [
        ('computer science', False), ('khoa học máy tính', False),
        ('công nghệ thông tin', False), ('cntt', False),
        ('kỹ thuật phần mềm', False), ('information technology', False),
        ('software engineering', False),
    ],
}

CERTIFICATIONS = {
    'cissp': [(r'\bcissp\b', True)],
    'cism': [(r'\bcism\b', True)],
    'ceh': [(r'\bceh\b', True)],
    'oscp': [(r'\boscp\b', True)],
    'security+': [('security+', False)],
    'aws certified': [('aws certified', False), ('aws security specialty', False), ('aws solutions architect', False)],
    'azure certified': [('azure certified', False), ('azure fundamentals', False)],
    'gcp certified': [('gcp certified', False), ('google cloud certified', False)],
    'cfa': [(r'\bcfa\b', True)],
    'frm': [(r'\bfrm\b', True)],
    'pmp': [(r'\bpmp\b', True)],
    'istqb': [(r'\bistqb\b', True)],
    'scrum master': [('scrum master', False), (r'\bcsm\b', True), (r'\bpsm\b', True)],
    'itil': [(r'\bitil\b', True)],
    'comptia': [('comptia', False), ('comptiaa+', False)],
    'ccna/ccnp': [(r'\bccna\b', True), (r'\bccnp\b', True)],
    'iso 27001': [('iso27001', False), ('iso 27001', False)],
    'data science cert': [('data science certification', False), ('machine learning certification', False)],
}

# 1b. BIÊN DỊCH TRƯỚC REGEX (tối ưu tốc độ)

def _build_compiled_mapping(mapping):
    """Pre-compile tất cả patterns trong mapping thành 1 regex duy nhất per keyword."""
    compiled = {}
    for canonical, patterns in mapping.items():
        parts = []
        for pattern_str, is_regex in patterns:
            if is_regex:
                parts.append(f'(?:{pattern_str})')
            else:
                escaped = re.escape(pattern_str.lower())
                parts.append(r'(?:(?:^|\b|(?<=\s))' + escaped + r'(?:\b|$|(?=\s)))')
        compiled[canonical] = re.compile('|'.join(parts), re.IGNORECASE)
    return compiled


_C_ROLE = _build_compiled_mapping(ROLE_CATEGORY)
_C_EXPERIENCE = _build_compiled_mapping(EXPERIENCE_LEVEL)
_C_LANGUAGES = _build_compiled_mapping(LANGUAGES)
_C_FRAMEWORKS = _build_compiled_mapping(FRAMEWORKS)
_C_DATA_AI = _build_compiled_mapping(DATA_AI)
_C_DATABASES = _build_compiled_mapping(DATABASES)
_C_CLOUD = _build_compiled_mapping(CLOUD)
_C_DEVOPS = _build_compiled_mapping(DEVOPS_TOOLS)
_C_VERSION_CONTROL = _build_compiled_mapping(VERSION_CONTROL)
_C_PM_TOOLS = _build_compiled_mapping(PM_TOOLS)
_C_SOFT_SKILLS = _build_compiled_mapping(SOFT_SKILLS)
_C_LANGUAGE_REQ = _build_compiled_mapping(LANGUAGE_REQUIREMENT)
_C_METHODOLOGY = _build_compiled_mapping(METHODOLOGY)
_C_WORK_STYLE = _build_compiled_mapping(WORK_STYLE)
_C_EDUCATION = _build_compiled_mapping(EDUCATION)
_C_CERTIFICATIONS = _build_compiled_mapping(CERTIFICATIONS)

# 2. HÀM TRÍCH XUẤT NÂNG CAO

def extract_salary(text):
    """Trích xuất khoảng lương từ text."""
    if not text:
        return None
    res = {}

    # VND dạng "20 - 35M" hoặc "20 35m vnd"
    vnd_m = re.findall(r'(\d+)\s*[-–]\s*(\d+)\s*m\s*(?:vnd|vnđ)', text, re.IGNORECASE)
    if vnd_m:
        res['salary_min'] = int(vnd_m[0][0]) * 1000000
        res['salary_max'] = int(vnd_m[0][1]) * 1000000
        res['currency'] = 'VND'
        return res

    # VND dạng "15 - 25 Tr" hoặc "15 - 25 triệu"
    trieu = re.findall(r'(\d+)\s*[-–]\s*(\d+)\s*(?:triệu|tr\b)', text, re.IGNORECASE)
    if trieu:
        res['salary_min'] = int(trieu[0][0]) * 1000000
        res['salary_max'] = int(trieu[0][1]) * 1000000
        res['currency'] = 'VND'
        return res

    # VND dạng "up to 45,000,000" hoặc "lên tới 45000000"
    vnd_full = re.findall(r'(?:up to|lên tới|đến)\s*([\d,. ]+)\s*(?:vnd|vnđ|đồng)', text, re.IGNORECASE)
    if vnd_full:
        cleaned_val = re.sub(r'[,.\s]', '', vnd_full[0]).strip()
        if cleaned_val and cleaned_val.isdigit():
            val = int(cleaned_val)
            if val > 1000:  # loại bỏ số nhỏ vô nghĩa
                res['salary_max'] = val
                res['currency'] = 'VND'
                return res

    # USD dạng "1,000 USD" hoặc "$1000"
    usd = re.findall(r'(\d[\d,]*)\s*(?:usd|\$)', text, re.IGNORECASE)
    if usd:
        val = int(re.sub(r'[,]', '', usd[0]))
        res['salary_max'] = val
        res['currency'] = 'USD'
        return res

    # USD dạng "xxx - yyy usd"
    usd_range = re.findall(r'(\d+)\s*[-–]\s*(\d+)\s*(?:usd|\$)', text, re.IGNORECASE)
    if usd_range:
        res['salary_min'] = int(usd_range[0][0])
        res['salary_max'] = int(usd_range[0][1])
        res['currency'] = 'USD'
        return res

    return None


def extract_experience(text):
    """Trích xuất số năm kinh nghiệm tối thiểu."""
    if not text:
        return None
    # Patterns: "3+ năm", "3 năm", "3-5 năm", "3+ years", "3 years"
    nums = re.findall(r'(\d+)\s*[+]?\s*(?:năm|year)', text, re.IGNORECASE)
    if nums:
        return int(nums[0])
    # Pattern: "tối thiểu X năm" đã được bắt ở trên
    return None


def _match_keywords(text, compiled_mapping):
    """
    Tìm từ khóa trong text dựa trên compiled mapping (pre-compiled regex).
    TẤT CẢ patterns đều sử dụng word boundary để tránh false positive.
    """
    if not text:
        return None
    found = []
    for canonical, pattern in compiled_mapping.items():
        if pattern.search(text):
            found.append(canonical)
    return found if found else None


# 3. GIAO DIỆN CÔNG KHAI

def extract_keywords(df):
    """
    Trích xuất từ khóa từ DataFrame đã cleaned.
    
    Chiến lược quét khác nhau cho từng loại thông tin:
    - role_category: chỉ từ job_name + position + role_responsibilities
    - experience_level: chỉ từ level + job_name  
    - tech stack (languages, frameworks...): từ full text (trừ benefits)
    - soft skills, language_req...: từ skills_qualifications
    - salary, experience: từ full text
    """
    # Xác định các cột quét
    all_cols = list(df.columns)
    cols_lower = {c: c.lower() for c in all_cols}

    # Cột role: job_name, position, role_responsibilities, description
    role_cols = [c for c in all_cols if any(kw in cols_lower[c] for kw in ['job_name', 'position', 'role_responsibilities', 'description'])]
    if not role_cols:
        role_cols = [c for c in all_cols if cols_lower[c] in ['job_name', 'position']]

    # Cột level: level + job_name + requirements + skills (để bắt "3+ years", "senior level")
    # KHÔNG bao gồm benefits (tránh career path pollution)
    level_cols = [c for c in all_cols if any(kw in cols_lower[c] for kw in [
        'level', 'job_name', 'requirement', 'skill', 'qualification',
        'description', 'role_responsibilities', 'years of experience',
    ]) and not any(excl in cols_lower[c] for excl in ['benefit', 'welfare', 'reason'])]

    # Cột tech: tất cả trừ benefits
    tech_cols = [c for c in all_cols if not any(kw in cols_lower[c] for kw in ['benefit', 'welfare', 'phúc lợi', 'reason_you_like', 'three_reasons'])]

    # Cột kỹ năng mềm + yêu cầu ngôn ngữ: mở rộng quét từ nhiều cột hơn
    # Bao gồm: skills, requirements, description, role_responsibilities, educational level
    # KHÔNG bao gồm: benefits, reasons (tránh nhiễu từ phúc lợi)
    skill_cols = [c for c in all_cols if any(kw in cols_lower[c] for kw in [
        'skill', 'qualification', 'requirement', 'role_responsibilities',
        'description', 'job_name', 'position', 'educational',
    ]) and not any(excl in cols_lower[c] for excl in ['benefit', 'welfare', 'reason'])]
    if not skill_cols:
        skill_cols = tech_cols

    # Cột full text (để quét salary, experience)
    full_cols = all_cols

    print(f"  Cột quét Role:   {role_cols}")
    print(f"  Cột quét Level:  {level_cols}")
    print(f"  Cột quét Tech:   {tech_cols}")
    print(f"  Cột quét Skills: {skill_cols}")

    # Tạo văn bản tổng hợp cho mỗi nhóm
    def combine_cols(cols):
        return df[cols].fillna("").astype(str).agg(" ".join, axis=1).str.lower()

    role_text = combine_cols(role_cols)
    level_text = combine_cols(level_cols)
    tech_text = combine_cols(tech_cols)
    skill_text = combine_cols(skill_cols)
    full_text = combine_cols(full_cols)

    res_df = pd.DataFrame(index=df.index)

    # Vai trò và Cấp bậc
    print("    - Đang quét Role & Level...")
    res_df['role_category'] = role_text.apply(lambda x: _match_keywords(x, _C_ROLE))
    res_df['experience_level'] = level_text.apply(lambda x: _match_keywords(x, _C_EXPERIENCE))

    # Công nghệ (quét trên tech_text — tất cả trừ phúc lợi)
    print("    - Đang quét Tech Stack...")
    res_df['languages'] = tech_text.apply(lambda x: _match_keywords(x, _C_LANGUAGES))
    res_df['frameworks'] = tech_text.apply(lambda x: _match_keywords(x, _C_FRAMEWORKS))
    res_df['data_ai'] = tech_text.apply(lambda x: _match_keywords(x, _C_DATA_AI))
    res_df['databases'] = tech_text.apply(lambda x: _match_keywords(x, _C_DATABASES))
    res_df['cloud'] = tech_text.apply(lambda x: _match_keywords(x, _C_CLOUD))
    res_df['devops_tools'] = tech_text.apply(lambda x: _match_keywords(x, _C_DEVOPS))

    # Công cụ làm việc
    print("    - Đang quét Work Tools (Git, Jira...)...")
    res_df['version_control'] = tech_text.apply(lambda x: _match_keywords(x, _C_VERSION_CONTROL))
    res_df['pm_tools'] = skill_text.apply(lambda x: _match_keywords(x, _C_PM_TOOLS))

    # Kỹ năng mềm và các thông tin khác (quét trên skill_text)
    print("    - Đang quét Soft Skills & Requirements...")
    res_df['soft_skills'] = skill_text.apply(lambda x: _match_keywords(x, _C_SOFT_SKILLS))
    res_df['language_requirement'] = skill_text.apply(lambda x: _match_keywords(x, _C_LANGUAGE_REQ))
    res_df['methodology'] = skill_text.apply(lambda x: _match_keywords(x, _C_METHODOLOGY))
    res_df['work_style'] = skill_text.apply(lambda x: _match_keywords(x, _C_WORK_STYLE))
    res_df['education'] = skill_text.apply(lambda x: _match_keywords(x, _C_EDUCATION))
    res_df['certifications'] = skill_text.apply(lambda x: _match_keywords(x, _C_CERTIFICATIONS))

    # Lương và Kinh nghiệm (quét toàn bộ văn bản)
    print("    - Đang trích xuất Lương & Kinh nghiệm...")
    salary_info = full_text.apply(extract_salary)
    res_df['salary_min'] = salary_info.apply(lambda x: x.get('salary_min') if x else np.nan)
    res_df['salary_max'] = salary_info.apply(lambda x: x.get('salary_max') if x else np.nan)
    res_df['currency'] = salary_info.apply(lambda x: x.get('currency') if x else np.nan)
    res_df['years_of_exp'] = full_text.apply(extract_experience)

    return res_df
