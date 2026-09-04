# PPT Generator Pro - Claude Code Skill

## 📋 元数据

- **Skill 名称**: ppt-generator-pro
- **版本**: 2.0.0
- **描述**: 基于 AI 自动生成高质量 PPT 图片和视频，支持智能转场和交互式播放
- **作者**: 歸藏
- **标签**: ppt, presentation, video, ai, nano-banana, kling-ai, image-generation

## ✨ 功能特性

### 核心功能
- 🤖 **智能文档分析** - 自动提取核心要点，规划 PPT 内容结构
- 🎨 **多风格支持** - 内置渐变毛玻璃、矢量插画两种专业风格
- 🖼️ **高质量图片** - 使用 Nano Banana Pro 生成 16:9 高清 PPT
- 🎬 **AI 转场视频** - 可灵 AI 生成流畅的页面过渡动画
- 🎮 **交互式播放器** - 视频+图片混合播放，支持键盘导航
- 🎥 **完整视频导出** - FFmpeg 合成包含所有转场的完整 PPT 视频

### 新功能 (v2.0)
- 🔄 **首页循环预览** - 自动生成吸引眼球的循环动画
- 🎞️ **智能转场** - 自动生成页面间的过渡视频
- 🔧 **参数统一** - 自动统一所有视频分辨率和帧率

## 📦 系统要求

### 环境变量

**必需：**
- `GEMINI_API_KEY`: Google AI API 密钥（用于生成 PPT 图片）

**可选（用于视频功能）：**
- `KLING_ACCESS_KEY`: 可灵 AI Access Key
- `KLING_SECRET_KEY`: 可灵 AI Secret Key

**可选（Gemini 官方 API 不能直连时的第二条出图路径）：**
- `ATLASCLOUD_API_KEY`: [Atlas Cloud](https://www.atlascloud.ai/?utm_source=github&utm_medium=link&utm_campaign=nanobanana-ppt-skills) API 密钥，配合 `--provider atlas` 使用
- `ATLASCLOUD_IMAGE_MODEL`: 覆盖模型（默认 `bytedance/seedream-v4`）

```bash
# 走 Atlas 出图，其余参数不变
python3 generate_ppt.py --plan slides_plan.json --style styles/gradient-glass.md \
  --resolution 2K --provider atlas
```

实测要点：

- **2K / 4K 都保住了**：默认模型 `bytedance/seedream-v4` 精确遵守请求尺寸，脚本把
  16:9 的两档换算成 `2048*1152` / `3840*2160`，实测出图正好是这两个尺寸。
- **不要换成 nano-banana 系列**：实测那一系列忽略尺寸参数、只认 `aspect_ratio`，
  出图约 1376×768，做 PPT 不够用。
- 该模型返回 JPEG，而 viewer HTML 引用的是 `images/slide-XX.png`，所以脚本会把
  产物转成 PNG 落盘，不会写出名不副实的文件。
- **这条路不需要 `google-genai`**：`--provider atlas` 分支在导入 `google.genai`
  之前就返回了，只用标准库 + pillow。

### Python 依赖

```bash
pip install google-genai pillow python-dotenv
```

### 视频功能依赖

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

## 🚀 使用方法

### 在 Claude Code 中调用

```bash
/ppt-generator-pro
```

或直接告诉 Claude：

```
我想基于以下文档生成一个 5 页的 PPT，使用渐变毛玻璃风格。

[文档内容...]
```

## 📝 Skill 执行流程

### 阶段 1: 收集用户输入

#### 1.1 获取文档内容

**选项 A: 文档路径**
```
用户: 基于 my-document.md 生成 PPT
→ 使用 Read 工具读取文件内容
```

**选项 B: 直接文本**
```
用户: 我想生成一个关于 AI 产品设计的 PPT
主要内容：
1. 现状分析
2. 设计原则
3. 案例研究
```

**选项 C: 主动询问**
```
如果用户未提供内容，询问：
"请提供文档路径或直接粘贴文档内容"
```

#### 1.2 选择风格

扫描 `styles/` 目录，列出可用风格：

```python
# 自动检测风格文件
styles = ['gradient-glass.md', 'vector-illustration.md']
```

**如果有多个风格，使用 AskUserQuestion：**

```markdown
问题: 请选择 PPT 风格
选项:
- 渐变毛玻璃卡片风格（科技感、商务演示）
- 矢量插画风格（温暖、教育培训）
```

#### 1.3 选择页数范围

使用 AskUserQuestion 询问：

```markdown
问题: 希望生成多少页 PPT？
选项:
- 5 页（5 分钟演讲）
- 5-10 页（10-15 分钟演讲）
- 10-15 页（20-30 分钟演讲）
- 20-25 页（45-60 分钟演讲）
```

#### 1.4 选择分辨率

```markdown
问题: 选择图片分辨率
选项:
- 2K (2752x1536) - 推荐，快速生成
- 4K (5504x3072) - 高质量，适合打印
```

#### 1.5 是否生成视频（可选）

如果配置了可灵 AI 密钥，询问：

```markdown
问题: 是否生成转场视频？
选项:
- 仅图片（快速）
- 图片 + 转场视频（完整体验）
```

### 阶段 2: 文档分析与内容规划

#### 2.1 内容规划策略

根据页数范围，智能规划每一页内容：

**5 页版本：**
1. 封面：标题 + 核心主题
2. 要点 1：第一个核心观点
3. 要点 2：第二个核心观点
4. 要点 3：第三个核心观点
5. 总结：核心结论或行动建议

**5-10 页版本：**
1. 封面
2-3. 引言/背景
4-7. 核心内容（3-4 个关键观点）
8-9. 案例或数据支持
10. 总结与行动建议

**10-15 页版本：**
1. 封面
2-3. 引言/目录
4-6. 第一章节（3 页）
7-9. 第二章节（3 页）
10-12. 第三章节/案例研究
13-14. 数据可视化
15. 总结与下一步

**20-25 页版本：**
1. 封面
2. 目录
3-4. 引言和背景
5-8. 第一部分（4 页）
9-12. 第二部分（4 页）
13-16. 第三部分（4 页）
17-19. 案例研究
20-22. 数据分析和洞察
23-24. 关键发现和建议
25. 总结与致谢

#### 2.2 生成 slides_plan.json

创建 JSON 文件：

```json
{
  "title": "文档标题",
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

**重要：** 将此文件保存到：
- 独立使用：`./slides_plan.json`
- Skill 模式：`.claude/skills/ppt-generator/slides_plan.json`

### 阶段 3: 生成 PPT 图片

#### 3.1 确定工作目录

**独立模式：**
```bash
cd /path/to/ppt-generator
```

**Skill 模式：**
```bash
cd ~/.claude/skills/ppt-generator
```

#### 3.2 执行生成命令

```bash
python generate_ppt.py \
  --plan slides_plan.json \
  --style styles/gradient-glass.md \
  --resolution 2K
```

**或使用 uv run（推荐）：**
```bash
uv run python generate_ppt.py \
  --plan slides_plan.json \
  --style styles/gradient-glass.md \
  --resolution 2K
```

**参数说明：**
- `--plan`: slides 规划 JSON 文件路径
- `--style`: 风格文件路径
- `--resolution`: 分辨率（2K 或 4K）
- `--template`: HTML 模板路径（可选）

#### 3.3 监控生成进度

脚本会输出进度信息：

```
✅ 已加载环境变量: /path/to/.env
📊 开始生成 PPT 图片...
   总页数: 5
   分辨率: 2K (2752x1536)
   风格: 渐变毛玻璃卡片风格

🎨 生成第 1 页 (封面页)...
   提示词已生成
   调用 Nano Banana Pro API...
   ✅ 第 1 页生成成功 (32.5 秒)

🎨 生成第 2 页 (内容页)...
   ✅ 第 2 页生成成功 (28.3 秒)

...

✅ 所有页面生成完成！
📁 输出目录: outputs/20260112_143022/
```

### 阶段 4: 生成转场提示词（视频模式需要）

**这是 Skill 的核心优势**：我（Claude Code）会分析生成的 PPT 图片，为每个转场生成精准的视频提示词。

#### 4.1 读取并分析 PPT 图片

我会读取所有生成的图片：

```python
# 自动读取输出目录中的所有图片
slides = ['slide-01.png', 'slide-02.png', ...]
```

#### 4.2 分析图片差异并生成提示词

对于每对相邻图片，我会：
1. **视觉分析**：理解两张图片的布局、元素、色彩差异
2. **生成预览提示词**：为首页创建可循环的微动效描述
3. **生成转场提示词**：详细描述如何从起始帧过渡到结束帧

**示例输出：**
```json
{
  "preview": {
    "slide_path": "outputs/.../slide-01.png",
    "prompt": "画面保持封面的静态构图，中心的3D玻璃环缓慢旋转..."
  },
  "transitions": [
    {
      "from_slide": 1,
      "to_slide": 2,
      "prompt": "镜头从封面开始，玻璃环逐渐解构，分裂成透明碎片..."
    }
  ]
}
```

#### 4.3 保存提示词文件

我会将生成的提示词保存到：
```
outputs/TIMESTAMP/transition_prompts.json
```

**关键优势：**
- ✅ 不需要单独的 Claude API 密钥
- ✅ 提示词针对实际图片内容定制
- ✅ 考虑文字稳定性，避免视频模型弄模糊文字
- ✅ 符合渐变毛玻璃风格的视觉语言

### 阶段 5: 生成转场视频（可选）

如果用户选择生成视频，使用阶段 4 生成的提示词文件：

```bash
python generate_ppt_video.py \
  --slides-dir outputs/20260112_143022/images \
  --output-dir outputs/20260112_143022_video \
  --prompts-file outputs/20260112_143022/transition_prompts.json
```

**生成内容：**
- 首页循环预览视频（`preview.mp4`）
- 页面间转场视频（`transition_01_to_02.mp4` 等）
- 交互式视频播放器（`video_index.html`）
- 完整视频（`full_ppt_video.mp4`）

### 阶段 6: 返回结果

#### 6.1 仅图片模式

```
✅ PPT 生成成功！

📁 输出目录: outputs/20260112_143022/
🖼️ PPT 图片: outputs/20260112_143022/images/
🎬 播放网页: outputs/20260112_143022/index.html

打开播放网页:
open outputs/20260112_143022/index.html

播放器快捷键:
- ← → 键: 切换页面
- ↑ Home: 回到首页
- ↓ End: 跳到末页
- 空格: 暂停/继续自动播放
- ESC: 全屏切换
- H: 隐藏/显示控件
```

#### 5.2 视频模式

```
✅ PPT 视频生成成功！

📁 输出目录: outputs/20260112_143022_video/
🖼️ PPT 图片: outputs/20260112_143022/images/
🎬 转场视频: outputs/20260112_143022_video/videos/
🎮 交互式播放器: outputs/20260112_143022_video/video_index.html
🎥 完整视频: outputs/20260112_143022_video/full_ppt_video.mp4

打开交互式播放器:
open outputs/20260112_143022_video/video_index.html

播放逻辑:
1. 首页: 播放循环预览视频
2. 按右键 → 播放转场视频 → 显示目标页图片（2 秒）
3. 再按右键 → 播放下一个转场 → 显示下一页图片
4. 依此类推...

视频播放器快捷键:
- ← → 键: 上一页/下一页（含转场）
- 空格: 播放/暂停当前视频
- ESC: 全屏切换
- H: 隐藏/显示控件
```

## 🔧 环境变量配置

### .env 文件位置

Skill 会按以下顺序查找 `.env` 文件：

1. **脚本所在目录** - `./ppt-generator/.env`
2. **向上查找项目根目录** - 直到找到包含 `.git` 或 `.env` 的目录
3. **Claude Skill 标准位置** - `~/.claude/skills/ppt-generator/.env`
4. **系统环境变量** - 如果以上都未找到

### .env 文件示例

```bash
# Google AI API 密钥（必需）
GEMINI_API_KEY=your_gemini_api_key_here

# 可灵 AI API 密钥（可选，用于视频功能）
KLING_ACCESS_KEY=your_kling_access_key_here
KLING_SECRET_KEY=your_kling_secret_key_here
```

## ⚠️ 错误处理

### 常见错误及解决方案

**1. API 密钥未设置**
```
错误: ⚠️ 未找到 .env 文件，尝试使用系统环境变量
      未设置 GEMINI_API_KEY 环境变量

解决:
1. 创建 .env 文件
2. 添加 GEMINI_API_KEY=your_key_here
```

**2. Python 依赖缺失**
```
错误: ModuleNotFoundError: No module named 'google.genai'

解决: pip install google-genai pillow python-dotenv
```

**3. FFmpeg 未安装**
```
错误: ❌ FFmpeg 不可用！

解决: brew install ffmpeg  # macOS
      sudo apt-get install ffmpeg  # Ubuntu
```

**4. API 调用失败**
```
错误: API 调用超时或失败

解决:
1. 检查网络连接
2. 确认 API 密钥有效
3. 稍后重试
```

**5. 视频生成失败**
```
错误: 可灵 AI 密钥未配置

解决:
1. 如果只需要图片，跳过视频生成步骤
2. 如果需要视频，配置 KLING_ACCESS_KEY 和 KLING_SECRET_KEY
```

## 🎨 风格系统

### 已内置风格

#### 1. 渐变毛玻璃卡片风格 (`gradient-glass.md`)

**视觉特点：**
- Apple Keynote 极简主义
- 玻璃拟态效果
- 霓虹紫/电光蓝/珊瑚橙渐变
- 3D 玻璃物体 + 电影级光照

**适用场景：**
- 科技产品发布
- 商务演示
- 数据报告
- 企业品牌展示

#### 2. 矢量插画风格 (`vector-illustration.md`)

**视觉特点：**
- 扁平化矢量设计
- 统一黑色轮廓线
- 复古柔和配色
- 几何化简化

**适用场景：**
- 教育培训
- 创意提案
- 儿童相关
- 温暖品牌故事

### 添加自定义风格

1. 在 `styles/` 目录创建新的 `.md` 文件
2. 按照现有风格格式编写
3. Skill 会自动识别并提供选择

## 📊 技术细节

### API 配置

**Nano Banana Pro（图片生成）：**
- 模型：`gemini-3-pro-image-preview`
- 比例：`16:9`
- 响应模式：`IMAGE`
- 分辨率：2K (2752x1536) 或 4K (5504x3072)

**可灵 AI（视频生成）：**
- 模式：专业模式（professional）
- 时长：5 秒
- 分辨率：1920x1080
- 帧率：24fps

**FFmpeg（视频合成）：**
- 编码：H.264
- 质量：CRF 23
- 帧率：24fps（统一）
- 分辨率：1920x1080（统一）

### 性能指标

**生成速度：**
- PPT 图片：~30 秒/页（2K）| ~60 秒/页（4K）
- 转场视频：~30-60 秒/段
- 视频合成：~5-10 秒

**文件大小：**
- PPT 图片：~2.5MB/页（2K）| ~8MB/页（4K）
- 转场视频：~3-5MB/段（1080p，5 秒）
- 完整视频：~12-20MB（5 页 PPT + 转场）

## 📁 文件组织

### 输出目录结构

**仅图片模式：**
```
outputs/20260112_143022/
├── images/
│   ├── slide-01.png
│   ├── slide-02.png
│   └── ...
├── index.html          # 图片播放器
└── prompts.json        # 提示词记录
```

**视频模式：**
```
outputs/20260112_143022_video/
├── videos/
│   ├── preview.mp4              # 首页循环预览
│   ├── transition_01_to_02.mp4
│   ├── transition_02_to_03.mp4
│   └── ...
├── video_index.html             # 交互式播放器
└── full_ppt_video.mp4           # 完整视频
```

## 🎯 最佳实践

1. **文档质量**：输入文档内容越清晰结构化，生成的 PPT 质量越高
2. **页数选择**：根据文档长度和演示场景合理选择页数
3. **分辨率选择**：日常使用推荐 2K，重要展示场合可选 4K
4. **视频功能**：首次使用建议先尝试仅图片模式，熟悉后再使用视频功能
5. **提示词调整**：查看 `prompts.json` 了解生成逻辑，可手动调整后重新生成

## 📝 使用示例

### 示例 1: 快速生成

**用户输入：**
```
我需要基于这份会议纪要生成一个 5 页的 PPT，使用矢量插画风格。

会议主题：Q1 产品路线图规划
参与人：产品团队

讨论内容：
1. 用户反馈汇总
2. 新功能优先级
3. 技术可行性评估
4. Q1 里程碑
5. 下一步行动项
```

**Skill 执行：**
1. 收集输入（已提供内容）
2. 确认风格（矢量插画）
3. 确认页数（5 页）
4. 确认分辨率（询问用户）
5. 生成 slides_plan.json
6. 执行生成命令
7. 返回结果

### 示例 2: 完整流程

**用户输入：**
```
基于 AI-Product-Design.md 文档，生成一个 15 页的 PPT，使用渐变毛玻璃风格，需要转场视频。
```

**Skill 执行：**
1. 读取文档内容
2. 确认风格（渐变毛玻璃）
3. 确认页数（15 页）
4. 确认分辨率（询问用户）
5. 确认生成视频（是）
6. 分析文档，规划 15 页内容
7. 生成 slides_plan.json
8. 生成 PPT 图片
9. 生成转场视频
10. 合成完整视频
11. 返回所有结果

## 🔄 更新日志

### v2.0.0 (2026-01-12)

- 🎬 **新增视频功能**
  - 可灵 AI 转场视频生成
  - 交互式视频播放器
  - FFmpeg 完整视频合成
  - 首页循环预览视频
- 🔧 **优化视频合成**
  - 自动统一分辨率和帧率
  - 修复视频拼接兼容性问题
  - 静态图片展示时间改为 2 秒
- 🔑 **改进环境变量**
  - 智能查找 .env 文件
  - 支持多种部署模式
  - 自动向上查找项目根目录
- 📚 **文档完善**
  - 重命名为 SKILL.md（符合官方规范）
  - 更新所有路径和命令
  - 添加视频功能使用指南

### v1.0.0 (2026-01-09)

- ✨ 首次发布
- 🎨 内置 2 种专业风格
- 🖼️ 支持 2K/4K 分辨率
- 🎬 HTML5 图片播放器
- 📊 智能文档分析

## 📄 许可证

MIT License

## 📞 技术支持

- 项目架构：参见 `ARCHITECTURE.md`
- API 管理：参见 `API_MANAGEMENT.md`
- 环境配置：参见 `ENV_SETUP.md`
- 安全说明：参见 `SECURITY.md`
- 完整文档：参见 `README.md`
