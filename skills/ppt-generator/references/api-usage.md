# Nano Banana Pro API 使用参考

## API 概述

Nano Banana Pro 是 Google 的 Gemini 3 Pro Image Preview 模型，专为高质量图像生成设计。

## 配置

### API 密钥获取

访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 获取 API 密钥。

### 环境变量设置

```bash
# macOS/Linux (zsh)
echo 'export GEMINI_API_KEY="your-api-key"' >> ~/.zshrc
source ~/.zshrc

# macOS/Linux (bash)
echo 'export GEMINI_API_KEY="your-api-key"' >> ~/.bashrc
source ~/.bashrc

# Windows PowerShell
$env:GEMINI_API_KEY = "your-api-key"
# 或永久设置
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-api-key", "User")
```

## API 调用示例

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_modalities=['IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="2K"  # 或 "4K"
        )
    )
)

for part in response.parts:
    if part.inline_data is not None:
        image = part.as_image()
        image.save("output.png")
```

## 分辨率选项

| 分辨率 | 尺寸 | 文件大小 | 生成速度 | 推荐场景 |
|--------|------|----------|----------|----------|
| 2K | 2752x1536 | ~2.5MB/页 | ~30秒/页 | 日常演示、在线分享 |
| 4K | 5504x3072 | ~8MB/页 | ~60秒/页 | 打印输出、大屏展示 |

## 比例选项

支持的宽高比：
- `16:9` - 标准演示文稿比例（推荐）
- `4:3` - 传统屏幕比例
- `1:1` - 正方形
- `9:16` - 竖屏比例

## 错误处理

### 常见错误码

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `INVALID_API_KEY` | API 密钥无效 | 检查密钥是否正确 |
| `QUOTA_EXCEEDED` | 配额超限 | 等待配额重置或升级 |
| `TIMEOUT` | 请求超时 | 网络问题，稍后重试 |
| `CONTENT_FILTERED` | 内容被过滤 | 修改提示词内容 |

### 重试策略

建议实现指数退避重试：

```python
import time

def generate_with_retry(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return generate_image(prompt)
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise e
```

## 配额与限制

- 免费层：有每日请求限制
- 付费层：根据计划不同限制不同

详情请参阅 [Google AI 定价页面](https://ai.google.dev/pricing)。

## 使用条款

使用生成的图像请遵守 [Google AI 使用条款](https://ai.google.dev/terms)。
