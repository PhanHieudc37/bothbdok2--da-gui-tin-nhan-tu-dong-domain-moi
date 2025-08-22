import asyncio
import sqlite3
import random
import time
from playwright.async_api import async_playwright
import re
import csv
import os
import aiohttp
import json

class DomainScraper:
    def __init__(self):
        self.db_name = "domain.db"
        # Cấu hình Telegram Bot
        self.telegram_token = "7581650289:AAFpcYzuxp1grrOKjZBV1HBx9AImvyilIt8"
        self.telegram_chat_id = "7159305763"
        self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_token}"
        
        self.init_database()
    
    def init_database(self):
        """Khởi tạo cơ sở dữ liệu SQLite"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print("Đã khởi tạo cơ sở dữ liệu domain.db")
    
    async def send_telegram_message(self, message):
        """Gửi tin nhắn đến Telegram Bot"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    'chat_id': self.telegram_chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                }
                
                async with session.post(
                    f"{self.telegram_api_url}/sendMessage",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        print(f"✅ Đã gửi tin nhắn Telegram thành công")
                        return True
                    else:
                        print(f"❌ Lỗi gửi Telegram: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Lỗi kết nối Telegram: {e}")
            return False
    
    async def send_domain_notification(self, domains):
        """Gửi thông báo domain mới đến Telegram"""
        if not domains:
            return
        
        # Tạo tin nhắn thông báo
        message = f"🔔 <b>DOMAIN MỚI PHÁT HIỆN!</b>\n\n"
        message += f"📊 Tổng cộng: <b>{len(domains)}</b> domain mới\n\n"
        
        # Thêm danh sách domain (giới hạn 10 domain đầu tiên để tránh tin nhắn quá dài)
        for i, domain in enumerate(domains[:10], 1):
            name = domain['name']
            price = domain['price']
            message += f"{i}. <code>{name}</code> - <b>￥{price}</b>\n"
        
        if len(domains) > 10:
            message += f"\n... và {len(domains) - 10} domain khác\n"
        
        message += f"\n⏰ Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Gửi tin nhắn
        await self.send_telegram_message(message)
    
    async def random_delay(self, min_delay=1, max_delay=3):
        """Tạo độ trễ ngẫu nhiên để giống hành vi người dùng"""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    async def human_like_typing(self, page, selector, text):
        """Mô phỏng việc gõ phím như người thật"""
        await page.click(selector)
        await self.random_delay(0.5, 1)
        
        for char in text:
            await page.type(selector, char, delay=random.uniform(50, 150))
            await asyncio.sleep(random.uniform(0.05, 0.15))
    
    async def setup_browser(self):
        """Thiết lập trình duyệt với các tùy chọn chống phát hiện bot"""
        playwright = await async_playwright().start()
        
        # Tạo context với các tùy chọn chống phát hiện bot
        browser = await playwright.chromium.launch(
            headless=False,  # Hiển thị trình duyệt để debug
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-sync',
                '--disable-translate',
                '--hide-scrollbars',
                '--mute-audio',
                '--no-default-browser-check',
                '--no-pings',
                '--no-zygote',
                '--disable-background-networking',
                '--disable-component-extensions-with-background-pages',
                '--disable-domain-reliability',
                '--disable-features=AudioServiceOutOfProcess',
                '--disable-print-preview',
                '--disable-prompt-on-repost',
                '--disable-sync-preferences',
                '--disable-web-resources',
                '--metrics-recording-only',
                '--no-first-run',
                '--safebrowsing-disable-auto-update'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
        )
        
        # Thêm script để ẩn webdriver và các dấu hiệu automation
        await context.add_init_script("""
            // Ẩn webdriver property
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Ẩn các thuộc tính automation
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            
            // Ẩn các thuộc tính automation khác
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en'],
            });
            
            // Mô phỏng permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Ẩn automation flags
            Object.defineProperty(navigator, 'automation', {
                get: () => undefined,
            });
            
            // Mô phỏng chrome runtime
            if (!window.chrome) {
                window.chrome = {
                    runtime: {},
                };
            }
        """)
        
        page = await context.new_page()
        
        # Thêm các event listeners để mô phỏng hành vi người dùng
        await page.add_init_script("""
            // Mô phỏng di chuyển chuột ngẫu nhiên
            let mouseMovements = 0;
            document.addEventListener('mousemove', () => {
                mouseMovements++;
            });
            
            // Mô phỏng cuộn trang
            let scrollEvents = 0;
            document.addEventListener('scroll', () => {
                scrollEvents++;
            });
            
            // Mô phỏng focus events
            document.addEventListener('focusin', () => {
                // Tạo các event focus ngẫu nhiên
            });
            
            // Mô phỏng keyboard events
            document.addEventListener('keydown', () => {
                // Tạo các event keyboard ngẫu nhiên
            });
        """)
        
        return playwright, browser, context, page
    
    async def login(self, page):
        """Thực hiện đăng nhập vào trang web"""
        print("Đang mở trang đăng nhập...")
        await page.goto("https://my.22.cn/", wait_until="networkidle")
        await self.random_delay(2, 4)
        
        # Nhập tên người dùng
        print("Đang nhập tên người dùng...")
        await self.human_like_typing(page, "#input_register", "15212172775")
        await self.random_delay(1, 2)
        
        # Nhập mật khẩu
        print("Đang nhập mật khẩu...")
        await self.human_like_typing(page, "#input_registera", "291631..")
        await self.random_delay(1, 2)
        
        # Ấn nút đăng nhập
        print("Đang ấn nút đăng nhập...")
        await page.click("#denglu_button")
        await self.random_delay(3, 5)
        
        # Kiểm tra trạng thái đăng nhập
        try:
            # Chờ và kiểm tra xem có link đến i.22.cn không
            await page.wait_for_selector('a[href="https://i.22.cn"]', timeout=10000)
            print("Đăng nhập thành công!")
            return True
        except:
            print("Đăng nhập thất bại hoặc cần xác thực thêm")
            return False
    
    async def navigate_to_domain_page(self, page):
        """Chuyển hướng đến trang domain"""
        print("Đang chuyển hướng đến trang domain...")
        await page.goto("https://am.22.cn/ykj/", wait_until="networkidle")
        await self.random_delay(2, 4)
    
    async def configure_search(self, page, min_price, max_price):
        """Cấu hình tìm kiếm domain với khoảng giá cụ thể"""
        print(f"Đang cấu hình tìm kiếm với giá {min_price}-{max_price}...")
        
        # Chọn "爱名网" trong dropdown
        await page.select_option("#registrar", "1")
        await self.random_delay(1, 2)
        
        # Xóa giá cũ và nhập giá tối thiểu mới
        await page.click("#txtMinPrice")
        await page.keyboard.press("Control+a")
        await page.keyboard.press("Backspace")
        await self.human_like_typing(page, "#txtMinPrice", str(min_price))
        await self.random_delay(0.5, 1)
        
        # Xóa giá cũ và nhập giá tối đa mới
        await page.click("#txtMaxPrice")
        await page.keyboard.press("Control+a")
        await page.keyboard.press("Backspace")
        await self.human_like_typing(page, "#txtMaxPrice", str(max_price))
        await self.random_delay(0.5, 1)
        
        # Ấn nút tìm kiếm
        print("Đang ấn nút tìm kiếm...")
        await page.click("#btn_search")
        await self.random_delay(3, 5)
        
        # Chọn hiển thị 200 kết quả mỗi trang
        try:
            await page.click('a[name="a_change_pagecount"][data="200"]')
            await self.random_delay(2, 3)
        except:
            print("Không tìm thấy tùy chọn hiển thị 200 kết quả")
    
    def extract_price(self, price_text):
        """Trích xuất giá từ text"""
        if not price_text:
            return "0"
        # Loại bỏ ký tự ￥ và các ký tự không phải số
        price = re.sub(r'[^\d.]', '', price_text)
        return price if price else "0"
    
    async def scrape_domains(self, page):
        """Thu thập dữ liệu domain từ bảng kết quả"""
        print("Đang thu thập dữ liệu domain...")
        
        try:
            # Chờ bảng kết quả xuất hiện với timeout dài hơn
            await page.wait_for_selector(".paimai-tb", timeout=15000)
            await self.random_delay(2, 3)
            
            # Kiểm tra xem có dữ liệu không
            rows_count = await page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('.paimai-tb tbody tr');
                    return rows.length;
                }
            """)
            
            if rows_count == 0:
                print("Không tìm thấy dữ liệu domain trong bảng kết quả")
                return []
            
            # Thu thập dữ liệu từ bảng
            domains_data = await page.evaluate("""
                () => {
                    const rows = document.querySelectorAll('.paimai-tb tbody tr');
                    const domains = [];
                    
                    rows.forEach(row => {
                        const nameElement = row.querySelector('td:nth-child(2) a');
                        const priceElement = row.querySelector('td:nth-child(5)');
                        
                        if (nameElement && priceElement) {
                            const name = nameElement.textContent.trim();
                            const price = priceElement.textContent.trim();
                            
                            // Chỉ lấy domain có tên hợp lệ
                            if (name && name.length > 0 && price && price.length > 0) {
                                domains.push({
                                    name: name,
                                    price: price
                                });
                            }
                        }
                    });
                    
                    return domains;
                }
            """)
            
            # Lưu vào cơ sở dữ liệu
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            saved_count = 0
            new_domains = []  # Danh sách domain mới để gửi thông báo
            
            for domain in domains_data:
                name = domain['name']
                price = self.extract_price(domain['price'])
                
                # Kiểm tra xem domain đã tồn tại chưa
                cursor.execute("SELECT id FROM domains WHERE name = ?", (name,))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO domains (name, price) VALUES (?, ?)", (name, price))
                    saved_count += 1
                    print(f"Đã lưu: {name} - {price}")
                    
                    # Thêm vào danh sách domain mới
                    new_domains.append({
                        'name': name,
                        'price': price
                    })
            
            conn.commit()
            conn.close()
            
            print(f"Đã thu thập {len(domains_data)} domain, lưu {saved_count} domain mới vào cơ sở dữ liệu")
            
            # Gửi thông báo Telegram nếu có domain mới
            if new_domains:
                print("Đang gửi thông báo Telegram...")
                await self.send_domain_notification(new_domains)
            
            return domains_data
            
        except Exception as e:
            print(f"Lỗi khi thu thập dữ liệu: {e}")
            return []
    
    def export_to_csv(self):
        """Xuất dữ liệu từ SQLite ra file CSV theo định dạng yêu cầu"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Lấy tất cả domain từ database
            cursor.execute("SELECT name, price FROM domains ORDER BY name")
            domains = cursor.fetchall()
            
            conn.close()
            
            # Xuất ra file CSV
            csv_filename = "domains_export.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['名称', '当前价格'])  # Header
                
                for name, price in domains:
                    writer.writerow([name, price])
            
            print(f"Đã xuất {len(domains)} domain ra file {csv_filename}")
            return csv_filename
            
        except Exception as e:
            print(f"Lỗi khi xuất file CSV: {e}")
            return None
    
    async def run(self):
        """Chạy toàn bộ quy trình"""
        try:
            # Gửi thông báo khởi động
            start_message = f"🚀 <b>BOT DOMAIN 22.CN ĐÃ KHỞI ĐỘNG!</b>\n\n"
            start_message += f"⏰ Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            start_message += f"📋 Bắt đầu thu thập dữ liệu domain..."
            
            await self.send_telegram_message(start_message)
            
            playwright, browser, context, page = await self.setup_browser()
            
            # Thực hiện đăng nhập
            login_success = await self.login(page)
            if not login_success:
                print("Không thể đăng nhập. Vui lòng kiểm tra thông tin đăng nhập.")
                return
            
            # Chuyển hướng đến trang domain
            await self.navigate_to_domain_page(page)
            
            # Định nghĩa các khoảng giá cần thu thập
            price_ranges = [
                (0, 100),      # Khoảng giá đầu tiên
                (101, 500),    # Khoảng giá thứ hai
                (501, 999),    # Khoảng giá thứ ba
                (1000, 1999),  # Khoảng giá thứ tư
                (2000, 3000),  # Khoảng giá thứ năm
                (3001, 5000)   # Khoảng giá thứ sáu
            ]
            
            total_domains = 0
            
            # Thu thập dữ liệu từ từng khoảng giá
            for i, (min_price, max_price) in enumerate(price_ranges, 1):
                print(f"\n=== Đang thu thập khoảng giá {i}: {min_price}-{max_price} ===")
                
                # Cấu hình tìm kiếm cho khoảng giá hiện tại
                await self.configure_search(page, min_price, max_price)
                
                # Thu thập dữ liệu
                domains = await self.scrape_domains(page)
                total_domains += len(domains)
                
                print(f"Đã thu thập {len(domains)} domain từ khoảng giá {min_price}-{max_price}")
                
                # Đợi một chút trước khi chuyển sang khoảng giá tiếp theo
                if i < len(price_ranges):
                    await self.random_delay(3, 5)
            
            print(f"\n=== HOÀN THÀNH! ===")
            print(f"Tổng cộng đã thu thập {total_domains} domain từ tất cả các khoảng giá")
            
            # Xuất dữ liệu ra file CSV
            print("\nĐang xuất dữ liệu ra file CSV...")
            csv_file = self.export_to_csv()
            if csv_file:
                print(f"Đã xuất dữ liệu ra file: {csv_file}")
            
            # Gửi thông báo hoàn thành
            end_message = f"✅ <b>HOÀN THÀNH THU THẬP DOMAIN!</b>\n\n"
            end_message += f"📊 Tổng cộng: <b>{total_domains}</b> domain\n"
            end_message += f"📁 File CSV: <code>{csv_file}</code>\n"
            end_message += f"⏰ Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            await self.send_telegram_message(end_message)
            
            # Giữ trình duyệt mở một lúc để xem kết quả
            await self.random_delay(5, 10)
            
        except Exception as e:
            print(f"Lỗi: {e}")
        finally:
            try:
                await browser.close()
                await playwright.stop()
            except:
                pass

async def main():
    """Hàm chính"""
    scraper = DomainScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())
