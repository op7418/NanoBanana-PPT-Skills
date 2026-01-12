---
name: ppt-generator
description: 此技能应在用户需要基于文档内容自动生成专业 PPT 图片或视频时使用。支持智能文档分析、多种视觉风格（渐变毛玻璃卡片、矢量插画）、16:9 高清输出。图片支持 Gemini 和 ComfyUI 引擎，视频支持可灵 API 生成过渡动效和 FFmpeg 合成完整视频。
version: 2.0.0
author: 歸藏 (guizang)
license: MIT
---

# PPT 生成器技能

## 概述

PPT Generator 是一个强大的文档到演示文稿转换技能，能够智能分析文档内容，自动生成专业的 PPT 图片和视频。

### 图片生成引擎

- **Gemini (Nano Banana Pro)** - Google Gemini 3 Pro Image Preview 模型
- **ComfyUI** - 本地部署的 Stable Diffusion 工作流（支持 z_image_turbo 等模型）

### 视频生成引擎

- **可灵 (Kling) API** - 图生视频，支持首尾帧控制，生成过渡动效
- **FFmpeg** - 视频合成，将静态图片和过渡视频拼接为完整 PPT 视频

支持多种视觉风格，生成 16:9 高清 PPT，并附带优雅的 HTML5 播放器。

### 核心能力

- **智能文档分析** - 自动提取核心要点，规划 PPT 内容结构
- **多风格支持** - 内置渐变毛玻璃卡片风格和矢量插画风格
- **高质量输出** - 16:9 比例，2K/4K 分辨率可选
- **智能布局** - 封面页、内容页、数据页自动识别
- **HTML5 播放器** - 支持键盘导航、全屏、自动播放
- **双引擎支持** - Gemini 云端 API 或 ComfyUI 本地生成
- **视频生成** - 可灵 API 生成页面过渡动效（首尾帧控制）
- **视频合成** - FFmpeg 将图片和过渡视频合成完整 PPT 视频
- **视频播放器** - 支持过渡动效的 HTML5 视频播放器

## 触发场景

此技能应在以下场景触发：

1. 用户请求生成 PPT、演示文稿或幻灯片
2. 用户提供文档并要求转换为演示材料
3. 用户提到使用 Nano Banana Pro 或 ComfyUI 生成图片
4. 用户需要将内容可视化为演示格式
5. 用户请求生成 PPT 视频或带转场动效的演示
6. 用户需要将 PPT 图片转换为视频
7. 用户提到使用可灵 API 生成过渡视频

## 系统要求

### 环境变量

```bash
# 图片生成 - Gemini 引擎（使用 --engine gemini 时必需）
GEMINI_API_KEY=your-google-ai-api-key

# 图片生成 - ComfyUI 引擎（可选，默认 http://127.0.0.1:8188）
COMFYUI_SERVER_URL=http://127.0.0.1:8188

# 视频生成 - 可灵 API（生成视频时必需）
Kling_Access_Key=your-kling-access-key
Kling_Secret_Key=your-kling-secret-key

# 视频生成 - Claude API（完整版转场提示词，可选）
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Python 依赖

```bash
# Gemini 引擎
pip install google-genai pillow

# 可灵视频 API
pip install pyjwt requests

# ComfyUI 引擎（无额外依赖，使用标准库）
```

### 系统依赖

```bash
# FFmpeg（视频合成必需）
# Windows
choco install ffmpeg
# 或
scoop install ffmpeg

# macOS
brew install ffmpeg

# Linux
apt install ffmpeg
```

### ComfyUI 模型准备

使用 ComfyUI 引擎时，需要预先下载 z_image_turbo 模型：

```
ComfyUI/models/
├── text_encoders/
│   └── qwen_3_4b.safetensors
├── diffusion_models/
│   └── z_image_turbo_bf16.safetensors
└── vae/
    └── ae.safetensors
```

下载链接：https://huggingface.co/Comfy-Org/z_image_turbo

## 工作流程

### 阶段 1：收集用户输入

1. **获取文档内容**
   - 如果用户提供了文档路径，读取文件内容
   - 如果用户直接提供文本内容，使用该内容
   - 如果用户未提供，询问用户提供文档路径或内容

2. **选择风格**
   - 扫描 `assets/styles/` 目录，列出所有可用风格
   - 提供风格选项让用户选择：
     - `gradient-glass` - 渐变毛玻璃卡片风格（高端科技感）
     - `vector-illustration` - 矢量插画风格（温暖可爱）

3. **选择页数范围**
   - 5 页：精简版，适合快速演示（5 分钟）
   - 5-10 页：标准版，适合一般演示（10-15 分钟）
   - 10-15 页：详细版，适合深入讲解（20-30 分钟）
   - 20-25 页：完整版，适合全面展示（45-60 分钟）

4. **选择分辨率**
   - 2K (1920x1080)：推荐，平衡质量和生成速度
   - 4K (3840x2160)：高质量，生成耗时较长

5. **选择图片生成引擎**
   - `gemini` - 使用 Google Gemini API（默认）
   - `comfyui` - 使用本地 ComfyUI 服务

6. **选择输出类型**（新增）
   - `images` - 仅生成 PPT 图片
   - `video` - 仅生成视频（需要先有图片）
   - `both` - 生成图片和视频

### 阶段 2：文档分析与内容规划

根据用户选择的页数范围，分析文档内容并规划每一页的内容。

#### 内容规划策略

**5 页版本**:
1. 封面：标题 + 核心主题
2. 要点 1：第一个核心观点
3. 要点 2：第二个核心观点
4. 要点 3：第三个核心观点
5. 总结：核心结论或行动建议

**5-10 页版本**:
1. 封面：标题 + 核心主题
2-3. 引言/背景：问题陈述或背景介绍
4-7. 核心内容：3-4 个关键观点的详细展开
8-9. 案例或数据支持
10. 总结与行动建议

**10-15 页版本**:
1. 封面
2-3. 引言/目录
4-6. 第一章节（3 页详细展开）
7-9. 第二章节（3 页详细展开）
10-12. 第三章节或案例研究
13-14. 数据可视化或对比分析
15. 总结与下一步

**20-25 页版本**:
1. 封面
2. 目录
3-4. 引言和背景
5-8. 第一部分（4 页）
9-12. 第二部分（4 页）
13-16. 第三部分（4 页）
17-19. 案例研究或实践应用
20-22. 数据分析和洞察
23-24. 关键发现和建议
25. 总结与致谢

#### 创建规划文件

创建 JSON 规划文件，保存为 `slides_plan.json`：

```json
{
  "title": "文档标题",
  "total_slides": 5,
  "slides": [
    {
      "slide_number": 1,
      "page_type": "cover",
      "content": "标题：XXX\n副标题：XXX"
    },
    {
      "slide_number": 2,
      "page_type": "content",
      "content": "要点1：XXX\n- 子要点1\n- 子要点2"
    },
    {
      "slide_number": 3,
      "page_type": "content",
      "content": "要点2：XXX\n- 子要点1\n- 子要点2"
    },
    {
      "slide_number": 4,
      "page_type": "content",
      "content": "要点3：XXX\n- 子要点1\n- 子要点2"
    },
    {
      "slide_number": 5,
      "page_type": "data",
      "content": "总结\n- 核心发现1\n- 核心发现2\n- 行动建议"
    }
  ]
}
```

### 阶段 3：生成 PPT 图片

#### 使用 Gemini 引擎（默认）

```bash
python scripts/generate_ppt.py \
  --plan slides_plan.json \
  --style assets/styles/gradient-glass.md \
  --resolution 2K \
  --template assets/templates/viewer.html
```

#### 使用 ComfyUI 引擎

```bash
python scripts/generate_ppt.py \
  --plan slides_plan.json \
  --style assets/styles/gradient-glass.md \
  --engine comfyui \
  --resolution 2K \
  --template assets/templates/viewer.html
```

#### 使用 ComfyUI + 自定义工作流

```bash
python scripts/generate_ppt.py \
  --plan slides_plan.json \
  --style assets/styles/gradient-glass.md \
  --engine comfyui \
  --workflow ./my_workflow.json \
  --prompt-node 6 \
  --size-node 3
```

#### 图片生成参数说明

基础参数：
- `--plan`: slides 规划 JSON 文件路径
- `--style`: 风格模板文件路径
- `--resolution`: 图片分辨率（2K 或 4K）
- `--template`: HTML 播放器模板路径
- `--output`: 可选，自定义输出目录路径

引擎选择：
- `--engine`: 图片生成引擎（gemini 或 comfyui，默认 gemini）

ComfyUI 参数：
- `--comfyui-server`: ComfyUI 服务器地址（默认 http://127.0.0.1:8188）
- `--workflow`: 自定义工作流 JSON 文件路径（默认使用内置 z_image_turbo）
- `--prompt-node`: Prompt 节点 ID（默认 45）
- `--size-node`: 尺寸节点 ID（默认 41）
- `--timeout`: 生成超时时间，秒（默认 600）

### 阶段 4：生成转场提示词（视频）

如果用户选择生成视频，此阶段分析每两页之间的差异，生成转场动效描述。

**提示词生成方式：**
- **完整版**（需要 Claude API）：使用 Claude 分析首尾帧图片，智能生成转场描述
- **简化版**（无需 API）：使用预定义的转场模板

```python
# 完整版（Claude API）
from scripts.transition_prompt_generator import TransitionPromptGenerator
generator = TransitionPromptGenerator()

# 简化版（预定义模板）
from scripts.simple_transition_prompt_generator import SimpleTransitionPromptGenerator
generator = SimpleTransitionPromptGenerator()

# 从文件读取（用户自定义）
from scripts.prompt_file_reader import PromptFileReader
generator = PromptFileReader("prompts.json")
```

### 阶段 5：生成视频素材（视频）

使用可灵 API 生成预览视频和过渡视频。

```bash
python scripts/generate_ppt_video.py \
  --slides-dir outputs/xxx/images \
  --output-dir outputs/xxx_video \
  --video-mode both \
  --video-duration 5 \
  --video-quality pro \
  --max-concurrent 3
```

**视频生成参数说明：**

- `--slides-dir`: PPT 图片目录（包含 slide-01.png, slide-02.png 等）
- `--output-dir`: 输出目录
- `--video-mode`: 输出模式
  - `both` - 本地视频 + 网页播放器（默认）
  - `local` - 仅本地视频文件
  - `web` - 仅网页播放器
- `--video-duration`: 过渡视频时长（5 或 10 秒）
- `--slide-duration`: 每页停留时长（秒，默认 5）
- `--video-quality`: 视频质量
  - `std` - 标准质量
  - `pro` - 高品质（首尾帧必需，默认）
- `--max-concurrent`: 最大并发数（默认 3，可灵 API 限制）
- `--skip-preview`: 跳过预览视频生成
- `--prompts-file`: 自定义提示词文件路径

### 阶段 6：合成完整视频（视频）

使用 FFmpeg 将静态图片和过渡视频合成为完整的 PPT 视频。

**合成流程：**
1. 将每页 PPT 图片转换为静态视频片段（指定停留时长）
2. 按顺序拼接：过渡视频 → 静态视频 → 过渡视频 → 静态视频...
3. 统一分辨率和帧率（1920x1080, 24fps）
4. 输出 H.264 编码的 MP4 文件

### 阶段 7：返回结果

生成完成后，向用户报告：

**图片生成结果：**
```
✅ PPT 图片生成成功！

📁 输出目录: outputs/[timestamp]/
🎬 播放网页: outputs/[timestamp]/index.html
📝 提示词记录: outputs/[timestamp]/prompts.json

播放器使用说明:
- ← → 键: 切换页面
- ↑ Home: 回到首页
- ↓ End: 跳到末页
- 空格: 暂停/继续自动播放
- ESC: 全屏切换
- H: 隐藏/显示控件
```

**视频生成结果：**
```
✅ PPT 视频生成成功！

📁 输出目录: outputs/[timestamp]_video/
🎬 完整视频: outputs/[timestamp]_video/full_ppt_video.mp4
🌐 网页播放器: outputs/[timestamp]_video/video_index.html
📹 视频素材: outputs/[timestamp]_video/videos/
📝 元数据: outputs/[timestamp]_video/videos/video_metadata.json

生成统计:
- PPT 页数: N
- 视频素材: X 成功, Y 失败
- 总耗时: Z 秒
```

## 风格说明

### 渐变毛玻璃卡片风格 (gradient-glass)

**视觉特点**：
- Apple Keynote 极简主义
- 玻璃拟态效果 + 霓虹渐变
- 3D 玻璃物体
- 电影级体积光照

**适用场景**：科技产品发布、商务演示、数据报告、企业品牌展示

### 矢量插画风格 (vector-illustration)

**视觉特点**：
- 扁平化矢量设计
- 统一黑色轮廓线
- 复古柔和配色
- 玩具模型感

**适用场景**：教育培训、创意提案、儿童内容、品牌故事

## 页面类型

- `cover` - 封面页：标题和主题展示
- `content` - 内容页：核心观点和要点
- `data` - 数据页：数据可视化、统计信息、总结

## ComfyUI 配置说明

### 预设工作流

内置 `z_image_turbo_16x9.json` 工作流，基于 z_image_turbo 模型，已预配置 16:9 输出比例。

**关键节点 ID：**
- 节点 45 (`CLIPTextEncode`): Prompt 输入
- 节点 41 (`EmptySD3LatentImage`): 图像尺寸
- 节点 44 (`KSampler`): 采样器（9 步，cfg=1）
- 节点 9 (`SaveImage`): 输出保存

### 自定义工作流

如需使用自定义工作流：

1. 在 ComfyUI 中创建并保存工作流 JSON
2. 记录 Prompt 节点和尺寸节点的 ID
3. 使用 `--workflow`、`--prompt-node`、`--size-node` 参数指定

### 支持的工作流格式

- ComfyUI GUI 格式（包含 nodes 数组）- 自动转换
- ComfyUI API 格式（节点 ID 为 key）- 直接使用

## 可灵视频 API 说明

### 模型选择

- `kling-v2-6` - 推荐，支持首尾帧控制

### 生成模式

- `std` - 标准模式，消耗较少
- `pro` - 高品质模式，首尾帧控制必需

### 并发限制

可灵 API 最大并发数为 3，脚本已内置并发控制。

### 详细文档

参考 `references/kling-api-usage.md` 获取完整 API 说明。

## 错误处理

### 图片生成错误

1. **Gemini API 密钥未设置**
   ```
   错误: 未设置 GEMINI_API_KEY 环境变量
   解决: export GEMINI_API_KEY='your-api-key'
   ```

2. **Python 依赖缺失**
   ```
   错误: 未安装 google-genai 库
   解决: pip install google-genai pillow
   ```

3. **Gemini API 调用失败**
   ```
   错误: API 调用超时或失败
   解决: 检查网络连接，确认 API 密钥有效，稍后重试
   ```

4. **ComfyUI 连接失败**
   ```
   错误: 无法连接到 ComfyUI 服务器
   解决: 确认 ComfyUI 已启动，检查服务器地址是否正确
   ```

5. **ComfyUI 工作流错误**
   ```
   错误: 工作流文件不存在 / 节点 ID 不存在
   解决: 检查工作流文件路径，确认节点 ID 正确
   ```

6. **ComfyUI 模型缺失**
   ```
   错误: 模型加载失败
   解决: 下载所需模型到 ComfyUI/models 对应目录
   ```

### 视频生成错误

7. **可灵 API 密钥未设置**
   ```
   错误: 可灵API密钥未配置
   解决: 在 .env 文件中配置 Kling_Access_Key 和 Kling_Secret_Key
   ```

8. **可灵 API 认证失败**
   ```
   错误: JWT Token 验证失败
   解决: 检查 Access Key 和 Secret Key 是否正确
   ```

9. **可灵 API 任务超时**
   ```
   错误: 任务超时
   解决: 可灵视频生成通常需要 90-120 秒，请耐心等待
   ```

10. **FFmpeg 未安装**
    ```
    错误: FFmpeg 不可用
    解决: 安装 FFmpeg（Windows: choco install ffmpeg, macOS: brew install ffmpeg）
    ```

11. **视频拼接失败**
    ```
    错误: FFmpeg 执行失败
    解决: 检查输入视频文件是否存在，确认视频格式兼容
    ```

## 扩展风格

在 `assets/styles/` 目录创建新的 `.md` 风格文件，按照现有风格文件格式编写。风格文件需包含：

1. 风格 ID
2. 风格名称
3. 基础提示词模板
4. 页面类型模板（封面页、内容页、数据页）

## 文件组织

```
ppt-generator/
├── SKILL.md                              # 技能定义文件
├── scripts/
│   ├── generate_ppt.py                   # 图片生成脚本
│   ├── comfyui_client.py                 # ComfyUI 客户端模块
│   ├── kling_api.py                      # 可灵 API 封装
│   ├── video_materials.py                # 视频素材生成模块
│   ├── video_composer.py                 # FFmpeg 视频合成模块
│   ├── generate_ppt_video.py             # 视频生成主流程脚本
│   ├── transition_prompt_generator.py    # 转场提示词生成器（Claude API）
│   ├── simple_transition_prompt_generator.py  # 简化版提示词生成器
│   └── prompt_file_reader.py             # 提示词文件读取器
├── assets/
│   ├── styles/
│   │   ├── gradient-glass.md             # 渐变毛玻璃风格
│   │   └── vector-illustration.md        # 矢量插画风格
│   ├── templates/
│   │   ├── viewer.html                   # 图片 HTML5 播放器模板
│   │   └── video_viewer.html             # 视频 HTML5 播放器模板
│   ├── workflows/
│   │   └── z_image_turbo_16x9.json       # ComfyUI 预设工作流
│   └── prompts/
│       └── transition_template.md        # 转场提示词模板
└── references/
    ├── api-usage.md                      # Gemini API 使用参考
    └── kling-api-usage.md                # 可灵 API 使用参考
```

## 最佳实践

### 图片生成

1. **文档质量**: 输入文档内容越清晰结构化，生成的 PPT 质量越高
2. **页数选择**: 根据文档长度和演示场景合理选择页数
3. **分辨率选择**: 日常使用推荐 2K，重要展示场合可选 4K
4. **引擎选择**: 
   - Gemini：适合快速生成，无需本地 GPU
   - ComfyUI：适合有 GPU 的用户，可自定义模型和参数
5. **提示词调整**: 查看 `prompts.json` 了解生成逻辑，可手动调整后重新生成

### 视频生成

1. **图片优先**: 先生成满意的 PPT 图片，再生成视频
2. **质量模式**: 首尾帧控制必须使用 `pro` 模式
3. **时长选择**: 过渡视频推荐 5 秒，10 秒可能显得过长
4. **并发控制**: 可灵 API 限制为 3 并发，脚本已自动控制
5. **耐心等待**: 视频生成较慢，每个过渡约需 90-120 秒
6. **提示词优化**: 如效果不佳，可使用 `--prompts-file` 提供自定义提示词
