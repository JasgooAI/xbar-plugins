# 上下文迁移文档

用于在新的 Claude Code 会话中快速恢复工作状态。

## 迁移 Prompt（直接粘贴到新会话）

```
你好，我上次配置了一个 xbar 插件用于监控 Claude Code 的 5 小时计费窗口用量。

**相关文件：**
- 插件路径：~/Library/Application Support/xbar/plugins/claude-usage.2m.py
- GitHub：https://github.com/JasgooAI/xbar-plugins

**关键配置：**
- ccusage 版本：v17.2.1（全局安装于 /opt/homebrew/bin/ccusage）
- TOKEN_LIMIT = 14_800_000（校准值，与 /config 对齐）
- 刷新频率：每 2 分钟（文件名 .2m. 控制）

**当前状态栏格式：** `💚 29%  ⏱2h19m`
- 💚 < 50%，💛 50-75%，💔 > 75%，字体白色

**如需校准 TOKEN_LIMIT：**
TOKEN_LIMIT = 当前tokens ÷ (/config显示百分比 / 100)

请帮我继续改进这个插件。
```

## 完整上下文摘要

### 完成了什么
在 macOS 状态栏搭建了 Claude Code 用量监控系统，从零完成环境安装、插件开发、校准调试，并存档到 GitHub。

### 关键决策

| 决策 | 原因 |
|------|------|
| ccusage v17.2.1 而非最新版 | v18+ 需要 Node.js v24，用户只有 v23.9.0 |
| 固定 `TOKEN_LIMIT` 而非历史最高值 | 历史最高（16.6M）导致百分比偏低，实际限额约 14.8M |
| TOKEN_LIMIT = 14_800_000 | 反推：4.3M tokens ÷ 0.29 ≈ 14.8M，与 `/config` 对齐 |
| 刷新频率 2 分钟 | 文件名 `.2m.` 控制，xbar 约定 |

### 踩过的坑
- xbar 插件必须 `chmod +x` 否则不执行
- ccusage `--json` 的 `maxTokens` 字段返回 `null`，无法直接用
- Claude Code 实际 token 限额通过 API 下发，本地无文件记录
- 状态栏文字必须加 `| color=white`，否则深色模式看不清

### 环境信息
- macOS、Apple Silicon（/opt/homebrew）
- Node.js v23.9.0
- xbar 已安装：`/Applications/xbar.app`
- ccusage 全局路径：`/opt/homebrew/bin/ccusage`
