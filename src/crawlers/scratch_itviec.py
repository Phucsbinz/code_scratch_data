import requests
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
skills_all=[]
domain_company_all=[]
List_three_reason_join_company=[]
list_job_names_all=[]
list_description_of_work_all=[] # chứa thông tin về mô tả công việc
list_requirement_all=[] # chứa thông tin về kỹ năng và yêu cầu
list_reason_you_like_to_work_all=[] # chứa thông tin về quyền lợi
list_positions_all=[] # chứa thông tin về vị trí ứng tuyển
list_search=["Software-Engineer", "Data-Engineer","Data-Science","AI-Engineer","ML-Engineer","Security","BA","DA","QA"]
# danh sách tìm kiếm
for i in list_search:
    url = f"https://itviec.com/viec-lam-it/{i}"  # url tìm kiếm theo từ khóa trong danh sách tren dev tp[]]
    # Sử dụng Session để giữ Cookies và thêm Headers để tránh 403
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    })
    try: # try axcept để bắt lỗi trạng thái
        print(f"Đang cào dữ liệu cho từ khóa: {i}")
        time.sleep(2)
        response = session.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code != 200:
            print("Bị chặn hoặc lỗi! Tạm nghỉ 10s...")
            time.sleep(10)
            continue
        print("có thể cào dữ liệu.") 
    except Exception as e:
        print(f"Lỗi: {e}")
        continue
    while True: # Sử dụng while True để luôn chạy ít nhất 1 lần (cho trang đầu tiên)
        soup=BeautifulSoup(response.text, "lxml")
        list_links = soup.find_all("h3",class_="imt-3 text-break")
        for j in list_links: # vòng lặp qua từng link công việc
            link=j["data-url"]
            url2=f"{link}"
            time.sleep(2) # Nghỉ 2 giây để tránh bị Cloudflare chặn
            try:
                r2 = session.get(url2)
            except Exception as e:
                print(f"Lỗi kết nối: {e}")
                continue
                
            if r2.status_code != 200:
                print(f"Bị lỗi hoặc chặn tại link (Mã {r2.status_code}): {url2}")
                time.sleep(5) # Nghỉ thêm nếu bị chặn
                continue
            else:
                soup2 = BeautifulSoup(r2.text, "lxml")
                job_name = soup2.find("h1",class_="ipt-xl-6 text-it-black")
                div= soup2.find("div",class_="imy-3 paragraph")
                reason_join_company=div.find("ul") if div else None
                skills=soup2.find("div",class_="d-flex flex-wrap igap-2")
                domain_company=soup2.find("div",class_="itag bg-light-grey itag-sm cursor-default")
                role_div = soup2.find_all("div", class_="imy-5 paragraph")
                if job_name:
                    list_job_names_all.append(job_name.get_text(separator="\n", strip=True).replace("\n", ""))
                else:
                    list_job_names_all.append("")
                if domain_company:
                    domain_company_all.append(domain_company.get_text(separator="\n", strip=True).replace("\n", "_"))
                else: domain_company_all.append("")
                if skills:
                    skills_all.append(skills.get_text(separator="\n", strip=True).replace("\n", "_"))
                else: skills_all.append("")
                if reason_join_company:
                    List_three_reason_join_company.append(reason_join_company.get_text(separator="\n", strip=True).replace("\n", "_"))
                else: List_three_reason_join_company.append("")
                list_positions_all.append(i.replace("+", " "))
                if role_div:
                    for divtext in role_div:
                        # Tìm tất cả thẻ h2 và xóa (tránh lỗi nếu không có thẻ h2 nào)
                        for h2 in divtext.find_all("h2"):
                            h2.decompose()
                    desc = role_div[0].get_text(separator="\n", strip=True).replace("\n", "_") if len(role_div) > 0 else ""
                    req = role_div[1].get_text(separator="\n", strip=True).replace("\n", "_") if len(role_div) > 1 else ""
                    reason = role_div[2].get_text(separator="\n", strip=True).replace("\n", "_") if len(role_div) > 2 else ""
                    list_description_of_work_all.append(desc)
                    list_requirement_all.append(req)
                    list_reason_you_like_to_work_all.append(reason)
                else:
                    list_description_of_work_all.append("")
                    list_requirement_all.append("")
                    list_reason_you_like_to_work_all.append("")
        page_next=soup.find("div",class_="page next")
        page_next=page_next.find("a",{"rel":"next"})["href"] if page_next else None
        
        if page_next:
            url=f"https://itviec.com{page_next}"
            time.sleep(2)
            response = session.get(url)
        else:
            break # Nếu không có trang kế tiếp thì thoát vòng lặp while
df= pd.DataFrame({
    "job_name": list_job_names_all,
    "position": list_positions_all,
    "skills": skills_all,
    "domain_company": domain_company_all,
    "three_reasons_join_company": List_three_reason_join_company,
    "description_of_work": list_description_of_work_all,
    "requirements": list_requirement_all,
    "reason_you_like_to_work": list_reason_you_like_to_work_all
})
df.to_csv(os.path.join(config.RAW_DATA_DIR, "jobs_itviec_final.csv"), index=False, encoding="utf-8-sig")
print(df)
