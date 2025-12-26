"""
明星照片爬虫 - 按自定义关键词爬取
使用 Selenium 版本，直接根据输入的关键词搜索并下载图片
"""

import time
from pathlib import Path
from typing import List

from selenium_image_client import SeleniumImageClient


class KeywordPhotoCrawler:
    def __init__(self, base_dir: str = "star_photos", headless: bool = False):
        """
        初始化关键词爬虫
        
        Args:
            base_dir: 保存照片的基础目录
            headless: 是否使用无头模式
        """
        self.base_dir = base_dir
        self.headless = headless
        
        # 使用公共 Selenium 客户端
        self.client = SeleniumImageClient(headless=headless, base_dir=base_dir)
    
    def crawl_by_keyword(self, keyword: str, per_keyword: int = 50):
        """
        按单一关键词爬取照片
        
        Args:
            keyword: 单个关键词
            per_keyword: 每个关键词下载的图片数量
        """
        keyword = keyword.strip()
        if not keyword:
            print("关键词为空，退出。")
            return

        print(f"开始爬取关键词：{keyword}")
        # 文件夹名称加上时间戳
        self.base_keyword_dir = f"{self.base_dir}/{keyword}_{time.strftime('%Y%m%d%H%M%S')}"
        keyword_dir = Path(self.base_keyword_dir)
        keyword_dir.mkdir(parents=True, exist_ok=True)

        try:
            # 搜索图片
            print(f"  正在搜索关键词: {keyword}")
            image_urls = self.client.search_baidu_images(keyword, max_images=per_keyword)

            if not image_urls:
                print(f"  {keyword} 没有找到图片")
                return

            print(f"  找到 {len(image_urls)} 张图片，开始下载...")

            downloaded_count = 0
            for idx, img_url in enumerate(image_urls):
                # 生成文件名
                ext = self.client.get_image_extension(img_url)
                filename = f"{keyword}_{downloaded_count + 1:03d}{ext}"
                save_path = keyword_dir / filename

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

            print(f"  ✓ {keyword} 完成，共下载 {downloaded_count} 张照片")

        finally:
            # 关闭浏览器
            if self.client.driver:
                self.client.driver.quit()

        print(f"\n✓ 爬取完成！保存在 {Path(self.base_dir)} 目录")


def main():
    """主函数"""
    print("=" * 60)
    print("明星照片爬虫 - 按关键词爬取")
    print("=" * 60)
    
    # 输入关键词（单个）
    keyword = input("请输入关键词（直接输入要搜索的内容）: ").strip()
    if not keyword:
        print("关键词不能为空！")
        return

    # 询问是否使用无头模式
    headless_input = input("是否使用无头模式（不显示浏览器）？(y/n,默认y): ").strip().lower()
    headless = headless_input != 'n'

    # 询问下载数量
    per_keyword_input = input("下载多少张图片？(默认500): ").strip()
    per_keyword = int(per_keyword_input) if per_keyword_input.isdigit() else 500

    # 创建爬虫实例并开始爬取
    try:
        crawler = KeywordPhotoCrawler(headless=headless)
        crawler.crawl_by_keyword(keyword, per_keyword=per_keyword)
    except KeyboardInterrupt:
        print("\n\n用户中断爬取")
    except Exception as e:
        print(f"\n爬取过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
