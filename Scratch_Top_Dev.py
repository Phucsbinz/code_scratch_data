import requests
from bs4 import BeautifulSoup
import pandas as pd
from googletrans import Translator
import time
import sys
sys.stdout.reconfigure(encoding='utf-8') # không bị lỗi tiếng việt khi in ra console
list_your_role_responsibilities_all=[] # chứa thông tin về mô tả công việc
list_Your_skills_qualifications_all=[] # chứa thông tin về kỹ năng và yêu cầu
list_Benefits_all=[] # chứa thông tin về quyền lợi
list_positions_all=[] # chứa thông tin về vị trí ứng tuyển
list_search=["Software+Engineer", "Data+Scientist","Data+Science","AI+Engineer","ML+Engineer","Scurity","BA","DA","QA"]
# danh sách tìm kiếm
for i in list_search:
    url = f"https://topdev.vn/jobs/search?keyword={i}"  # url tìm kiếm theo từ khóa trong danh sách tren dev tp[]]
    # Sử dụng Session để giữ Cookies
    session = requests.Session()
    try: # try axcept để bắt lỗi trạng thái
        response = session.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("có thể cào dữ liệu.") 
    except Exception as e:
        print(f"Lỗi: {e}")
    soup=BeautifulSoup(response.text, "lxml")
    list_links = soup.find_all("a",class_="line-clamp-1 text-sm/[18px] font-semibold text-brand-500 md:line-clamp-1 md:text-base/[24px]")
    for j in list_links: # vòng lặp qua từng link công việc
        link=j["href"]
        url2=f"https://topdev.vn{link}"
        r2 = session.get(url2)
        if r2.status_code == 404:
            print(f"Page not found: {url2}")
        else:
            soup2 = BeautifulSoup(r2.text, "lxml")
            role_div = soup2.find_all("div", class_="prose-ul text-text-900 bg-[#F5F5F5] px-2 py-4 text-sm")
            role_div2 = soup2.find_all("div", class_="td-px-6 lg:td-px-12")
            if role_div:
                list_your_role_responsibilities_all.append(role_div[0].get_text(separator="\n", strip=True).replace("\n", ""))
                list_Your_skills_qualifications_all.append(role_div[1].get_text(separator="\n", strip=True).replace("\n", ""))
                list_Benefits_all.append(role_div[2].get_text(separator="\n", strip=True).replace("\n", ""))
                list_positions_all.append(i.replace("+", " "))
            elif role_div2:
                list_your_role_responsibilities_all.append(role_div2[0].get_text(separator="\n", strip=True).replace("\n", ""))
                list_Your_skills_qualifications_all.append(role_div2[1].get_text(separator="\n", strip=True).replace("\n", ""))
                list_Benefits_all.append(role_div2[2].get_text(separator="\n", strip=True).replace("\n", ""))
                list_positions_all.append(i.replace("+", " "))
            else:
                list_your_role_responsibilities_all.append("")
                list_Your_skills_qualifications_all.append("")
                list_Benefits_all.append("")
                list_positions_all.append(i.replace("+", " "))
df= pd.DataFrame({
    "position": list_positions_all,
    "role_responsibilities": list_your_role_responsibilities_all,
    "skills_qualifications": list_Your_skills_qualifications_all,
    "benefits": list_Benefits_all
})
df.to_csv("jobs_dev_top_final.csv", index=False, encoding="utf-8")
print(df)
