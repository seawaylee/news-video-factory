# Lessons Learned

## Logic & Common Sense
- **Date & Zodiac Accuracy**: Always check the specific year when generating content about Chinese New Year.
  - 2024 = Dragon (龙)
  - 2025 = Snake (蛇)
  - 2026 = Horse (马)
  - Feb 9, 2026 is strictly **pre-CNY (Horse)**. Do not refer to it as "Dragon Year" or "Snake Year".
- **Market Terminology**:
  - "Red Packet Campaign" (红包行情) = Pre-holiday rise expectation.
  - "Good Start" (开门红) = Post-holiday first trading day rise.
  - Do not mix these terms.

## Content Generation
- **Visual Safety**: Always leave significant margins (padding) for text in vertical videos (9:16) to prevent cropping by UI elements on TikTok/Douyin.
- **Retry Mechanisms**: External APIs (like image generation) can be unstable. Always implement retry logic (at least 3 retries) for critical API calls.
