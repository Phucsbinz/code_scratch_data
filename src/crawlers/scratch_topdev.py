import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd
from googletrans import Translator
import time
import sys
import os

# Add project root to sys.path to support imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
import config

sys.stdout.reconfigure(encoding='utf-8') # không bị lỗi tiếng việt khi in ra console
list_job_names_all=[]
list_level_all=[]
list_your_role_responsibilities_all=[] # chứa thông tin về mô tả công việc
list_Your_skills_qualifications_all=[] # chứa thông tin về kỹ năng và yêu cầu
list_Benefits_all=[] # chứa thông tin về quyền lợi
list_positions_all=[] # chứa thông tin về vị trí ứng tuyển
list_search=["Software+Engineer", "Data+Engineer","Data+Science","AI+Engineer","ML+Engineer","Security","BA","DA","QA"]
# danh sách tìm kiếm

# Thiết lập Session với Headers và Retry
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
session = requests.Session()
session.headers.update(headers)
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

for i in list_search:
    url = f"https://topdev.vn/jobs/search?keyword={i}"  # url tìm kiếm theo từ khóa trong danh sách tren dev tp[]]
    time.sleep(2) # Nghỉ 2s trước khi search từ khóa mới
    try: # try axcept để bắt lỗi trạng thái
        response = session.get(url, timeout=10)
        print(f"[{i}] Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"[{i}] có thể cào dữ liệu.") 
    except Exception as e:
        print(f"Lỗi: {e}")
    soup=BeautifulSoup(response.text, "lxml")
    list_links = soup.find_all("a",class_="line-clamp-1 text-sm/[18px] font-semibold text-brand-500 md:line-clamp-1 md:text-base/[24px]")
    for j in list_links: # vòng lặp qua từng link công việc
        link=j["href"]
        url2=f"https://topdev.vn{link}"
        time.sleep(1) # Thêm delay 1s để tránh bị block
        try:
            r2 = session.get(url2, timeout=10)
        except Exception as e:
            print(f"Lỗi khi truy cập trang con {url2}: {e}")
            continue

        if r2.status_code == 404:
            print(f"Page not found: {url2}")
        else:
            soup2 = BeautifulSoup(r2.text, "lxml")
            board= soup2.find_all("span",class_="flex items-center gap-1 text-xs/[12px] font-medium text-text-500 md:text-sm")
            level=board[1]
            job_name = soup2.find("a",class_="line-clamp-1 text-sm/[18px] font-semibold text-brand-500 md:line-clamp-1 md:text-base/[24px]")
            role_div = soup2.find_all("div", class_="prose-ul text-text-900 bg-[#F5F5F5] px-2 py-4 text-sm")
            role_div2 = soup2.find_all("div", class_="td-mb-2 td-ml-4 td-mt-4 td-flex td-items-center td-gap-2 lg:td-mb-5 lg:td-ml-20 lg:td-mt-8")
            role_div3  =soup2.find_all("div",class_="td-flex td-items-center td-gap-1")
            
            list_job_names_all.append(job_name.get_text(separator="\n", strip=True).replace("\n", ""))
            if level:
                list_level_all.append(level.get_text(separator="\n", strip=True).replace("\n", ""))
            else:
                list_level_all.append("")

            if role_div:
                list_your_role_responsibilities_all.append(role_div[0].get_text(separator="\n", strip=True).replace("\n", "")) if len(role_div)>0 else list_your_role_responsibilities_all.append("")
                list_Your_skills_qualifications_all.append(role_div[1].get_text(separator="\n", strip=True).replace("\n", "")) if len(role_div)>1 else list_Your_skills_qualifications_all.append("")
                list_Benefits_all.append(role_div[2].get_text(separator="\n", strip=True).replace("\n", "")) if len(role_div)>2 else list_Benefits_all.append("")
                list_positions_all.append(i.replace("+", " "))
                
            elif role_div2:
                note=[]
                for x in role_div2:
                    note.append(x.find_next_sibling("div"))
                if len(note) >= 3:
                    list_your_role_responsibilities_all.append(note[0].get_text(separator="\n", strip=True).replace("\n", ""))
                    list_Your_skills_qualifications_all.append(note[1].get_text(separator="\n", strip=True).replace("\n", ""))
                    list_Benefits_all.append(note[2].get_text(separator="\n", strip=True).replace("\n", ""))
                else:
                    # Đề phòng trường hợp job này đăng thiếu mục
                    list_your_role_responsibilities_all.append("")
                    list_Your_skills_qualifications_all.append("")
                    list_Benefits_all.append("")
                
                list_positions_all.append(i.replace("+", " "))
            elif role_div3:
                list_your_role_responsibilities_all.append(role_div3[0].get_text(separator="\n", strip=True).replace("\n", ""))
                list_Your_skills_qualifications_all.append(role_div3[1].get_text(separator="\n", strip=True).replace("\n", ""))
                list_Benefits_all.append(role_div3[2].get_text(separator="\n", strip=True).replace("\n", ""))
                list_positions_all.append(i.replace("+", " "))
                
            else:
                list_your_role_responsibilities_all.append("")
                list_Your_skills_qualifications_all.append("")
                list_Benefits_all.append("")
                list_positions_all.append(i.replace("+", " "))
df= pd.DataFrame({
    "job_name": list_job_names_all,
    "position": list_positions_all,
    "level": list_level_all,
    "role_responsibilities": list_your_role_responsibilities_all,
    "skills_qualifications": list_Your_skills_qualifications_all,
    "benefits": list_Benefits_all
})
df.to_csv(os.path.join(config.RAW_DATA_DIR, "jobs_dev_top_final.csv"), index=False, encoding="utf-8-sig")
print(df)
