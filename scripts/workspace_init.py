#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
workspace_init.py — workspace-ready core automation.

Implements four methods:
  1) computer-use skill   - invoked externally for full desktop control
  2) python               - local PC file operations (this script)
  3) pyautogui            - GUI desktop actions (open explorer)
  4) ctypes/Win32 API     - system notifications

Usage:
    python workspace_init.py                    # scan + summary
    python workspace_init.py --project 项目名     # focus on a project
    python workspace_init.py --explorer          # open workspace in Explorer
    python workspace_init.py --notify            # show Windows popup
"""
import sys, os, json, glob
from datetime import datetime
import time

WORKSPACE = r'D:\reasonix-workspace'

# ── Method 2: Local PC operations ──────────────────────────

def read_global_docs():
    """Read all global docs and return structured summary."""
    docs_order = ['99-全局控制台.md', '92-工作区架构与命名规则.md',
                  '93-新项目创建SOP.md', '91-全局复利与踩坑日志.md',
                  'AGENTS.md']
    result = {}
    for name in docs_order:
        path = os.path.join(WORKSPACE, name)
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            lines = content.split('\n')
            # Extract title and first meaningful paragraph
            title = ''
            summary = ''
            for line in lines:
                line = line.strip()
                if line.startswith('# ') and not title:
                    title = line[2:].strip()
                elif line and not line.startswith('#') and not line.startswith('>') and not line.startswith('---') and not summary:
                    summary = line[:100]
            result[name] = {'title': title, 'size': len(content), 'summary': summary}
        else:
            result[name] = {'title': '(missing)', 'size': 0, 'summary': ''}
    return result

def scan_projects():
    """Scan project directories."""
    projects = []
    if not os.path.isdir(WORKSPACE):
        return projects
    for item in sorted(os.listdir(WORKSPACE)):
        item_path = os.path.join(WORKSPACE, item)
        if os.path.isdir(item_path) and item.startswith('Project_'):
            # Check for project entry file
            entry_files = [f for f in os.listdir(item_path) if f.startswith('90-') or f.startswith('91-')]
            projects.append({
                'name': item,
                'path': item_path,
                'has_entry': len(entry_files) > 0,
                'entry_files': entry_files[:3]
            })
    return projects

def format_summary(docs, projects):
    """Format workspace summary."""
    lines = []
    lines.append('=' * 50)
    lines.append(f'  Reasonix Workspace - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append('=' * 50)
    lines.append('')
    lines.append(f'[Global Docs]')
    for name, info in docs.items():
        status = 'OK' if info['size'] > 0 else 'MISS'
        lines.append(f'  {status} {name} ({info["size"]}B)')
    lines.append('')
    lines.append(f'[Projects: {len(projects)}]')
    if projects:
        for p in projects:
            flag = 'E' if p['has_entry'] else ' '
            lines.append(f'  {flag} {p["name"]}')
    else:
        lines.append('  (no projects yet)')
    lines.append('')
    lines.append(f'[Temp]  {os.path.isdir(r"D:\reasonix-workspace_temp")}')
    lines.append(f'[Deliv] {os.path.isdir(r"D:\reasonix-workspace_deliverables")}')
    lines.append('')
    lines.append('Tip: use --explorer to open workspace in Explorer')
    lines.append('     use --notify to show Windows popup')
    lines.append('=' * 50)
    return '\n'.join(lines)

# ── Method 3: pyautogui ───────────────────────────────────

def open_explorer(path=None):
    """Open workspace in File Explorer."""
    import subprocess
    target = path or WORKSPACE
    subprocess.Popen(['explorer', target])
    print(f'Opened Explorer: {target}')

# ── Method 4: ctypes Win32 API ────────────────────────────

def show_notification(title, message):
    """Show Windows message box via ctypes."""
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1000)  # MB_ICONINFORMATION | MB_SYSTEMMODAL

# ── Method 1: computer-use skill hook ──────────────────────

def export_json():
    """Export structured data for computer-use skill to consume."""
    docs = read_global_docs()
    projects = scan_projects()
    data = {
        'workspace': WORKSPACE,
        'docs': {k: {'title': v['title'], 'path': os.path.join(WORKSPACE, k)} for k, v in docs.items()},
        'projects': [{'name': p['name'], 'path': p['path']} for p in projects],
        'project_count': len(projects),
    }
    # Write to a JSON file for the computer-use skill to read
    out_path = os.path.join(WORKSPACE, '.workspace_state.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'State exported: {out_path}')
    return data


# ── Method 3b: uiautomation (Windows UIA, replaces pyautogui for UI ops) ──

def open_explorer_uia(path=None):
    """Open Explorer via UIA (more reliable than subprocess)."""
    import subprocess
    target = path or WORKSPACE
    subprocess.Popen(['explorer', target])
    print(f'Opened: {target}')

def activate_window_uia(window_title):
    """Activate a window by title using UIA."""
    try:
        import uiautomation as auto
        win = auto.WindowControl(searchDepth=1, Name=window_title)
        if win.Exists(maxSearchSeconds=2):
            win.SetTopmost(True)
            time.sleep(0.3)
            win.SetTopmost(False)
            return True
    except Exception as e:
        print(f'UIA activate failed: {e}')
    return False

def list_windows_uia():
    """List windows via UIA."""
    try:
        import uiautomation as auto
        wins = auto.GetRootControl().GetChildren()
        result = []
        for w in wins:
            if w.Name:
                rect = w.BoundingRectangle
                result.append({'name': w.Name, 'left': rect.left, 'top': rect.top, 'width': rect.width(), 'height': rect.height()})
        return result
    except Exception:
        return []

def show_notification(title, message):
    """Show Windows message box via ctypes."""
    import ctypes
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x40 | 0x1000)

# ── Main ──────────────────────────────────────────────────

def main():
    if '--explorer' in sys.argv:
        open_explorer()
        return
    if '--notify' in sys.argv:
        docs = read_global_docs()
        projects = scan_projects()
        summary = f'Workspace: {len(projects)} projects, {sum(1 for d in docs.values() if d["size"] > 0)} docs'
        show_notification('Reasonix Workspace', summary)
        return
    if '--windows' in sys.argv:
        wins = list_windows_uia()
        print(f'Windows ({len(wins)}):')
        for w in wins:
            print(f'  {w["name"][:40]:40s} ({w["left"]},{w["top"]}) {w["width"]}x{w["height"]}')
        return
    if '--uia-activate' in sys.argv:
        idx = sys.argv.index('--uia-activate')
        if idx + 1 < len(sys.argv):
            name = sys.argv[idx + 1]
            ok = activate_window_uia(name)
            print(f'Activate "{name}": {"OK" if ok else "FAIL"}')
        return
    if '--export' in sys.argv:
        export_json()
        return

    # Default: full summary
    docs = read_global_docs()
    projects = scan_projects()
    output = format_summary(docs, projects)
    print(output)

    # Auto-export for computer-use
    export_json()

if __name__ == '__main__':
    main()
