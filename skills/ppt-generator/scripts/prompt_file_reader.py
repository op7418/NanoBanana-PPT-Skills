#!/usr/bin/env python3
"""
提示词文件读取器
从 JSON 文件读取预定义的转场提示词
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class PromptFileReader:
    """提示词文件读取器"""

    def __init__(self, prompts_file: str):
        """
        初始化读取器

        Args:
            prompts_file: 提示词 JSON 文件路径

        JSON 文件格式:
        {
            "preview": "预览视频提示词",
            "transitions": {
                "01-02": "第1-2页转场提示词",
                "02-03": "第2-3页转场提示词",
                ...
            }
        }
        """
        self.prompts_file = prompts_file
        self.prompts_data: Dict[str, Any] = {}

        if not os.path.exists(prompts_file):
            raise FileNotFoundError(
                f"❌ 提示词文件未找到: {prompts_file}\n"
                f"请确保文件存在"
            )

        # 加载提示词文件
        with open(prompts_file, 'r', encoding='utf-8') as f:
            self.prompts_data = json.load(f)

        print(f"✅ 提示词文件已加载")
        print(f"   路径: {prompts_file}")

        # 统计信息
        preview_exists = "preview" in self.prompts_data
        transitions_count = len(self.prompts_data.get("transitions", {}))
        print(f"   预览提示词: {'✓' if preview_exists else '✗'}")
        print(f"   转场提示词: {transitions_count} 个")

    def generate_prompt(
        self,
        frame_start_path: str,
        frame_end_path: str,
        content_context: Optional[str] = None
    ) -> str:
        """
        获取转场提示词

        Args:
            frame_start_path: 起始帧图片路径
            frame_end_path: 结束帧图片路径
            content_context: 内容上下文（不使用）

        Returns:
            prompt: 转场描述文本
        """
        # 从文件名提取页码
        from_num = self._extract_slide_number(frame_start_path)
        to_num = self._extract_slide_number(frame_end_path)
        transition_key = f"{from_num}-{to_num}"

        print(f"\n🎬 读取转场提示词...")
        print(f"   起始帧: {Path(frame_start_path).name}")
        print(f"   结束帧: {Path(frame_end_path).name}")
        print(f"   转场键: {transition_key}")

        # 获取提示词
        transitions = self.prompts_data.get("transitions", {})
        prompt = transitions.get(transition_key)

        if not prompt:
            # 尝试其他格式的键
            alt_key = f"{int(from_num)}-{int(to_num)}"
            prompt = transitions.get(alt_key)

        if not prompt:
            raise KeyError(
                f"❌ 未找到转场提示词: {transition_key}\n"
                f"可用的转场键: {list(transitions.keys())}"
            )

        print(f"✅ 转场提示词读取成功！")
        print(f"\n转场描述：")
        print(f"{'='*60}")
        print(prompt)
        print(f"{'='*60}\n")

        return prompt

    def generate_preview_prompt(self, first_slide_path: str) -> str:
        """
        获取预览视频提示词

        Args:
            first_slide_path: 首页图片路径

        Returns:
            prompt: 预览视频提示词
        """
        print(f"\n🎬 读取预览提示词...")
        print(f"   首页: {Path(first_slide_path).name}")

        prompt = self.prompts_data.get("preview")

        if not prompt:
            raise KeyError(
                f"❌ 未找到预览提示词\n"
                f"请在 JSON 文件中添加 'preview' 字段"
            )

        print(f"✅ 预览提示词读取成功！")
        print(f"\n预览动效描述：")
        print(f"{'='*60}")
        print(prompt)
        print(f"{'='*60}\n")

        return prompt

    def _extract_slide_number(self, file_path: str) -> str:
        """
        从文件路径提取幻灯片编号

        Args:
            file_path: 文件路径（如 slide-01.png）

        Returns:
            slide_num: 幻灯片编号（如 "01"）
        """
        filename = Path(file_path).stem  # 获取不含扩展名的文件名
        # 尝试从 "slide-XX" 格式提取
        if '-' in filename:
            parts = filename.split('-')
            return parts[-1]  # 返回最后一部分
        return filename

    def get_all_transition_keys(self) -> list:
        """获取所有可用的转场键"""
        return list(self.prompts_data.get("transitions", {}).keys())


if __name__ == "__main__":
    """测试代码"""
    # 创建测试 JSON 文件
    test_data = {
        "preview": "A gentle breathing animation brings the cover to life. "
                   "Soft light rays sweep across glass surfaces while tiny particles float. "
                   "Text remains perfectly crisp and stable.",
        "transitions": {
            "01-02": "Smooth camera push with parallax motion. Glass elements shift gracefully.",
            "02-03": "Elegant lateral movement. Gradients blend through rich colors.",
            "03-04": "Cinematic zoom reveals new composition. Frosted glass panels slide."
        }
    }

    # 写入测试文件
    test_file = "test_prompts.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    # 测试读取器
    reader = PromptFileReader(test_file)

    # 测试获取预览提示词
    preview = reader.generate_preview_prompt("slide-01.png")

    # 测试获取转场提示词
    for i in range(1, 4):
        try:
            prompt = reader.generate_prompt(
                f"slide-0{i}.png",
                f"slide-0{i+1}.png"
            )
        except KeyError as e:
            print(e)

    # 清理测试文件
    os.remove(test_file)
