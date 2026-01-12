#!/usr/bin/env python3
"""
FFmpeg 视频合成模块
负责将静态图片转视频、拼接视频片段、合成完整PPT视频
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional


class VideoComposer:
    """视频合成器"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        初始化合成器

        Args:
            ffmpeg_path: FFmpeg可执行文件路径
        """
        self.ffmpeg_path = ffmpeg_path

        # 检查FFmpeg是否可用
        try:
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ FFmpeg已就绪: {version_line}")
            else:
                raise Exception("FFmpeg版本检查失败")
        except Exception as e:
            raise Exception(
                f"❌ FFmpeg不可用！\n"
                f"请安装FFmpeg：\n"
                f"  Windows: choco install ffmpeg 或 scoop install ffmpeg\n"
                f"  macOS: brew install ffmpeg\n"
                f"  Linux: apt install ffmpeg\n"
                f"错误: {str(e)}"
            )

    def _run_ffmpeg(self, cmd: List[str], description: str = "") -> bool:
        """
        运行FFmpeg命令

        Args:
            cmd: FFmpeg命令参数列表
            description: 操作描述

        Returns:
            success: 是否成功
        """
        if description:
            print(f"🎬 {description}...")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            if result.returncode != 0:
                print(f"❌ FFmpeg执行失败:")
                print(f"   命令: {' '.join(cmd)}")
                print(f"   错误: {result.stderr}")
                return False

            if description:
                print(f"✅ {description}完成")

            return True

        except subprocess.TimeoutExpired:
            print(f"❌ FFmpeg执行超时")
            return False
        except Exception as e:
            print(f"❌ FFmpeg执行异常: {str(e)}")
            return False

    def create_static_video(
        self,
        image_path: str,
        duration: int = 2,
        output_path: Optional[str] = None,
        resolution: str = "1920x1080",
        fps: int = 24
    ) -> Optional[str]:
        """
        将静态图片转换为视频（停留N秒）

        Args:
            image_path: 图片路径
            duration: 停留时长（秒）
            output_path: 输出视频路径（如不指定，自动生成）
            resolution: 分辨率
            fps: 帧率

        Returns:
            output_path: 输出视频路径，失败返回None
        """
        if not os.path.exists(image_path):
            print(f"❌ 图片不存在: {image_path}")
            return None

        # 自动生成输出路径
        if not output_path:
            stem = Path(image_path).stem
            output_dir = Path(image_path).parent
            output_path = str(output_dir / f"{stem}_static.mp4")

        # 构建FFmpeg命令
        # 分离宽和高
        width, height = resolution.split('x')

        cmd = [
            self.ffmpeg_path,
            "-y",  # 覆盖输出文件
            "-loop", "1",  # 循环输入图片
            "-i", image_path,  # 输入图片
            "-c:v", "libx264",  # 使用H.264编码
            "-t", str(duration),  # 时长
            "-pix_fmt", "yuv420p",  # 像素格式（兼容性好）
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-r", str(fps),  # 帧率
            output_path
        ]

        description = f"图片转视频 ({Path(image_path).name}, {duration}秒)"
        success = self._run_ffmpeg(cmd, description)

        return output_path if success else None

    def concat_videos(
        self,
        video_list: List[str],
        output_path: str,
        use_concat_protocol: bool = True,
        normalize_params: bool = True,
        target_resolution: str = "1920x1080",
        target_fps: int = 24
    ) -> bool:
        """
        拼接多个视频

        Args:
            video_list: 视频路径列表（按顺序）
            output_path: 输出路径
            use_concat_protocol: 使用concat协议（更快，要求视频参数一致）
            normalize_params: 是否统一视频参数（重新编码）
            target_resolution: 目标分辨率
            target_fps: 目标帧率

        Returns:
            success: 是否成功
        """
        if not video_list:
            print("❌ 视频列表为空")
            return False

        # 检查所有视频是否存在
        for video_path in video_list:
            if not os.path.exists(video_path):
                print(f"❌ 视频不存在: {video_path}")
                return False

        if use_concat_protocol and not normalize_params:
            # 方法1: 使用concat demuxer（推荐，速度快，但要求参数一致）
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                concat_file = f.name
                for video_path in video_list:
                    abs_path = os.path.abspath(video_path)
                    f.write(f"file '{abs_path}'\n")

            try:
                cmd = [
                    self.ffmpeg_path,
                    "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_file,
                    "-c", "copy",
                    output_path
                ]

                description = f"拼接 {len(video_list)} 个视频（快速模式）"
                success = self._run_ffmpeg(cmd, description)

                return success

            finally:
                if os.path.exists(concat_file):
                    os.remove(concat_file)

        else:
            # 方法2: 使用concat filter（兼容性好，会重新编码）
            inputs = []
            for i, video_path in enumerate(video_list):
                inputs.extend(["-i", video_path])

            width, height = target_resolution.split('x')

            filter_parts = []
            for i in range(len(video_list)):
                filter_parts.append(
                    f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                    f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,"
                    f"fps={target_fps}[v{i}]"
                )

            filters_normalize = ";".join(filter_parts)
            concat_filter = "".join([f"[v{i}]" for i in range(len(video_list))])
            concat_filter += f"concat=n={len(video_list)}:v=1:a=0[outv]"

            filter_complex = filters_normalize + ";" + concat_filter

            cmd = [
                self.ffmpeg_path,
                "-y"
            ] + inputs + [
                "-filter_complex", filter_complex,
                "-map", "[outv]",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                output_path
            ]

            description = f"拼接 {len(video_list)} 个视频（统一参数模式）"
            success = self._run_ffmpeg(cmd, description)

            return success

    def compose_full_ppt_video(
        self,
        slides_paths: List[str],
        transitions_dict: Dict[str, str],
        output_path: str,
        slide_duration: int = 2,
        include_preview: bool = False,
        preview_video_path: Optional[str] = None,
        resolution: str = "1920x1080",
        fps: int = 24
    ) -> bool:
        """
        合成完整PPT视频

        流程：
        1. [可选] 预览视频
        2. 切换视频1-2
        3. 第2页静态（2秒）
        4. 切换视频2-3
        5. 第3页静态（2秒）
        ...

        Args:
            slides_paths: PPT图片路径列表
            transitions_dict: 过渡视频字典 {'1-2': 'path/to/video.mp4', ...}
            output_path: 最终输出路径
            slide_duration: 每页停留时长（秒）
            include_preview: 是否包含预览视频
            preview_video_path: 预览视频路径
            resolution: 分辨率
            fps: 帧率

        Returns:
            success: 是否成功
        """
        print("\n" + "="*80)
        print("🎬 合成完整PPT视频")
        print("="*80)

        num_slides = len(slides_paths)
        print(f"\n📊 合成参数：")
        print(f"   总页数: {num_slides}")
        print(f"   每页停留: {slide_duration}秒")
        print(f"   包含预览: {'是' if include_preview else '否'}")
        print(f"   分辨率: {resolution}")
        print(f"   帧率: {fps}fps\n")

        # 创建临时目录存放静态视频
        temp_dir = tempfile.mkdtemp(prefix="ppt_video_")
        print(f"📁 临时目录: {temp_dir}\n")

        try:
            # 1. 生成所有静态视频（除了第一页）
            print("📹 生成静态视频片段...")
            static_videos = {}

            for i in range(1, num_slides):  # 跳过第一页
                slide_path = slides_paths[i]
                slide_num = Path(slide_path).stem.split('-')[-1]

                static_path = os.path.join(temp_dir, f"slide-{slide_num}-static.mp4")

                result = self.create_static_video(
                    image_path=slide_path,
                    duration=slide_duration,
                    output_path=static_path,
                    resolution=resolution,
                    fps=fps
                )

                if not result:
                    print(f"❌ 第{slide_num}页静态视频生成失败")
                    return False

                static_videos[slide_num] = static_path

            print(f"✅ {len(static_videos)} 个静态视频生成完成\n")

            # 2. 按顺序组装视频片段列表
            print("📝 组装视频序列...")
            video_sequence = []

            # 可选：添加预览视频
            if include_preview and preview_video_path and os.path.exists(preview_video_path):
                video_sequence.append(preview_video_path)
                print(f"   + 预览视频")

            # 添加过渡和静态视频
            for i in range(num_slides - 1):
                from_num = Path(slides_paths[i]).stem.split('-')[-1]
                to_num = Path(slides_paths[i+1]).stem.split('-')[-1]
                transition_key = f"{from_num}-{to_num}"

                # 添加过渡视频
                if transition_key in transitions_dict:
                    transition_path = transitions_dict[transition_key]
                    if os.path.exists(transition_path):
                        video_sequence.append(transition_path)
                        print(f"   + 过渡视频 {transition_key}")
                    else:
                        print(f"   ⚠️  过渡视频缺失: {transition_key}")
                else:
                    print(f"   ⚠️  过渡视频未定义: {transition_key}")

                # 添加目标页静态视频
                if to_num in static_videos:
                    video_sequence.append(static_videos[to_num])
                    print(f"   + 静态视频 slide-{to_num} ({slide_duration}秒)")

            print(f"\n📊 视频序列：共 {len(video_sequence)} 个片段\n")

            # 3. 拼接所有视频
            if not video_sequence:
                print("❌ 没有可拼接的视频片段")
                return False

            print("🔗 开始拼接视频...")
            success = self.concat_videos(
                video_list=video_sequence,
                output_path=output_path,
                use_concat_protocol=True,
                normalize_params=True,
                target_resolution=resolution,
                target_fps=fps
            )

            if success:
                file_size = os.path.getsize(output_path)
                file_size_mb = file_size / (1024 * 1024)

                print("\n" + "="*80)
                print("✅ 完整PPT视频合成完成！")
                print("="*80)
                print(f"   输出路径: {output_path}")
                print(f"   文件大小: {file_size_mb:.2f} MB")
                print(f"   视频片段: {len(video_sequence)} 个")
                print("="*80 + "\n")
            else:
                print("\n❌ 视频拼接失败")

            return success

        finally:
            # 清理临时文件
            print(f"🧹 清理临时文件...")
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                print(f"✅ 临时目录已删除: {temp_dir}\n")


if __name__ == "__main__":
    """测试代码"""
    # 初始化合成器
    composer = VideoComposer()

    # 测试：图片转视频
    test_image = "outputs/20260109_121822/images/slide-02.png"
    if os.path.exists(test_image):
        print("\n测试1: 图片转静态视频")
        result = composer.create_static_video(
            image_path=test_image,
            duration=3,
            output_path="test_outputs/test_static.mp4"
        )
        if result:
            print(f"✅ 测试1通过: {result}")
        else:
            print("❌ 测试1失败")
    else:
        print(f"跳过测试：测试图片不存在 {test_image}")
