# 热点新闻视频生成器 (News Video Factory)

自动将热点新闻转化为竖屏短视频的工具。

## 功能特性

- 🔍 **智能搜索**: 自动联网采集新闻信息
- 📝 **轻松解读**: AI生成接地气的新闻解读文案
- 🎨 **场景可视化**: 自动生成新闻场景插图
- 🎙️ **语音合成**: 豆包TTS生成高质量解说音频
- 🎬 **视频合成**: 自动合成竖屏短视频(9:16)

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的API密钥:

```bash
cp .env.example .env
```

需要配置:
- LLM API (用于内容生成)
- 搜索API (Serper.dev 或 Tavily)
- 图片生成API
- 豆包TTS API

### 3. 生成新闻视频

```bash
python main.py -t "DeepSeek发布R1模型" -d 20260207
```

参数说明:
- `-t, --topic`: 新闻主题 (必需)
- `-d, --date`: 日期 YYYYMMDD格式 (可选)
- `--skip-research`: 跳过网络搜索,直接使用LLM生成 (可选)

## 输出结构

```
results/{topic_slug}/
├── news_data.json          # 核心数据
├── research_raw.json       # 搜索原始数据
├── 封面图/
│   ├── act1.png
│   ├── act2.png
│   └── act3.png
├── 播客mp3/
│   ├── act1.mp3
│   ├── act2.mp3
│   └── act3.mp3
├── 小红书文案/
│   └── xiaohongshu.txt
└── {topic}_新闻视频.mp4
```

## 内容结构

视频采用**三幕式结构**:
1. **起因** - 事件背景和触发原因
2. **发展** - 事件进展和关键转折
3. **影响** - 结果分析和社会影响

## 技术架构

基于成熟的 [horoscope-fortune](https://github.com/seawaylee/horoscope-fortune) 项目改编:

- 复用: 图片生成、TTS、视频合成模块
- 新增: 网络搜索与信息总结
- 改编: 内容生成提示词和数据结构

## 许可证

MIT License
