#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reasonix_automation.py — Reasonix 统一自动化引擎

子命令：
  scan             扫描工作区（文档+项目）
  explorer         打开资源管理器
  windows          列出所有窗口
  activate <标题>   激活指定窗口
  notify           桌面通知
  wechat <人> <消息>  发送微信消息
  help             帮助信息
"""
import sys, os, json, time, subprocess
from datetime import datetime
import pyautogui, pyperclip
import uiautomation as auto

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.25

WORKSPACE = r'D:\reasonix-workspace'


# ── 工作区扫描 ──

def cmd_scan():
    docs = {}
    for name in ['99-全局控制台.md', '92-工作区架构与命名规则.md',
                 '93-新项目创建SOP.md', '91-全局复利与踩坑日志.md', 'AGENTS.md']:
        path = os.path.join(WORKSPACE, name)
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                c = f.read()
            title = ''
            for line in c.split('\n'):
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            docs[name] = {'title': title, 'size': len(c)}
        else:
            docs[name] = {'title': '(missing)', 'size': 0}

    projects = []
    if os.path.isdir(WORKSPACE):
        for item in sorted(os.listdir(WORKSPACE)):
            fp = os.path.join(WORKSPACE, item)
            if os.path.isdir(fp) and item.startswith('Project_'):
                projects.append(item)

    # Check temp/deliv
    base_parent = os.path.dirname(WORKSPACE)
    ws_name = os.path.basename(WORKSPACE)
    temp_ok = os.path.isdir(os.path.join(base_parent, ws_name + '_temp'))
    deliv_ok = os.path.isdir(os.path.join(base_parent, ws_name + '_deliverables'))

    print('=' * 50)
    print(f'  Reasonix Workspace - {datetime.now():%Y-%m-%d %H:%M}')
    print('=' * 50)
    print(f'\nDocs ({sum(1 for d in docs.values() if d["size"]>0)}/5):')
    for name, info in docs.items():
        s = 'OK' if info['size'] else '--'
        print(f'  [{s}] {name} ({info["size"]}B)')
    print(f'\nProjects: {len(projects)}')
    for p in projects:
        print(f'  - {p}')
    print(f'\nTemp:   {temp_ok}')
    print(f'Deliv:  {deliv_ok}')

    data = {
        'workspace': WORKSPACE,
        'docs': {k: {'title': v['title'], 'path': os.path.join(WORKSPACE, k)}
                 for k, v in docs.items()},
        'projects': projects,
    }
    with open(os.path.join(WORKSPACE, '.workspace_state.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ── 桌面操作 ──

def cmd_explorer():
    subprocess.Popen(['explorer', WORKSPACE])
    print(f'Explorer: {WORKSPACE}')


def cmd_windows():
    wins = []
    for w in auto.GetRootControl().GetChildren():
        if w.Name:
            r = w.BoundingRectangle
            wins.append({
                'name': w.Name.strip(),
                'x': r.left, 'y': r.top,
                'w': r.right - r.left,
                'h': r.bottom - r.top,
            })
    print(f'Windows ({len(wins)}):')
    for w in sorted(wins, key=lambda x: -x['h']):
        name = w['name'][:40]
        print(f'  {name:40s} ({w["x"]},{w["y"]}) {w["w"]}x{w["h"]}')


def cmd_activate(title):
    win = auto.WindowControl(searchDepth=1, Name=title)
    if win.Exists(maxSearchSeconds=2):
        win.SwitchToThisWindow()
        print(f'Activated: {title}')
        return True
    for w in auto.GetRootControl().GetChildren():
        if w.Name and title in w.Name:
            auto.WindowControl(searchDepth=1, Name=w.Name).SwitchToThisWindow()
            print(f'Activated: {w.Name}')
            return True
    print(f'Not found: {title}')
    return False


def cmd_notify():
    count = 0
    for name in ['99-全局控制台.md', '91-全局复利与踩坑日志.md',
                 '92-工作区架构与命名规则.md', '93-新项目创建SOP.md', 'AGENTS.md']:
        if os.path.isfile(os.path.join(WORKSPACE, name)):
            count += 1
    import ctypes
    msg = f'Workspace: {count}/5 docs\n{WORKSPACE}'
    ctypes.windll.user32.MessageBoxW(0, msg, 'Reasonix Automation', 0x40 | 0x1000)


# ── 微信操作 ──

def cmd_wechat(contact, message):
    wx = auto.WindowControl(searchDepth=1, Name='\u5fae\u4fe1')
    if not wx.Exists(maxSearchSeconds=2):
        print('WeChat not found')
        return False
    wx.SwitchToThisWindow()
    time.sleep(0.6)

    r = wx.BoundingRectangle
    left, top, right, bottom = r.left, r.top, r.right, r.bottom

    # Search contact
    pyautogui.click(left + 100, top + 40)
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.15)
    pyperclip.copy(contact)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.7)

    # Click result
    pyautogui.click(left + 120, top + 100)
    time.sleep(0.4)

    # Focus input (double click)
    ix, iy = left + (right - left) // 2 + 50, bottom - 60
    pyautogui.click(ix, iy)
    time.sleep(0.15)
    pyautogui.click(ix, iy)
    time.sleep(0.3)

    # Send message
    pyperclip.copy(message)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.25)
    pyautogui.press('enter')
    print(f'WeChat -> {contact}: {message[:30]}')
    return True


# ── 入口 ──

def main():
    if len(sys.argv) < 2:
        print('Reasonix Automation\n子命令: scan | explorer | windows | activate <标题> | notify | wechat <人> <消息> | help')
        return

    cmd = sys.argv[1]

    if cmd == 'scan':
        cmd_scan()
    elif cmd == 'explorer':
        cmd_explorer()
    elif cmd == 'windows':
        cmd_windows()
    elif cmd == 'activate' and len(sys.argv) > 2:
        cmd_activate(sys.argv[2])
    elif cmd == 'notify':
        cmd_notify()
    elif cmd == 'wechat' and len(sys.argv) > 3:
        cmd_wechat(sys.argv[2], sys.argv[3])
    elif cmd == 'help':
        print('子命令: scan | explorer | windows | activate <标题> | notify | wechat <人> <消息>')
    else:
        print(f'Unknown: {cmd}')
        print('子命令: scan | explorer | windows | activate <标题> | notify | wechat <人> <消息>')


if __name__ == '__main__':
    main()
