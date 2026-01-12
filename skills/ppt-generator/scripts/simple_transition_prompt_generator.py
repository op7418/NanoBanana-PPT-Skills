#!/usr/bin/env python3
"""
简化版转场提示词生成器
不依赖 Claude API，使用预定义模板生成转场描述
"""

import os
from pathlib import Path
from typing import Optional


class SimpleTransitionPromptGenerator:
    """简化版转场提示词生成器"""

    # 预定义的转场提示词模板
    TRANSITION_TEMPLATES = [
        "The scene smoothly transitions with a gentle camera push forward. "
        "Background elements shift with subtle parallax motion while the glass surfaces "
        "catch soft light reflections. Text elements fade out gracefully and new text "
        "fades in with clarity maintained throughout. Ambient light particles drift "
        "slowly across the frame.",

        "A cinematic dolly movement guides the viewer's eye as the composition transforms. "
        "Gradient colors blend seamlessly while 3D glass objects rotate with elegant motion. "
        "All text remains crisp and stable, transitioning through a soft cross-dissolve. "
        "Volumetric lighting creates depth as the scene evolves.",

        "The transition unfolds with smooth lateral camera motion. Glassmorphism elements "
        "shift with fluid grace, their reflections dancing subtly. Background gradients "
        "morph through complementary hues. Text crossfades cleanly without distortion. "
        "Soft glow effects pulse gently during the change.",

        "A graceful zoom transition reveals the new composition. Frosted glass panels "
        "slide with organic motion while neon accent lights pulse softly. The background "
        "gradient shifts through rich, saturated tones. All typography maintains perfect "
        "clarity through a delicate fade transition.",

        "The scene transforms with an elegant orbital camera movement. Glass surfaces "
        "catch and release light in hypnotic patterns. Floating particles trace gentle "
        "arcs through the air. Text elements transition through smooth opacity changes, "
        "remaining sharp and readable throughout.",
    ]

    # 预定义的预览提示词模板
    PREVIEW_TEMPLATES = [
        "A subtle breathing effect animates the scene. Soft aurora-like light streams "
        "flow gently across the glass surfaces, creating mesmerizing reflections. "
        "Background gradients shift imperceptibly through harmonious color variations. "
        "Tiny luminous particles float lazily through the composition. All text remains "
        "perfectly still and crystal clear. The atmosphere is serene and contemplative, "
        "inviting interaction.",

        "The composition pulses with gentle life. Glassmorphism elements catch subtle "
        "light variations that sweep slowly across their surfaces. The gradient background "
        "breathes through soft color transitions. Ambient particles drift with peaceful "
        "motion. Typography stays completely stable and sharp. The scene radiates calm "
        "elegance and quiet anticipation.",

        "A serene micro-animation brings depth to the static image. Soft volumetric light "
        "rays drift slowly through the scene, illuminating glass surfaces with dancing "
        "highlights. The color palette shifts through gentle gradations. Floating light "
        "motes add subtle movement. All text elements remain crisp and motionless. "
        "The mood is tranquil and inviting.",
    ]

    def __init__(self):
        """初始化简化版生成器"""
        self._template_index = 0
        self._preview_index = 0
        print("✅ 简化版转场提示词生成器初始化完成")
        print("   模式: 预定义模板（不依赖 Claude API）")

    def generate_prompt(
        self,
        frame_start_path: str,
        frame_end_path: str,
        content_context: Optional[str] = None
    ) -> str:
        """
        生成转场提示词

        Args:
            frame_start_path: 起始帧图片路径
            frame_end_path: 结束帧图片路径
            content_context: 内容上下文（可选，在简化版中不使用）

        Returns:
            prompt: 转场描述文本
        """
        print(f"\n🎬 生成转场提示词（简化版）...")
        print(f"   起始帧: {Path(frame_start_path).name}")
        print(f"   结束帧: {Path(frame_end_path).name}")

        # 循环使用模板
        prompt = self.TRANSITION_TEMPLATES[self._template_index % len(self.TRANSITION_TEMPLATES)]
        self._template_index += 1

        print(f"✅ 转场提示词生成完成！")
        print(f"\n转场描述：")
        print(f"{'='*60}")
        print(prompt)
        print(f"{'='*60}\n")

        return prompt

    def generate_preview_prompt(self, first_slide_path: str) -> str:
        """
        生成首页预览视频的提示词（首尾帧相同，微动效）

        Args:
            first_slide_path: 首页图片路径

        Returns:
            prompt: 预览视频提示词
        """
        print(f"\n🎬 生成首页预览提示词（简化版）...")
        print(f"   首页: {Path(first_slide_path).name}")

        # 循环使用模板
        prompt = self.PREVIEW_TEMPLATES[self._preview_index % len(self.PREVIEW_TEMPLATES)]
        self._preview_index += 1

        print(f"✅ 预览提示词生成完成！")
        print(f"\n预览动效描述：")
        print(f"{'='*60}")
        print(prompt)
        print(f"{'='*60}\n")

        return prompt


if __name__ == "__main__":
    """测试代码"""
    generator = SimpleTransitionPromptGenerator()

    # 测试转场提示词生成
    for i in range(3):
        prompt = generator.generate_prompt(
            f"slide-0{i+1}.png",
            f"slide-0{i+2}.png"
        )

    # 测试预览提示词生成
    preview = generator.generate_preview_prompt("slide-01.png")
