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

def review_content(topic, scripts, prompts):
    """
    审校 TTS 文稿和图片 Prompt 的逻辑性、事实性（年份/生肖/节日）和安全性。
    返回修正后的 (scripts, prompts)。
    """
    print(f"\n🕵️‍♂️ 启动逻辑审校节点 (Reviewer Agent)...")

    # 构造审校 Prompt
    system_prompt = """你是一个严格的内容审核主编 (Reviewer Agent)。
你的任务是审查并修正“新闻视频文案 (TTS Scripts)”和“AI绘画提示词 (Image Prompts)”中的逻辑错误、事实谬误和常识性问题。

🔍 **核心审查标准 (CRITICAL)**：
1. **时间与生肖逻辑 (Date & Zodiac)**：
   - **当前基准**：2026年 (马年/Horse Year)。
   - **严禁错误**：2026年绝不能说是“龙年”或“蛇年”。
   - **节前vs节后**：“红包行情”=节前上涨预期；“开门红”=节后首日上涨。
   - **修正动作**：如果发现“龙年A股”、“蛇年开局”等错误，必须立刻修正为“马年”或删除年份特指。

2. **Prompt 视觉安全 (Visual Safety)**：
   - 检查 Prompt 中是否包含防遮挡指令（如 "Leave margin", "Safe from edges", "Center composition"）。
   - 如果缺失，**必须**强制添加到 Prompt 末尾。

3. **文案一致性**：
   - 确保文案内容不自相矛盾（例如前一句说大涨，后一句说大跌）。

📥 **输入**：包含 topic, scripts, prompts 的 JSON。
📤 **输出**：严格的 JSON 格式，包含修正后的内容。
{
    "scripts": ["修正后的脚本1", "脚本2", "脚本3"],
    "prompts": ["修正后的Prompt1", "Prompt2", "Prompt3"],
    "review_comments": "简要说明发现了什么错误并如何修正了（例如：'修正了龙年为马年'，'添加了安全边距指令'）"
}
"""

    user_content = json.dumps({
        "topic": topic,
        "scripts": scripts,
        "prompts": prompts
    }, ensure_ascii=False)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # 使用智能模型进行审核
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.1 # 低温度以保持严谨和确定性
        )

        result_text = response.choices[0].message.content.strip()
        result = json.loads(result_text)

        comments = result.get('review_comments', '无修改')
        print(f"   ✅ 审校报告: {comments}")

        # 返回修正后的内容，如果格式不对则回退到原始值
        new_scripts = result.get("scripts", scripts)
        new_prompts = result.get("prompts", prompts)

        if len(new_scripts) != len(scripts):
            print("   ⚠️ 审校后脚本数量不一致，回退到原始脚本")
            new_scripts = scripts

        if len(new_prompts) != len(prompts):
            print("   ⚠️ 审校后Prompt数量不一致，回退到原始Prompt")
            new_prompts = prompts

        return new_scripts, new_prompts

    except Exception as e:
        print(f"   ⚠️ 审校服务异常 ({e})，跳过审校，使用原始内容。")
        return scripts, prompts
