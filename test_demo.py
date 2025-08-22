#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo test cho chương trình thu thập domain 22.cn
"""

import asyncio
import sqlite3
import importlib.util
import sys

# Import module 22cn
spec = importlib.util.spec_from_file_location("module", "22cn.py")
module = importlib.util.module_from_spec(spec)
sys.modules["module"] = module
spec.loader.exec_module(module)
DomainScraper = module.DomainScraper

async def test_database():
    """Test cơ sở dữ liệu"""
    print("=== TEST CƠ SỞ DỮ LIỆU ===")
    
    scraper = DomainScraper()
    
    # Test thêm dữ liệu mẫu
    conn = sqlite3.connect(scraper.db_name)
    cursor = conn.cursor()
    
    # Thêm một số domain mẫu
    test_domains = [
        ("example1.com", "88"),
        ("example2.cn", "150"),
        ("test-domain.net", "299"),
        ("demo-site.org", "450")
    ]
    
    for name, price in test_domains:
        cursor.execute("INSERT OR IGNORE INTO domains (name, price) VALUES (?, ?)", (name, price))
        print(f"Đã thêm: {name} - {price}")
    
    conn.commit()
    conn.close()
    
    # Test xuất CSV
    print("\n=== TEST XUẤT CSV ===")
    csv_file = scraper.export_to_csv()
    if csv_file:
        print(f"Đã xuất file: {csv_file}")
        
        # Đọc và hiển thị nội dung file CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"\nNội dung file CSV:\n{content}")

def test_price_extraction():
    """Test trích xuất giá"""
    print("\n=== TEST TRÍCH XUẤT GIÁ ===")
    
    scraper = DomainScraper()
    
    test_prices = [
        "￥88",
        "￥150.50",
        "￥299",
        "￥1,000",
        "￥2,500.00",
        "免费",
        ""
    ]
    
    for price in test_prices:
        extracted = scraper.extract_price(price)
        print(f"'{price}' -> '{extracted}'")

if __name__ == "__main__":
    print("=== DEMO CHƯƠNG TRÌNH THU THẬP DOMAIN 22.CN ===\n")
    
    # Test trích xuất giá
    test_price_extraction()
    
    # Test cơ sở dữ liệu
    asyncio.run(test_database())
    
    print("\n=== HOÀN THÀNH DEMO ===")
    print("Chương trình đã sẵn sàng chạy với lệnh: python 22cn.py")
