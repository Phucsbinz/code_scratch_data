import pandas as pd
import re
import sys
import io
import os
import json
from collections import Counter, OrderedDict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to sys.path to support imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
import config

BASE_DIR = config.RAW_DATA_DIR

files = {
    'jobs_dev_top_final.csv': 'TopDev',
    'jobs_itviec_final.csv': 'ITviec',
    'jobs_vietnamworks.csv': 'VietnamWorks_sync',
    'jobs_vietnamworks_async_parallel.csv': 'VietnamWorks_async'
}

result = OrderedDict()

# ============================================================
# 1. Analyze special characters per column per file
# ============================================================
print("Analyzing special characters...")

for fname, label in files.items():
    print(f"  Processing: {fname}")
    df = pd.read_csv(os.path.join(BASE_DIR, fname), encoding='utf-8')
    
    file_result = OrderedDict()
    file_result['source'] = label
    file_result['shape'] = {'rows': int(df.shape[0]), 'cols': int(df.shape[1])}
    file_result['columns'] = list(df.columns)
    file_result['null_counts'] = {col: int(df[col].isnull().sum()) for col in df.columns}
    
    # Special characters per column
    special_chars = OrderedDict()
    for col in df.columns:
        all_text = ' '.join(df[col].dropna().astype(str).tolist())
        chars = re.findall(r'[^\w\s\u00C0-\u024F\u1EA0-\u1EFF]', all_text)
        char_counts = Counter(chars)
        if char_counts:
            col_chars = []
            for ch, cnt in char_counts.most_common(30):
                col_chars.append({
                    'char': ch,
                    'unicode': f'U+{ord(ch):04X}',
                    'count': cnt
                })
            special_chars[col] = col_chars
    file_result['special_characters'] = special_chars
    
    result[fname] = file_result

# ============================================================
# 2. Unique values in key columns
# ============================================================
print("Analyzing unique values in key columns...")

# --- TopDev ---
df = pd.read_csv(os.path.join(BASE_DIR, 'jobs_dev_top_final.csv'), encoding='utf-8')
result['jobs_dev_top_final.csv']['unique_values'] = OrderedDict()
result['jobs_dev_top_final.csv']['unique_values']['position'] = sorted(df['position'].dropna().unique().tolist())
result['jobs_dev_top_final.csv']['unique_values']['level'] = sorted(df['level'].dropna().unique().tolist())

# --- ITviec ---
df = pd.read_csv(os.path.join(BASE_DIR, 'jobs_itviec_final.csv'), encoding='utf-8')
result['jobs_itviec_final.csv']['unique_values'] = OrderedDict()
result['jobs_itviec_final.csv']['unique_values']['position'] = sorted(df['position'].dropna().unique().tolist())

# Skills (split by underscore _ since ITviec uses _ as separator)
all_skills = []
for v in df['skills'].dropna():
    # ITviec skills are separated by underscore groups, keep as-is for now
    all_skills.append(str(v))
skill_counts = Counter(all_skills)
result['jobs_itviec_final.csv']['unique_values']['skills_top80'] = [
    {'skill': s, 'count': c} for s, c in skill_counts.most_common(80)
]

# Domain company
all_domains = []
for v in df['domain_company'].dropna():
    parts = re.split(r'[,;|]', str(v))
    for p in parts:
        p = p.strip()
        if p:
            all_domains.append(p)
domain_counts = Counter(all_domains)
result['jobs_itviec_final.csv']['unique_values']['domain_company'] = [
    {'domain': d, 'count': c} for d, c in domain_counts.most_common(50)
]

# --- VietnamWorks sync & async ---
for fname in ['jobs_vietnamworks.csv', 'jobs_vietnamworks_async_parallel.csv']:
    df = pd.read_csv(os.path.join(BASE_DIR, fname), encoding='utf-8')
    result[fname]['unique_values'] = OrderedDict()
    
    result[fname]['unique_values']['Position'] = sorted(df['Position'].dropna().unique().tolist())
    
    # Skills (comma-separated)
    all_skills = []
    for v in df['Skills'].dropna():
        parts = re.split(r'[,;|]', str(v))
        for p in parts:
            p = p.strip()
            if p:
                all_skills.append(p)
    skill_counts = Counter(all_skills)
    result[fname]['unique_values']['Skills_top80'] = [
        {'skill': s, 'count': c} for s, c in skill_counts.most_common(80)
    ]
    
    result[fname]['unique_values']['Level'] = sorted(df['Level'].dropna().unique().tolist())
    result[fname]['unique_values']['Years_of_Experience'] = sorted(df['Years of Experience'].dropna().unique().tolist())
    result[fname]['unique_values']['Educational_Level'] = sorted(df['Educational Level'].dropna().unique().tolist())
    
    # Job Title samples (first 50)
    result[fname]['unique_values']['Job_Title_sample50'] = sorted(df['Job Title'].dropna().unique().tolist())[:50]

# ============================================================
# 3. Technology term variants across all files
# ============================================================
print("Analyzing technology term variants...")

tech_patterns = {
    'C#': [r'\bC#\b', r'\bC-Sharp\b', r'\bCSharp\b', r'\bC Sharp\b', r'\bc#\b', r'\bcsharp\b', r'\bC-sharp\b'],
    'C++': [r'\bC\+\+\b', r'\bCPP\b', r'\bcpp\b', r'\bC\s*\+\s*\+\b'],
    'JavaScript': [r'\bJavaScript\b', r'\bJavascript\b', r'\bjavascript\b', r'\bJS\b', r'\bJs\b', r'\bjs\b'],
    'TypeScript': [r'\bTypeScript\b', r'\bTypescript\b', r'\btypescript\b', r'\bTS\b'],
    'Python': [r'\bPython\b', r'\bpython\b', r'\bPYTHON\b'],
    'Node.js': [r'\bNode\.js\b', r'\bNodeJS\b', r'\bNodejs\b', r'\bnode\.js\b', r'\bnodejs\b', r'\bNode\.JS\b', r'\bNODEJS\b'],
    'React': [r'\bReact\b', r'\bReactJS\b', r'\bReact\.js\b', r'\breact\b', r'\breactjs\b', r'\breact\.js\b'],
    'Angular': [r'\bAngular\b', r'\bAngularJS\b', r'\bAngular\.js\b', r'\bangular\b', r'\bangularjs\b'],
    'Vue': [r'\bVue\b', r'\bVuejs\b', r'\bVue\.js\b', r'\bVueJS\b', r'\bvue\b', r'\bvuejs\b', r'\bvue\.js\b'],
    '.NET': [r'\.NET\b', r'\bDotNet\b', r'\bdotnet\b', r'\bDot Net\b', r'\bASP\.NET\b', r'\basp\.net\b'],
    'SQL': [r'\bSQL\b', r'\bsql\b', r'\bMySQL\b', r'\bmysql\b', r'\bMSSQL\b', r'\bmssql\b', r'\bPostgreSQL\b', r'\bpostgresql\b', r'\bPostgres\b', r'\bpostgres\b'],
    'Java': [r'\bJava\b', r'\bjava\b', r'\bJAVA\b'],
    'PHP': [r'\bPHP\b', r'\bphp\b', r'\bPhp\b'],
    'Ruby': [r'\bRuby\b', r'\bruby\b', r'\bRuby on Rails\b', r'\bRails\b', r'\brails\b'],
    'Go/Golang': [r'\bGolang\b', r'\bgolang\b', r'\bGo\b', r'\bgo\b'],
    'Kotlin': [r'\bKotlin\b', r'\bkotlin\b'],
    'Swift': [r'\bSwift\b', r'\bswift\b'],
    'Flutter': [r'\bFlutter\b', r'\bflutter\b'],
    'React Native': [r'\bReact Native\b', r'\bReact-Native\b', r'\breact native\b', r'\breact-native\b', r'\bReactNative\b'],
    'Docker': [r'\bDocker\b', r'\bdocker\b', r'\bDOCKER\b'],
    'Kubernetes': [r'\bKubernetes\b', r'\bkubernetes\b', r'\bK8s\b', r'\bk8s\b'],
    'AWS': [r'\bAWS\b', r'\baws\b', r'\bAmazon Web Services\b'],
    'Azure': [r'\bAzure\b', r'\bazure\b', r'\bAZURE\b'],
    'GCP': [r'\bGCP\b', r'\bgcp\b', r'\bGoogle Cloud\b', r'\bgoogle cloud\b'],
    'CI/CD': [r'\bCI/CD\b', r'\bCI CD\b', r'\bCICD\b', r'\bci/cd\b', r'\bcicd\b'],
    'DevOps': [r'\bDevOps\b', r'\bDevops\b', r'\bdevops\b', r'\bDEVOPS\b', r'\bDev Ops\b'],
    'Machine Learning': [r'\bMachine Learning\b', r'\bmachine learning\b', r'\bML\b', r'\bml\b', r'\bMachine learning\b'],
    'AI': [r'\bAI\b', r'\bai\b', r'\bArtificial Intelligence\b', r'\bartificial intelligence\b'],
    'Agile': [r'\bAgile\b', r'\bagile\b', r'\bAGILE\b'],
    'Scrum': [r'\bScrum\b', r'\bscrum\b'],
    'HTML': [r'\bHTML\b', r'\bhtml\b', r'\bHTML5\b'],
    'CSS': [r'\bCSS\b', r'\bcss\b', r'\bCSS3\b'],
    'Git': [r'\bGit\b', r'\bgit\b', r'\bGIT\b', r'\bGitHub\b', r'\bGitLab\b'],
    'MongoDB': [r'\bMongoDB\b', r'\bmongodb\b', r'\bMongo\b', r'\bmongo\b', r'\bMongoDb\b'],
    'Redis': [r'\bRedis\b', r'\bredis\b', r'\bREDIS\b'],
    'Elasticsearch': [r'\bElasticsearch\b', r'\belasticsearch\b', r'\bElastic Search\b', r'\bElasticSearch\b', r'\bELASTICSEARCH\b'],
    'Spring': [r'\bSpring\b', r'\bSpring Boot\b', r'\bSpringBoot\b', r'\bspring\b', r'\bspring boot\b'],
    'Django': [r'\bDjango\b', r'\bdjango\b'],
    'Laravel': [r'\bLaravel\b', r'\blaravel\b'],
    'Next.js': [r'\bNext\.js\b', r'\bNextJS\b', r'\bNextjs\b', r'\bnextjs\b', r'\bnext\.js\b'],
    'Linux': [r'\bLinux\b', r'\blinux\b', r'\bLINUX\b'],
    'OOP': [r'\bOOP\b', r'\boop\b', r'\bObject-Oriented\b', r'\bobject-oriented\b', r'\bObject Oriented\b'],
    'REST/API': [r'\bREST\b', r'\bRESTful\b', r'\bRest\b', r'\brest\b', r'\bAPI\b', r'\bapi\b', r'\bAPIs\b'],
}

tech_variants_all = OrderedDict()

for fname, label in files.items():
    print(f"  Scanning: {fname}")
    df = pd.read_csv(os.path.join(BASE_DIR, fname), encoding='utf-8')
    all_text = ' '.join(df.fillna('').astype(str).values.flatten())
    
    file_tech = OrderedDict()
    
    for tech, patterns in tech_patterns.items():
        found_variants = {}
        for pat in patterns:
            matches = re.findall(pat, all_text)
            if matches:
                for m in matches:
                    found_variants[m] = found_variants.get(m, 0) + 1
        
        if found_variants:
            total = sum(found_variants.values())
            has_variants = len(found_variants) > 1
            sorted_variants = sorted(found_variants.items(), key=lambda x: -x[1])
            
            file_tech[tech] = {
                'total_count': total,
                'has_variants': has_variants,
                'variants': {k: v for k, v in sorted_variants}
            }
    
    tech_variants_all[fname] = file_tech

# ============================================================
# 4. Build final output
# ============================================================
output = OrderedDict()
output['_metadata'] = {
    'description': 'CSV Analysis Report - Special Characters, Unique Values, and Tech Term Variants',
    'generated_by': 'analyze_csv_content.py',
    'files_analyzed': list(files.keys())
}

output['file_overview'] = result
output['tech_term_variants'] = tech_variants_all

# ============================================================
# 5. Write to JSON
# ============================================================
output_path = os.path.join(config.REPORTS_DIR, 'csv_analysis_result.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n✅ Done! Results saved to: {output_path}")
print(f"   File size: {os.path.getsize(output_path) / 1024:.1f} KB")
