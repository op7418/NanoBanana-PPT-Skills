# 系统环境变量配置指南

## ✅ 当前配置状态

您的项目现在使用**系统环境变量**来管理API密钥，这是最安全的方案！

### 🎯 优势对比

| 方案 | 安全性 | 便利性 | Git安全 |
|------|--------|--------|---------|
| 硬编码 | ❌ 极低 | ✓ 方便 | ❌ 会泄露 |
| .env文件 | ⚠️ 中等 | ✓ 方便 | ⚠️ 需配置.gitignore |
| **系统环境变量** | ✅ **高** | ✅ **最方便** | ✅ **完全安全** |

## 📋 已完成的配置

### 1. 系统环境变量 ✅

API密钥和配置已添加到您的 `~/.zshrc` 文件中：

```bash
# Google AI API Key for PPT Generator (Gemini 引擎必需)
export GEMINI_API_KEY="your-api-key-here"

# ComfyUI 服务器地址（ComfyUI 引擎可选，默认 http://127.0.0.1:8188）
export COMFYUI_SERVER_URL="http://127.0.0.1:8188"
```

**验证方法**：
```bash
echo $GEMINI_API_KEY
# 应显示您的API密钥

echo $COMFYUI_SERVER_URL
# 应显示 ComfyUI 服务器地址（如果已设置）
```

### 2. run.sh 智能识别 ✅

启动脚本已更新，优先级顺序：
1. **系统环境变量**（最高优先级）✅
2. .env 文件（备用方案）

当您运行 `./run.sh` 时，会显示：
```
✅ 使用系统环境变量中的API密钥
```

### 3. 项目文件清理 ✅

- ✅ `.env` 文件已删除
- ✅ `.env.example` 保留（作为模板）
- ✅ `run.sh` 不包含硬编码密钥
- ✅ 所有文档使用占位符

## 🔐 Git提交安全性

### 现在提交到GitHub，绝对安全！

**不会被提交的内容**：
- ❌ API密钥（存储在系统环境变量中）
- ❌ `.env` 文件（已删除且在.gitignore中）
- ❌ 虚拟环境（venv/）
- ❌ 输出文件（outputs/）

**会被提交的内容（全部安全）**：
- ✅ `.env.example` - 仅包含模板（包含 GEMINI_API_KEY 和 COMFYUI_SERVER_URL 示例）
- ✅ `.gitignore` - Git忽略规则
- ✅ `run.sh` - 从环境变量读取配置
- ✅ `generate_ppt.py` - Python脚本
- ✅ 所有文档和风格文件

### 验证命令

```bash
# 搜索项目中的API密钥
grep -r "AIzaSy" --exclude-dir=.git --exclude-dir=venv .

# 应该没有任何输出！✅
```

## 🚀 使用方法

### 在当前项目中使用

直接运行即可，会自动使用系统环境变量：

```bash
./run.sh --plan ../test_slides_plan.json --style styles/gradient-glass.md --resolution 2K
```

输出显示：
```
✅ 使用系统环境变量中的API密钥
```

### 在其他机器上使用

当您在新机器上克隆项目时：

**步骤1**: 克隆仓库
```bash
git clone https://github.com/你的用户名/ppt-generator.git
cd ppt-generator
```

**步骤2**: 配置环境变量（根据Shell选择）

**zsh用户**（推荐）：
```bash
# Gemini API 密钥（使用 --engine gemini 时必需）
echo 'export GEMINI_API_KEY="your-api-key"' >> ~/.zshrc

# ComfyUI 服务器地址（使用 --engine comfyui 时可选）
echo 'export COMFYUI_SERVER_URL="http://127.0.0.1:8188"' >> ~/.zshrc

source ~/.zshrc
```

**bash用户**：
```bash
# Gemini API 密钥
echo 'export GEMINI_API_KEY="your-api-key"' >> ~/.bashrc

# ComfyUI 服务器地址
echo 'export COMFYUI_SERVER_URL="http://127.0.0.1:8188"' >> ~/.bashrc

source ~/.bashrc
```

**fish用户**：
```bash
set -Ux GEMINI_API_KEY "your-api-key"
set -Ux COMFYUI_SERVER_URL "http://127.0.0.1:8188"
```

**Windows PowerShell 用户**：
```powershell
# 临时设置（当前会话）
$env:GEMINI_API_KEY="your-api-key"
$env:COMFYUI_SERVER_URL="http://127.0.0.1:8188"

# 永久设置（用户级别）
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-api-key", "User")
[System.Environment]::SetEnvironmentVariable("COMFYUI_SERVER_URL", "http://127.0.0.1:8188", "User")
```

**Windows CMD 用户**：
```cmd
REM 临时设置（当前会话）
set GEMINI_API_KEY=your-api-key
set COMFYUI_SERVER_URL=http://127.0.0.1:8188

REM 永久设置（用户级别）
setx GEMINI_API_KEY "your-api-key"
setx COMFYUI_SERVER_URL "http://127.0.0.1:8188"
```

**步骤3**: 安装依赖并运行
```bash
python3 -m venv venv
source venv/bin/activate
pip install google-genai pillow
./run.sh --help
```

## 🔄 管理环境变量

### 查看当前配置

```bash
# 查看 Gemini API 密钥
echo $GEMINI_API_KEY

# 查看 ComfyUI 服务器地址
echo $COMFYUI_SERVER_URL
```

### 临时修改配置（当前会话）

```bash
# 修改 Gemini API 密钥
export GEMINI_API_KEY="new-key-here"

# 修改 ComfyUI 服务器地址
export COMFYUI_SERVER_URL="http://192.168.1.100:8188"
```

### 永久修改配置

编辑配置文件：
```bash
nano ~/.zshrc  # 或使用你喜欢的编辑器
```

找到相关行并修改：
```bash
export GEMINI_API_KEY="新的密钥"
export COMFYUI_SERVER_URL="新的服务器地址"
```

重新加载配置：
```bash
source ~/.zshrc
```

### 删除配置

编辑 `~/.zshrc`，删除包含相关变量的行，然后：
```bash
source ~/.zshrc
unset GEMINI_API_KEY
unset COMFYUI_SERVER_URL
```

## 🎨 ComfyUI 配置说明

### ComfyUI 服务器地址设置

ComfyUI 服务器地址用于指定本地或远程 ComfyUI 服务的访问地址。

**默认值**：`http://127.0.0.1:8188`

**常见场景**：

1. **本地 ComfyUI（默认）**
   ```bash
   export COMFYUI_SERVER_URL="http://127.0.0.1:8188"
   ```
   适用于 ComfyUI 运行在同一台机器上

2. **局域网内其他机器**
   ```bash
   export COMFYUI_SERVER_URL="http://192.168.1.100:8188"
   ```
   将 `192.168.1.100` 替换为实际的 ComfyUI 服务器 IP

3. **自定义端口**
   ```bash
   export COMFYUI_SERVER_URL="http://127.0.0.1:8189"
   ```
   如果 ComfyUI 运行在非默认端口

4. **HTTPS 服务器**
   ```bash
   export COMFYUI_SERVER_URL="https://comfyui.example.com"
   ```
   适用于通过 HTTPS 访问的远程服务器

**验证 ComfyUI 连接**：
```bash
# 测试 ComfyUI 服务器是否可访问
curl http://127.0.0.1:8188/system_stats
# 如果返回 JSON 数据，说明连接正常
```

**注意事项**：
- 如果未设置 `COMFYUI_SERVER_URL`，程序会使用默认值 `http://127.0.0.1:8188`
- 使用 `--comfyui-server` 命令行参数可以临时覆盖环境变量设置
- 确保 ComfyUI 服务已启动并可以访问

## 💡 最佳实践

### ✓ 推荐做法

1. **使用系统环境变量存储所有配置**
   ```bash
   # 示例：添加多个API密钥和配置
   export GEMINI_API_KEY="..."
   export COMFYUI_SERVER_URL="http://127.0.0.1:8188"
   export OPENAI_API_KEY="..."
   export AWS_ACCESS_KEY="..."
   ```

2. **定期轮换API密钥**
   - 每3-6个月更新一次
   - 发现异常使用立即更新

3. **不同项目使用不同密钥**（可选）
   - 便于追踪使用情况
   - 限制单个密钥的影响范围

4. **备份环境变量配置**
   ```bash
   # 导出配置（注意安全存储）
   grep "export.*_KEY" ~/.zshrc > ~/my-env-backup.txt
   ```

### ✗ 避免做法

- ❌ 在代码中硬编码密钥
- ❌ 将 `.zshrc` 提交到Git
- ❌ 通过邮件发送密钥
- ❌ 在截图中暴露密钥
- ❌ 使用同一密钥在多个公共项目

## 🛡️ 安全检查清单

在提交到GitHub前，确认：

- [ ] 运行 `grep -r "AIzaSy" .` 无输出
- [ ] `.env` 文件不存在或已在 .gitignore
- [ ] `run.sh` 不包含硬编码密钥
- [ ] 所有文档使用 `your-api-key-here` 占位符
- [ ] `git status` 不显示敏感文件
- [ ] `.zshrc` 不在Git仓库中

全部✅后，可以安全提交！

## 📊 安全等级对比

```
┌─────────────────────────────────────────────┐
│ 安全等级：系统环境变量方案                    │
├─────────────────────────────────────────────┤
│                                             │
│  Git泄露风险         ████████████ 0%       │
│  代码泄露风险         ████████████ 0%       │
│  文档泄露风险         ████████████ 0%       │
│  便利性             ████████████ 100%      │
│  多项目共享          ████████████ 100%      │
│                                             │
└─────────────────────────────────────────────┘
```

## 🎉 总结

您现在拥有最安全的API密钥管理方案：

✅ **API密钥存储在系统环境变量中**
✅ **项目代码完全不含密钥**
✅ **可以放心提交到GitHub**
✅ **跨项目共享同一密钥**
✅ **新机器配置简单快速**

---

**需要帮助？**
- 系统环境变量配置问题：查看本文档"管理API密钥"部分
- Git提交问题：查看 SECURITY.md
- 项目使用问题：查看 README.md 和 QUICKSTART.md
