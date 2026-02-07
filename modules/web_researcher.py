import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 初始化客户端
llm_client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def search_with_serper(query, num_results=10):
    """
    使用 Serper.dev API 进行搜索
    """
    if not SERPER_API_KEY:
        return None

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": num_results,
        "gl": "cn",  # 地理位置: 中国
        "hl": "zh-cn"  # 语言: 中文
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Serper API 返回错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Serper API 请求失败: {e}")
        return None

def search_with_tavily(query, max_results=10):
    """
    使用 Tavily AI API 进行搜索
    """
    if not TAVILY_API_KEY:
        return None

    url = "https://api.tavily.com/search"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": False
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ Tavily API 返回错误: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Tavily API 请求失败: {e}")
        return None

def format_search_results(serper_data=None, tavily_data=None):
    """
    统一格式化搜索结果
    """
    formatted_results = []

    # 处理 Serper 结果
    if serper_data and "organic" in serper_data:
        for item in serper_data["organic"][:10]:
            formatted_results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
                "source": "serper"
            })

    # 处理 Tavily 结果
    if tavily_data and "results" in tavily_data:
        for item in tavily_data["results"][:10]:
            formatted_results.append({
                "title": item.get("title", ""),
                "snippet": item.get("content", ""),
                "url": item.get("url", ""),
                "source": "tavily"
            })

    return formatted_results

def summarize_with_llm(query, search_results):
    """
    使用 LLM 总结搜索结果
    """
    # 构建搜索结果文本
    results_text = "\n\n".join([
        f"【{i+1}】{r['title']}\n{r['snippet']}\n来源: {r['url']}"
        for i, r in enumerate(search_results[:10])
    ])

    system_prompt = """你是一个专业的新闻分析师。你的任务是从搜索结果中提取关键信息，并以结构化的JSON格式返回。

要求：
1. 提取事件的关键事实
2. 梳理时间线（起因、发展、影响）
3. 识别关键人物/机构
4. 判断舆情倾向（positive/negative/neutral）
5. 撰写200字综述

返回格式必须是有效的JSON，不要包含任何其他文字。"""

    user_prompt = f"""请分析以下关于"{query}"的搜索结果，并返回JSON格式的分析：

{results_text}

请返回以下JSON结构：
{{
  "key_facts": ["事实1", "事实2", "事实3"],
  "timeline": {{
    "cause": "事件起因（60-80字）",
    "development": "发展过程（60-80字）",
    "impact": "影响/结果（60-80字）"
  }},
  "key_actors": ["主体1", "主体2"],
  "sentiment": "positive/negative/neutral",
  "summary": "200字综述",
  "sources": ["{search_results[0]['url'] if search_results else ''}", "{search_results[1]['url'] if len(search_results) > 1 else ''}"]
}}"""

    try:
        response = llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        return json.loads(result_text)

    except Exception as e:
        print(f"❌ LLM 分析失败: {e}")
        return None

def research_topic(topic, date=None):
    """
    主入口：搜索 + 总结
    Returns: {
        "key_facts": [...],
        "timeline": {...},
        "key_actors": [...],
        "sentiment": "positive/negative/neutral",
        "summary": "200字综述",
        "sources": ["url1", "url2", ...]
    }
    """
    print(f"🔍 开始研究主题: {topic}")

    # 构建搜索查询
    search_query = f"{topic} 新闻" if date is None else f"{topic} {date} 新闻"

    # 尝试多个搜索源
    serper_result = None
    tavily_result = None

    if SERPER_API_KEY:
        print("  - 使用 Serper.dev 搜索...")
        serper_result = search_with_serper(search_query)

    if TAVILY_API_KEY and not serper_result:
        print("  - 使用 Tavily AI 搜索...")
        tavily_result = search_with_tavily(search_query)

    # 格式化搜索结果
    search_results = format_search_results(serper_result, tavily_result)

    if not search_results:
        print("⚠️ 未获取到搜索结果，将使用 LLM 生成内容")
        # 返回空结构，后续由 LLM 直接生成
        return {
            "key_facts": [],
            "timeline": {
                "cause": "",
                "development": "",
                "impact": ""
            },
            "key_actors": [],
            "sentiment": "neutral",
            "summary": "",
            "sources": [],
            "raw_results": []
        }

    print(f"  ✅ 获取到 {len(search_results)} 条搜索结果")

    # 使用 LLM 分析
    print("  - 使用 LLM 分析搜索结果...")
    analysis = summarize_with_llm(topic, search_results)

    if analysis:
        analysis["raw_results"] = search_results
        print("  ✅ 研究完成")
        return analysis
    else:
        # LLM 失败时返回原始结果
        return {
            "key_facts": [r["snippet"] for r in search_results[:5]],
            "timeline": {
                "cause": "",
                "development": "",
                "impact": ""
            },
            "key_actors": [],
            "sentiment": "neutral",
            "summary": search_results[0]["snippet"] if search_results else "",
            "sources": [r["url"] for r in search_results[:5]],
            "raw_results": search_results
        }
