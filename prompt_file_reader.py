#!/usr/bin/env python3
"""
提示词文件读取器
从 Claude Code 生成的提示词文件中读取转场描述
"""

import json
from pathlib import Path
from typing import Optional


class PromptFileReader:
    """从文件读取提示词"""

    def __init__(self, prompts_file: str):
        """
        初始化读取器

        Args:
            prompts_file: 提示词 JSON 文件路径
        """
        self.prompts_file = prompts_file

        with open(prompts_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        print(f"✅ 已加载提示词文件: {prompts_file}")
        print(f"   预览提示词: {'有' if self.data.get('preview') else '无'}")
        print(f"   转场提示词数: {len(self.data.get('transitions', []))}")

    def generate_prompt(
        self,
        frame_start_path: str,
        frame_end_path: str,
        content_context: Optional[str] = None
    ) -> str:
        """
        读取转场提示词

        Args:
            frame_start_path: 起始帧图片路径
            frame_end_path: 结束帧图片路径
            content_context: 内容上下文（忽略）

        Returns:
            prompt: 转场描述文本
        """
        # 从文件名提取页码
        start_name = Path(frame_start_path).stem
        end_name = Path(frame_end_path).stem

        start_num = int(start_name.split('-')[-1])
        end_num = int(end_name.split('-')[-1])

        print(f"\n🎬 读取转场提示词...")
        print(f"   起始帧: {Path(frame_start_path).name} (第{start_num}页)")
        print(f"   结束帧: {Path(frame_end_path).name} (第{end_num}页)")

        # 查找对应的转场提示词
        for transition in self.data.get('transitions', []):
            if transition['from_slide'] == start_num and transition['to_slide'] == end_num:
                prompt = transition['prompt']
                print(f"✅ 找到转场提示词！")
                print(f"\n转场描述：")
                print(f"{'='*60}")
                print(prompt)
                print(f"{'='*60}\n")
                return prompt

        # 如果没找到，返回错误
        raise ValueError(
            f"❌ 未找到转场提示词: {start_num} -> {end_num}\n"
            f"请确保提示词文件包含此转场"
        )

    def generate_preview_prompt(self, first_slide_path: str) -> str:
        """
        读取首页预览提示词

        Args:
            first_slide_path: 首页图片路径

        Returns:
            prompt: 预览视频提示词
        """
        print(f"\n🎬 读取首页预览提示词...")
        print(f"   首页: {Path(first_slide_path).name}")

        preview_data = self.data.get('preview')
        if not preview_data:
            raise ValueError("❌ 提示词文件中没有预览提示词")

        prompt = preview_data['prompt']
        print(f"✅ 找到预览提示词！")

        return prompt


if __name__ == "__main__":
    """测试代码"""
    import os

    test_file = "outputs/20260112_012753/transition_prompts.json"
    if os.path.exists(test_file):
        reader = PromptFileReader(test_file)

        # 测试转场提示词
        prompt = reader.generate_prompt(
            "outputs/20260112_012753/images/slide-01.png",
            "outputs/20260112_012753/images/slide-02.png"
        )
        print(f"\n提示词长度: {len(prompt)} 字符")

        # 测试预览提示词
        preview = reader.generate_preview_prompt(
            "outputs/20260112_012753/images/slide-01.png"
        )
        print(f"\n预览提示词长度: {len(preview)} 字符")
