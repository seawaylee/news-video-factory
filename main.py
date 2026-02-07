#!/usr/bin/env python3
"""
热点新闻视频生成器 - 主程序
改编自 horoscope-fortune 项目
"""
import os
import json
import argparse
import re
from modules.web_researcher import research_topic
from modules.news_generator import generate_news_analysis
from modules.news_script import generate_news_script
from modules.image_prompts import generate_news_image_prompts
from modules.copy_generator import generate_news_copy
from modules.audio_generator import generate_audio
from modules.image_generator import generate_images
from modules.video_generator import generate_video

def slugify(text):
    """
    将中文主题转为文件名安全的slug
    """
    # 移除特殊字符，保留中英文数字
    text = re.sub(r'[^\w\s-]', '', text)
    # 替换空格为连字符
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-').lower()[:50]  # 限制长度

def ensure_directories(topic_slug):
    """
    确保输出目录存在
    """
    base_path = f"results/{topic_slug}"
    dirs = {
        "root": base_path,
        "images": os.path.join(base_path, "封面图"),
        "audio": os.path.join(base_path, "播客mp3"),
        "copy": os.path.join(base_path, "小红书文案")
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    return dirs

def main():
    parser = argparse.ArgumentParser(description="热点新闻视频自动化生成器")
    parser.add_argument("-t", "--topic", type=str, required=True, help="新闻主题 (例如: 'DeepSeek发布R1模型')")
    parser.add_argument("-d", "--date", type=str, help="日期 (格式: YYYYMMDD, 例如: 20260207)")
    parser.add_argument("--skip-research", action="store_true", help="跳过网络搜索，直接使用 LLM 生成")
    args = parser.parse_args()

    topic = args.topic
    date = args.date or ""

    print(f"🚀 新闻视频生成器启动")
    print(f"   主题: {topic}")
    print(f"   日期: {date or '自动'}")
    print(f"   搜索: {'关闭' if args.skip_research else '开启'}")
    print("")

    # 1. 创建目录
    topic_slug = slugify(topic)
    dirs = ensure_directories(topic_slug)
    print(f"📁 输出目录: {dirs['root']}")

    # 2. 网络研究
    research_data = None
    research_file = os.path.join(dirs["root"], "research_raw.json")

    if not args.skip_research:
        if os.path.exists(research_file):
            print(f"\n🔍 发现本地研究数据，直接读取...")
            try:
                with open(research_file, "r", encoding="utf-8") as f:
                    research_data = json.load(f)
            except Exception as e:
                print(f"   ⚠️ 读取失败 ({e})，重新搜索...")

        if not research_data:
            print(f"\n🔍 开始网络研究...")
            research_data = research_topic(topic, date)
            # 保存原始数据
            with open(research_file, "w", encoding="utf-8") as f:
                json.dump(research_data, f, ensure_ascii=False, indent=2)
            print(f"   ✅ 研究数据已保存")
    else:
        print(f"\n⏭️  跳过网络搜索")

    # 3. 生成新闻分析
    news_file = os.path.join(dirs["root"], "news_data.json")
    news_data = None

    if os.path.exists(news_file):
        print(f"\n📰 发现本地新闻数据，直接读取...")
        try:
            with open(news_file, "r", encoding="utf-8") as f:
                news_data = json.load(f)
        except Exception as e:
            print(f"   ⚠️ 读取失败 ({e})，重新生成...")

    if not news_data:
        print(f"\n📰 生成新闻分析...")
        news_data = generate_news_analysis(topic, date, research_data)
        # 保存数据
        with open(news_file, "w", encoding="utf-8") as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ 新闻数据已保存")

    # 4. 生成小红书文案
    copy_path = os.path.join(dirs["copy"], "xiaohongshu.txt")
    if not os.path.exists(copy_path):
        print(f"\n📝 生成小红书文案...")
        xhs_copy = generate_news_copy(news_data)
        with open(copy_path, "w", encoding="utf-8") as f:
            f.write(xhs_copy)
        print(f"   ✅ 文案已保存")
    else:
        print(f"\n📝 小红书文案已存在，跳过")

    # 5. 生成图片提示词
    print(f"\n🎨 生成图片提示词...")
    prompts = generate_news_image_prompts(news_data)
    for i, prompt in enumerate(prompts):
        prompt_path = os.path.join(dirs["images"], f"prompt_act{i+1}.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(prompt)
    print(f"   ✅ 提示词已保存")

    # 6. 生成图片
    print(f"\n🖼️  生成封面图...")
    image_paths = generate_images(topic_slug, prompts, dirs["images"])
    # 确保路径排序正确
    image_paths.sort()

    if len(image_paths) < 3:
        print(f"   ⚠️ 图片生成不完整 ({len(image_paths)}/3)，可能无法生成视频")

    # 7. 生成脚本和音频
    print(f"\n🎙️  生成播客脚本和音频...")
    script_tracks = generate_news_script(news_data)
    audio_paths = []

    for i, track_text in enumerate(script_tracks):
        track_idx = i + 1
        script_path = os.path.join(dirs["audio"], f"script_act{track_idx}.txt")
        audio_path = os.path.join(dirs["audio"], f"act{track_idx}.mp3")

        # 保存脚本
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(track_text)

        # 生成音频
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
            print(f"   - 生成音频 Act {track_idx}...")
            generate_audio(track_text, audio_path)
        else:
            print(f"   - 音频 Act {track_idx} 已存在")

        audio_paths.append(audio_path)

    # 8. 合成视频
    if len(image_paths) == 3 and len(audio_paths) == 3:
        video_path = os.path.join(dirs["root"], f"{topic_slug}_新闻视频.mp4")
        if not os.path.exists(video_path):
            print(f"\n🎬 合成视频...")
            try:
                generate_video(image_paths, audio_paths, video_path)
                print(f"   ✅ 视频已保存: {video_path}")
            except Exception as e:
                print(f"   ❌ 视频生成失败: {e}")
        else:
            print(f"\n🎬 视频已存在: {video_path}")
    else:
        print(f"\n⚠️ 素材不足，跳过视频生成 (图片: {len(image_paths)}/3, 音频: {len(audio_paths)}/3)")

    print(f"\n✅ 所有任务完成！")
    print(f"   输出目录: {dirs['root']}")
    print(f"   视频文件: {topic_slug}_新闻视频.mp4")

if __name__ == "__main__":
    main()
