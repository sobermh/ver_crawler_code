"""
明星照片爬虫 - 按年龄段爬取
使用 Selenium 版本，按年龄段搜索并下载明星照片
"""

import time
from pathlib import Path
from typing import List

from selenium_image_client import SeleniumImageClient


class AgePhotoCrawler:
    def __init__(self, star_name: str, base_dir: str = "star_photos", headless: bool = False):
        """
        初始化年龄段爬虫
        
        Args:
            star_name: 明星姓名
            base_dir: 保存照片的基础目录
            headless: 是否使用无头模式
        """
        self.star_name = star_name
        self.base_dir = base_dir
        self.headless = headless
        
        
        # 创建基础目录
        Path(self.base_dir).mkdir(exist_ok=True)
        
        # 使用公共 Selenium 客户端
        self.client = SeleniumImageClient(headless=headless, base_dir=base_dir)
    
    def crawl_by_age(self, age_ranges: List[str], max_images_per_age: int = 50):
        """
        按年龄段爬取照片
        
        Args:
            age_ranges: 年龄段列表，格式如 ["20-25岁", "26-30岁", ...]
            max_images_per_age: 每个年龄段最多下载的图片数量
        """
        print(f"开始爬取 {self.star_name} 的照片...")

        # 文件夹名称加上时间戳
        self.base_star_dir = f"{self.base_dir}/{self.star_name}_{time.strftime('%Y%m%d%H%M%S')}"
        
        try:
            for age_range in age_ranges:
                print(f"\n正在爬取 {age_range} 的照片...")
                
                # 创建年龄段文件夹
                age_dir = Path(self.base_star_dir) / age_range
                age_dir.mkdir(parents=True, exist_ok=True)
                
                # 构建搜索关键词 - 使用年龄区间
                keyword = f"{self.star_name} {age_range}"
                
                # 搜索图片
                print(f"  正在搜索关键词: {keyword}")
                image_urls = self.client.search_baidu_images(keyword, max_images=max_images_per_age)
                
                if not image_urls:
                    print(f"  {age_range} 没有找到图片")
                    continue
                
                print(f"  找到 {len(image_urls)} 张图片，开始下载...")
                
                downloaded_count = 0
                for idx, img_url in enumerate(image_urls):
                    # 生成文件名
                    ext = self.client.get_image_extension(img_url)
                    filename = f"{age_range}_{downloaded_count + 1:03d}{ext}"
                    save_path = age_dir / filename
                    
                    # 如果文件已存在，跳过
                    if save_path.exists():
                        downloaded_count += 1
                        continue
                    
                    # 下载图片
                    if self.client.download_image(img_url, save_path):
                        downloaded_count += 1
                        if downloaded_count % 5 == 0:
                            print(f"    已下载 {downloaded_count}/{len(image_urls)} 张...")
                    
                    # 避免请求过快
                    time.sleep(0.3)
                
                print(f"  ✓ {age_range} 完成，共下载 {downloaded_count} 张照片")
                
                # 年龄段间延迟
                time.sleep(2)
        
        finally:
            # 关闭浏览器
            if self.client.driver:
                self.client.driver.quit()
        
        print(f"\n✓ 所有照片爬取完成！保存在 {Path(self.base_dir) / self.star_name} 目录")


def main():
    """主函数"""
    print("=" * 60)
    print("明星照片爬虫 - 按年龄段爬取")
    print("=" * 60)
    
    # 输入明星姓名
    star_name = input("请输入明星姓名(默认陈冲): ").strip()
    if not star_name:
        star_name = "陈冲"
        print(f"明星姓名不能为空！使用默认明星姓名: {star_name}")

    # 询问是否使用无头模式
    headless_input = input("是否使用无头模式（不显示浏览器）？(y/n,默认y): ").strip().lower()
    headless = headless_input != 'n'
    
    # 询问年龄段
    print("\n请输入年龄段（多个年龄段用逗号分隔，例如：10-15岁,16-20岁）")
    print("或者直接回车使用默认年龄段")
    age_input = input("年龄段: ").strip()
    
    if age_input:
        # 使用用户输入的年龄段
        age_ranges = [age.strip() for age in age_input.split(',') if age.strip()]
    else:
        # 使用默认年龄段
        age_ranges = [
            "10-15岁",
            "16-20岁",
            "21-25岁",
            "26-30岁",
            "31-35岁",
            "36-40岁",
            "41-45岁",
            "46-50岁",
            "51-55岁",
            "56-60岁",
        ]
        print(f"使用默认年龄段: {', '.join(age_ranges)}")
    
    # 询问每个年龄段下载数量
    max_images_input = input("每个年龄段下载多少张图片？(默认500): ").strip()
    max_images_per_age = int(max_images_input) if max_images_input.isdigit() else 500
    
    # 创建爬虫实例
    try:
        crawler = AgePhotoCrawler(star_name, headless=headless)
        
        # 开始爬取
        crawler.crawl_by_age(age_ranges, max_images_per_age=max_images_per_age)
    except KeyboardInterrupt:
        print("\n\n用户中断爬取")
    except Exception as e:
        print(f"\n爬取过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

