# xbar-plugins

macOS 状态栏插件合集，基于 [xbar](https://github.com/matryer/xbar)。

---

## claude-usage.2m.py

在 macOS 状态栏实时监控 **Claude Code 当前 5 小时计费窗口**的 token 用量。

### 效果

```
💚 29%  ⏱2h19m
```

- **💚** 用量 < 50%（充足）
- **💛** 用量 50–75%（不太够）
- **💔** 用量 > 75%（告急）
- **⏱** 当前 5 小时窗口的剩余时间（窗口结束后额度重置）
- 每 **2 分钟**自动刷新

### 依赖

| 工具 | 安装方式 |
|------|----------|
| [xbar](https://github.com/matryer/xbar) | `brew install --cask xbar` |
| [ccusage](https://github.com/ryoppippi/ccusage) | `npm install -g ccusage@17.2.1` |
| Python 3 | macOS 自带 |

> ⚠️ ccusage 最新版（v18+）需要 Node.js v24，v17.x 兼容 Node.js v20+。

### 安装

```bash
# 1. 安装依赖
brew install --cask xbar
npm install -g ccusage@17.2.1

# 2. 复制插件
cp claude-usage.2m.py ~/Library/Application\ Support/xbar/plugins/
chmod +x ~/Library/Application\ Support/xbar/plugins/claude-usage.2m.py

# 3. 启动 xbar
open -a xbar
```

### 配置

打开脚本，修改顶部的 `TOKEN_LIMIT`，使百分比与 Claude Code 内 `/config` 显示一致：

```python
# 每 5 小时窗口的 token 上限
# 校准方法：TOKEN_LIMIT = 当前 tokens ÷ /config 显示的百分比
TOKEN_LIMIT = 14_800_000
```

**校准公式：**

```
TOKEN_LIMIT = 当前 token 数 ÷ (Claude Code /config 显示的百分比 / 100)
```

例如当前用了 4.3M tokens，`/config` 显示 29%：
```
TOKEN_LIMIT = 4,300,000 ÷ 0.29 ≈ 14,800,000
```

### 下拉菜单说明

点击状态栏图标展开：

```
💚 当前窗口  21:00 – 02:00  29.0%
   已用：4.3M tokens  /  $1.66
   剩余：2h19m（窗口将在 02:00 重置）
   速率：31K/min  ($0.74/h)
   预测：8.6M tokens  /  $3.41
   上限：14.8M（可在脚本顶部调整）
---
📅 今日（2026-02-24）
   Token：6.5M
   费用：$2.95
   模型：sonnet, haiku
---
🔄 立即刷新
📊 查看详细报告
```
