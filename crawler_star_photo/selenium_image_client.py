"""
Selenium 公共封装：驱动初始化、图片搜索、下载工具
"""

import os
import platform
import subprocess
import time
from pathlib import Path
from typing import List

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

try:
    from webdriver_manager.chrome import ChromeDriverManager

    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


class SeleniumImageClient:
    def __init__(self, headless: bool = False, base_dir: str = "star_photos"):
        self.headless = headless
        self.base_dir = base_dir
        Path(self.base_dir).mkdir(exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Referer": "https://image.baidu.com/",
            }
        )

        self.driver = None
        self.init_driver()

    # ---------- 驱动与环境 ----------
    def check_chrome_installed(self) -> bool:
        system = platform.system()
        chrome_paths = []
        if system == "Windows":
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
        elif system == "Darwin":
            chrome_paths = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
        else:
            chrome_paths = ["/usr/bin/google-chrome", "/usr/bin/chromium-browser", "/usr/bin/chromium"]

        for path in chrome_paths:
            if os.path.exists(path):
                return True

        try:
            if system == "Windows":
                result = subprocess.run(["where", "chrome"], capture_output=True, text=True, timeout=5)
            else:
                result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False

    def init_driver(self):
        if not self.check_chrome_installed():
            print("⚠️  未检测到 Chrome，程序仍会尝试启动。")

        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")

        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            self.driver = webdriver.Chrome(options=chrome_options)

    # ---------- 核心功能 ----------
    def search_baidu_images(self, keyword: str, max_images: int = 50) -> List[str]:
        image_urls: List[str] = []
        try:
            search_url = f"https://image.baidu.com/search/index?tn=baiduimage&word={keyword}"
            self.driver.get(search_url)
            time.sleep(2)

            scroll_pause_time = 1
            last_height = self.driver.execute_script("return document.body.scrollHeight")

            while len(image_urls) < max_images:
                selectors = [
                    "img.main_img",
                    "img[data-imgurl]",
                    "img[data-objurl]",
                    ".imgbox img",
                    ".imgitem img",
                    ".img-wrapper img",
                ]
                seen = set(image_urls)
                for selector in selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for img in elements:
                        try:
                            url = (
                                img.get_attribute("data-imgurl")
                                or img.get_attribute("data-objurl")
                                or img.get_attribute("src")
                            )
                            if url and url.startswith("http") and url not in seen:
                                seen.add(url)
                                image_urls.append(url)
                                if len(image_urls) >= max_images:
                                    break
                        except Exception:
                            continue
                    if len(image_urls) >= max_images:
                        break

                if len(image_urls) >= max_images:
                    break

                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause_time)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            return list(dict.fromkeys(image_urls))[:max_images]
        except Exception as e:
            print(f"搜索图片失败: {e}")
            return []

    def get_image_extension(self, url: str) -> str:
        lower = url.lower()
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            if ext in lower:
                return ext
        return ".jpg"

    def download_image(self, url: str, save_path: Path,retry: int = 3) -> bool:
        for i in range(retry):
            try:
                resp = self.session.get(url, timeout=15, stream=True, allow_redirects=True)
                resp.raise_for_status()
                if "image" not in resp.headers.get("content-type", "") and len(resp.content) < 1024:
                    return False
                with open(save_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                if save_path.stat().st_size < 1024:
                    save_path.unlink()
                    return False
                return True
            except Exception as e:
                print(f"第{i+1}次下载失败 {url[:50]}...: {e}")
                if i < retry - 1:
                    time.sleep(2)
                else:
                    print(f"下载失败 {url[:50]}...: {e}，重试次数已用完")
        return False

    def close(self):
        if self.driver:
            self.driver.quit()

