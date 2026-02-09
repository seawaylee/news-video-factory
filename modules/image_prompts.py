"""
新闻场景图片提示词生成模块
从 image_prompts.py 改编，移除占星元素，改为新闻场景可视化
"""

def smart_truncate(text, max_length=80):
    """
    智能截断文本，优先在标点符号处断句

    :param text: 原始文本
    :param max_length: 最大长度
    :return: 截断后的文本
    """
    if len(text) <= max_length:
        return text

    # 优先在句号、感叹号、问号处截断
    for sep in ['。', '！', '？', '；']:
        pos = text[:max_length].rfind(sep)
        if pos > max_length * 0.6:  # 至少保留60%的内容
            return text[:pos+1]

    # 其次在逗号、顿号处截断
    for sep in ['，', '、']:
        pos = text[:max_length].rfind(sep)
        if pos > max_length * 0.6:
            return text[:pos+1] + '...'

    # 最后在空格处截断
    pos = text[:max_length].rfind(' ')
    if pos > max_length * 0.6:
        return text[:pos] + '...'

    # 实在找不到合适的位置，直接截断并加省略号
    return text[:max_length-3] + '...'

def generate_news_image_prompts(news_data):
    """
    根据新闻数据生成3个场景图的 Prompt
    风格: 手绘草图、信息图表风、竖屏海报

    :param news_data: 新闻分析数据
    :return: [prompt1, prompt2, prompt3] 三个提示词
    """

    # 基础风格 - 保持手绘风格，改为新闻场景
    base_style = """(masterpiece, best quality), (vertical:1.4), (aspect ratio: 9:16), (sketch style), (hand drawn), (journalistic infographic), (Chinese New Year theme), (Festive atmosphere)
Create a TALL VERTICAL PORTRAIT IMAGE (Aspect Ratio 9:16) HAND-DRAWN SKETCH style infographic poster.

**CRITICAL: HAND-DRAWN AESTHETIC (Editorial Illustration Style)**
- Use ONLY pencil sketch lines, charcoal shading, ink pen strokes.
- Visible paper grain texture throughout (sketch paper grain).
- Line wobbles and imperfections (authentic hand-drawn feel).
- NO digital smoothness, NO vector graphics.
- Shading: crosshatching, stippling, charcoal smudges only.
- Background: Hand-drawn vintage paper texture (Beige/Parchment).
- Dominant Color: CHINESE RED and GOLD.
- **IMPORTANT**: Leave SIGNIFICANT margin (padding) around the text and central illustration to prevent cropping on mobile screens (TikTok/Douyin). Keep content CENTERED and SAFE from edges.
"""

    topic = news_data.get("topic", "热点新闻")
    headline = news_data.get("headline", "")
    timeline = news_data.get("timeline", {})

    # 提取三幕内容 - 智能截断
    cause = smart_truncate(timeline.get("cause", ""), max_length=80)
    development = smart_truncate(timeline.get("development", ""), max_length=80)
    impact = smart_truncate(timeline.get("impact", ""), max_length=80)

    prompts = []

    # 1. 起因场景 - 事件背景
    prompt_cause = f"""{base_style}
**CONTENT TO RENDER (Text must be legible hand-written style):**
1. Top Title: "📰 {headline}"
2. Section Label: "直击现场" (Bold hand-lettering)
3. Brief Text (Write this on the paper): "{cause}"

**VISUAL COMPOSITION:**
- Center: A detailed sketch symbolizing the event's origin or trigger point.
- Scene suggestion: Document, meeting room, announcement scene, or symbolic representation of the cause.
- Layout: Infographic style with text sections separated by hand-drawn dividers.
- Color Palette: Chinese Red, Gold, Warm Sepia, Charcoal Grey.
- Add subtle icons or symbols related to the news topic (hand-drawn style).
"""
    prompts.append(prompt_cause)

    # 2. 发展场景 - 事件进展
    prompt_development = f"""{base_style}
**CONTENT TO RENDER (Text must be legible hand-written style):**
1. Top Title: "📰 {headline}"
2. Section Label: "精彩瞬间" (Bold hand-lettering)
3. Brief Text (Write this on the paper): "{development}"

**VISUAL COMPOSITION:**
- Center: A detailed sketch showing the progression or key turning point.
- Scene suggestion: Timeline visualization, multiple actors interacting, or process illustration.
- Layout: Infographic style with text sections separated by hand-drawn dividers.
- Color Palette: Vibrant Red, Orange, Gold, Pencil Lead Black.
- Add arrows or flow indicators showing progression (hand-drawn style).
"""
    prompts.append(prompt_development)

    # 3. 影响场景 - 结果与影响
    prompt_impact = f"""{base_style}
**CONTENT TO RENDER (Text must be legible hand-written style):**
1. Top Title: "📰 {headline}"
2. Section Label: "深度观察" (Bold hand-lettering)
3. Brief Text (Write this on the paper): "{impact}"

**VISUAL COMPOSITION:**
- Center: A detailed sketch illustrating the impact or consequences.
- Scene suggestion: Ripple effect, affected parties, outcome visualization, or future implications.
- Layout: Infographic style with text sections separated by hand-drawn dividers.
- Color Palette: Deep Red, Festive Gold, Emerald accents.
- Add impact indicators or result symbols (hand-drawn style).
"""
    prompts.append(prompt_impact)

    return prompts
