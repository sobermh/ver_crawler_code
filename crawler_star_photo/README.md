# 明星照片爬虫

一个用于爬取明星各个年龄段照片的Python爬虫工具，支持按年龄段分类保存。

## 功能特点

- 🎯 按年龄段搜索和下载明星照片
- 📁 自动按年龄段分类保存到文件夹
- 🔍 支持百度图片搜索
- 🚀 提供两种版本：基础版本和Selenium版本
- ⚡ 自动去重，避免重复下载
- 📊 显示下载进度

## 安装依赖

### 使用 uv（推荐）

```bash
# 安装 uv（如果还没有安装）
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境并安装依赖
uv venv
uv pip install -e .

# 或者直接使用 uv run（自动管理环境）
uv run python star_photo_crawler_selenium.py
```

### 使用 pip（传统方式）

```bash
pip install -r requirements.txt
```

### Selenium版本额外要求

如果使用 `star_photo_crawler_selenium.py`，还需要：

1. 安装Chrome浏览器
2. ChromeDriver 会自动通过 `webdriver-manager` 管理，无需手动安装

## 使用方法

### 方法一：使用启动脚本（最简单，推荐）

**Windows:**
```bash
# 双击运行或在命令行执行
run.bat
```

**Linux/macOS:**
```bash
# 添加执行权限（首次运行）
chmod +x run.sh

# 运行
./run.sh
```

### 方法二：使用 uv 命令

```bash
# 使用 uv run（自动管理环境）
uv run python star_photo_crawler_selenium.py

# 或者先激活虚拟环境
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python star_photo_crawler_selenium.py
```

### 方法三：使用传统方式

```bash
# 基础版本（推荐先尝试）
python star_photo_crawler.py

# Selenium版本（更稳定，推荐）
python star_photo_crawler_selenium.py
```

然后按提示输入明星姓名，选择是否使用无头模式。

## 输出结构

照片会按以下结构保存：

```
star_photos/
└── [明星姓名]/
    ├── 10-15岁/
    │   ├── 10-15岁_001.jpg
    │   ├── 10-15岁_002.jpg
    │   └── ...
    ├── 16-20岁/
    │   ├── 16-20岁_001.jpg
    │   └── ...
    └── ...
```

## 自定义年龄段

可以在代码中修改 `age_ranges` 变量来自定义年龄段：

```python
age_ranges = [
    "10-15岁",
    "16-20岁",
    "21-25岁",
    # 添加更多年龄段...
]
```

注意：现在直接使用年龄区间进行搜索，例如搜索"10-15岁"而不是单个年龄"10岁"，这样搜索结果会更准确。

## 注意事项

1. ⚠️ 请遵守网站的robots.txt和使用条款
2. ⚠️ 不要过于频繁地请求，避免被封IP
3. ⚠️ 下载的图片仅供学习研究使用，请勿用于商业用途
4. ⚠️ 部分图片可能因为URL失效而无法下载
5. ⚠️ 建议在网络良好的环境下使用

## 常见问题

### Q: 下载失败怎么办？
A: 可能是网络问题或图片URL失效，程序会自动跳过失败的图片继续下载。

### Q: 如何修改下载数量？
A: 在代码中找到 `max_images` 参数，修改为你想要的数量。

### Q: ChromeDriver版本不匹配？
A: 确保ChromeDriver版本与Chrome浏览器版本匹配，或使用webdriver-manager自动管理。

## 许可证

本项目仅供学习交流使用。

