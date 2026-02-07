import os
import json
import uuid
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

# Configuration
# 豆包语音合成 v3 API (OpenSpeech)
DOUBAO_API_URL = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"
DOUBAO_ACCESS_TOKEN = os.getenv("DOUBAO_ACCESS_TOKEN")
DOUBAO_APP_ID = os.getenv("DOUBAO_APP_ID")
DOUBAO_RESOURCE_ID = os.getenv("DOUBAO_RESOURCE_ID", "seed-tts-2.0")
VOICE_TYPE = os.getenv("VOICE_TYPE", "zh_male_m191_uranus_bigtts")

def generate_podcast_segments(zodiac, fortune_data):
    """
    生成分段播客脚本，用于分段 TTS
    返回一个字典，包含各个环节的文本
    """
    zodiac_name = zodiac.split(' ')[0]
    month_str = f"{fortune_data['month'][-2:]}月"

    # 处理星星符号，转换为文字
    def parse_stars(score):
        count = score.count('⭐')
        return f"{count}颗星" if count > 0 else score

    love_score = parse_stars(fortune_data['love']['score'])
    career_score = parse_stars(fortune_data['career']['score'])
    wealth_score = parse_stars(fortune_data['wealth']['score'])

    segments = {
        "01_开场": f"""
这里是星运电台，欢迎收听{zodiac_name}的{month_str}运势播报。
亲爱的{zodiac_name}朋友们，本月你们的整体状态非常值得期待。
""",
        "02_爱情": f"""
首先是大家最关心的爱情运势。
本月{zodiac_name}的爱情运给到了{love_score}的评价，关键词是“{fortune_data['love']['keyword']}”。
{fortune_data['love']['content']}
""",
        "03_事业": f"""
接着来看看事业方面。
事业运势{career_score}。关键词“{fortune_data['career']['keyword']}”。
{fortune_data['career']['content']}
""",
        "04_财运": f"""
最后是财运，给到{wealth_score}。
{fortune_data['wealth']['content']}
""",
        "05_结语": f"""
总结一下，{month_str}对于{zodiac_name}来说，是一个{fortune_data['advice']}的好时机。
希望大家都能把握住机会，我们下期再见！
"""
    }

    # 去除首尾空白
    return {k: v.strip() for k, v in segments.items()}

def generate_podcast_script(zodiac, fortune_data):
    """保留旧接口以兼容（或者直接弃用）"""
    segs = generate_podcast_segments(zodiac, fortune_data)
    return "\n\n".join(segs.values())

def generate_three_act_script(zodiac, fortune_data):
    """
    生成三幕式脚本，专门用于匹配 3 张封面图
    Track 1 (对应爱情图): 开场白 + 爱情运势
    Track 2 (对应事业图): 事业运势
    Track 3 (对应财富图): 财富运势 + 结语
    """
    segments = generate_podcast_segments(zodiac, fortune_data)

    tracks = [
        # Track 1: Intro + Love
        f"{segments['01_开场']}\n\n{segments['02_爱情']}",

        # Track 2: Career
        f"{segments['03_事业']}",

        # Track 3: Wealth + Outro
        f"{segments['04_财运']}\n\n{segments['05_结语']}"
    ]

    return tracks

def generate_audio(text, output_path):
    """
    调用豆包语音合成 v3 API 生成音频文件
    """
    if not DOUBAO_ACCESS_TOKEN:
        print("⚠️ 未配置 DOUBAO_ACCESS_TOKEN，跳过音频生成")
        return

    print(f"正在调用豆包 TTS v3 生成音频: {output_path}...")

    # 构造请求头
    # 根据截图文档：Token 使用 X-Api-Access-Key
    headers = {
        "X-Api-Access-Key": DOUBAO_ACCESS_TOKEN,
        "X-Api-Resource-Id": DOUBAO_RESOURCE_ID,
        "X-Api-App-Key": DOUBAO_APP_ID,
        "Content-Type": "application/json",
        "Connection": "keep-alive"
    }

    # 构造请求体
    # 移除文本中的指令，改用 audio_params 中的 emotion 参数

    payload = {
        "req_params": {
            "text": text,
            "speaker": VOICE_TYPE,
            "additions": json.dumps({
                "disable_markdown_filter": False,
                "enable_language_detector": True,
                "enable_latex_tn": True,
                "disable_default_bit_rate": True,
                "max_length_to_filter_parenthesis": 0,
                "cache_config": {"text_type": 1, "use_cache": True}
            }),
            "audio_params": {
                "format": "mp3",
                "sample_rate": 24000,
                "speed_ratio": 1.1, # 语速稍快
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
                "emotion": "story"  # 使用 story 情感模式，适合运势播报
            }
        }
    }

    try:
        response = requests.post(DOUBAO_API_URL, json=payload, headers=headers, timeout=60, stream=True) # Enable streaming

        if response.status_code == 200:
            # 准备一个 buffer 或者直接追加写入文件
            with open(output_path, "wb") as f:
                # 豆包 v3 协议可能是流式返回多个 JSON 对象，每个对象以换行符分隔
                # 或者是一个持续的 SSE 流。requests 的 iter_lines 可以处理。
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        # line 是 bytes，需要 decode
                        line_text = line.decode('utf-8')
                        data = json.loads(line_text)

                        # 提取音频数据
                        # 兼容 v3 常见结构: data["data"]["audio"] (base64)
                        if data and "data" in data and isinstance(data["data"], dict) and "audio" in data["data"]:
                            audio_chunk = base64.b64decode(data["data"]["audio"])
                            f.write(audio_chunk)
                        # 兼容可能得直接 Base64 (较少见但保留逻辑)
                        elif data and "data" in data and isinstance(data["data"], str) and len(data["data"]) > 100:
                            audio_chunk = base64.b64decode(data["data"])
                            f.write(audio_chunk)

                        # 检查是否结束 (部分协议有 is_last 字段，但通常读完 stream 即可)

                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        print(f"⚠️ 解析 Chunk 出错: {e}")

            # 验证文件大小
            file_size = os.path.getsize(output_path)
            if file_size > 10000: # 大于 10KB 才算有效
                print(f"✅ 音频生成成功: {output_path} (Size: {file_size/1024:.2f} KB)")
            else:
                print(f"⚠️ 音频生成可能不完整: {output_path} (Size: {file_size} bytes)")

        else:
            print(f"❌ 请求失败: {response.status_code}")
            try:
                print(f"   Response: {response.json()}")
            except:
                print(f"   Response: {response.text}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"❌ 请求异常: {str(e)}")
