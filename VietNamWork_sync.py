from playwright.sync_api import sync_playwright
import pandas as pd
from playwright_stealth import Stealth
import time
import random
import os

# Cấu hình proxy xoay tự động (Vui lòng điền proxy của bạn nếu cần)
PROXY_DICT = {
    "server": "http://YOUR_PROXY_SERVER:PORT",
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD"
}

job_links=[]
list_positions_all=[]
job_name_all=[]
describe_job=[]
require_job=[]
level_job=[]
skills=[]
years_of_experience=[]
educational_level=[]
list_search=["Software Engineer", "Data Engineer","Data Science","AI Engineer","ML Engineer","Security","BA","DA","QA"]
with sync_playwright() as p:
    # Chọn proxy ProxyNo1 cho lần chạy đầu
    first_proxy = PROXY_DICT
    browser = p.chromium.launch(
        headless=False,
        proxy=first_proxy
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    Stealth().use_sync(page)
    page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())

    for i in list_search:
        page.goto("https://www.vietnamworks.com/?utm_source=google&utm_medium=ppc&utm_campaign=google_ppc_inhouse_Pmax-all-VN-seasonal&utm_source=google&utm_medium=cpa&utm_campaign=pmax&gad_source=1&gad_campaignid=22825164658&gbraid=0AAAAA_y-oNvHrGa_EGjS2mzrM0tQkOBLA&gclid=CjwKCAjwqubPBhBOEiwAzgZX2smaOtPm6bwV1YJmnYdMnHZ-CvL_AycOm85Ak93Nyahwc1Z5QqrRzRoCRvoQAvD_BwE")
        search_input = page.get_by_placeholder("Tìm kiếm việc làm, công ty, kỹ năng")
        search_input.click()  # focus vào ô input
        search_input.fill("")  # xóa sạch text cũ
        page.wait_for_timeout(500)  # đợi input clear xong
        search_input.fill(i)  # điền từ khóa mới
        page.wait_for_timeout(500)  # đợi autocomplete dropdown biến mất
        page.get_by_role("button", name="Tìm kiếm").click()
        page.wait_for_selector('h2 a', timeout=60000)  # đợi kết quả load xong
        page.get_by_role("main").get_by_text("Liên quan nhất", exact=True).click()
        page.wait_for_timeout(1500)  # đợi kết quả re-sort

        j = 1
        while True:
            j += 1
            prev_count = 0
            while True:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)  # chờ data load (giảm từ 2000)
                current_count = page.locator("h2 a").count()
                if current_count == prev_count:
                    break
                prev_count = current_count

            new_links = page.locator('h2 a').evaluate_all(
                "links => links.map(link => link.href)")
            job_links.extend(new_links)
            list_positions_all.extend([i] * len(new_links))  # gán search term cho từng link
            print(f"[{i}] Trang {j-1} - Tổng links: {len(job_links)}")

            # Gọi locator 1 lần duy nhất, tránh gọi 3 lần
            next_button = page.get_by_role("button", name=f"{j}")
            try:
                if next_button.is_visible() and next_button.is_enabled():
                    next_button.scroll_into_view_if_needed()
                    next_button.click()
                    page.wait_for_selector('h2 a', timeout=60000)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(800)  # giảm từ 1000
                else:
                    break
            except Exception:
                # stealth plugin conflict → coi như hết trang
                break
    # --- Vòng 2: Scrape từng link ---
    for idx, link in enumerate(job_links, 1):
        print(f"Đang lấy link thứ: [{idx}/{len(job_links)}]")
        try:
            page.goto(link, wait_until="domcontentloaded")
            # Bọc try-except riêng vì stealth plugin có thể gây crash is_visible()
            try:
                page.wait_for_timeout(1000)  # đợi stealth plugin xử lý xong
                btn_xem_day_du = page.get_by_role("button", name="Xem đầy đủ mô tả công việc")
                if btn_xem_day_du.count() > 0 and btn_xem_day_du.is_visible():
                    btn_xem_day_du.click()
            except Exception:
                pass  # nút không có hoặc stealth conflict → bỏ qua
            try:
                btn_xem_them = page.get_by_role("button", name="Xem thêm")
                if btn_xem_them.count() > 0 and btn_xem_them.is_visible():
                    btn_xem_them.click()
            except Exception:
                pass
            # Helper: lấy text an toàn, tránh gọi locator 2 lần
            def safe_text(selector):
                loc = page.locator(selector)
                return loc.inner_text() if loc.count() > 0 else ""
            tmp_name = safe_text('h1[name="title"]')
            tmp_desc = safe_text('h2:has-text("Mô tả công việc") + div')
            tmp_req = safe_text('h2:has-text("Yêu cầu công việc") + div + div')
            tmp_level = safe_text('div:has(> label:has-text("CẤP BẬC")) p')
            tmp_skills = safe_text('div:has(> label:has-text("KỸ NĂNG")) p')
            tmp_years_of_experience = safe_text('div:has(> label:has-text("SỐ NĂM KINH NGHIỆM TỐI THIỂU")) p')
            tmp_educational_level = safe_text('div:has(> label:has-text("TRÌNH ĐỘ HỌC VẤN TỐI THIỂU")) p')
            job_name_all.append(tmp_name)
            describe_job.append(tmp_desc)
            require_job.append(tmp_req)
            level_job.append(tmp_level)
            skills.append(tmp_skills)
            years_of_experience.append(tmp_years_of_experience)
            educational_level.append(tmp_educational_level)
        except Exception as e:
            print(f"Error scraping {link}: {e}")
            job_name_all.append("")
            describe_job.append("")
            require_job.append("")
            level_job.append("")
            skills.append("")
            years_of_experience.append("")
            educational_level.append("")

    df = pd.DataFrame({
        "Position": list_positions_all,
        "Job Title": job_name_all,
        "Skills": skills,
        "Description": describe_job,
        "Requirement": require_job,
        "Level": level_job,
        "Years of Experience": years_of_experience,
        "Educational Level": educational_level,
    })
    print(df)
    df.to_csv("jobs_vietnamworks.csv", index=False, encoding="utf-8-sig")
    browser.close()