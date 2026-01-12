#!/usr/bin/env python3
"""
转场提示词生成器
使用 Claude + 首尾帧视频生成提示词模板，分析图片差异并生成转场描述
"""

import os
import base64
from pathlib import Path
from typing import Optional
from anthropic import Anthropic


class TransitionPromptGenerator:
    """转场提示词生成器"""

    # 默认模板路径（相对于技能目录）
    DEFAULT_TEMPLATE_PATH = "assets/prompts/transition_template.md"

    def __init__(self, template_path: Optional[str] = None):
        """
        初始化生成器

        Args:
            template_path: 首尾帧提示词模板路径（可选）
        """
        # 确定模板路径
        if template_path:
            self.template_path = template_path
        else:
            # 尝试从技能目录查找
            skill_dir = Path(__file__).parent.parent
            self.template_path = str(skill_dir / self.DEFAULT_TEMPLATE_PATH)

        # 加载提示词模板
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(
                f"❌ 首尾帧提示词模板未找到: {self.template_path}\n"
                f"请确保文件存在"
            )

        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.template = f.read()

        print(f"✅ 首尾帧提示词模板已加载")
        print(f"   路径: {self.template_path}")

        # 初始化Claude客户端
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            self.client = Anthropic(api_key=api_key)
        else:
            try:
                self.client = Anthropic()
            except Exception as e:
                raise ValueError(
                    f"❌ Claude API初始化失败！\n"
                    f"请在.env文件中配置：ANTHROPIC_API_KEY=your-api-key\n"
                    f"或确保在Claude Code环境中运行\n"
                    f"错误: {str(e)}"
                )

        print(f"✅ Claude API客户端初始化成功")

    def _encode_image_to_base64(self, image_path: str) -> tuple[str, str]:
        """
        将图片编码为Base64

        Args:
            image_path: 图片路径

        Returns:
            (base64_str, media_type): Base64字符串和媒体类型
        """
        with open(image_path, 'rb') as f:
            image_data = f.read()

        base64_str = base64.standard_b64encode(image_data).decode('utf-8')

        ext = Path(image_path).suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }

        media_type = media_type_map.get(ext, 'image/jpeg')

        return base64_str, media_type

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
            content_context: 内容上下文（可选，帮助理解页面关联性）

        Returns:
            prompt: 转场描述文本
        """
        print(f"\n🎬 正在分析转场场景...")
        print(f"   起始帧: {Path(frame_start_path).name}")
        print(f"   结束帧: {Path(frame_end_path).name}")

        # 编码图片
        start_b64, start_media = self._encode_image_to_base64(frame_start_path)
        end_b64, end_media = self._encode_image_to_base64(frame_end_path)

        # 构建消息内容
        system_message = self.template + """

⚠️ **特别注意 - 文字处理规则**：
1. 视频模型在处理文字时容易出现问题（模糊、变形、乱码），请务必避免文字内容的变化、变形或模糊
2. 如果画面中有文字，请在描述中明确指出"文字内容保持清晰稳定"
3. 优先通过背景元素、装饰物、光效、色彩的变化来实现转场
4. 如果必须涉及文字区域，使用淡入淡出而非变形或移动
5. 避免使用"文字逐渐变化"、"文字移动"、"文字旋转"等会导致文字变形的描述
6. 推荐使用："文字通过淡入淡出完成切换"、"文字保持清晰稳定"

现在，请根据我提供的【起始帧】（图片A）和【结束帧】（图片B），生成你的转场描述。
"""

        if content_context:
            system_message += f"\n**内容上下文**：{content_context}\n"

        system_message += "\n请生成转场描述。"

        # 构建多模态消息
        message_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": start_media,
                    "data": start_b64
                }
            },
            {
                "type": "text",
                "text": "这是【起始帧】（图片A）"
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": end_media,
                    "data": end_b64
                }
            },
            {
                "type": "text",
                "text": "这是【结束帧】（图片B）"
            },
            {
                "type": "text",
                "text": system_message
            }
        ]

        print(f"🤖 正在调用Claude API分析转场...")

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            )

            transition_prompt = response.content[0].text.strip()

            print(f"✅ 转场提示词生成完成！")
            print(f"\n转场描述：")
            print(f"{'='*60}")
            print(transition_prompt)
            print(f"{'='*60}\n")

            return transition_prompt

        except Exception as e:
            raise Exception(
                f"❌ Claude API调用失败！\n"
                f"错误: {str(e)}"
            )

    def generate_preview_prompt(self, first_slide_path: str) -> str:
        """
        生成首页预览视频的提示词（首尾帧相同，微动效）

        Args:
            first_slide_path: 首页图片路径

        Returns:
            prompt: 预览视频提示词
        """
        print(f"\n🎬 正在生成首页预览提示词...")
        print(f"   首页: {Path(first_slide_path).name}")

        image_b64, media_type = self._encode_image_to_base64(first_slide_path)

        message_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": image_b64
                }
            },
            {
                "type": "text",
                "text": """请为这张PPT封面图生成一个微动效提示词，用于创建可循环播放的预览视频。

要求：
1. 首帧和尾帧是同一张图片，视频应该能够无缝循环
2. 动效要微妙、优雅，不要过于夸张
3. 建议的动效类型：
   - 光效流动（如极光般的光线缓慢移动）
   - 玻璃表面的呼吸效果（轻微的反光变化）
   - 背景渐变色的轻微变化
   - 3D物体的缓慢旋转（如果有）
   - 微粒效果（如浮动的光点）
4. ⚠️ 特别注意：文字内容必须保持清晰稳定，不发生任何变化、变形或模糊
5. 整体氛围应该是静谧、呼吸感、等待被点击的状态

请用一段话描述这个微动效（150-250字）。"""
            }
        ]

        print(f"🤖 正在调用Claude API生成预览提示词...")

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": message_content
                    }
                ]
            )

            preview_prompt = response.content[0].text.strip()

            print(f"✅ 预览提示词生成完成！")
            print(f"\n预览动效描述：")
            print(f"{'='*60}")
            print(preview_prompt)
            print(f"{'='*60}\n")

            return preview_prompt

        except Exception as e:
            raise Exception(
                f"❌ Claude API调用失败！\n"
                f"错误: {str(e)}"
            )


if __name__ == "__main__":
    """测试代码"""
    generator = TransitionPromptGenerator()
