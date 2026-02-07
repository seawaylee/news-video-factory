"""
新闻场景图片提示词生成模块
从 image_prompts.py 改编，移除占星元素，改为新闻场景可视化
"""

def generate_news_image_prompts(news_data):
    """
    根据新闻数据生成3个场景图的 Prompt
    风格: 手绘草图、信息图表风、竖屏海报

    :param news_data: 新闻分析数据
    :return: [prompt1, prompt2, prompt3] 三个提示词
    """

    # 基础风格 - 保持手绘风格，改为新闻场景
    base_style = """(masterpiece, best quality), (vertical:1.4), (aspect ratio: 9:16), (sketch style), (hand drawn), (journalistic infographic)
Create a TALL VERTICAL PORTRAIT IMAGE (Aspect Ratio 9:16) HAND-DRAWN SKETCH style infographic poster.

**CRITICAL: HAND-DRAWN AESTHETIC (Editorial Illustration Style)**
- Use ONLY pencil sketch lines, charcoal shading, ink pen strokes.
- Visible paper grain texture throughout (sketch paper grain).
- Line wobbles and imperfections (authentic hand-drawn feel).
- NO digital smoothness, NO vector graphics.
- Shading: crosshatching, stippling, charcoal smudges only.
- Background: Hand-drawn vintage paper texture (Beige/Parchment).
"""

    topic = news_data.get("topic", "热点新闻")
    headline = news_data.get("headline", "")
    timeline = news_data.get("timeline", {})

    # 提取三幕内容
    cause = timeline.get("cause", "")[:80]
    development = timeline.get("development", "")[:80]
    impact = timeline.get("impact", "")[:80]

    prompts = []

    # 1. 起因场景 - 事件背景
    prompt_cause = f"""{base_style}
**CONTENT TO RENDER (Text must be legible hand-written style):**
1. Top Title: "📰 {headline}"
2. Section Label: "起因" (Bold hand-lettering)
3. Brief Text (Write this on the paper): "{cause}"

**VISUAL COMPOSITION:**
- Center: A detailed sketch symbolizing the event's origin or trigger point.
- Scene suggestion: Document, meeting room, announcement scene, or symbolic representation of the cause.
- Layout: Infographic style with text sections separated by hand-drawn dividers.
- Color Palette: Warm Sepia, Charcoal Grey, Pencil Lead Black.
- Add subtle icons or symbols related to the news topic (hand-drawn style).
"""
    prompts.append(prompt_cause)

    # 2. 发展场景 - 事件进展
    prompt_development = f"""{base_style}
**CONTENT TO RENDER (Text must be legible hand-written style):**
1. Top Title: "📰 {headline}"
2. Section Label: "发展" (Bold hand-lettering)
3. Brief Text (Write this on the paper): "{development}"

**VISUAL COMPOSITION:**
- Center: A detailed sketch showing the progression or key turning point.
- Scene suggestion: Timeline visualization, multiple actors interacting, or process illustration.
- Layout: Infographic style with text sections separated by hand-drawn dividers.
- Color Palette: Cool Blue, Navy, Pencil Lead Black.
- Add arrows or flow indicators showing progression (hand-drawn style).
"""
    prompts.append(prompt_development)

    # 3. 影响场景 - 结果与影响
    prompt_impact = f"""{base_style}
**CONTENT TO RENDER (Text must be legible hand-written style):**
1. Top Title: "📰 {headline}"
2. Section Label: "影响" (Bold hand-lettering)
3. Brief Text (Write this on the paper): "{impact}"

**VISUAL COMPOSITION:**
- Center: A detailed sketch illustrating the impact or consequences.
- Scene suggestion: Ripple effect, affected parties, outcome visualization, or future implications.
- Layout: Infographic style with text sections separated by hand-drawn dividers.
- Color Palette: Emerald Green, Gold highlights, Pencil Lead Black.
- Add impact indicators or result symbols (hand-drawn style).
"""
    prompts.append(prompt_impact)

    return prompts
