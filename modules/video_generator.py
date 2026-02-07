import os
from moviepy import *

def generate_video(image_paths, audio_paths, output_path):
    """
    将图片和音频合并成视频
    :param image_paths: 图片路径列表 [img1, img2, img3]
    :param audio_paths: 音频路径列表 [aud1, aud2, aud3]
    :param output_path: 输出视频路径
    """
    print(f"🎬 开始生成视频: {output_path}")

    clips = []

    # 确保图片和音频数量一致
    min_len = min(len(image_paths), len(audio_paths))

    for i in range(min_len):
        img_path = image_paths[i]
        aud_path = audio_paths[i]

        try:
            # 加载音频
            audio_clip = AudioFileClip(aud_path)

            # 加载图片并设置持续时间与音频一致
            # ImageClip in v2 might need explicit duration
            image_clip = ImageClip(img_path).with_duration(audio_clip.duration)

            # 设置音频
            video_clip = image_clip.with_audio(audio_clip)

            # 可选：添加简单的淡入淡出效果
            if i > 0:
                video_clip = video_clip.with_effects([vfx.CrossFadeIn(1.0)])

            clips.append(video_clip)
            print(f"  - 片段 {i+1} 就绪: Img={os.path.basename(img_path)} + Aud={os.path.basename(aud_path)} ({audio_clip.duration:.1f}s)")

        except Exception as e:
            print(f"  ❌ 处理片段 {i+1} 失败: {e}")
            return

    if not clips:
        print("❌ 没有有效的片段用于生成视频")
        return

    try:
        # 拼接所有片段
        final_video = concatenate_videoclips(clips, method="compose")

        # 导出视频
        # preset='ultrafast' for speed (sacrifice little compression for speed)
        # threads=None lets ffmpeg decide optimal thread count
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",  # 改为最快模式
            threads=8,          # 增加线程数
            logger=None,
            ffmpeg_params=["-pix_fmt", "yuv420p"]
        )
        print(f"✅ 视频生成成功！")

    except Exception as e:
        print(f"❌ 视频导出失败: {e}")
