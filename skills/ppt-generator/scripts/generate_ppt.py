#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PPT生成器
支持 Google Gemini (Nano Banana Pro) 和 ComfyUI 两种图片生成引擎
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 设置标准输出编码为 UTF-8（Windows 兼容）
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Python < 3.7
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def load_env_file(env_path='.env'):
    """加载 .env 文件到环境变量"""
    env_file = Path(env_path)
    if not env_file.exists():
        # 尝试在项目根目录查找
        project_root = Path(__file__).parent.parent.parent.parent
        env_file = project_root / '.env'
        if not env_file.exists():
            return
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    # 如果环境变量不存在，则设置它（.env 文件的优先级低于系统环境变量）
                    if key and key not in os.environ:
                        os.environ[key] = value
    except Exception as e:
        print(f"警告: 加载 .env 文件失败: {e}")


# 在导入其他模块前加载 .env 文件
load_env_file()


def load_style_template(style_path):
    """加载风格模板"""
    with open(style_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取基础提示词模板部分
    start_marker = "## 基础提示词模板"
    end_marker = "## 页面类型模板"

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print("警告: 无法解析风格模板，使用完整文件内容")
        return content

    template = content[start_idx + len(start_marker):end_idx].strip()
    return template


def generate_prompt(style_template, page_type, content_text, slide_number, total_slides):
    """生成单页提示词"""
    prompt = f"{style_template}\n\n"

    if page_type == "cover" or slide_number == 1:
        # 封面页
        prompt += f"""请根据视觉平衡美学，生成封面页。在中心放置一个巨大的复杂3D玻璃物体，并覆盖粗体大字：

{content_text}

背景有延伸的极光波浪。"""

    elif page_type == "data" or slide_number == total_slides:
        # 数据页/总结页
        prompt += f"""请生成数据页或总结页。使用分屏设计，左侧排版以下文字，右侧悬浮巨大的发光3D数据可视化图表：

{content_text}"""

    else:
        # 内容页
        prompt += f"""请生成内容页。使用Bento网格布局，将以下内容组织在模块化的圆角矩形容器中，容器材质必须是带有模糊效果的磨砂玻璃：

{content_text}"""

    return prompt


def generate_slide_gemini(prompt, slide_number, output_dir, resolution="2K"):
    """生成单页PPT图片（使用Gemini API）"""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print("错误: 未安装 google-genai 库")
        print("请运行: pip install google-genai")
        sys.exit(1)

    # 获取API密钥
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("错误: 未设置 GEMINI_API_KEY 环境变量")
        print("请设置: export GEMINI_API_KEY='your-api-key'")
        sys.exit(1)

    print(f"正在生成第 {slide_number} 页 (Gemini)...")

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE'],
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                    image_size=resolution
                )
            )
        )

        for part in response.parts:
            if part.inline_data is not None:
                image = part.as_image()
                image_path = os.path.join(output_dir, "images", f"slide-{slide_number:02d}.png")
                image.save(image_path)
                print(f"✓ 第 {slide_number} 页已保存: {image_path}")
                return image_path

        print(f"✗ 第 {slide_number} 页生成失败: 未收到图片数据")
        return None

    except Exception as e:
        print(f"✗ 第 {slide_number} 页生成失败: {e}")
        return None


def generate_slide_comfyui(prompt, slide_number, output_dir, comfyui_config):
    """生成单页PPT图片（使用ComfyUI）"""
    from comfyui_client import ComfyUIClient
    
    print(f"正在生成第 {slide_number} 页 (ComfyUI)...")
    
    try:
        client = ComfyUIClient(
            server_url=comfyui_config['server_url'],
            workflow_file=comfyui_config['workflow_file'],
            prompt_node=comfyui_config['prompt_node'],
            size_node=comfyui_config['size_node'],
            timeout=comfyui_config.get('timeout', 600)
        )
        
        output_path = os.path.join(output_dir, "images", f"slide-{slide_number:02d}.png")
        
        # 根据分辨率设置尺寸
        resolution = comfyui_config.get('resolution', '2K')
        if resolution == '4K':
            width, height = 3840, 2160
        else:  # 2K
            width, height = 1920, 1080
        
        result = client.generate_image(
            prompt=prompt,
            output_path=output_path,
            width=width,
            height=height
        )
        
        if result:
            print(f"✓ 第 {slide_number} 页已保存: {result}")
            return result
        else:
            print(f"✗ 第 {slide_number} 页生成失败")
            return None
            
    except Exception as e:
        print(f"✗ 第 {slide_number} 页生成失败: {e}")
        return None


def get_default_workflow_path():
    """获取默认工作流路径"""
    # 尝试多个可能的路径
    script_dir = Path(__file__).parent
    possible_paths = [
        # skills 目录下的工作流
        script_dir.parent / "assets" / "workflows" / "z_image_turbo_16x9.json",
        # 项目根目录的工作流
        script_dir.parent.parent.parent / "comfyui-workflows" / "image_z_image_turbo.json",
        # 相对于当前工作目录
        Path("comfyui-workflows") / "image_z_image_turbo.json",
        Path("skills/ppt-generator/assets/workflows/z_image_turbo_16x9.json"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    return None


def generate_viewer_html(output_dir, slide_count, template_path):
    """生成播放网页"""
    # 读取HTML模板
    with open(template_path, 'r', encoding='utf-8') as f:
        html_template = f.read()

    # 生成图片列表
    slides_list = [f"'images/slide-{i:02d}.png'" for i in range(1, slide_count + 1)]

    # 替换占位符
    html_content = html_template.replace(
        "/* IMAGE_LIST_PLACEHOLDER */",
        ",\n            ".join(slides_list)
    )

    # 保存HTML文件
    html_path = os.path.join(output_dir, "index.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ 播放网页已生成: {html_path}")
    return html_path


def save_prompts(output_dir, prompts_data):
    """保存所有提示词到JSON文件"""
    prompts_path = os.path.join(output_dir, "prompts.json")
    with open(prompts_path, 'w', encoding='utf-8') as f:
        json.dump(prompts_data, f, ensure_ascii=False, indent=2)
    print(f"✓ 提示词已保存: {prompts_path}")


def main():
    parser = argparse.ArgumentParser(
        description='PPT生成器 - 支持 Gemini 和 ComfyUI 两种引擎',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用 Gemini (默认)
  python generate_ppt.py --plan slides_plan.json --style styles/gradient-glass.md

  # 使用 ComfyUI
  python generate_ppt.py --plan slides_plan.json --style styles/gradient-glass.md --engine comfyui

  # 使用 ComfyUI + 自定义工作流
  python generate_ppt.py --plan slides_plan.json --style styles/gradient-glass.md \\
    --engine comfyui --workflow ./my_workflow.json --prompt-node 6

环境变量:
  GEMINI_API_KEY: Google AI API密钥（gemini 引擎必需）
  COMFYUI_SERVER_URL: ComfyUI 服务器地址（默认: http://127.0.0.1:8188）
"""
    )

    # 基础参数
    parser.add_argument(
        '--plan',
        required=True,
        help='slides规划JSON文件路径（由Skill生成）'
    )
    parser.add_argument(
        '--style',
        required=True,
        help='风格模板文件路径'
    )
    parser.add_argument(
        '--resolution',
        choices=['2K', '4K'],
        default='2K',
        help='图片分辨率 (默认: 2K)'
    )
    parser.add_argument(
        '--output',
        help='输出目录路径（默认: outputs/TIMESTAMP）'
    )
    parser.add_argument(
        '--template',
        default='templates/viewer.html',
        help='HTML模板路径（默认: templates/viewer.html）'
    )
    
    # 引擎选择参数
    parser.add_argument(
        '--engine',
        choices=['gemini', 'comfyui'],
        default='gemini',
        help='图片生成引擎 (默认: gemini)'
    )
    
    # ComfyUI 相关参数
    parser.add_argument(
        '--comfyui-server',
        default=None,
        help='ComfyUI 服务器地址 (默认: http://127.0.0.1:8188)'
    )
    parser.add_argument(
        '--workflow',
        help='ComfyUI 工作流文件路径 (默认: 内置 z_image_turbo)'
    )
    parser.add_argument(
        '--prompt-node',
        default='45',
        help='ComfyUI Prompt 节点 ID (默认: 45)'
    )
    parser.add_argument(
        '--size-node',
        default='41',
        help='ComfyUI 尺寸节点 ID (默认: 41)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=600,
        help='ComfyUI 生成超时时间，秒 (默认: 600)'
    )

    args = parser.parse_args()

    # 读取slides规划
    with open(args.plan, 'r', encoding='utf-8') as f:
        slides_plan = json.load(f)

    # 加载风格模板
    style_template = load_style_template(args.style)

    # 创建输出目录
    if args.output:
        output_dir = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"outputs/{timestamp}"

    os.makedirs(os.path.join(output_dir, "images"), exist_ok=True)

    # 准备 ComfyUI 配置
    comfyui_config = None
    if args.engine == 'comfyui':
        workflow_file = args.workflow or get_default_workflow_path()
        if not workflow_file:
            print("错误: 未找到 ComfyUI 工作流文件")
            print("请使用 --workflow 参数指定工作流文件路径")
            sys.exit(1)
        
        if not os.path.exists(workflow_file):
            print(f"错误: 工作流文件不存在: {workflow_file}")
            sys.exit(1)
        
        comfyui_config = {
            'server_url': args.comfyui_server or os.environ.get("COMFYUI_SERVER_URL", "http://127.0.0.1:8188"),
            'workflow_file': workflow_file,
            'prompt_node': args.prompt_node,
            'size_node': args.size_node,
            'timeout': args.timeout,
            'resolution': args.resolution
        }

    print("=" * 60)
    print("PPT生成器启动")
    print("=" * 60)
    print(f"引擎: {args.engine}")
    print(f"风格: {args.style}")
    print(f"分辨率: {args.resolution}")
    print(f"页数: {len(slides_plan['slides'])}")
    print(f"输出目录: {output_dir}")
    if args.engine == 'comfyui':
        print(f"ComfyUI 服务器: {comfyui_config['server_url']}")
        print(f"工作流: {comfyui_config['workflow_file']}")
    print("=" * 60)
    print()

    # 生成每一页
    prompts_data = {
        "metadata": {
            "title": slides_plan.get("title", "未命名演示"),
            "total_slides": len(slides_plan['slides']),
            "resolution": args.resolution,
            "style": args.style,
            "engine": args.engine,
            "generated_at": datetime.now().isoformat()
        },
        "slides": []
    }

    total_slides = len(slides_plan['slides'])

    for slide_info in slides_plan['slides']:
        slide_number = slide_info['slide_number']
        page_type = slide_info.get('page_type', 'content')
        content_text = slide_info['content']

        # 生成提示词
        prompt = generate_prompt(
            style_template,
            page_type,
            content_text,
            slide_number,
            total_slides
        )

        # 根据引擎选择生成方式
        if args.engine == 'comfyui':
            image_path = generate_slide_comfyui(prompt, slide_number, output_dir, comfyui_config)
        else:
            image_path = generate_slide_gemini(prompt, slide_number, output_dir, args.resolution)

        # 记录提示词
        prompts_data['slides'].append({
            "slide_number": slide_number,
            "page_type": page_type,
            "content": content_text,
            "prompt": prompt,
            "image_path": image_path
        })

        print()

    # 保存提示词
    save_prompts(output_dir, prompts_data)

    # 生成播放网页
    generate_viewer_html(output_dir, total_slides, args.template)

    print()
    print("=" * 60)
    print("生成完成！")
    print("=" * 60)
    print(f"输出目录: {output_dir}")
    print(f"播放网页: {os.path.join(output_dir, 'index.html')}")
    print()
    print("打开播放网页查看PPT:")
    print(f"  open {os.path.join(output_dir, 'index.html')}")
    print()


if __name__ == "__main__":
    main()
