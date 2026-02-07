import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 配置 OpenAI Client
client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://127.0.0.1:8045/v1"),
    api_key=os.getenv("LLM_API_KEY")
)

def generate_news_analysis(topic, date, research_data=None):
    """
    使用 LLM 生成新闻分析内容

    :param topic: 新闻主题
    :param date: 日期 (YYYYMMDD)
    :param research_data: 网络研究数据 (来自 web_researcher)
    :return: 新闻分析数据字典
    """
    print(f"🤖 AI 正在分析新闻: {topic}...")

    # 构建上下文信息
    context = ""
    if research_data and research_data.get("summary"):
        context = f"\n\n【搜索结果概要】\n{research_data['summary']}\n"
        if research_data.get("key_facts"):
            context += f"\n【关键事实】\n" + "\n".join(f"- {fact}" for fact in research_data['key_facts'][:5])

    system_prompt = """你是一位专业的新闻分析师,擅长用通俗易懂、现代感强的方式解读热点事件。

【核心要求】
1. **风格**: 现代、幽默、有见地。**绝对禁止**使用"哥们儿姐们儿"、"亲爱的朋友们"、"家人们"等过时或油腻的开场白。直入主题，不要废话。
2. **结构**: 三幕式叙事
   - 起因 (60-80字): 事件背景和触发原因
   - 发展 (60-80字): 事件进展和关键转折
   - 影响 (60-80字): 结果分析和社会影响
3. **情感倾向**: 准确判断 positive/negative/neutral
4. **轻松总结**: 200字左右的通俗易懂总结

【输出格式】
严格的 JSON 格式,不要包含 markdown 代码块标记:
{
  "topic": "新闻主题",
  "date": "YYYYMMDD",
  "headline": "吸引人的标题(10-15字)",
  "timeline": {
    "cause": "起因描述(60-80字,口语化)",
    "development": "发展描述(60-80字,有画面感)",
    "impact": "影响描述(60-80字,贴近生活)"
  },
  "key_actors": ["主体1", "主体2"],
  "sentiment": "positive/negative/neutral",
  "sources": ["url1", "url2"],
  "casual_summary": "轻松总结(200字,观点犀利,不落俗套,直接讲事)"
}
"""

    user_prompt = f"""请分析以下新闻事件: {topic}
日期: {date or "最近"}
{context}

要求:
1. 标题要简洁有力,吸引眼球
2. 三幕式内容要像讲故事,有画面感
3. 轻松总结要通俗易懂,避免官话套话
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 使用本地API支持的模型名
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        content = response.choices[0].message.content.strip()
        # 清理可能存在的 markdown 标记
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]

        data = json.loads(content)

        # 确保字段存在
        data['topic'] = topic
        data['date'] = date or ""

        # 如果有研究数据,补充来源
        if research_data and research_data.get("sources"):
            data['sources'] = research_data['sources'][:5]

        return data

    except Exception as e:
        print(f"❌ 新闻分析生成失败: {e}")
        # Fallback 数据,防止程序崩溃
        return {
            "topic": topic,
            "date": date or "",
            "headline": f"{topic}深度解读",
            "timeline": {
                "cause": "AI 生成出错,请检查 API 连接。",
                "development": "AI 生成出错,请检查 API 连接。",
                "impact": "AI 生成出错,请检查 API 连接。"
            },
            "key_actors": [],
            "sentiment": "neutral",
            "sources": [],
            "casual_summary": "AI 生成出错,请检查网络配置。"
        }
