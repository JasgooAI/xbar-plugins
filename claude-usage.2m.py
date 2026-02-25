#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# <xbar.title>Claude Code Usage</xbar.title>
# <xbar.version>v2.0</xbar.version>
# <xbar.desc>Monitor Claude Code 5h billing block usage with color indicators</xbar.desc>
# <xbar.dependencies>python3,ccusage</xbar.dependencies>

import json
import os
import subprocess
from datetime import datetime, timezone

# xbar 使用最小化环境，需手动补充 PATH 让 node/ccusage 可用
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ.get("PATH", "")

CCUSAGE = "/opt/homebrew/bin/ccusage"

# ── 可配置：每 5 小时窗口的 token 上限 ──────────────────────
# Claude Code 的实际限额通过 API 动态下发，无本地记录。
# 这里用反推值，如显示百分比与 /config 不符，请手动调整。
# 单位：tokens（例如 12_000_000 = 1200 万）
TOKEN_LIMIT = 24_300_000

# 颜色阈值（基于用量百分比）
# 💚 < 50%，💛 50~75%，💔 > 75%
def pct_emoji(pct):
    if pct < 50:
        return "💚"
    elif pct < 75:
        return "💛"
    else:
        return "💔"

def run(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return json.loads(result.stdout)
    except Exception:
        return None

def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(n)

def fmt_duration(minutes):
    h = int(minutes // 60)
    m = int(minutes % 60)
    if h > 0:
        return f"{h}h{m:02d}m"
    return f"{m}m"

def main():
    blocks_data = run([CCUSAGE, "blocks", "--json"])
    daily_data  = run([CCUSAGE, "daily",  "--json"])

    # ── 解析当前活跃 block ────────────────────────────────────
    active_block = None
    if blocks_data:
        for b in blocks_data.get("blocks", []):
            if b.get("isActive") and not b.get("isGap"):
                active_block = b

    # ── 今日数据 ──────────────────────────────────────────────
    today_str = datetime.now().strftime("%Y-%m-%d")
    today = None
    if daily_data:
        for d in daily_data.get("daily", []):
            if d.get("date") == today_str:
                today = d

    # ── 状态栏 ────────────────────────────────────────────────
    if active_block:
        tokens = active_block["totalTokens"]
        end_time = datetime.fromisoformat(active_block["endTime"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        remaining_min = max(0, (end_time - now).total_seconds() / 60)

        pct = min(100, tokens / TOKEN_LIMIT * 100)
        icon = pct_emoji(pct)
        menubar = f"{icon} {pct:.0f}%  ⏱{fmt_duration(remaining_min)} | color=white"
    else:
        menubar = "💚 Claude 空闲 | color=white"

    print(menubar)
    print("---")

    # ── 下拉：当前 5h 窗口详情 ────────────────────────────────
    if active_block:
        tokens = active_block["totalTokens"]
        cost   = active_block.get("costUSD", 0)
        end_time = datetime.fromisoformat(active_block["endTime"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        remaining_min = max(0, (end_time - now).total_seconds() / 60)
        start_local = datetime.fromisoformat(
            active_block["startTime"].replace("Z", "+00:00")
        ).astimezone().strftime("%H:%M")
        end_local = end_time.astimezone().strftime("%H:%M")

        pct = min(100, tokens / TOKEN_LIMIT * 100)
        icon = pct_emoji(pct)
        print(f"{icon} 当前窗口  {start_local} – {end_local}  {pct:.1f}%")

        print(f"   已用：{fmt_tokens(tokens)} tokens  /  ${cost:.3f}")
        print(f"   剩余：{fmt_duration(remaining_min)}（窗口将在 {end_local} 重置）")

        burn = active_block.get("burnRate")
        if burn and burn.get("tokensPerMinute"):
            tpm = burn["tokensPerMinute"]
            cph = burn.get("costPerHour", 0)
            print(f"   速率：{fmt_tokens(int(tpm))}/min  (${cph:.2f}/h)")

        proj = active_block.get("projection")
        if proj and proj.get("totalTokens"):
            print(f"   预测：{fmt_tokens(proj['totalTokens'])} tokens  /  ${proj.get('totalCost', 0):.2f}")

        print(f"   上限：{fmt_tokens(TOKEN_LIMIT)}（可在脚本顶部调整）")
    else:
        print("💤 当前无活跃计费窗口")

    print("---")

    # ── 下拉：今日汇总 ────────────────────────────────────────
    if today:
        print(f"📅 今日（{today_str}）")
        print(f"   Token：{fmt_tokens(today['totalTokens'])}")
        print(f"   费用：${today['totalCost']:.4f}")
        models = today.get("modelsUsed", [])
        if models:
            short = ", ".join(m.split("-")[1] if "-" in m else m for m in models[:3])
            print(f"   模型：{short}")
    else:
        print(f"📅 今日（{today_str}）：暂无数据")

    print("---")
    print("🔄 立即刷新 | refresh=true")
    print(f"⏰ 每 2 分钟自动刷新")
    print("📊 查看详细报告 | bash=/opt/homebrew/bin/ccusage param1=blocks terminal=true")

if __name__ == "__main__":
    main()
