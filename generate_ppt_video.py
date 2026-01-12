#!/usr/bin/env python3
"""
PPT视频生成主流程脚本
整合图片生成、视频素材生成、视频合成功能
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入模块
from video_materials import VideoMaterialsGenerator
from video_composer import VideoComposer


def generate_ppt_video_from_images(
    slides_dir: str,
    output_dir: str,
    video_mode: str = "both",
    video_duration: str = "5",
    slide_duration: int = 5,
    video_quality: str = "pro",
    max_concurrent: int = 3,
    skip_preview: bool = False,
    prompts_file: Optional[str] = None  # 新增：提示词文件路径
):
    """
    从已有的PPT图片生成视频

    Args:
        slides_dir: PPT图片目录
        output_dir: 输出目录
        video_mode: 输出模式 - both（本地视频+网页）/ local（仅本地）/ web（仅网页）
        video_duration: 过渡视频时长（5或10秒）
        slide_duration: 每页停留时长
        video_quality: 视频质量（std/pro）
        max_concurrent: 最大并发数
        skip_preview: 是否跳过预览视频
    """
    print("\n" + "="*80)
    print("🎬 PPT视频生成 - 完整流程")
    print("="*80)

    # 1. 扫描PPT图片
    print(f"\n📁 扫描PPT图片目录: {slides_dir}")
    slides_paths = sorted(Path(slides_dir).glob("slide-*.png"))

    if not slides_paths:
        print(f"❌ 未找到PPT图片（格式：slide-*.png）")
        return None

    slides_paths = [str(p) for p in slides_paths]
    num_slides = len(slides_paths)

    print(f"✅ 找到 {num_slides} 页PPT")
    for i, path in enumerate(slides_paths, 1):
        print(f"   {i}. {Path(path).name}")

    # 2. 创建输出目录结构
    os.makedirs(output_dir, exist_ok=True)
    videos_dir = os.path.join(output_dir, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    print(f"\n📁 输出目录: {output_dir}")
    print(f"   视频素材: {videos_dir}/")

    # 3. 生成视频素材
    print("\n" + "="*80)
    print("阶段1: 生成视频素材（预览+过渡）")
    print("="*80)

    materials_generator = VideoMaterialsGenerator(
        max_concurrent=max_concurrent,
        prompts_file=prompts_file  # 传入提示词文件
    )

    # 准备内容上下文（可选，帮助生成更好的转场提示词）
    content_contexts = []
    for i in range(num_slides - 1):
        context = f"从第{i+1}页过渡到第{i+2}页"
        content_contexts.append(context)

    # 生成所有视频素材
    materials_result = materials_generator.generate_all_materials(
        slides_paths=slides_paths,
        output_dir=videos_dir,
        content_contexts=content_contexts,
        duration=video_duration,
        mode=video_quality,
        skip_preview=skip_preview
    )

    if materials_result['failed_count'] > 0:
        print(f"\n⚠️  警告：{materials_result['failed_count']} 个视频生成失败")
        print("继续合成，但最终视频可能不完整...")

    # 4. 合成完整视频（如果需要）
    if video_mode in ["both", "local"]:
        print("\n" + "="*80)
        print("阶段2: 合成完整PPT视频")
        print("="*80)

        composer = VideoComposer()

        # 准备过渡视频字典
        transitions_dict = {}
        for key, result in materials_result['transitions'].items():
            if result['success']:
                transitions_dict[key] = result['video_path']

        # 合成完整视频
        full_video_path = os.path.join(output_dir, "full_ppt_video.mp4")

        preview_video = None
        if materials_result['preview'] and not skip_preview:
            preview_video = materials_result['preview']['video_path']

        compose_success = composer.compose_full_ppt_video(
            slides_paths=slides_paths,
            transitions_dict=transitions_dict,
            output_path=full_video_path,
            slide_duration=slide_duration,
            include_preview=False,  # 预览视频通常用于网页端，不放入完整视频
            preview_video_path=preview_video
        )

        if compose_success:
            print(f"✅ 完整视频已生成: {full_video_path}")
        else:
            print(f"❌ 完整视频合成失败")

    # 5. 生成网页播放器（如果需要）
    if video_mode in ["both", "web"]:
        print("\n" + "="*80)
        print("阶段3: 生成网页播放器")
        print("="*80)

        generate_video_viewer(
            slides_paths=slides_paths,
            transitions_result=materials_result['transitions'],
            preview_result=materials_result.get('preview'),
            output_dir=output_dir,
            videos_dir=videos_dir
        )

    # 6. 生成汇总报告
    print("\n" + "="*80)
    print("🎉 PPT视频生成完成！")
    print("="*80)

    print(f"\n📊 生成统计：")
    print(f"   PPT页数: {num_slides}")
    print(f"   视频素材: {materials_result['success_count']} 成功, {materials_result['failed_count']} 失败")
    print(f"   总耗时: {materials_result['total_duration']}秒 ({materials_result['total_duration']/60:.1f}分钟)")

    print(f"\n📁 输出文件：")
    if video_mode in ["both", "local"]:
        print(f"   完整视频: {output_dir}/full_ppt_video.mp4")
    if video_mode in ["both", "web"]:
        print(f"   网页播放器: {output_dir}/video_index.html")
    print(f"   视频素材: {videos_dir}/")
    print(f"   元数据: {videos_dir}/video_metadata.json")

    print("\n" + "="*80 + "\n")

    return {
        'output_dir': output_dir,
        'num_slides': num_slides,
        'materials_result': materials_result,
        'video_mode': video_mode
    }


def generate_video_viewer(
    slides_paths: List[str],
    transitions_result: Dict,
    preview_result: Optional[Dict],
    output_dir: str,
    videos_dir: str
):
    """
    生成网页视频播放器

    Args:
        slides_paths: PPT图片路径列表
        transitions_result: 过渡视频结果
        preview_result: 预览视频结果
        output_dir: 输出目录
        videos_dir: 视频素材目录
    """
    from pathlib import Path
    import shutil

    print(f"📄 生成网页播放器...")

    # 复制模板文件
    template_path = "templates/video_viewer.html"
    output_html = os.path.join(output_dir, "video_index.html")

    if not os.path.exists(template_path):
        print(f"⚠️  模板文件不存在: {template_path}，跳过网页生成")
        return

    # 构建数据
    slides_data = []
    for slide_path in slides_paths:
        rel_path = os.path.relpath(slide_path, output_dir)
        slides_data.append(rel_path)

    transitions_data = {}
    for key, result in transitions_result.items():
        if result['success']:
            rel_path = os.path.relpath(result['video_path'], output_dir)
            transitions_data[key] = rel_path

    preview_data = None
    if preview_result:
        preview_data = os.path.relpath(preview_result['video_path'], output_dir)

    # 读取模板
    with open(template_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 替换占位符
    html_content = html_content.replace(
        "/* SLIDES_DATA_PLACEHOLDER */",
        json.dumps(slides_data, ensure_ascii=False)
    )
    html_content = html_content.replace(
        "/* TRANSITIONS_DATA_PLACEHOLDER */",
        json.dumps(transitions_data, ensure_ascii=False)
    )
    html_content = html_content.replace(
        "/* PREVIEW_DATA_PLACEHOLDER */",
        json.dumps(preview_data, ensure_ascii=False) if preview_data else "null"
    )

    # 写入输出文件
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ 网页播放器已生成: {output_html}")


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description='PPT视频生成工具 - 从PPT图片生成带转场动效的视频',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法（使用Claude Code生成的提示词文件）
  python generate_ppt_video.py \\
    --slides-dir outputs/xxx/images \\
    --output-dir outputs/xxx_video \\
    --prompts-file outputs/xxx/transition_prompts.json

  # 完整参数
  python generate_ppt_video.py \\
    --slides-dir outputs/xxx/images \\
    --output-dir outputs/xxx_video \\
    --prompts-file outputs/xxx/transition_prompts.json \\
    --video-mode both \\
    --video-duration 5 \\
    --slide-duration 5 \\
    --video-quality pro \\
    --max-concurrent 3

工作流程:
  1. 生成PPT图片: python generate_ppt.py ...
  2. 让Claude Code分析图片生成提示词:
     在Claude Code中运行: "请分析outputs/xxx/images中的图片，生成转场提示词"
  3. 生成转场视频: python generate_ppt_video.py --prompts-file ...

注意事项:
  - 确保.env文件中配置了KLING_ACCESS_KEY和KLING_SECRET_KEY
  - 必须先用Claude Code分析图片生成transition_prompts.json文件
  - 首尾帧视频生成必须使用pro模式（高质量）
  - 可灵API并发限制为3，生成时间较长请耐心等待
        """
    )

    parser.add_argument(
        '--slides-dir',
        required=True,
        help='PPT图片目录（包含slide-01.png, slide-02.png等）'
    )

    parser.add_argument(
        '--output-dir',
        required=True,
        help='输出目录'
    )

    parser.add_argument(
        '--video-mode',
        choices=['both', 'local', 'web'],
        default='both',
        help='输出模式：both（本地视频+网页）/ local（仅本地）/ web（仅网页）'
    )

    parser.add_argument(
        '--video-duration',
        choices=['5', '10'],
        default='5',
        help='过渡视频时长（秒）'
    )

    parser.add_argument(
        '--slide-duration',
        type=int,
        default=5,
        help='每页停留时长（秒）'
    )

    parser.add_argument(
        '--video-quality',
        choices=['std', 'pro'],
        default='pro',
        help='视频质量：std（标准）/ pro（高品质，首尾帧必需）'
    )

    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=3,
        help='最大并发数（默认3，可灵API限制）'
    )

    parser.add_argument(
        '--skip-preview',
        action='store_true',
        help='跳过预览视频生成'
    )

    parser.add_argument(
        '--prompts-file',
        required=True,
        help='转场提示词文件路径（JSON格式，必须由Claude Code分析图片后生成）'
    )

    args = parser.parse_args()

    # 验证输入目录
    if not os.path.exists(args.slides_dir):
        print(f"❌ 错误: PPT图片目录不存在: {args.slides_dir}")
        sys.exit(1)

    # 验证提示词文件
    if not os.path.exists(args.prompts_file):
        print(f"❌ 错误: 提示词文件不存在: {args.prompts_file}")
        print(f"\n💡 如何生成提示词文件：")
        print(f"   1. 在 Claude Code 中运行以下提示：")
        print(f"      '请分析 {args.slides_dir} 中的图片，生成转场视频提示词，")
        print(f"       保存为 transition_prompts.json'")
        print(f"   2. 然后使用 --prompts-file 参数指定生成的文件路径")
        sys.exit(1)

    # 执行生成
    try:
        result = generate_ppt_video_from_images(
            slides_dir=args.slides_dir,
            output_dir=args.output_dir,
            video_mode=args.video_mode,
            video_duration=args.video_duration,
            slide_duration=args.slide_duration,
            video_quality=args.video_quality,
            max_concurrent=args.max_concurrent,
            skip_preview=args.skip_preview,
            prompts_file=args.prompts_file  # 传入提示词文件
        )

        if result:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
