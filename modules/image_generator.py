import os
from openai import OpenAI
from dotenv import load_dotenv
import base64
import requests

load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("IMAGE_API_KEY"),
    base_url=os.getenv("IMAGE_API_BASE_URL")
)

def generate_images(topic_name, prompts, output_dir):
    """
    根据 Prompts 调用 API 生成图片 (NanoBanana Pro)
    """
    generated_paths = []

    for i, prompt in enumerate(prompts):
        print(f"    - 正在处理第 {i+1}/3 张封面图 ({topic_name})...")

        # 确定文件名
        # 1=起因, 2=发展, 3=影响
        suffix = ["起因", "发展", "影响"]
        file_name = f"act{i+1}_{suffix[i]}.png"
        output_path = os.path.join(output_dir, file_name)

        # 检查文件是否已存在
        if os.path.exists(output_path):
            print(f"      ⏭️ 图片已存在，跳过生成: {file_name}")
            generated_paths.append(output_path)
            continue

        try:
            print(f"      🎨 调用 NanoBanana Pro 生成中...")
            # 调用生图 API
            response = client.images.generate(
                model="NanoBanana Pro",
                prompt=prompt,
                n=1,
                size="1024x1792", # 9:16 竖屏
                response_format="b64_json"
            )

            # 保存图片
            if response.data[0].b64_json:
                image_data = base64.b64decode(response.data[0].b64_json)
                with open(output_path, "wb") as f:
                    f.write(image_data)
                print(f"      ✅ 图片已保存: {file_name}")
                generated_paths.append(output_path)
            elif response.data[0].url:
                img_res = requests.get(response.data[0].url)
                with open(output_path, "wb") as f:
                    f.write(img_res.content)
                print(f"      ✅ 图片已下载: {file_name}")
                generated_paths.append(output_path)

        except Exception as e:
            print(f"      ❌ 第 {i+1} 张图片生成失败: {e}")

    return generated_paths
