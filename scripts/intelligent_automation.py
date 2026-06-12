#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intelligent_automation.py — Reasonix 智能自动化引擎

功能：
  status   全面感知工作区+桌面状态，给出智能建议
  suggest  基于上下文推荐下一步操作
  auto     自动执行最合适的操作

特点：
  • 上下文感知 — 扫描工作区 + 桌面窗口 + 微信状态
  • 智能决策 — 基于当前状态推荐最优操作
  • 自动化执行 — 一键执行推荐操作
"""
import sys, os, json, time, subprocess
from datetime import datetime
import uiautomation as auto

WORKSPACE = r'D:\reasonix-workspace'


# ═══════════════ 上下文感知 ═══════════════

def sense_workspace():
    """感知工作区状态"""
    docs = {}
    for name in ['99-全局控制台.md', '91-全局复利与踩坑日志.md',
                 '92-工作区架构与命名规则.md', '93-新项目创建SOP.md', 'AGENTS.md']:
        path = os.path.join(WORKSPACE, name)
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                c = f.read()
            title = ''
            for line in c.split('\n'):
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            docs[name] = {'exists': True, 'title': title, 'size': len(c)}
        else:
            docs[name] = {'exists': False, 'title': '', 'size': 0}

    projects = []
    if os.path.isdir(WORKSPACE):
        for item in sorted(os.listdir(WORKSPACE)):
            fp = os.path.join(WORKSPACE, item)
            if os.path.isdir(fp) and item.startswith('Project_'):
                projects.append(item)

    # Check sub-directories
    has_templates = os.path.isdir(os.path.join(WORKSPACE, 'templates'))
    has_scripts = os.path.isdir(os.path.join(WORKSPACE, 'scripts'))

    return {
        'docs': docs,
        'doc_count': sum(1 for d in docs.values() if d['exists']),
        'projects': projects,
        'project_count': len(projects),
        'has_templates': has_templates,
        'has_scripts': has_scripts,
    }


def sense_desktop():
    """感知桌面状态"""
    result = {
        'windows': [],
        'wechat_running': False,
        'wechat_visible': False,
        'wechat_rect': None,
        'active_window': '',
    }

    try:
        for w in auto.GetRootControl().GetChildren():
            if w.Name:
                r = w.BoundingRectangle
                info = {
                    'name': w.Name.strip(),
                    'x': r.left, 'y': r.top,
                    'w': r.right - r.left,
                    'h': r.bottom - r.top,
                }
                result['windows'].append(info)

                if '\u5fae\u4fe1' in w.Name or '微信' in w.Name:
                    result['wechat_running'] = True
                    if r.left > -100:  # visible on screen
                        result['wechat_visible'] = True
                        result['wechat_rect'] = (r.left, r.top, r.right - r.left, r.bottom - r.top)
    except:
        pass

    result['window_count'] = len(result['windows'])
    return result


def sense_all():
    """全面感知 — 工作区 + 桌面"""
    ws = sense_workspace()
    ds = sense_desktop()
    return {
        'time': datetime.now().isoformat(),
        'workspace': ws,
        'desktop': ds,
    }


# ═══════════════ 智能建议 ═══════════════

def generate_suggestions(context):
    """基于上下文生成智能建议"""
    suggestions = []
    ws = context['workspace']
    ds = context['desktop']

    # 文档检查
    if ws['doc_count'] < 5:
        missing = [k for k, v in ws['docs'].items() if not v['exists']]
        suggestions.append({
            'priority': 'high',
            'action': '修复缺失文档',
            'detail': f'缺少 {len(missing)} 份全局文档: {", ".join(missing)}',
            'command': f'python scripts/reasonix_automation.py scan',
        })

    # 项目建议
    if ws['project_count'] == 0:
        suggestions.append({
            'priority': 'medium',
            'action': '创建第一个项目',
            'detail': '工作区还没有项目，建议创建第一个项目',
            'command': r'powershell -File "D:\reasonix-workspace\scripts\create_project.ps1" -ProjectName "项目名"',
        })

    # 微信状态
    if ds['wechat_running']:
        if not ds['wechat_visible']:
            suggestions.append({
                'priority': 'low',
                'action': '激活微信窗口',
                'detail': '微信正在运行但在后台',
                'command': 'python scripts/reasonix_automation.py activate 微信',
            })
    else:
        suggestions.append({
            'priority': 'low',
            'action': '启动微信',
            'detail': '微信未运行',
            'command': 'start WeChat',
        })

    # 模板目录检查
    if not ws['has_templates']:
        suggestions.append({
            'priority': 'medium',
            'action': '创建模板目录',
            'detail': '项目模板目录不存在',
            'command': f'mkdir "D:\reasonix-workspace\\templates"',
        })

    return suggestions


# ═══════════════ 智能报告 ═══════════════

def cmd_status():
    """输出全面智能状态报告"""
    context = sense_all()
    ws = context['workspace']
    ds = context['desktop']
    suggestions = generate_suggestions(context)

    print('=' * 54)
    print(f'  Reasonix 智能感知报告')
    print(f'  {datetime.now():%Y-%m-%d %H:%M}')
    print('=' * 54)

    print(f'\n📁 工作区')
    print(f'  文档: {ws["doc_count"]}/5')
    for name, info in ws['docs'].items():
        s = '✅' if info['exists'] else '❌'
        print(f'    {s} {name}')
    print(f'  项目: {ws["project_count"]}')
    for p in ws['projects']:
        print(f'    📂 {p}')
    print(f'  模板: {"✅" if ws["has_templates"] else "❌"}')
    print(f'  脚本: {"✅" if ws["has_scripts"] else "❌"}')

    print(f'\n🖥️  桌面')
    print(f'  微信: {"✅ 运行中" if ds["wechat_running"] else "❌ 未运行"}')
    if ds['wechat_visible']:
        print(f'  微信窗口可见: ✅')
    print(f'  总窗口数: {ds["window_count"]}')

    print(f'\n💡 智能建议 ({len(suggestions)})')
    for s in suggestions:
        icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(s['priority'], '⚪')
        print(f'  {icon} [{s["priority"]}] {s["action"]}')
        print(f'     {s["detail"]}')
        print(f'     → {s["command"]}')

    print()
    print('=' * 54)
    print('  可用命令: python intelligent_automation.py suggest')
    print('            python intelligent_automation.py auto')
    print('=' * 54)

    return context


def cmd_suggest():
    """输出智能建议"""
    context = sense_all()
    suggestions = generate_suggestions(context)

    print(f'💡 智能建议 ({len(suggestions)})')
    for i, s in enumerate(suggestions, 1):
        icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(s['priority'], '⚪')
        print(f'\n{icon} 建议 {i}: {s["action"]}')
        print(f'   优先级: {s["priority"]}')
        print(f'   说明: {s["detail"]}')
        print(f'   命令: {s["command"]}')


def cmd_auto():
    """自动执行最高优先级的建议"""
    context = sense_all()
    suggestions = generate_suggestions(context)

    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    suggestions.sort(key=lambda x: priority_order.get(x['priority'], 99))

    if not suggestions:
        print('一切正常，无需操作 ✅')
        return

    top = suggestions[0]
    print(f'自动执行: {top["action"]}')
    print(f'命令: {top["command"]}')
    # Execute
    os.system(top['command'])
    print(f'执行完毕 ✅')


# ═══════════════ 入口 ═══════════════

if __name__ == '__main__':
    if len(sys.argv) < 2:
        cmd_status()
    elif sys.argv[1] == 'status':
        cmd_status()
    elif sys.argv[1] == 'suggest':
        cmd_suggest()
    elif sys.argv[1] == 'auto':
        cmd_auto()
    else:
        print('用法: python intelligent_automation.py [status|suggest|auto]')
