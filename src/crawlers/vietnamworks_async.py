import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from playwright_stealth import Stealth
import random
import os
import sys

# Add project root to sys.path to support imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
import config

# Cấu hình proxy xoay tự động (Vui lòng điền proxy của bạn nếu cần)
PROXY_DICT = {
    "server": "http://YOUR_PROXY_SERVER:PORT",
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD"
}

# Biến toàn cục để lưu kết quả an toàn kể cả khi dừng đột ngột
all_scraped_jobs = []

def export_csv(filename):
    if len(all_scraped_jobs) > 0:
        df = pd.DataFrame(all_scraped_jobs)
        cols = ["Position", "Job Title", "Skills", "Description", "Requirement", "Level", "Years of Experience", "Educational Level"]
        for col in cols:
            if col not in df.columns:
                df[col] = ""
        df = df[cols]
        out_path = os.path.join(config.RAW_DATA_DIR, filename)
        print(f"\n💾 Đang lưu {len(all_scraped_jobs)} dòng ra file {out_path}...")
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print("🎉 Hoàn tất!")
    else:
        print("\n⚠️ Chưa cào được chi tiết công việc nào để lưu.")

async def gather_links_for_keyword(browser, keyword, semaphore):
    async with semaphore:
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        await page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())
        
        links_data = []
        print(f"🔎 Đang tìm kiếm từ khóa: {keyword}")
        try:
            keyword_encoded = keyword.replace(" ", "%20")
            url = f"https://www.vietnamworks.com/viec-lam?q={keyword_encoded}"
            await page.goto(url, timeout=60000)
            
            await page.wait_for_selector('h2 a', timeout=60000)
            
            try:
                btn_lien_quan = page.get_by_role("main").get_by_text("Liên quan nhất", exact=True)
                if await btn_lien_quan.is_visible():
                    await btn_lien_quan.click()
                    await page.wait_for_timeout(1500)
            except Exception:
                pass
            
            j = 1
            while True:
                j += 1
                prev_count = 0
                while True:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1500)
                    current_count = await page.locator("h2 a").count()
                    if current_count == prev_count:
                        break
                    prev_count = current_count

                new_links = await page.locator('h2 a').evaluate_all("links => links.map(link => link.href)")
                
                for link in new_links:
                    links_data.append({
                        "Position": keyword,
                        "Link": link
                    })
                    
                print(f"[{keyword}] Trang {j-1} - Tìm được: {len(new_links)} links")

                next_button = page.get_by_role("button", name=str(j), exact=True)
                try:
                    if await next_button.is_visible() and await next_button.is_enabled():
                        await next_button.scroll_into_view_if_needed()
                        await next_button.click()
                        await page.wait_for_selector('h2 a', timeout=60000)
                        await page.evaluate("window.scrollTo(0, 0)")
                        await page.wait_for_timeout(800)
                    else:
                        break
                except Exception:
                    break
                    
        except Exception as e:
            print(f"❌ Lỗi khi lấy link cho keyword '{keyword}': {e}")
        finally:
            await page.close()
            await context.close()
            
        return links_data

async def scrape_job_detail(context, job_data, semaphore, idx, total):
    async with semaphore:
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        await page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())
        link = job_data["Link"]
        
        print(f"⏳ Đang cào chi tiết link thứ: [{idx}/{total}]")
        try:
            # Dùng 'load' thay vì 'domcontentloaded' để web tải xong hẳn
            await page.goto(link, wait_until="load", timeout=60000)
            
            # Chủ động chờ tiêu đề web hiện lên, nếu mạng/proxy chậm
            try:
                await page.wait_for_selector('h1[name="title"]', timeout=8000)
            except Exception:
                await page.wait_for_timeout(3000) # Đợi thêm tí nếu timeout
            
            try:
                await page.wait_for_timeout(1000)
                btn_xem_day_du = page.get_by_role("button", name="Xem đầy đủ mô tả công việc")
                if await btn_xem_day_du.count() > 0 and await btn_xem_day_du.is_visible():
                    await btn_xem_day_du.click()
            except Exception:
                pass
                
            try:
                await page.wait_for_timeout(500)
                btn_xem_them = page.get_by_role("button", name="Xem thêm")
                if await btn_xem_them.count() > 0 and await btn_xem_them.is_visible():
                    await btn_xem_them.click()
            except Exception:
                pass

            async def safe_text(selector):
                loc = page.locator(selector)
                if await loc.count() > 0:
                    text = await loc.first.text_content()
                    return text.strip() if text else ""
                return ""
                
            job_data["Job Title"] = await safe_text('h1[name="title"]')
            job_data["Description"] = await safe_text('h2:has-text("Mô tả công việc") + div')
            job_data["Requirement"] = await safe_text('h2:has-text("Yêu cầu công việc") + div + div')
            job_data["Level"] = await safe_text('label:has-text("CẤP BẬC") + *')
            job_data["Skills"] = await safe_text('label:has-text("KỸ NĂNG") + *')
            job_data["Years of Experience"] = await safe_text('label:has-text("SỐ NĂM KINH NGHIỆM TỐI THIỂU") + *')
            job_data["Educational Level"] = await safe_text('label:has-text("TRÌNH ĐỘ HỌC VẤN TỐI THIỂU") + *')
            
            # Cào thành công mới đưa vào biến tổng
            all_scraped_jobs.append(job_data)
            
        except Exception as e:
            print(f"❌ Lỗi khi cào {link}: {e}")
        finally:
            await page.close()

async def main():
    list_search = ["Software Engineer", "Data Engineer", "Data Science", "AI Engineer", "ML Engineer", "Security", "BA", "DA", "QA"]
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            proxy=PROXY_DICT
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )

        print("==================================================")
        print("🚀 BẮT ĐẦU VÒNG 1: LẤY DANH SÁCH LINKS SONG SONG")
        print("==================================================")
        link_semaphore = asyncio.Semaphore(3)
        
        link_tasks = [gather_links_for_keyword(browser, kw, link_semaphore) for kw in list_search]
        results = await asyncio.gather(*link_tasks)
        
        all_jobs = []
        for res in results:
            all_jobs.extend(res)
            
        print(f"\n✅ Đã lấy xong tổng cộng: {len(all_jobs)} links (chưa lọc trùng).")

        print("\n==================================================")
        print("🚀 BẮT ĐẦU VÒNG 2: LẤY CHI TIẾT CÔNG VIỆC SONG SONG")
        print("==================================================")
        
        # Có thể nâng concurrency lên 4 hoặc 5 vì đã có cơ chế delay ngẫu nhiên an toàn
        detail_semaphore = asyncio.Semaphore(10)
        
        total_jobs = len(all_jobs)
        detail_tasks = [scrape_job_detail(context, job, detail_semaphore, idx, total_jobs) for idx, job in enumerate(all_jobs, 1)]
        
        await asyncio.gather(*detail_tasks)

        export_csv("jobs_vietnamworks_async_parallel.csv")
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Dừng đột ngột bởi người dùng! Đang lưu các data đã cào được...")
        export_csv("jobs_vietnamworks_async_parallel_partial.csv")
