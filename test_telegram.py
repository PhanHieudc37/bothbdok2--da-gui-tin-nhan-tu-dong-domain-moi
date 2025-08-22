#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test kết nối Telegram Bot
"""

import asyncio
import aiohttp
import time

class TelegramTester:
    def __init__(self):
        self.telegram_token = "7581650289:AAFpcYzuxp1grrOKjZBV1HBx9AImvyilIt8"
        self.telegram_chat_id = "7159305763"
        self.telegram_api_url = f"https://api.telegram.org/bot{self.telegram_token}"
    
    async def test_connection(self):
        """Test kết nối đến Telegram Bot"""
        print("=== TEST KẾT NỐI TELEGRAM BOT ===\n")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test 1: Kiểm tra thông tin bot
                print("1. Kiểm tra thông tin bot...")
                async with session.get(f"{self.telegram_api_url}/getMe") as response:
                    if response.status == 200:
                        bot_info = await response.json()
                        print(f"✅ Bot name: {bot_info['result']['first_name']}")
                        print(f"✅ Bot username: @{bot_info['result']['username']}")
                    else:
                        print(f"❌ Lỗi: {response.status}")
                        return False
                
                # Test 2: Gửi tin nhắn test
                print("\n2. Gửi tin nhắn test...")
                test_message = f"🧪 <b>TEST KẾT NỐI TELEGRAM BOT</b>\n\n"
                test_message += f"✅ Kết nối thành công!\n"
                test_message += f"⏰ Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                test_message += f"🤖 Bot đã sẵn sàng nhận thông báo domain mới!"
                
                payload = {
                    'chat_id': self.telegram_chat_id,
                    'text': test_message,
                    'parse_mode': 'HTML'
                }
                
                async with session.post(
                    f"{self.telegram_api_url}/sendMessage",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        print("✅ Đã gửi tin nhắn test thành công!")
                        result = await response.json()
                        print(f"✅ Message ID: {result['result']['message_id']}")
                    else:
                        print(f"❌ Lỗi gửi tin nhắn: {response.status}")
                        error_text = await response.text()
                        print(f"❌ Chi tiết: {error_text}")
                        return False
                
                # Test 3: Gửi thông báo domain mới mẫu
                print("\n3. Gửi thông báo domain mới mẫu...")
                sample_domains = [
                    {'name': 'example1.com', 'price': '88'},
                    {'name': 'test-domain.cn', 'price': '150'},
                    {'name': 'demo-site.net', 'price': '299'}
                ]
                
                domain_message = f"🔔 <b>DOMAIN MỚI PHÁT HIỆN!</b>\n\n"
                domain_message += f"📊 Tổng cộng: <b>{len(sample_domains)}</b> domain mới\n\n"
                
                for i, domain in enumerate(sample_domains, 1):
                    name = domain['name']
                    price = domain['price']
                    domain_message += f"{i}. <code>{name}</code> - <b>￥{price}</b>\n"
                
                domain_message += f"\n⏰ Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}"
                
                payload = {
                    'chat_id': self.telegram_chat_id,
                    'text': domain_message,
                    'parse_mode': 'HTML'
                }
                
                async with session.post(
                    f"{self.telegram_api_url}/sendMessage",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        print("✅ Đã gửi thông báo domain mẫu thành công!")
                    else:
                        print(f"❌ Lỗi gửi thông báo domain: {response.status}")
                        return False
                
                print("\n=== HOÀN THÀNH TEST ===")
                print("✅ Telegram Bot đã sẵn sàng!")
                print("🚀 Bạn có thể chạy chương trình chính: python 22cn.py")
                return True
                
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return False

async def main():
    tester = TelegramTester()
    await tester.test_connection()

if __name__ == "__main__":
    asyncio.run(main())
