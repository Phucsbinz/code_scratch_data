from playwright.sync_api import sync_playwright
import pandas as pd
from playwright_stealth import Stealth
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
    browser = p.chromium.launch(headless=False)  # bỏ slow_mo để chạy nhanh
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
        page.wait_for_selector('h2 a')  # đợi kết quả load xong
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

            job_links.extend(page.locator('h2 a').evaluate_all(
                "links => links.map(link => link.href)"))
            print(f"[{i}] Trang {j-1} - Tổng links: {len(job_links)}")

            # Gọi locator 1 lần duy nhất, tránh gọi 3 lần
            next_button = page.get_by_role("button", name=f"{j}")
            try:
                if next_button.is_visible() and next_button.is_enabled():
                    next_button.scroll_into_view_if_needed()
                    next_button.click()
                    page.wait_for_selector('h2 a')
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(800)  # giảm từ 1000
                else:
                    break
            except Exception:
                # stealth plugin conflict → coi như hết trang
                break

    print(f"\n=== TỔNG CỘNG: {len(job_links)} links ===")
    browser.close()
