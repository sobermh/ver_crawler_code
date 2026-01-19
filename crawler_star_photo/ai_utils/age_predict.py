import asyncio
import os
import shutil
import re
from volcenginesdkarkruntime import AsyncArk
import dotenv

dotenv.load_dotenv()

# --- 路径配置 ---
CURRENT_SCRIPT_PATH = os.path.abspath(__file__)
PROJECT_PATH = os.path.dirname(os.path.dirname(CURRENT_SCRIPT_PATH))
SOURCE_DIR = os.path.join(PROJECT_PATH, "star_photos", "于适 蛟龙行动")
OUTPUT_ROOT = os.path.join(PROJECT_PATH, "star_photos", "于适 蛟龙行动_age")

client = AsyncArk(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key=os.getenv('ARK_API_KEY')
)

# 限制并发数：比如同时有 5 个请求在跑，防止被 API 封禁
sem = asyncio.Semaphore(10)

async def predict_and_move(file_name):
    """封装：预测 + 移动文件"""
    async with sem:  # 使用信号量控制并发
        src_path = os.path.join(SOURCE_DIR, file_name)
        try:
            print(f"开始分析: {file_name}")
            abs_img_path = os.path.abspath(src_path)
            
            response = await client.responses.create(
                model="doubao-seed-1-8-251228",
                input=[
                    {"role": "user", "content": [
                        {"type": "input_image", "image_url": f"file://{abs_img_path}"},
                        {"type": "input_text", "text": "判断图片中的人物年龄是几岁,只返回区间(如:21-25)。区间:16-20,21-25,26-30。"}
                    ]},
                ]
            )
            
            res_text = ""
            for item in response.output:
                if hasattr(item, 'type') and item.type == 'message':
                    res_text = item.content[0].text
                    break
            
            # 使用正则清洗，只保留 "数字-数字" 格式，防止文件夹名出错
            match = re.search(r'\d+-\d+', res_text)
            age_range = match.group() if match else "unknown"
            
            # 移动逻辑
            target_dir = os.path.join(OUTPUT_ROOT, age_range)
            os.makedirs(target_dir, exist_ok=True)
            dest_path = os.path.join(target_dir, file_name)
            
            if os.path.exists(dest_path):
                os.remove(dest_path)
            
            shutil.move(src_path, dest_path)
            print(f"✅ 完成: {file_name} -> {age_range}")
            
        except Exception as e:
            print(f"❌ 出错 {file_name}: {e}")

async def main():
    os.makedirs(SOURCE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not files:
        print("未找到图片文件。")
        return

    print(f"检测到 {len(files)} 张图片，开始并发处理...")
    
    # 创建任务列表
    tasks = [predict_and_move(f) for f in files]
    
    # 并发执行所有任务
    await asyncio.gather(*tasks)
    print("--- 所有任务已完成 ---")

if __name__ == "__main__":
    asyncio.run(main())