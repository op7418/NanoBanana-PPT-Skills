# NanoBanana PPT Skills

> 基于 AI 自动生成高质量 PPT 图片和视频的强大工具，支持智能转场和交互式播放

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)

**创作者**: [歸藏](https://github.com/op7418)

[效果演示](#-效果演示) • [功能特性](#-功能特性) • [一键安装](#-一键安装) • [作为 Skill 使用](#-作为-claude-code-skill-使用) • [使用指南](#-使用指南) • [视频功能](#-视频功能) • [架构文档](ARCHITECTURE.md) • [常见问题](#-常见问题)

</div>

---

## 🎬 效果演示

<div align="center">

<video src="https://github.com/op7418/NanoBanana-PPT-Skills/raw/main/PPT-Skills-Demo.mp4" controls width="800">
  您的浏览器不支持视频播放，请<a href="https://github.com/op7418/NanoBanana-PPT-Skills/raw/main/PPT-Skills-Demo.mp4">点击下载查看</a>
</video>

*AI 自动生成 PPT 并添加流畅转场动画 - 从文档分析到视频合成一键完成*

</div>

---

## 📖 简介

NanoBanana PPT Skills 是一个强大的 AI 驱动的 PPT 生成工具，能够：

- 📄 **智能分析文档**，自动提取核心要点并规划 PPT 结构
- 🎨 **生成高质量图片**，使用 Google Nano Banana Pro（Gemini 3 Pro Image Preview）
- 🎬 **自动生成转场视频**，使用可灵 AI 创建流畅的页面过渡动画
- 🎮 **交互式视频播放器**，支持键盘控制、循环预览、智能转场
- 🎥 **完整视频导出**，一键合成包含所有转场的完整 PPT 视频

### 🎨 视觉风格

**渐变毛玻璃卡片风格**
- 高端科技感，Apple Keynote 极简主义
- 3D 玻璃物体 + 霓虹渐变
- 电影级光照效果
- 适合：科技产品、商务演示、数据报告

**矢量插画风格**
- 温暖扁平化设计，复古配色
- 黑色轮廓线 + 几何化处理
- 玩具模型般的可爱感
- 适合：教育培训、创意提案、品牌故事

---

## ✨ 功能特性

### 🎯 核心能力

- 🤖 **智能文档分析** - 自动提取核心要点，规划 PPT 内容结构
- 🎨 **多风格支持** - 内置 2 种专业风格，可无限扩展
- 🖼️ **高质量图片** - 16:9 比例，2K/4K 分辨率可选
- 🎬 **AI 转场视频** - 可灵 AI 生成流畅的页面过渡动画
- 🎮 **交互式播放器** - 视频+图片混合播放，支持键盘导航
- 🎥 **完整视频导出** - FFmpeg 合成包含转场的完整 PPT 视频
- 📊 **智能布局** - 封面页、内容页、数据页自动识别
- ⚡ **快速生成** - 2K 约 30 秒/页

### 🆕 视频功能（v2.0）

- 🎬 **首页循环预览** - 自动生成吸引眼球的循环动画
- 🎞️ **智能转场** - 自动生成页面间的过渡视频
- 🎮 **交互式播放** - 按键翻页时播放转场视频，结束后显示静态图片
- 🎥 **完整视频导出** - 合成包含所有转场和静态页的完整视频
- 🔧 **参数统一** - 自动统一所有视频分辨率和帧率，确保流畅播放

### 🛠️ 技术亮点

- ✅ Google Nano Banana Pro（Gemini 3 Pro Image Preview）图像生成
- ✅ 可灵 AI API 集成（视频生成、数字人、主体库）
- ✅ FFmpeg 视频合成与参数统一
- ✅ 完整的提示词工程和风格管理系统
- ✅ 安全的 .env 环境变量管理
- ✅ 模块化设计，易于扩展

---

## 🚀 一键安装

### 方法一：Claude Code 自动安装（推荐）

**只需复制以下提示词，发送给 Claude Code，它会自动完成全部安装！**

```
请帮我安装 NanoBanana PPT Skills：

1. 克隆项目并进入目录：
   git clone https://github.com/op7418/NanoBanana-PPT-Skills.git
   cd NanoBanana-PPT-Skills

2. 创建 Python 虚拟环境：
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

3. 安装依赖：
   pip install google-genai pillow python-dotenv

4. 配置 API 密钥 - 创建 .env 文件：
   cp .env.example .env

5. 编辑 .env 文件，填入我的 API 密钥：

   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   KLING_ACCESS_KEY=YOUR_KLING_ACCESS_KEY
   KLING_SECRET_KEY=YOUR_KLING_SECRET_KEY

   注意：
   - GEMINI_API_KEY: Google AI API 密钥（必需，用于生成 PPT 图片）
   - KLING_ACCESS_KEY 和 KLING_SECRET_KEY: 可灵 AI 密钥（可选，用于生成转场视频）

6. 验证安装：
   python3 generate_ppt.py --help

完成后，告诉我安装结果和如何使用。

我的 API 密钥：
- GEMINI_API_KEY: YOUR_GEMINI_API_KEY_HERE
- KLING_ACCESS_KEY: YOUR_KLING_ACCESS_KEY_HERE (可选)
- KLING_SECRET_KEY: YOUR_KLING_SECRET_KEY_HERE (可选)
```

**使用说明**：
1. 先获取 API 密钥：
   - **必需**: [Google AI API 密钥](https://aistudio.google.com/apikey)
   - **可选**: [可灵 AI API 密钥](https://klingai.com)（用于视频转场功能）
2. 复制上面的提示词
3. 将 `YOUR_GEMINI_API_KEY_HERE` 等替换为你的真实 API 密钥
4. 发送给 Claude Code
5. Claude Code 会自动执行所有安装步骤并告知结果

### 方法二：手动安装

如果你想手动安装，按照以下步骤操作：

#### 1. 克隆项目

```bash
git clone https://github.com/op7418/NanoBanana-PPT-Skills.git
cd NanoBanana-PPT-Skills
```

#### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

#### 3. 安装依赖

```bash
pip install google-genai pillow
```

如果需要视频功能，还需要安装 FFmpeg：

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# 下载 FFmpeg 并添加到系统 PATH
```

#### 4. 配置 API 密钥

**推荐方式：.env 文件（已内置支持）**

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用你喜欢的编辑器
```

在 `.env` 文件中填入你的 API 密钥：

```bash
# Google AI API 密钥（必需）
GEMINI_API_KEY=your_gemini_api_key_here

# 可灵 AI API 密钥（可选，用于视频转场功能）
KLING_ACCESS_KEY=your_kling_access_key_here
KLING_SECRET_KEY=your_kling_secret_key_here
```

**替代方式：系统环境变量**

```bash
# zsh 用户 (macOS 默认)
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc

# bash 用户
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### 5. 验证安装

```bash
python3 generate_ppt.py --help
```

应该显示帮助信息，表示安装成功。

---

## 🎯 作为 Claude Code Skill 使用

NanoBanana PPT Skills 完全支持 Claude Code Skill 标准，可以直接通过 Claude Code 调用。

### 快速安装为 Skill

**方法一：Claude Code 自动安装为 Skill（最简单）**

**只需复制以下提示词，发送给 Claude Code，它会自动完成 Skill 安装！**

```
请帮我将 NanoBanana PPT Skills 安装为 Claude Code Skill：

1. 创建 Skill 目录：
   mkdir -p ~/.claude/skills/ppt-generator

2. 克隆项目到 Skill 目录：
   git clone https://github.com/op7418/NanoBanana-PPT-Skills.git ~/.claude/skills/ppt-generator

3. 进入目录并安装依赖：
   cd ~/.claude/skills/ppt-generator
   python3 -m venv venv
   source venv/bin/activate
   pip install google-genai pillow python-dotenv

4. 配置 API 密钥：
   cp .env.example .env

   然后编辑 .env 文件，填入我的 API 密钥：
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   KLING_ACCESS_KEY=YOUR_KLING_ACCESS_KEY
   KLING_SECRET_KEY=YOUR_KLING_SECRET_KEY

5. 验证安装：
   python3 generate_ppt.py --help

完成后，告诉我如何在 Claude Code 中使用这个 Skill。

我的 API 密钥：
- GEMINI_API_KEY: YOUR_GEMINI_API_KEY_HERE
- KLING_ACCESS_KEY: YOUR_KLING_ACCESS_KEY_HERE (可选)
- KLING_SECRET_KEY: YOUR_KLING_SECRET_KEY_HERE (可选)
```

**方法二：使用安装脚本**

```bash
# 克隆项目
git clone https://github.com/op7418/NanoBanana-PPT-Skills.git
cd NanoBanana-PPT-Skills

# 运行安装脚本
bash install_as_skill.sh
```

安装脚本会自动：
1. 创建 `~/.claude/skills/ppt-generator/` 目录
2. 复制所有必要文件
3. 安装 Python 依赖
4. 引导配置 API 密钥

**方法三：手动安装**

```bash
# 1. 创建 Skill 目录
mkdir -p ~/.claude/skills/ppt-generator

# 2. 克隆项目到 Skill 目录
git clone https://github.com/op7418/NanoBanana-PPT-Skills.git ~/.claude/skills/ppt-generator

# 3. 安装依赖
cd ~/.claude/skills/ppt-generator
pip install google-genai pillow python-dotenv

# 4. 配置 API 密钥
cp .env.example .env
nano .env  # 填入你的 API 密钥
```

### 环境变量配置

Skill 会智能查找 `.env` 文件，按以下优先级：

1. **脚本所在目录** - `~/.claude/skills/ppt-generator/.env`
2. **向上查找项目根目录** - 直到找到包含 `.git` 或 `.env` 的目录
3. **用户主目录** - `~/.env`
4. **系统环境变量** - 作为最后的备选方案

**推荐配置方式：**

```bash
# 在 Skill 目录下创建 .env 文件
cat > ~/.claude/skills/ppt-generator/.env << EOF
# Google AI API 密钥（必需）
GEMINI_API_KEY=your_gemini_api_key_here

# 可灵 AI API 密钥（可选，用于视频功能）
KLING_ACCESS_KEY=your_kling_access_key_here
KLING_SECRET_KEY=your_kling_secret_key_here
EOF
```

### 在 Claude Code 中使用

安装完成后，直接在 Claude Code 中调用：

```bash
/ppt-generator-pro
```

或者告诉 Claude：

```
我想基于以下文档生成一个 5 页的 PPT，使用渐变毛玻璃风格。

[文档内容...]
```

Claude 会自动：
1. 分析文档内容
2. 询问风格、页数、分辨率等选项
3. 生成 slides_plan.json
4. 调用 generate_ppt.py 生成图片
5. （可选）生成转场视频
6. 返回结果路径

### Skill 模式 vs 独立模式

| 特性 | Skill 模式 | 独立模式 |
|------|-----------|---------|
| 安装位置 | `~/.claude/skills/ppt-generator/` | 任意目录 |
| 调用方式 | `/ppt-generator-pro` 或自然语言 | 手动执行 Python 脚本 |
| 文档分析 | Claude 自动分析 | 需手动准备 JSON |
| 交互体验 | 对话式，自动询问选项 | 命令行参数 |
| .env 位置 | Skill 目录或项目根目录 | 脚本所在目录 |
| 适用场景 | 日常使用，快速生成 | 批量生成，自动化脚本 |

### 详细使用文档

完整的 Skill 使用文档请参考 [SKILL.md](SKILL.md)，包含：
- 完整的执行流程
- 用户输入收集策略
- 内容规划方法
- 错误处理指南
- 最佳实践建议

---

## 💡 使用指南

### 基础使用：生成 PPT 图片

#### 1. 准备内容规划文件

创建 `my_slides_plan.json`：

```json
{
  "title": "AI 产品设计指南",
  "total_slides": 5,
  "slides": [
    {
      "slide_number": 1,
      "page_type": "cover",
      "content": "标题：AI 产品设计指南\n副标题：构建以用户为中心的智能体验"
    },
    {
      "slide_number": 2,
      "page_type": "content",
      "content": "核心原则\n- 简单直观\n- 快速响应\n- 透明可控"
    },
    {
      "slide_number": 3,
      "page_type": "content",
      "content": "设计流程\n1. 用户研究\n2. 原型设计\n3. 测试迭代"
    },
    {
      "slide_number": 4,
      "page_type": "data",
      "content": "用户满意度\n使用前：65%\n使用后：92%\n提升：+27%"
    },
    {
      "slide_number": 5,
      "page_type": "content",
      "content": "总结\n- 以用户为中心\n- 持续优化迭代\n- 数据驱动决策"
    }
  ]
}
```

#### 2. 生成 PPT 图片

```bash
python3 generate_ppt.py \
  --plan my_slides_plan.json \
  --style styles/gradient-glass.md \
  --resolution 2K
```

#### 3. 查看结果

```bash
# 在浏览器中打开图片播放器
open outputs/TIMESTAMP/index.html
```

### 高级使用：生成带转场视频的 PPT

#### 1. 生成 PPT 图片

```bash
python3 generate_ppt.py \
  --plan my_slides_plan.json \
  --style styles/gradient-glass.md \
  --resolution 2K
```

#### 2. 使用 Claude Code 生成转场提示词（必需）

在 Claude Code 中执行：

```
我刚生成了 5 页 PPT 图片在 outputs/TIMESTAMP/images 目录下。
请帮我分析这些图片，为每个页面转场生成视频提示词，
保存为 outputs/TIMESTAMP/transition_prompts.json
```

Claude Code 会：
1. 读取所有 PPT 图片
2. 分析每两页之间的视觉差异
3. 生成精准的转场描述
4. 保存为 JSON 文件

#### 3. 生成转场视频

```bash
python3 generate_ppt_video.py \
  --slides-dir outputs/TIMESTAMP/images \
  --output-dir outputs/TIMESTAMP_video \
  --prompts-file outputs/TIMESTAMP/transition_prompts.json
```

这会生成：
- 首页循环预览视频
- 每个页面间的转场视频
- 交互式视频播放器 HTML
- 完整视频 (full_ppt_video.mp4)

#### 4. 播放交互式视频 PPT

```bash
open outputs/TIMESTAMP_video/video_index.html
```

**播放逻辑**：
1. 首页：播放循环预览视频
2. 按右键：播放转场视频 → 显示目标页图片（停留 2 秒）
3. 再按右键：播放下一个转场视频 → 显示下一页图片
4. 依此类推...

#### 4. 导出完整视频（可选）

交互式播放器会自动生成完整视频：

```bash
# 视频文件
outputs/TIMESTAMP_video/full_ppt_video.mp4
```

完整视频包含：
- 首页预览（如果有）
- 转场视频 01→02
- 第 2 页静态（2 秒）
- 转场视频 02→03
- 第 3 页静态（2 秒）
- ...

---

## 🎬 视频功能

### 转场视频生成

使用可灵 AI 自动生成页面间的转场视频：

```bash
python3 generate_ppt_video.py \
  --slides-dir outputs/20260111_160221/images \
  --output-dir outputs/20260111_video \
  --mode professional \
  --duration 5
```

**参数说明**：
- `--slides-dir`: PPT 图片目录
- `--output-dir`: 输出目录
- `--mode`: 转场模式（`professional` 或 `creative`）
- `--duration`: 转场视频时长（秒，默认 5）

### 交互式播放器

生成的 `video_index.html` 支持：

| 功能 | 快捷键 | 说明 |
|------|--------|------|
| 下一页 | `→` `↓` | 播放转场视频，然后显示下一页 |
| 上一页 | `←` `↑` | 返回上一页（直接显示） |
| 首页 | `Home` | 返回首页预览 |
| 末页 | `End` | 跳到最后一页 |
| 播放/暂停 | `空格` | 暂停/继续当前视频 |
| 全屏 | `ESC` | 切换全屏模式 |
| 隐藏控件 | `H` | 隐藏/显示控制提示 |

### 完整视频合成

使用 FFmpeg 自动合成完整视频：

```python
from video_composer import VideoComposer

composer = VideoComposer()
composer.compose_full_ppt_video(
    slides_paths=[...],
    transitions_dict={...},
    output_path='output.mp4',
    slide_duration=2,  # 每页停留 2 秒
    include_preview=True,
    preview_video_path='preview.mp4',
    resolution='1920x1080',
    fps=24
)
```

**特性**：
- 自动统一所有视频的分辨率和帧率
- 保持宽高比，添加黑边
- 支持预览视频循环
- 高质量 H.264 编码

---

## 🎨 风格库

### 已内置风格

#### 1. 渐变毛玻璃卡片风格 (`gradient-glass.md`)

**视觉特点**：
- Apple Keynote 极简主义
- 玻璃拟态效果
- 霓虹紫/电光蓝/珊瑚橙渐变
- 3D 玻璃物体 + 电影级光照

**适用场景**：
- 🚀 科技产品发布
- 💼 商务演示
- 📊 数据报告
- 🏢 企业品牌展示

#### 2. 矢量插画风格 (`vector-illustration.md`)

**视觉特点**：
- 扁平化矢量设计
- 统一黑色轮廓线
- 复古柔和配色
- 几何化简化

**适用场景**：
- 📚 教育培训
- 🎨 创意提案
- 👶 儿童相关
- 💖 温暖品牌故事

### 添加自定义风格

1. 在 `styles/` 目录创建新的 `.md` 文件
2. 按照模板编写风格定义（参考现有风格）
3. 直接使用新风格生成 PPT

---

## 📚 项目结构

```
ppt-generator/
├── README.md                      # 本文件
├── API_MANAGEMENT.md              # API 密钥管理指南
├── ENV_SETUP.md                   # 环境变量配置指南
├── SECURITY.md                    # 安全最佳实践
├── .env.example                   # 环境变量模板
├── .env                          # 实际环境变量（不提交到 Git）
├── .gitignore                    # Git 忽略规则
│
├── generate_ppt.py               # PPT 图片生成脚本
├── generate_ppt_video.py         # 视频生成主脚本
├── kling_api.py                  # 可灵 AI API 封装
├── video_composer.py             # FFmpeg 视频合成
├── video_materials.py            # 视频素材管理
├── transition_prompt_generator.py # 转场提示词生成器
│
├── styles/                       # 风格库
│   ├── gradient-glass.md         # 渐变毛玻璃卡片风格
│   └── vector-illustration.md    # 矢量插画风格
│
├── templates/                    # HTML 模板
│   ├── viewer.html              # 图片播放器
│   └── video_viewer.html        # 视频播放器
│
├── prompts/                      # 提示词模板
│   └── transition_base.md       # 转场提示词基础模板
│
└── outputs/                      # 生成结果（自动创建）
    ├── TIMESTAMP/               # 图片版本
    │   ├── images/             # PPT 图片
    │   ├── index.html          # 图片播放器
    │   └── prompts.json        # 生成提示词记录
    └── TIMESTAMP_video/         # 视频版本
        ├── videos/             # 转场视频
        ├── video_index.html    # 视频播放器
        └── full_ppt_video.mp4  # 完整视频
```

---

## 🔧 配置选项

### 分辨率选择

| 分辨率 | 尺寸 | 文件大小 | 生成速度 | 推荐场景 |
|--------|------|----------|----------|----------|
| 2K | 2752x1536 | ~2.5MB/页 | ~30秒/页 | 日常演示、在线分享 ✅ |
| 4K | 5504x3072 | ~8MB/页 | ~60秒/页 | 打印输出、大屏展示 |

### 视频参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 分辨率 | 1920x1080 | 统一为 1080p，兼容可灵视频 |
| 帧率 | 24fps | 统一帧率，确保流畅拼接 |
| 静态图片时长 | 2秒 | 每页停留时间 |
| 转场视频时长 | 5秒 | 可灵生成的转场时长 |

### 页数建议

| 页数范围 | 演讲时长 | 适用场景 |
|----------|----------|----------|
| 5 页 | 5 分钟 | 电梯演讲、快速介绍 |
| 5-10 页 | 10-15 分钟 | 标准演示、产品介绍 |
| 10-15 页 | 20-30 分钟 | 深入讲解、培训课程 |
| 20-25 页 | 45-60 分钟 | 完整培训、研讨会 |

---

## ❓ 常见问题

### Q: 如何获取 API 密钥？

**A**:
- **Google AI API**: 访问 [Google AI Studio](https://aistudio.google.com/apikey)，登录后即可创建
- **可灵 AI API**: 访问 [可灵 AI 开放平台](https://klingai.com)，注册并创建应用获取密钥

### Q: 是否必须配置可灵 AI 密钥？

**A**: 不是必须的。
- **只生成 PPT 图片**：只需要 GEMINI_API_KEY
- **生成转场视频**：需要 KLING_ACCESS_KEY 和 KLING_SECRET_KEY

### Q: 视频合成失败怎么办？

**A**: 检查以下几点：
1. FFmpeg 是否已安装（`ffmpeg -version`）
2. 视频文件是否存在且完整
3. 磁盘空间是否充足
4. 查看详细错误信息

### Q: 如何修改静态图片展示时间？

**A**: 在 `video_composer.py` 中修改 `slide_duration` 参数（默认 2 秒）

### Q: 转场视频生成很慢怎么办？

**A**: 可灵 AI 生成视频需要一定时间（通常 30-60 秒/段）。可以：
- 减少转场数量
- 使用较短的转场时长
- 分批生成

### Q: 可以导出为 PDF 吗？

**A**: 可以。
1. 在浏览器中打开 `index.html`
2. 按 `Cmd+P` (Mac) 或 `Ctrl+P` (Windows)
3. 选择"另存为 PDF"

### Q: 生成的内容可以商用吗？

**A**: 请查阅相关服务条款：
- [Google AI 使用条款](https://ai.google.dev/terms)
- [可灵 AI 使用条款](https://klingai.com/terms)

一般情况下，你拥有生成内容的使用权。

---

## 🛡️ 安全说明

### API 密钥安全

本项目采用 `.env` 文件管理 API 密钥，确保安全：

- ✅ `.env` 文件已在 `.gitignore` 中，不会提交到 Git
- ✅ 代码中无硬编码密钥
- ✅ 支持系统环境变量作为备用方案
- ✅ `.env.example` 提供配置模板

**最佳实践**：

```bash
# ✅ 正确：使用 .env 文件
cp .env.example .env
# 编辑 .env 填入真实密钥

# ❌ 错误：直接在代码中写密钥
GEMINI_API_KEY = "AIzaSy..." # 永远不要这样做！
```

### 提交前检查

```bash
# 验证没有密钥泄露
grep -r "AIzaSy\|ak-" --exclude-dir=.git --exclude-dir=venv .
# 应该无输出

# 检查 .env 文件是否被排除
git status
# 确认 .env 不在待提交列表中
```

详细说明请查看：
- **API_MANAGEMENT.md** - API 密钥管理完整指南
- **ENV_SETUP.md** - 环境变量配置指南
- **SECURITY.md** - 安全最佳实践

---

## 📝 更新日志

### v2.0.0 (2026-01-11)

- 🎬 **新增视频功能**
  - 可灵 AI 转场视频生成
  - 交互式视频播放器（视频+图片混合）
  - FFmpeg 完整视频合成
  - 首页循环预览视频
- 🔧 **优化视频合成**
  - 自动统一分辨率和帧率
  - 修复视频拼接兼容性问题
  - 静态图片展示时间改为 2 秒
- 🐛 **Bug 修复**
  - 修复预览模式状态管理问题
  - 修复 FFmpeg 滤镜参数格式错误
- 📚 **文档更新**
  - 全面改写 README
  - 新增视频功能使用指南
  - 更新 API 密钥配置说明

### v1.0.0 (2026-01-09)

- ✨ 首次发布
- 🎨 内置 2 种专业风格
- 🖼️ 支持 2K/4K 分辨率
- 🎬 HTML5 图片播放器
- 📊 智能文档分析
- 🔐 安全的环境变量管理

---

## 🤝 贡献指南

欢迎贡献！你可以：

### 添加新风格

1. Fork 本项目
2. 在 `styles/` 创建新风格文件
3. 参考现有风格编写提示词
4. 测试生成效果
5. 提交 Pull Request

### 报告问题

在 [GitHub Issues](https://github.com/op7418/NanoBanana-PPT-Skills/issues) 提交问题，请包含：
- 错误信息
- 操作步骤
- 系统环境
- 日志文件（如有）

---

## 📄 许可证

MIT License

Copyright (c) 2026 歸藏

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🙏 致谢

- **Google Gemini Team** - 提供强大的 Nano Banana Pro 图像生成模型
- **可灵 AI 团队** - 提供高质量的视频生成服务
- **FFmpeg 项目** - 提供强大的视频处理工具
- **开源社区** - 提供的各种工具和灵感

---

## 📞 联系方式

- **创作者**: 歸藏
- **GitHub**: [@op7418](https://github.com/op7418)
- **Issues**: [GitHub Issues](https://github.com/op7418/NanoBanana-PPT-Skills/issues)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！**

Made with ❤️ by 歸藏 | Powered by Google Gemini & 可灵 AI & FFmpeg

</div>
