"""
社交媒体文案生成模块
从 copy_generator.py 改编，适配新闻内容
"""

def generate_news_copy(news_data):
    """
    生成小红书风格的新闻解读文案
    要求：Emoji丰富，分段清晰，吸引眼球

    :param news_data: 新闻分析数据
    :return: 小红书文案字符串
    """
    topic = news_data.get("topic", "热点新闻")
    headline = news_data.get("headline", "")
    timeline = news_data.get("timeline", {})
    casual_summary = news_data.get("casual_summary", "")
    sentiment = news_data.get("sentiment", "neutral")
    date = news_data.get("date", "")

    # 根据情感选择emoji
    sentiment_emoji = {
        "positive": "🎉",
        "negative": "⚠️",
        "neutral": "📰"
    }
    emoji = sentiment_emoji.get(sentiment, "📰")

    # 格式化日期
    date_str = f"{date[4:6]}月{date[6:8]}日" if len(date) == 8 else "最新"

    copy = f"""
📰 {topic} - {date_str}深度解读来啦！{emoji}

👋 小伙伴们集合！最近是不是被这个热点刷屏了？别急，咱们一起来捋一捋到底发生了啥！

🔍 **核心标题**
{headline}

📖 **事件回顾**

【起因】{timeline.get('cause', '')}

【发展】{timeline.get('development', '')}

【影响】{timeline.get('impact', '')}

💡 **轻松解读**
{casual_summary}

---
🌟 **我的看法**
这件事告诉我们：信息爆炸的时代，保持独立思考很重要！大家怎么看？欢迎评论区讨论~

👇 觉得有用的话，记得点赞收藏哦！不然划走就找不到啦~ 💖

#热点新闻 #{topic} #新闻解读 #深度分析 #热点追踪 #信息分享
"""
    return copy.strip()
