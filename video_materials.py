#!/usr/bin/env python3
"""
视频素材生成模块
负责生成预览视频和所有页面过渡视频
支持并发控制（最大并发数：3）
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from kling_api import KlingVideoGenerator
from prompt_file_reader import PromptFileReader


class VideoMaterialsGenerator:
    """视频素材生成器"""

    def __init__(
        self,
        kling_client: Optional[KlingVideoGenerator] = None,
        prompt_generator = None,
        max_concurrent: int = 3,
        prompts_file: Optional[str] = None
    ):
        """
        初始化生成器

        Args:
            kling_client: 可灵API客户端（如果不提供，自动创建）
            prompt_generator: 转场提示词生成器（如果不提供，必须提供prompts_file）
            max_concurrent: 最大并发数，默认3
            prompts_file: 提示词文件路径（必需，由Claude Code生成）
        """
        self.kling_client = kling_client or KlingVideoGenerator()

        # 选择提示词生成器（优先级：文件 > 自定义）
        if prompts_file:
            self.prompt_generator = PromptFileReader(prompts_file)
            print(f"✅ 使用提示词文件: {prompts_file}")
        elif prompt_generator:
            self.prompt_generator = prompt_generator
            print(f"✅ 使用自定义提示词生成器")
        else:
            raise ValueError(
                "❌ 缺少转场提示词！\n\n"
                "视频生成需要转场提示词文件，请按以下步骤操作：\n"
                "1. 在 Claude Code 中运行以下提示：\n"
                "   '请分析 outputs/xxx/images 中的图片，生成转场视频提示词，\n"
                "    保存为 outputs/xxx/transition_prompts.json'\n"
                "2. 然后使用 --prompts-file 参数指定生成的文件路径\n\n"
                "示例:\n"
                "  python generate_ppt_video.py \\\n"
                "    --slides-dir outputs/xxx/images \\\n"
                "    --output-dir outputs/xxx_video \\\n"
                "    --prompts-file outputs/xxx/transition_prompts.json"
            )

        self.max_concurrent = max_concurrent

        print(f"✅ 视频素材生成器初始化完成")
        print(f"   最大并发数: {max_concurrent}")

    def generate_preview_video(
        self,
        first_slide_path: str,
        output_dir: str,
        duration: str = "5",
        mode: str = "pro"
    ) -> Dict[str, str]:
        """
        生成首页预览视频（首尾帧相同，微动效）

        Args:
            first_slide_path: 第一页PPT图片路径
            output_dir: 输出目录
            duration: 视频时长（5或10秒）
            mode: 生成模式（std/pro，首尾帧必须用pro）

        Returns:
            result: {
                'video_path': 视频文件路径,
                'prompt': 使用的提示词,
                'duration': 实际耗时（秒）
            }
        """
        print("\n" + "="*80)
        print("🎬 生成首页预览视频")
        print("="*80)

        # 生成预览提示词
        preview_prompt = self.prompt_generator.generate_preview_prompt(first_slide_path)

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "preview.mp4")

        # 生成视频（首尾帧相同）
        print(f"\n🚀 开始生成预览视频...")
        start_time = time.time()

        try:
            self.kling_client.generate_and_download(
                image_start=first_slide_path,
                image_end=first_slide_path,  # 首尾帧相同
                prompt=preview_prompt,
                output_path=output_path,
                model_name="kling-v2-6",
                duration=duration,
                mode=mode
            )

            elapsed = int(time.time() - start_time)

            result = {
                'video_path': output_path,
                'prompt': preview_prompt,
                'duration': elapsed
            }

            print(f"\n✅ 预览视频生成完成！")
            print(f"   耗时: {elapsed}秒")
            print(f"   路径: {output_path}\n")

            return result

        except Exception as e:
            print(f"\n❌ 预览视频生成失败: {str(e)}\n")
            raise

    def _generate_single_transition(
        self,
        slide_from: str,
        slide_to: str,
        output_path: str,
        content_context: Optional[str] = None,
        duration: str = "5",
        mode: str = "pro"
    ) -> Dict[str, any]:
        """
        生成单个过渡视频（内部方法）

        Returns:
            result: {
                'from_to': '1-2',
                'video_path': 路径,
                'prompt': 提示词,
                'duration': 耗时,
                'success': True/False,
                'error': 错误信息（如果失败）
            }
        """
        from_num = Path(slide_from).stem.split('-')[-1]
        to_num = Path(slide_to).stem.split('-')[-1]
        transition_key = f"{from_num}-{to_num}"

        print(f"\n📹 生成过渡视频 [{transition_key}]")
        print(f"   {Path(slide_from).name} → {Path(slide_to).name}")

        try:
            # 生成转场提示词
            transition_prompt = self.prompt_generator.generate_prompt(
                frame_start_path=slide_from,
                frame_end_path=slide_to,
                content_context=content_context
            )

            # 生成视频
            start_time = time.time()

            self.kling_client.generate_and_download(
                image_start=slide_from,
                image_end=slide_to,
                prompt=transition_prompt,
                output_path=output_path,
                model_name="kling-v2-6",
                duration=duration,
                mode=mode
            )

            elapsed = int(time.time() - start_time)

            return {
                'from_to': transition_key,
                'video_path': output_path,
                'prompt': transition_prompt,
                'duration': elapsed,
                'success': True
            }

        except Exception as e:
            return {
                'from_to': transition_key,
                'video_path': output_path,
                'prompt': '',
                'duration': 0,
                'success': False,
                'error': str(e)
            }

    def generate_transition_videos(
        self,
        slides_paths: List[str],
        output_dir: str,
        content_contexts: Optional[List[str]] = None,
        duration: str = "5",
        mode: str = "pro"
    ) -> Dict[str, Dict]:
        """
        批量生成所有页面过渡视频（支持并发控制）

        Args:
            slides_paths: PPT图片路径列表（按顺序）
            output_dir: 输出目录
            content_contexts: 每个过渡的内容上下文列表（可选）
            duration: 视频时长
            mode: 生成模式

        Returns:
            transitions: {
                '1-2': {'video_path': ..., 'prompt': ..., 'duration': ...},
                '2-3': {...},
                ...
            }
        """
        print("\n" + "="*80)
        print("🎬 批量生成过渡视频")
        print("="*80)

        num_slides = len(slides_paths)
        num_transitions = num_slides - 1

        print(f"\n📊 任务统计：")
        print(f"   总页数: {num_slides}")
        print(f"   过渡视频数: {num_transitions}")
        print(f"   最大并发: {self.max_concurrent}")
        print(f"   预计耗时: {num_transitions * 100 / self.max_concurrent:.0f}-{num_transitions * 120 / self.max_concurrent:.0f}秒\n")

        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)

        # 准备任务列表
        tasks = []
        for i in range(num_transitions):
            slide_from = slides_paths[i]
            slide_to = slides_paths[i + 1]

            from_num = Path(slide_from).stem.split('-')[-1]
            to_num = Path(slide_to).stem.split('-')[-1]

            output_path = os.path.join(output_dir, f"transition_{from_num}_to_{to_num}.mp4")

            context = None
            if content_contexts and i < len(content_contexts):
                context = content_contexts[i]

            tasks.append({
                'slide_from': slide_from,
                'slide_to': slide_to,
                'output_path': output_path,
                'content_context': context
            })

        # 使用线程池执行（限制并发数）
        results = {}
        completed_count = 0
        failed_count = 0

        print(f"🚀 开始生成（并发数: {self.max_concurrent}）...\n")
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(
                    self._generate_single_transition,
                    task['slide_from'],
                    task['slide_to'],
                    task['output_path'],
                    task['content_context'],
                    duration,
                    mode
                ): task for task in tasks
            }

            # 收集结果
            for future in as_completed(future_to_task):
                result = future.result()
                transition_key = result['from_to']
                results[transition_key] = result

                completed_count += 1

                if result['success']:
                    print(f"✅ [{completed_count}/{num_transitions}] 过渡视频 {transition_key} 完成 ({result['duration']}秒)")
                else:
                    failed_count += 1
                    print(f"❌ [{completed_count}/{num_transitions}] 过渡视频 {transition_key} 失败: {result['error']}")

        total_elapsed = int(time.time() - start_time)

        # 汇总报告
        print("\n" + "="*80)
        print("📊 批量生成完成")
        print("="*80)
        print(f"   总耗时: {total_elapsed}秒 ({total_elapsed/60:.1f}分钟)")
        print(f"   成功: {num_transitions - failed_count}/{num_transitions}")
        print(f"   失败: {failed_count}/{num_transitions}")

        if failed_count > 0:
            print(f"\n⚠️  以下过渡视频生成失败：")
            for key, result in results.items():
                if not result['success']:
                    print(f"   - {key}: {result['error']}")

        print("="*80 + "\n")

        return results

    def save_metadata(self, output_dir: str, metadata: Dict):
        """
        保存元数据到JSON文件

        Args:
            output_dir: 输出目录
            metadata: 元数据字典
        """
        metadata_path = os.path.join(output_dir, "video_metadata.json")

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"💾 元数据已保存: {metadata_path}")

    def generate_all_materials(
        self,
        slides_paths: List[str],
        output_dir: str,
        content_contexts: Optional[List[str]] = None,
        duration: str = "5",
        mode: str = "pro",
        skip_preview: bool = False
    ) -> Dict:
        """
        一键生成所有视频素材（预览+所有过渡）

        Args:
            slides_paths: PPT图片路径列表
            output_dir: 输出目录
            content_contexts: 内容上下文列表
            duration: 视频时长
            mode: 生成模式
            skip_preview: 是否跳过预览视频生成

        Returns:
            all_results: {
                'preview': {...},
                'transitions': {...},
                'total_duration': 总耗时,
                'success_count': 成功数,
                'failed_count': 失败数
            }
        """
        print("\n" + "="*80)
        print("🎬 一键生成所有视频素材")
        print("="*80)

        total_start = time.time()
        all_results = {
            'preview': None,
            'transitions': {},
            'total_duration': 0,
            'success_count': 0,
            'failed_count': 0
        }

        # 1. 生成预览视频
        if not skip_preview:
            try:
                preview_result = self.generate_preview_video(
                    first_slide_path=slides_paths[0],
                    output_dir=output_dir,
                    duration=duration,
                    mode=mode
                )
                all_results['preview'] = preview_result
                all_results['success_count'] += 1
            except Exception as e:
                print(f"⚠️  预览视频生成失败，继续生成过渡视频: {str(e)}")
                all_results['failed_count'] += 1
        else:
            print("⏭️  跳过预览视频生成")

        # 2. 生成所有过渡视频
        transition_results = self.generate_transition_videos(
            slides_paths=slides_paths,
            output_dir=output_dir,
            content_contexts=content_contexts,
            duration=duration,
            mode=mode
        )

        all_results['transitions'] = transition_results

        # 统计成功/失败数
        for result in transition_results.values():
            if result['success']:
                all_results['success_count'] += 1
            else:
                all_results['failed_count'] += 1

        # 总耗时
        all_results['total_duration'] = int(time.time() - total_start)

        # 保存元数据
        self.save_metadata(output_dir, all_results)

        # 最终报告
        print("\n" + "="*80)
        print("🎉 所有视频素材生成完成！")
        print("="*80)
        print(f"   总耗时: {all_results['total_duration']}秒 ({all_results['total_duration']/60:.1f}分钟)")
        print(f"   成功: {all_results['success_count']}")
        print(f"   失败: {all_results['failed_count']}")
        print(f"   输出目录: {output_dir}")
        print("="*80 + "\n")

        return all_results


if __name__ == "__main__":
    """测试代码"""
    from dotenv import load_dotenv
    load_dotenv()

    # 初始化生成器
    generator = VideoMaterialsGenerator(max_concurrent=3)

    # 测试数据
    test_slides = [
        "outputs/20260109_121822/images/slide-01.png",
        "outputs/20260109_121822/images/slide-02.png",
        "outputs/20260109_121822/images/slide-03.png"
    ]

    # 内容上下文
    contexts = [
        "从封面页过渡到第一个内容页",
        "从第一个内容页过渡到第二个内容页"
    ]

    # 生成所有素材
    results = generator.generate_all_materials(
        slides_paths=test_slides,
        output_dir="test_outputs/video_materials",
        content_contexts=contexts,
        duration="5",
        mode="pro"
    )

    print(f"\n✅ 测试完成！")
    print(f"   预览视频: {results['preview']['video_path'] if results['preview'] else 'N/A'}")
    print(f"   过渡视频: {len(results['transitions'])} 个")
