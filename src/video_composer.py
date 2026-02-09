"""
视频合成模块
整合图片、音频、字幕、特效，生成最终视频

功能：
- 4段式视频合成（Hook-Reason-Emotion-CTA）
- 字幕叠加
- Ken Burns动效
- 文字特效叠加
"""

import os
import numpy as np
from moviepy import (
    ImageClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, TextClip, CompositeAudioClip
)
from typing import List, Dict, Optional
from src.video_effects import create_text_overlay, get_ken_burns_params
from src.subtitle_generator import generate_srt, save_srt
from PIL import Image


class VideoComposer:
    """
    视频合成器

    整合所有素材生成最终视频
    """

    def __init__(self, output_dir: str):
        """
        初始化视频合成器

        Args:
            output_dir: 输出目录路径
        """
        self.output_dir = output_dir
        self.target_size = (1080, 1920)  # 竖屏 9:16

    def compose(
        self,
        image_paths: List[str],
        audio_path: str,
        script_data: Dict,
        output_path: str,
        add_subtitles: bool = True,
        ken_burns: bool = True
    ) -> str:
        """
        合成视频主函数

        Args:
            image_paths: 图片路径列表（4张，对应Hook-Reason-Emotion-CTA）
            audio_path: 混音后的音频路径
            script_data: 脚本数据（包含时间戳和文本）
            output_path: 输出视频路径
            add_subtitles: 是否添加字幕
            ken_burns: 是否添加Ken Burns动效

        Returns:
            输出视频路径
        """
        if len(image_paths) != 4:
            raise ValueError(f"需要4张图片（Hook-Reason-Emotion-CTA），当前: {len(image_paths)}")

        # 1. 加载音频并获取总时长
        audio_clip = AudioFileClip(audio_path)
        total_duration = audio_clip.duration

        # 2. 从脚本数据提取4段时长
        script = script_data.get("script", {})
        segments = ["hook", "reason", "emotion", "cta"]
        durations = [script.get(seg, {}).get("duration", 0) for seg in segments]

        # 如果时长缺失，平均分配
        if sum(durations) == 0:
            durations = [total_duration / 4] * 4

        # 3. 为每张图片创建视频片段
        video_clips = []
        current_time = 0

        for i, (img_path, duration) in enumerate(zip(image_paths, durations)):
            segment_name = segments[i]

            # 加载图片
            img = Image.open(img_path)
            img_resized = self._resize_image(img, self.target_size)

            # 创建图片clip并应用Ken Burns动效
            img_array = np.array(img_resized)

            if ken_burns:
                # 获取该段落的动效类型
                effect_type = self._get_effect_type(segment_name)
                clip = self._create_ken_burns_clip(img_resized, duration, effect_type)
            else:
                clip = ImageClip(img_array, duration=duration)

            video_clips.append(clip)
            current_time += duration

        # 4. 拼接视频片段
        final_video = concatenate_videoclips(video_clips, method="compose")

        # 5. 添加音频（MoviePy 2.x使用with_audio而不是set_audio）
        final_video = final_video.with_audio(audio_clip)

        # 6. 生成字幕（可选）
        if add_subtitles:
            subtitle_segments = self._extract_subtitle_segments(script_data)
            srt_path = output_path.replace(".mp4", ".srt")
            save_srt(subtitle_segments, srt_path)
            # 注意：MoviePy的字幕叠加较复杂，这里仅生成SRT文件
            # 实际字幕渲染可使用ffmpeg或其他工具

        # 7. 导出视频（优化：降低fps提升速度）
        final_video.write_videofile(
            output_path,
            fps=24,  # 降低到24fps提升生成速度（原30fps）
            codec='libx264',
            audio_codec='aac',
            preset='ultrafast',  # 改为ultrafast加速编码
            threads=8  # 增加线程数
        )

        # 清理资源
        audio_clip.close()
        final_video.close()

        return output_path

    def _resize_image(self, img: Image.Image, target_size: tuple) -> Image.Image:
        """
        调整图片大小并裁剪以适应目标尺寸（保持纵横比）

        Args:
            img: PIL Image对象
            target_size: 目标尺寸 (width, height)

        Returns:
            调整后的PIL Image
        """
        target_w, target_h = target_size
        img_w, img_h = img.size

        # 计算缩放比例（取较大值以填充画面）
        scale = max(target_w / img_w, target_h / img_h)

        # 缩放图片
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 居中裁剪
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        img_cropped = img_resized.crop((left, top, left + target_w, top + target_h))

        return img_cropped

    def _get_effect_type(self, segment_name: str) -> str:
        """
        根据段落类型返回合适的Ken Burns动效

        Args:
            segment_name: 段落名称（hook/reason/emotion/cta）

        Returns:
            动效类型
        """
        effect_map = {
            "hook": "zoom_in",      # 吸引注意 - 放大
            "reason": "slow_zoom",  # 平稳展开 - 慢速放大
            "emotion": "zoom_in",   # 情绪渲染 - 放大
            "cta": "slow_zoom"      # 收束呼吁 - 慢速放大（避免zoom_out产生黑框）
        }
        return effect_map.get(segment_name, "zoom_in")

    def _create_ken_burns_clip(
        self,
        img: Image.Image,
        duration: float,
        effect_type: str
    ) -> ImageClip:
        """
        创建带Ken Burns动效的视频片段（MoviePy 2.x兼容版本）

        Args:
            img: PIL Image对象
            duration: 持续时间
            effect_type: 动效类型

        Returns:
            ImageClip对象
        """
        params = get_ken_burns_params(effect_type, duration)

        # 将PIL Image转换为numpy数组
        img_array = np.array(img)

        # 创建基础clip
        clip = ImageClip(img_array, duration=duration)

        # MoviePy 2.x: 使用resized方法应用缩放动效
        if params["start_scale"] != params["end_scale"]:
            # 定义缩放函数
            def resize_func(t):
                progress = t / duration
                scale = params["start_scale"] + (params["end_scale"] - params["start_scale"]) * progress
                return scale

            # MoviePy 2.x使用clip.resized()方法（注意是resized不是resize）
            clip = clip.resized(resize_func)

        return clip

    def _add_text_overlay(
        self,
        clip: ImageClip,
        text: str,
        style: str
    ) -> CompositeVideoClip:
        """
        在视频片段上添加文字叠加

        Args:
            clip: 视频片段
            text: 文字内容
            style: 文字样式

        Returns:
            合成后的视频片段
        """
        # 创建文字overlay图片
        overlay_img = create_text_overlay(text, self.target_size[0], 200, style)

        # 转换为ImageClip
        overlay_clip = ImageClip(overlay_img, duration=clip.duration)
        overlay_clip = overlay_clip.set_position(("center", 100))  # 顶部居中

        # 合成
        return CompositeVideoClip([clip, overlay_clip])

    def _extract_subtitle_segments(self, script_data: Dict) -> List[Dict]:
        """
        从脚本数据提取字幕片段

        Args:
            script_data: 脚本数据

        Returns:
            字幕片段列表 [{"start": 0, "end": 2, "text": "..."}]
        """
        segments = []
        script = script_data.get("script", {})

        current_time = 0
        for seg_name in ["hook", "reason", "emotion", "cta"]:
            seg_data = script.get(seg_name, {})
            text = seg_data.get("text", "")
            duration = seg_data.get("duration", 0)

            if text and duration > 0:
                # 简单分句（按句号、问号、感叹号分割）
                sentences = text.replace("？", "?").replace("！", "!").replace("。", ".").split(".")
                sentences = [s.strip() for s in sentences if s.strip()]

                # 平均分配时间
                if len(sentences) > 0:
                    time_per_sentence = duration / len(sentences)

                    for sentence in sentences:
                        segments.append({
                            "start": current_time,
                            "end": current_time + time_per_sentence,
                            "text": sentence
                        })
                        current_time += time_per_sentence
                else:
                    segments.append({
                        "start": current_time,
                        "end": current_time + duration,
                        "text": text
                    })
                    current_time += duration

        return segments
