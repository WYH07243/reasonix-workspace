#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reasonix_control_panel.py — Reasonix 控制面板（聊天内显示）

直接在聊天中运行，不需要浏览器：
  python scripts/reasonix_control_panel.py

实时显示：工作区状态 | 桌面状态 | 项目列表 | 快捷操作
"""
import sys, os, json, subprocess
from datetime import datetime

WORKSPACE = r'D:\reasonix-workspace'

def get_all_status():
    """采集所有状态"""
    # 文档
    docs = {}
    for name in ['99-全局控制台.md', '92-工作区架构与命名规则.md',
                 '93-新项目创建SOP.md', '91-全局复利与踩坑日志.md', 'AGENTS.md']:
        path = os.path.join(WORKSPACE, name)
        docs[name] = {'ok': os.path.isfile(path), 'size': os.path.getsize(path) if os.path.isfile(path) else 0}

    # 项目
    projects = []
    if os.path.isdir(WORKSPACE):
        for item in sorted(os.listdir(WORKSPACE)):
            fp = os.path.join(WORKSPACE, item)
            if os.path.isdir(fp) and item.startswith('Project_'):
                # 检查是否有进度文件
                has_entry = any(f.startswith('90-') or f.startswith('91-') for f in os.listdir(fp))
                projects.append({'name': item, 'has_entry': has_entry})

    # 脚本
    scripts_dir = os.path.join(WORKSPACE, 'scripts')
    scripts = []
    if os.path.isdir(scripts_dir):
        for f in sorted(os.listdir(scripts_dir)):
            if f.endswith('.py') or f.endswith('.ps1'):
                fp = os.path.join(scripts_dir, f)
                scripts.append({'name': f, 'size': os.path.getsize(fp), 'ext': os.path.splitext(f)[1]})

    # GitHub
    github_status = '未连接'
    repo_path = os.path.join(WORKSPACE, '.git')
    if os.path.isdir(repo_path):
        try:
            r = subprocess.run(['git', '-C', WORKSPACE, 'remote', '-v'], capture_output=True, text=True, timeout=5)
            for line in r.stdout.split('\n'):
                if 'origin' in line and 'push' in line:
                    github_status = line.split('\t')[1].split('.git')[0].split('/')[-1]
        except: pass

    # Token
    token_file = os.path.join(WORKSPACE, 'scripts', '.tokens.json')
    tokens = []
    if os.path.isfile(token_file):
        with open(token_file, 'r') as f:
            data = json.load(f)
            tokens = list(data.keys())

    return {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'docs': docs,
        'projects': projects,
        'scripts': scripts,
        'github': github_status,
        'tokens': tokens,
        'has_templates': os.path.isdir(os.path.join(WORKSPACE, 'templates')),
        'has_scripts': os.path.isdir(scripts_dir),
        'temp_ok': os.path.isdir(r'D:\reasonix-workspace_temp'),
        'deliv_ok': os.path.isdir(r'D:\reasonix-workspace_deliverables'),
        'total_size': sum(d['size'] for d in docs.values()),
    }


def show_panel(data):
    """显示控制面板"""
    d = data

    # ── 标题栏 ──
    print()
    print('╔' + '═' * 56 + '╗')
    title = '  ★  REASONIX  智  能  控  制  面  板  ★'
    print(f'║{title:^56}║')
    print('╠' + '═' * 56 + '╣')
    print(f'║  {d["time"]:^52}  ║')
    print('╚' + '═' * 56 + '╝')

    # ── 工作区状态 ──
    print()
    print('┌─ 📁 工作区 ───────────────────────────────┐')
    print(f'│  全局文档: {d["total_size"]:>6}B  ({sum(1 for x in d["docs"].values() if x["ok"])}/5)                │')
    for name, info in d['docs'].items():
        s = '✓' if info['ok'] else '✗'
        print(f'│    {s} {name:<30s} {info["size"]:>6}B{" " if info["ok"] else "  MISSING":>8} │')
    print(f'│  项目数: {len(d["projects"])}                                         │')
    if d['projects']:
        for p in d['projects']:
            flag = '📄' if p['has_entry'] else '📁'
            print(f'│    {flag} {p["name"]:<46s} │')
    print(f'│  模板: {"✓ 就绪":<7s}  脚本: {"✓ 就绪" if d["has_scripts"] else "✗ 缺失":<7s}              │')
    print(f'│  临时目录: {"✓" if d["temp_ok"] else "✗":<4s}  交付目录: {"✓" if d["deliv_ok"] else "✗":<4s}              │')
    print('└' + '─' * 52 + '┘')

    # ── 快捷操作 ──
    print()
    print('┌─ ⚡ 快捷操作 ──────────────────────────────┐')
    print('│  [1] 扫描工作区 (scan)                     │')
    print('│  [2] 打开文件夹 (explorer)                 │')
    print('│  [3] 桌面通知 (notify)                     │')
    print('│  [4] 微信消息 (wechat 联系人 内容)         │')
    print('│  [5] 激活窗口 (activate 窗口名)            │')
    print('│  [6] 列出窗口 (windows)                    │')
    print('│  [7] Token 管理 (token_manager.py)         │')
    print('│  [8] GitHub 推送 (需先 git add + commit)   │')
    print('└' + '─' * 52 + '┘')

    # ── 建议 ──
    print()
    print('┌─ 💡 建议 ─────────────────────────────────┐')
    if len(d['projects']) == 0:
        print('│  🟡 还没有项目 → 创建第一个                  │')
        print(f'│     python scripts/create_project.ps1       │')
    if os.path.isdir(WORKSPACE):
        script_count = len(d['scripts'])
        print(f'│  🟢 脚本 {script_count} 个就绪                    │')
    print('│  🟢 GitHub: ' + (d['github'] if d['github'] != '未连接' else '❌ 未连接').ljust(36) + '│')
    if d['tokens']:
        print(f'│  🔑 已保存 {len(d["tokens"])} 个 Token               │')
    print('└' + '─' * 52 + '┘')

    # ── 脚本列表 ──
    print()
    print('┌─ 📜 可用脚本 ─────────────────────────────┐')
    for s in d['scripts'][:12]:
        icon = '🐍' if s['ext'] == '.py' else '📦'
        print(f'│  {icon} {s["name"]:<35s} {s["size"]:>6}B │')
    if len(d['scripts']) > 12:
        print(f'│  ... 还有 {len(d["scripts"]) - 12} 个                         │')
    print('└' + '─' * 52 + '┘')

    print()
    print('提示: 在 Reasonix 里直接告诉我你想做什么')
    print('例如: "发微信给小光说晚上好"')
    print()


if __name__ == '__main__':
    data = get_all_status()
    show_panel(data)
