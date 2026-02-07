"""
新闻脚本生成模块
从 audio_generator.py 的三幕脚本逻辑改编
"""

def generate_news_script(news_data):
    """
    生成三幕式新闻脚本,用于匹配 3 张封面图

    :param news_data: 新闻分析数据 (来自 news_generator)
    :return: [track1, track2, track3] 三段脚本
    """

    topic = news_data.get("topic", "这个热点")
    headline = news_data.get("headline", "")
    timeline = news_data.get("timeline", {})
    casual_summary = news_data.get("casual_summary", "")

    # 提取三幕内容
    cause = timeline.get("cause", "")
    development = timeline.get("development", "")
    impact = timeline.get("impact", "")

    # 构建三幕脚本
    tracks = [
        # Track 1: 开场 + 起因
        f"""大家好,今天咱们聊聊{topic}。

{casual_summary if casual_summary else headline}

事情是这样的:
{cause}""",

        # Track 2: 发展
        f"""{development}""",

        # Track 3: 影响 + 结语
        f"""{impact}

总结一下,这件事的核心就是: {headline}。

以上就是今天的新闻解读,我们下次见!"""
    ]

    # 去除首尾空白
    return [track.strip() for track in tracks]
